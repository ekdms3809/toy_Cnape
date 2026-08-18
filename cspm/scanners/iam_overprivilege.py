"""[기능 1] IAM 과잉 권한·미사용 키 탐지 — 스텁.

탐지 로직 미구현. 2026-07-17 리뷰에서 Action=="*" 단순 매칭은 실무 미달 판정 — 재설계 대상.

재설계 시 반영해야 할 항목(확정된 결함 목록):
- glob 패턴 매칭 (예: iam:*, s3:Get* 등 와일드카드 확장)
- NotAction / NotResource 처리
- Effect(Allow/Deny) 우선순위, Condition 존재 시 평가
- 권한상승 조합 탐지 (예: iam:CreatePolicyVersion, iam:PassRole+lambda 등)
- 리소스 기반 정책까지 고려
- 미사용 키: 90일 기준 (GetAccessKeyLastUsed)
"""

from __future__ import annotations

from cspm.core.finding import Finding
from cspm.core.scanner import BaseScanner


class IamOverprivilegeScanner(BaseScanner):
    name = "iam"
    service = "iam"
    description = "과잉 권한 정책 + 90일 미사용 액세스키 탐지"

    def scan(self) -> list[Finding]:
        raise NotImplementedError("재설계 후 구현 — 모듈 docstring 참고")
