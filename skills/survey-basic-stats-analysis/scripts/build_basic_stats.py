"""survey-basic-stats-analysis canonical script.

Computes per-question descriptive statistics from a `cleaned_dataset.csv` +
`column_ledger.csv` pair produced by survey-data-preprocessing's
`build_cleaned_dataset.py`. Covers the three question families that carry the
bulk of analytical weight in native surveys:

- scale: mean, std, Top2 (score 6-7 of a 7-point scale), Bottom2 (1-2),
  full 1-7 distribution
- multiple-choice: per-option count, respondent-based % (of respondents who
  answered this question family) and response-based % (of total selections
  made within the family)
- ranking (max-N-choices style): same two percentage bases as
  multiple-choice, plus a weighted score (rank 1 = 3pt, rank 2 = 2pt,
  rank 3 = 1pt — the convention already used in native's own interim
  reports)

Verified against `26.GP.UXQ` survey2 (see validation_runs/survey-basic-stats-analysis/2026-08-19_26.GP.UXQ/
04_validation_notes.md) by reproducing exact figures from the
2026-08-17 validation round's `question_level_stats.csv` for a sample of
scale and ranking questions. Single-choice questions with a "완료 여부"-style
marker column (e.g. P3B2) are NOT fully replicated — see that same notes file
for the documented gap before trusting this script on that question type.

Usage:
    python build_basic_stats.py <cleaned_dataset.csv> <column_ledger.csv> <out_dir>
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def group_columns_by_question(ledger_rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in ledger_rows:
        if row["is_meta"] in ("True", "true"):
            continue
        groups[row["question_code"]].append(row)
    return groups


def to_number(value: str):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def scale_stats(question_code: str, question_text: str, column_key: str, data_rows: list[dict]) -> list[dict]:
    values = [to_number(row.get(column_key)) for row in data_rows]
    values = [v for v in values if v is not None]
    base_n = len(values)
    out = []
    if base_n == 0:
        return out

    mean = round(statistics.fmean(values), 3)
    std = round(statistics.stdev(values), 3) if base_n > 1 else 0.0
    top2 = sum(1 for v in values if v >= 6)
    bottom2 = sum(1 for v in values if v <= 2)

    out.append(_row(question_code, "scale", question_text, "summary", "mean", mean=mean, base_n=base_n))
    out.append(_row(question_code, "scale", question_text, "summary", "std", std=std, base_n=base_n))
    out.append(
        _row(
            question_code, "scale", question_text, "summary", "top2",
            count=top2, top_box=round(100 * top2 / base_n, 2), base_n=base_n,
        )
    )
    out.append(
        _row(
            question_code, "scale", question_text, "summary", "bottom2",
            count=bottom2, bottom_box=round(100 * bottom2 / base_n, 2), base_n=base_n,
        )
    )
    dist = defaultdict(int)
    for v in values:
        dist[int(v)] += 1
    for score in sorted(dist):
        cnt = dist[score]
        out.append(
            _row(
                question_code, "scale", question_text, "distribution", str(score),
                count=cnt, percentage=round(100 * cnt / base_n, 2), base_n=base_n,
            )
        )
    return out


def choice_or_ranking_stats(
    question_code: str, question_text: str, cols: list[dict], data_rows: list[dict], qtype: str
) -> list[dict]:
    col_keys = [c["column_key"] for c in cols]
    option_of = {c["column_key"]: (c.get("option_label") or c["column_key"]) for c in cols}

    respondent_answered = 0
    total_selections = 0
    option_count: dict = defaultdict(int)
    option_weighted: dict = defaultdict(float)

    for row in data_rows:
        row_has_answer = False
        for key in col_keys:
            raw = row.get(key)
            if raw in (None, ""):
                continue
            row_has_answer = True
            option = option_of[key]
            total_selections += 1
            option_count[option] += 1
            if qtype == "ranking":
                rank = to_number(raw)
                if rank is not None and rank in (1, 2, 3):
                    option_weighted[option] += {1: 3, 2: 2, 3: 1}[int(rank)]
        if row_has_answer:
            respondent_answered += 1

    base_n = respondent_answered
    out = []
    for option, cnt in sorted(option_count.items(), key=lambda kv: -kv[1]):
        respondent_pct = round(100 * cnt / base_n, 2) if base_n else None
        response_pct = round(100 * cnt / total_selections, 2) if total_selections else None
        extra = {}
        if qtype == "ranking":
            extra["weighted_score"] = option_weighted.get(option, 0)
        out.append(
            _row(
                question_code, qtype, question_text, "distribution", option,
                count=cnt, respondent_based_percentage=respondent_pct,
                response_based_percentage=response_pct, base_n=base_n, **extra,
            )
        )
    return out


def _row(question_code, question_type, question_text, stat_kind, stat_label, **kwargs) -> dict:
    row = {
        "question_code": question_code,
        "question_type": question_type,
        "question_text": question_text,
        "stat_kind": stat_kind,
        "stat_label": stat_label,
        "count": "",
        "percentage": "",
        "respondent_based_percentage": "",
        "response_based_percentage": "",
        "mean": "",
        "std": "",
        "top_box": "",
        "bottom_box": "",
        "base_n": "",
        "weighted_score": "",
    }
    row.update(kwargs)
    return row


def infer_question_type(cols: list[dict], data_rows: list[dict], option_labels: list) -> str:
    if len(cols) == 1:
        col_key = cols[0]["column_key"]
        values = [to_number(row.get(col_key)) for row in data_rows]
        numeric = [v for v in values if v is not None]
        non_null = [row.get(col_key) for row in data_rows if row.get(col_key) not in (None, "")]
        if numeric and len(numeric) == len(non_null):
            return "scale"
        return "single-choice"

    # multi-column: ranking if values are small integers (rank positions)
    sample_vals = []
    for c in cols:
        for row in data_rows:
            v = row.get(c["column_key"])
            if v not in (None, ""):
                sample_vals.append(v)
    numeric_like = sum(1 for v in sample_vals if to_number(v) is not None and to_number(v) in (1, 2, 3))
    if sample_vals and numeric_like / len(sample_vals) >= 0.9:
        return "ranking"
    return "multiple-choice"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cleaned_dataset_csv")
    parser.add_argument("column_ledger_csv")
    parser.add_argument("out_dir")
    args = parser.parse_args()

    data_rows = load_csv(Path(args.cleaned_dataset_csv))
    ledger_rows = load_csv(Path(args.column_ledger_csv))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    groups = group_columns_by_question(ledger_rows)

    all_stat_rows: list[dict] = []
    for question_code, cols in groups.items():
        question_text = cols[0]["question_text"]
        option_labels = [c.get("option_label") for c in cols]
        qtype = infer_question_type(cols, data_rows, option_labels)
        if qtype == "scale":
            all_stat_rows.extend(scale_stats(question_code, question_text, cols[0]["column_key"], data_rows))
        elif qtype in ("multiple-choice", "ranking"):
            all_stat_rows.extend(choice_or_ranking_stats(question_code, question_text, cols, data_rows, qtype))
        # single-choice left out of this pass — see module docstring.

    fieldnames = [
        "question_code", "question_type", "question_text", "stat_kind", "stat_label",
        "count", "percentage", "respondent_based_percentage", "response_based_percentage",
        "mean", "std", "top_box", "bottom_box", "base_n", "weighted_score",
    ]
    out_path = out_dir / "question_level_stats.csv"
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_stat_rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"wrote {len(all_stat_rows)} stat rows for {len(groups)} question families -> {out_path}")


if __name__ == "__main__":
    main()
