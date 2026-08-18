"""탐지 결과(Finding) 공통 스키마.

모든 스캐너는 이 스키마로 결과를 반환한다.
N2SF 통제 영역·CNAPP 분류 필드를 포함해 리포트/README 매핑에 그대로 쓴다.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Finding:
    check_id: str              # 예: "EC2-SG-001"
    title: str                 # 한 줄 요약
    severity: Severity
    service: str               # "ec2" | "s3" | "iam" | "cloudtrail"
    resource_id: str           # 리소스 식별자 (sg-xxx, 버킷명, 유저명 등)
    region: str
    description: str           # 무엇이 왜 위험한지
    evidence: dict[str, Any] = field(default_factory=dict)   # 판단 근거 원본 데이터
    remediation: str = ""      # 수정 방법 (자동수정 제안 기능이 이 필드 기반으로 스크립트 생성)
    n2sf_area: str = ""        # N2SF 통제 영역 (예: "분리·격리")
    cnapp_category: str = ""   # CSPM | CIEM | CWPP
    detected_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d
