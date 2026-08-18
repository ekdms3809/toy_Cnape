"""boto3 세션 팩토리. 프로파일/리전 지정 한 곳에서 관리."""

from __future__ import annotations

import boto3

DEFAULT_REGION = "ap-northeast-2"


def get_session(profile: str | None = None, region: str | None = None) -> boto3.Session:
    return boto3.Session(profile_name=profile, region_name=region or DEFAULT_REGION)
