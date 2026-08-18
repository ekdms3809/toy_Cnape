"""CLI 엔트리포인트 (1단계: 로컬 스크립트).

사용 예:
    python main.py --checks ec2               # EC2 보안그룹만
    python main.py --checks ec2,s3 --profile myprofile --region ap-northeast-2
    python main.py                            # 전체 (미구현 스캐너는 건너뜀)
"""

from __future__ import annotations

import argparse
import sys

from cspm.core.session import get_session
from cspm.report.reporter import print_summary, write_json
from cspm.scanners import SCANNERS


def main() -> int:
    parser = argparse.ArgumentParser(description="미니 CSPM — AWS 보안 설정 스캐너")
    parser.add_argument(
        "--checks",
        default="all",
        help=f"실행할 검사 (쉼표 구분): {', '.join(SCANNERS)} 또는 all",
    )
    parser.add_argument("--profile", default=None, help="AWS CLI 프로파일")
    parser.add_argument("--region", default=None, help="AWS 리전 (기본 ap-northeast-2)")
    parser.add_argument("--output-dir", default="reports", help="JSON 리포트 저장 경로")
    args = parser.parse_args()

    names = list(SCANNERS) if args.checks == "all" else [c.strip() for c in args.checks.split(",")]
    unknown = [n for n in names if n not in SCANNERS]
    if unknown:
        print(f"알 수 없는 검사: {unknown} (가능: {list(SCANNERS)})")
        return 1

    session = get_session(args.profile, args.region)
    findings = []
    for name in names:
        scanner = SCANNERS[name](session, args.region)
        try:
            result = scanner.scan()
            findings.extend(result)
            print(f"[{name}] 완료 — {len(result)}건")
        except NotImplementedError as e:
            print(f"[{name}] 건너뜀 — {e}")

    print_summary(findings)
    if findings:
        path = write_json(findings, args.output_dir)
        print(f"\n리포트 저장: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
