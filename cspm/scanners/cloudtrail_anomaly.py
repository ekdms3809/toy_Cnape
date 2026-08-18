"""[기능 4] CloudTrail 이상 API 탐지 — 스텁 (난이도 최상, 마지막 구현).

탐지 로직 미구현. 판단 기준 확정 후 구현한다.

확정 필요한 판단 기준(초안):
- root 계정 사용 이벤트 (userIdentity.type == "Root")
- MFA 없는 콘솔 로그인 (ConsoleLogin + additionalEventData.MFAUsed)
- 조회 방식: LookupEvents API vs S3 로그 파일 파싱 — 범위/비용 트레이드오프 결정 필요
- 조회 기간 기본값 결정 필요
"""

from __future__ import annotations

from cspm.core.finding import Finding
from cspm.core.scanner import BaseScanner


class CloudTrailAnomalyScanner(BaseScanner):
    name = "cloudtrail"
    service = "cloudtrail"
    description = "root 로그인·MFA 우회 시도 탐지"

    def scan(self) -> list[Finding]:
        raise NotImplementedError("판단 기준 확정 대기 — 모듈 docstring 참고")
