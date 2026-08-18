"""리포트 출력. 콘솔 요약 + reports/ 아래 JSON 저장."""

from __future__ import annotations

import json
import datetime
from pathlib import Path

from cspm.core.finding import Finding, Severity

SEVERITY_ORDER = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]


def print_summary(findings: list[Finding]) -> None:
    if not findings:
        print("탐지된 항목 없음.")
        return
    print(f"\n총 {len(findings)}건 탐지")
    for sev in SEVERITY_ORDER:
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        print(f"\n[{sev.value}] {len(group)}건")
        for f in group:
            print(f"  - {f.check_id} | {f.service} | {f.resource_id} | {f.title}")


def write_json(findings: list[Finding], output_dir: str | Path = "reports") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out / f"findings_{ts}.json"
    path.write_text(
        json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
