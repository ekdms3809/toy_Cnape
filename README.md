# toy_Cnape — 미니 CSPM/CNAPP

AWS 계정을 읽기 전용으로 스캔해 보안 오설정을 탐지·리포트하는 도구. 국내 **N2SF 보안통제기준**을 AWS 환경에 매핑해 자동화했다.

> **상태**: 골격 완성, EC2 보안그룹 스캐너 1개 구현 완료. 나머지 4개는 스텁(판단 기준은 확정, 코드 미작성).

## 왜 만드는가

기존 CSPM(Wiz, Prowler, AWS Security Hub 등)을 그대로 쓰면 빠르지만, 그러면 "API 호출 몇 번으로 결과 받았다"는 것 이상을 설명 못 한다. 이 프로젝트의 목적은 도구를 새로 발명하는 게 아니라, **상용 도구가 실제로 어떤 판단 기준으로 위험도를 매기는지 직접 재현하면서 이해하는 것**이다. 그래서 구현 전에 항상 벤더 레퍼런스(Prowler 소스, AWS Security Hub 컨트롤 정의, Trusted Advisor 체크 로직)를 먼저 읽고, 그 판단 기준을 코드로 옮긴다.

## 기능 및 N2SF 매핑

| 기능 | 탐지 대상 | N2SF 통제 영역 | CNAPP 분류 | 상태 |
|------|----------|--------------|-----------|------|
| EC2 보안그룹 스캔 | 0.0.0.0/0 + 위험포트(22/3389/3306/5432) | 분리·격리 | CSPM | ✅ |
| S3 오설정 감지 | 퍼블릭 공개·암호화 미적용 버킷 | 데이터 + 분리·격리 | CSPM | 🔲 |
| IAM 과잉권한·미사용키 | 와일드카드 권한, 권한상승 조합, 90일 미사용 키 | 권한 통제 | CIEM | 🔲 |
| CloudTrail 이상탐지 | root 로그인, MFA 우회 시도 | 정보자산 + 통제 | CWPP | 🔲 |
| 자동 수정 제안 | 탐지 결과 기반 dry-run 수정 스크립트 (자동 실행 안 함) | — | 자동화 | 🔲 |

## 설계 결정 — EC2 보안그룹 스캐너 (구현 완료분)

가장 먼저 이 스캐너부터 만든 이유: 판단 기준이 IAM(정책 JSON 결합)이나 S3(ACL+정책+PAB 3개 결합)보다 단순해서 "판단 기준을 코드로 정확히 옮기는 연습"을 하기 좋았다.

**단순 매칭으로 안 끝낸 부분**
- 포트 매칭을 `FromPort == 22` 같은 단순 비교가 아니라 `FromPort~ToPort` **범위 포함** 여부로 판정 (Prowler `check_security_group` 로직 참고)
- `IpProtocol == "-1"`(전 포트 오픈)은 개별 위험 포트 오픈과 분리해서 더 높은 등급으로 판정
- 심각도를 설정 상태 하나로 안 끝내고 **실제 노출 여부**까지 확인: SG가 ENI에 연결됐는지, 그 ENI가 퍼블릭 IP를 가졌는지 3단계(HIGH/MEDIUM/LOW)로 나눔. "설정만 위험"과 "실제 인터넷에 노출"을 구분하지 않으면 오탐이 쌓여서 진짜 위험이 묻힌다는 게 이유 — 이건 Wiz의 effective exposure 개념, AWS Trusted Advisor의 체크 티어링과 같은 방향

**참고한 레퍼런스**
- AWS Security Hub EC2.19 (고위험 포트 목록, 0.0.0.0/0 판정 기준)
- Prowler `ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_22` + `lib/security_groups.py`
- AWS Trusted Advisor "Security Groups - Specific Ports Unrestricted" (위험도 티어)

## 아직 안 끝낸 이유 (스텁 3개 + 자동수정)

- **S3**: 퍼블릭 여부를 ACL 하나만 보고 판정하면 오탐 — ACL + 버킷 정책 + Public Access Block 3개를 종합한 "유효 권한"으로 판정해야 함. 이 결합 로직을 아직 설계 중.
- **IAM**: 초안으로 `Action == "*"` 단순 매칭을 짰다가 리뷰에서 실무 미달 판정받음 (NotAction 누락, 권한상승 조합 미탐지, Effect/Condition 무시). 정책 평가 시맨틱을 제대로 반영해서 재설계 중.
- **CloudTrail**: LookupEvents API로 실시간 조회할지, S3 로그 파일을 파싱할지 비용·범위 트레이드오프를 아직 결정 못함. 난이도가 가장 높아 제일 마지막.
- **자동 수정 제안**: 탐지 4종이 끝나야 Finding 스키마가 안정화되므로 마지막에 통합. dry-run 스크립트 생성까지만 하고 자동 실행은 설계상 금지 — 신뢰 안 된 자동화가 오탐 하나로 실제 서비스를 끊는 사고를 만들 수 있어서.

## 구조

```
toy_Cnape/
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

## 검증 방법

각 스캐너는 True Positive(위험 상태 → 탐지) + False Positive(정상 상태 → 미탐지) 테스트를 함께 작성한다.

- EC2 SG: 0.0.0.0/0 + 위험포트 오픈 → 탐지 확인 / 인스턴스 미연결 SG는 실제 노출 아님으로 구분
- S3: 퍼블릭 액세스 on → 탐지 / off → 미탐지
- IAM: 와일드카드 권한 + 오래된 Access Key → 탐지 / 최소권한 + 최근 키 → 미탐지
- CloudTrail: root 로그인·MFA 우회 이벤트 → 탐지 (moto로 이벤트 모킹)

로컬 AWS 계정 대상 테스트 시 `test-only` 태그로 리소스 격리, 테스트 후 정리.

## 설계 원칙 (전체 요약)

- 스캔은 **읽기 전용 API만** 호출. 수정은 dry-run 스크립트 제안까지만.
- 탐지 기준은 오탐 감소를 우선: "설정만 위험"과 "실제 노출"을 구분
- IAM 탐지는 단순 문자열 매칭이 아닌 정책 평가 시맨틱(NotAction, glob, Effect/Condition, 권한상승 조합) 반영

## 개발 규칙

AI(Claude)와 페어로 개발 — 지켜야 할 규칙 → [`CLAUDE.md`](CLAUDE.md)
