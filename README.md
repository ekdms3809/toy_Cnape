# cloud-security-tool — 미니 CSPM/CNAPP

AWS 계정을 스캔해 보안 취약점을 자동 탐지·리포트하는 도구.
국내 **N2SF 보안통제기준**을 AWS 환경에서 자동화 구현한 미니 CSPM.

> **상태**: 골격 완성, 탐지 로직 구현 전 (구현 순서: EC2 → S3 → IAM → CloudTrail → 자동수정 → Lambda 파이프라인)

## 기능 및 N2SF 매핑

| 기능 | 탐지 대상 | N2SF 통제 영역 | CNAPP 분류 | 상태 |
|------|----------|--------------|-----------|------|
| EC2 보안그룹 스캔 | 0.0.0.0/0 + 위험포트(22/3389/3306/5432) | 분리·격리 | CSPM | ✅ |
| S3 오설정 감지 | 퍼블릭 공개·암호화 미적용 버킷 | 데이터 + 분리·격리 | CSPM | 🔲 |
| IAM 과잉권한·미사용키 | 와일드카드 권한, 권한상승 조합, 90일 미사용 키 | 권한 통제 | CIEM | 🔲 |
| CloudTrail 이상탐지 | root 로그인, MFA 우회 시도 | 정보자산 + 통제 | CWPP | 🔲 |
| 자동 수정 제안 | 탐지 결과 기반 수정 스크립트 (dry-run만, 자동 실행 금지) | — | 자동화 | 🔲 |

## 구조

```
cloud-security-tool/
├── main.py                     # CLI 엔트리 (--checks ec2,s3,iam,cloudtrail)
├── cspm/
│   ├── core/
│   │   ├── finding.py          # Finding 공통 스키마 (severity, evidence, N2SF 매핑 필드)
│   │   ├── scanner.py          # BaseScanner 추상 클래스
│   │   └── session.py          # boto3 세션 팩토리
│   ├── scanners/               # 탐지기 4종 (scanner당 파일 1개)
│   ├── remediation/            # 자동 수정 제안 (dry-run 전용)
│   └── report/                 # 콘솔 요약 + JSON 리포트
├── tests/                      # pytest + moto
└── reports/                    # 탐지 결과 JSON (gitignore)
```

## 사용법

```bash
pip install -r requirements.txt
python main.py --checks ec2 --profile <aws-profile> --region ap-northeast-2
```

## 개발 로드맵

1. **1단계** — 로컬 스크립트로 탐지 4종 구현·검증
2. **2단계** — Lambda 이식 (최소 권한 IAM Role)
3. **3단계** — EventBridge 스케줄 + SNS 알림 + 리포트 자동 생성

## 설계 원칙

- 스캔은 **읽기 전용 API만** 호출. 수정은 dry-run 스크립트 제안까지만.
- 탐지 기준은 오탐 감소를 우선: "설정만 위험"과 "실제 노출"을 구분 (예: SG가 퍼블릭 IP 인스턴스에 실제 연결됐는지)
- IAM 탐지는 단순 문자열 매칭이 아닌 정책 평가 시맨틱(NotAction, glob, Effect/Condition, 권한상승 조합) 반영

## 검증 방법

각 스캐너는 True Positive(위험 상태 → 탐지) + False Positive(정상 상태 → 미탐지) 테스트를 함께 작성한다.

- EC2 SG: 0.0.0.0/0 + 위험포트 오픈 → 탐지 확인 / 인스턴스 미연결 SG는 실제 노출 아님으로 구분
- S3: 퍼블릭 액세스 on → 탐지 / off → 미탐지
- IAM: 와일드카드 권한 + 오래된 Access Key → 탐지 / 최소권한 + 최근 키 → 미탐지
- CloudTrail: root 로그인·MFA 우회 이벤트 → 탐지 (moto로 이벤트 모킹)

로컬 AWS 계정 대상 테스트 시 `test-only` 태그로 리소스 격리, 테스트 후 정리.

## 기여 규칙

AI 협업 규칙·PR 워크플로우 → [`CLAUDE.md`](CLAUDE.md)
