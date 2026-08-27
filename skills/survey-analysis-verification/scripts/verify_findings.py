"""survey-analysis-verification canonical script.

Computes RQ/RH-tagged findings from `cleaned_dataset.csv` given a declarative
config that says *which columns* test *which hypothesis* and *how* (the
semantic judgment call a researcher/analyst makes once by reading the RH
catalog against the question metadata — see `configs/`). The statistical
computation itself is fully deterministic and reusable; the config is what
changes per project.

Two finding kinds are implemented:
- `correlation`: Pearson r between two numeric columns.
- `count_to_outcome`: derives a per-respondent selection count from a
  multi-select block (e.g. how many options they picked in a ranking/
  checkbox question), then correlates that count against one or more
  numeric outcome columns, plus a mean-by-count breakdown.

Verified against `26.GP.UXQ` survey2 by reproducing two of the five findings
in the 2026-08-17 validation round's `verified_key_findings.json` exactly
(RH02 correlation r=0.702; RH05 function_count_r=0.154, type_count_r=0.184).
RH03 (old-vs-new friction group comparison) and RH09 (positive-reason vs
recommendation gap) are NOT reproduced yet — the specific column and category
values those two hypotheses group respondents by were not re-identified in
this session. See `04_validation_notes.md` next to this output for the exact
gap description before extending the config for those two.

Usage:
    python verify_findings.py <cleaned_dataset.csv> <config.json> <out_dir>
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_number(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    denom = (var_x * var_y) ** 0.5
    return cov / denom if denom else 0.0


def compute_correlation(spec: dict, data_rows: list[dict]) -> dict:
    col_a, col_b = spec["columns"]
    pairs = [
        (to_number(row.get(col_a)), to_number(row.get(col_b)))
        for row in data_rows
    ]
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    xs, ys = zip(*pairs) if pairs else ([], [])
    r = round(pearson_r(list(xs), list(ys)), 3) if pairs else None
    return {
        "finding_id": spec["finding_id"],
        "rq_ids": spec.get("rq_ids", []),
        "rh_ids": spec.get("rh_ids", []),
        "source_question_ids": [col_a, col_b],
        "metric_name": spec["metric_name"],
        "metric_value": r,
        "base_n": len(pairs),
        "verification_status": "verified_descriptive",
        "caveat": "Correlation only, no p-value",
        "narrative_summary": spec.get("narrative_template", "").format(r=r, n=len(pairs)),
    }


def compute_count_to_outcome(spec: dict, data_rows: list[dict]) -> dict:
    select_cols = spec["select_columns"]
    outcome_col = spec["outcome_column"]

    counts = []
    outcomes = []
    for row in data_rows:
        outcome = to_number(row.get(outcome_col))
        if outcome is None:
            continue
        n_selected = sum(1 for c in select_cols if row.get(c) not in (None, ""))
        counts.append(n_selected)
        outcomes.append(outcome)

    r = round(pearson_r([float(c) for c in counts], outcomes), 3) if counts else None

    by_count: dict = {}
    for c, o in zip(counts, outcomes):
        by_count.setdefault(c, []).append(o)
    mean_by_count = {str(k): round(statistics.fmean(v), 3) for k, v in sorted(by_count.items())}

    return {
        "finding_id": spec["finding_id"],
        "rq_ids": spec.get("rq_ids", []),
        "rh_ids": spec.get("rh_ids", []),
        "source_question_ids": select_cols[:1] + [outcome_col],
        "metric_name": spec["metric_name"],
        "metric_value": {"correlation_r": r, "mean_by_count": mean_by_count},
        "base_n": len(counts),
        "verification_status": "verified_descriptive",
        "caveat": "No inferential test",
        "narrative_summary": spec.get("narrative_template", "").format(r=r, n=len(counts)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cleaned_dataset_csv")
    parser.add_argument("config_json")
    parser.add_argument("out_dir")
    args = parser.parse_args()

    data_rows = load_csv(Path(args.cleaned_dataset_csv))
    config = json.loads(Path(args.config_json).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    findings = []
    findings.append(
        {
            "finding_id": "total_n",
            "rq_ids": [],
            "rh_ids": [],
            "source_question_ids": [],
            "metric_name": "total_n",
            "metric_value": len(data_rows),
            "base_n": len(data_rows),
            "verification_status": "verified",
            "caveat": "schema validation run only",
            "narrative_summary": f"Raw export contains {len(data_rows)} rows.",
        }
    )

    for spec in config.get("findings", []):
        if spec["kind"] == "correlation":
            findings.append(compute_correlation(spec, data_rows))
        elif spec["kind"] == "count_to_outcome":
            findings.append(compute_count_to_outcome(spec, data_rows))
        else:
            raise ValueError(f"unknown finding kind: {spec['kind']}")

    out_path = out_dir / "verified_key_findings.json"
    out_path.write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(findings)} findings -> {out_path}")


if __name__ == "__main__":
    main()
