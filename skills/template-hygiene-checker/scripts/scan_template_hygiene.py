from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json", ".html", ".css", ".js", ".py", ".yaml", ".yml", ".toml"}
OFFICE_EXTENSIONS = {".docx", ".pptx", ".xlsx"}


@dataclass
class Finding:
    file: str
    location: str
    category: str
    severity: str
    evidence: str
    recommendation: str
    rule_id: str


RULES: list[tuple[str, str, str, str, re.Pattern[str], str]] = [
    (
        "R001",
        "secret_or_token",
        "critical",
        "Secret-like token detected.",
        re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
        "Remove the secret and rotate it if it was real.",
    ),
    (
        "R002",
        "direct_pii",
        "critical",
        "Email address detected.",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "Remove or replace with a placeholder email.",
    ),
    (
        "R003",
        "direct_pii",
        "critical",
        "Korean mobile phone number pattern detected.",
        re.compile(r"\b01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}\b"),
        "Remove or replace with a placeholder phone number.",
    ),
    (
        "R004",
        "direct_pii",
        "critical",
        "Account-like long number detected.",
        re.compile(r"\b\d{2,6}[-\s]\d{2,6}[-\s]\d{4,8}(?:[-\s]\d{1,4})?\b"),
        "Confirm whether this is a real account/ID value and replace if reusable.",
    ),
    (
        "R005",
        "internal_path",
        "high",
        "Local or internal path detected.",
        re.compile(r"(?i)([A-Z]:\\Users\\|내 드라이브|공유 드라이브|Documents\\GitHub|/Users/|/home/)"),
        "Replace with a portable relative path or remove before distribution.",
    ),
    (
        "R006",
        "real_project_identifier",
        "high",
        "Hana/project-specific identifier detected.",
        re.compile(r"(하나금융그룹|하나은행|하나금융융합기술원|AI연금투자솔루션|하나원큐|하나1Q|GBIUX|BIZWEB|BIZMOB|PAYAI|UXQ|MTSUX|HANAEZ)"),
        "If this is a generic template, replace project-specific values with placeholders after owner review.",
    ),
    (
        "R007",
        "comment_unresolved",
        "high",
        "Unresolved verification or data-quality note detected.",
        re.compile(r"(검증\s*필요|재확인|불일치|신뢰성|quote reliability|sample size|N\s*불일치|확인\s*필요)"),
        "Preserve and route to the owner; do not delete as simple residue.",
    ),
    (
        "R008",
        "editing_residue",
        "medium",
        "TODO/FIXME/editing note detected.",
        re.compile(r"(?i)(TODO|FIXME|TBD|임시|초안|나중에|수정\s*필요|작업\s*메모)"),
        "Clean in a copy or resolve before template release.",
    ),
    (
        "R009",
        "placeholder_conflict",
        "medium",
        "Explicit placeholder detected.",
        re.compile(r"(\[[^\]\n]{2,30}\]|\{[^}\n]{2,30}\}|<[^>\n]{2,30}>)"),
        "Check whether the artifact consistently uses placeholders instead of real values.",
    ),
    (
        "R010",
        "editing_residue",
        "low",
        "Repeated filler text detected.",
        re.compile(r"(내용\s*){3,}|(텍스트\s*){3,}|lorem ipsum", re.I),
        "Remove harmless filler when preparing a clean template.",
    ),
    (
        "R011",
        "broken_text",
        "medium",
        "Likely encoding residue detected.",
        re.compile(r"(���|ì|ë|í|ðŸ|\\u[0-9a-fA-F]{4})"),
        "Repair encoding from source or regenerate the export.",
    ),
]


def iter_target_files(target: Path) -> Iterable[Path]:
    if target.is_file():
        yield target
        return
    for path in target.rglob("*"):
        if path.is_file() and not any(part in {"__pycache__", ".git", "node_modules"} for part in path.parts):
            yield path


def safe_excerpt(text: str, start: int, end: int, limit: int = 160) -> str:
    left = max(0, start - 50)
    right = min(len(text), end + 50)
    excerpt = re.sub(r"\s+", " ", text[left:right]).strip()
    if len(excerpt) > limit:
        excerpt = excerpt[: limit - 3] + "..."
    return excerpt


def extract_office_text(path: Path) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            if not (
                name.startswith("word/")
                or name.startswith("ppt/")
                or name.startswith("xl/")
                or name.startswith("docProps/")
            ):
                continue
            try:
                root = ET.fromstring(archive.read(name))
            except ET.ParseError:
                continue
            texts = [node.text for node in root.iter() if node.text and node.text.strip()]
            if texts:
                chunks.append((name, "\n".join(texts)))
    return chunks


def extract_text_chunks(path: Path) -> list[tuple[str, str]]:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        try:
            return [(path.name, path.read_text(encoding="utf-8"))]
        except UnicodeDecodeError:
            return [(path.name, path.read_text(encoding="utf-8", errors="replace"))]
    if suffix in OFFICE_EXTENSIONS:
        try:
            return extract_office_text(path)
        except zipfile.BadZipFile:
            return []
    return []


def scan_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    relative = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    for location, text in extract_text_chunks(path):
        for rule_id, category, severity, label, pattern, recommendation in RULES:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        file=relative,
                        location=location,
                        category=category,
                        severity=severity,
                        evidence=safe_excerpt(text, match.start(), match.end()),
                        recommendation=recommendation,
                        rule_id=rule_id,
                    )
                )
    return findings


def write_reports(findings: list[Finding], output_dir: Path, target: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(item) for item in findings]

    json_path = output_dir / "hygiene_findings.json"
    csv_path = output_dir / "hygiene_findings.csv"
    md_path = output_dir / "hygiene_report.md"

    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "location", "category", "severity", "evidence", "recommendation", "rule_id"])
        writer.writeheader()
        writer.writerows(rows)

    severity_order = ["critical", "high", "medium", "low"]
    counts = {severity: sum(1 for item in findings if item.severity == severity) for severity in severity_order}
    lines = [
        "# Template hygiene report",
        "",
        f"- target: `{target}`",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- total_findings: {len(findings)}",
        f"- critical: {counts['critical']}",
        f"- high: {counts['high']}",
        f"- medium: {counts['medium']}",
        f"- low: {counts['low']}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No findings detected by the current rules. This does not guarantee release safety.")
    else:
        for item in sorted(findings, key=lambda x: (severity_order.index(x.severity), x.file, x.location, x.rule_id)):
            lines.extend(
                [
                    f"### {item.severity.upper()} · {item.category} · {item.rule_id}",
                    "",
                    f"- file: `{item.file}`",
                    f"- location: `{item.location}`",
                    f"- evidence: {item.evidence}",
                    f"- recommendation: {item.recommendation}",
                    "",
                ]
            )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan reusable UXR template artifacts for hygiene risks.")
    parser.add_argument("target", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("validation_runs/template-hygiene-checker/latest"))
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists():
        raise FileNotFoundError(target)
    root = target if target.is_dir() else target.parent

    findings: list[Finding] = []
    for path in iter_target_files(target):
        findings.extend(scan_file(path, root))

    write_reports(findings, args.output_dir, target)
    print(f"target={target}")
    print(f"files_scanned={sum(1 for _ in iter_target_files(target))}")
    print(f"findings={len(findings)}")
    print(f"report={args.output_dir / 'hygiene_report.md'}")


if __name__ == "__main__":
    main()
