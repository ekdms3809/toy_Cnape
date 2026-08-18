"""스캐너 공통 베이스 클래스.

각 탐지 기능은 BaseScanner를 상속하고 scan()만 구현한다.
탐지 로직(판단 기준)은 사람이 확정한 뒤에만 구현한다 — 그 전엔 NotImplementedError 유지.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import boto3

from cspm.core.finding import Finding


class BaseScanner(ABC):
    name: str = ""          # CLI에서 --checks 로 선택할 때 쓰는 이름
    service: str = ""       # 대상 AWS 서비스
    description: str = ""   # 한 줄 설명

    def __init__(self, session: boto3.Session, region: str | None = None):
        self.session = session
        self.region = region or session.region_name or "ap-northeast-2"

    @abstractmethod
    def scan(self) -> list[Finding]:
        """탐지 실행. Finding 리스트 반환. 읽기 전용 API만 호출한다."""
        raise NotImplementedError
