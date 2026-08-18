"""[기능 5] 자동 수정 제안 — 스텁.

원칙(확정): dry-run 스크립트 생성만. 자동 실행 금지.
탐지 4종 구현 완료 후 Finding.remediation 필드 기반으로 통합 구현한다.
"""

from __future__ import annotations

from cspm.core.finding import Finding


def generate_fix_script(findings: list[Finding]) -> str:
    raise NotImplementedError("탐지 4종 구현 후 통합 — 자동 실행 금지, dry-run 제안만")
