"""[기능 2] S3 오설정 감지 — 스텁.

탐지 로직 미구현. 판단 기준 확정 후 구현한다.

확정 필요한 판단 기준(초안):
- 퍼블릭 여부는 ACL + 버킷 정책 + Public Access Block 3개를 종합해 '유효 권한'으로 판단
  (하나만 보고 퍼블릭 판정하면 오탐)
- 암호화: 기본 암호화(SSE-S3/SSE-KMS) 미설정 버킷 탐지
  (2023-01 이후 신규 버킷은 SSE-S3 기본 적용 — 탐지 의미 범위 확인 필요)
"""

from __future__ import annotations

from cspm.core.finding import Finding
from cspm.core.scanner import BaseScanner


class S3MisconfigScanner(BaseScanner):
    name = "s3"
    service = "s3"
    description = "퍼블릭 공개·암호화 미적용 버킷 탐지"

    def scan(self) -> list[Finding]:
        raise NotImplementedError("판단 기준 확정 대기 — 모듈 docstring 참고")
