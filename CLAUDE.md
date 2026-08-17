# toy_Cnape — AI 협업 규칙

솔로 프로젝트(사용자 1인 + AI 페어). open-raw 팀 프로젝트 하네스(3단계 제약 + PR 워크플로우)를 1인 버전으로 축소 적용.

---

## 항상 강제 (모든 단계)

- 코드 작성 전 변경 범위·방법을 한국어로 제시 → 사용자 동의 후 작성
- 새 기능/버그수정에는 pytest 테스트 동반 (예외는 사용자 명시 승인)
- PR 전 lint + pytest 로컬 통과 확인 (전부 통과 전엔 PR 생성 금지)
- PR·이슈·커밋 메시지는 한국어
- 스캐너는 **읽기 전용 API만** 호출 — 수정은 dry-run 스크립트 제안까지만, 실제 실행 금지
- 탐지 기준은 오탐 감소 우선: "설정만 위험"과 "실제 노출"을 반드시 구분 (예: SG가 실제 인스턴스에 연결됐는지, 퍼블릭 IP 있는지)
- IAM 탐지는 단순 문자열 매칭 금지 — 정책 평가 시맨틱(NotAction, glob, Effect/Condition, 권한상승 조합) 반영
- 기능 하나 = 브랜치 하나 = PR 하나 (무관한 변경 섞지 않기)
- 각 스캐너는 True Positive(위험 세팅 → 탐지) + False Positive(정상 상태 → 미탐지) 테스트 둘 다 작성
- 머지된 PR은 다시 건드리지 않음 — 리뷰 피드백은 새 PR 대신 같은 브랜치에 커밋 추가

## 허가 필수 (사용자 승인 후 진행)

- 새 라이브러리/의존성 추가 (requirements.txt, requirements-dev.txt 변경)
- CI 설정(`.github/workflows/`) 추가·변경
- `.env.example` / 환경변수 키 추가·삭제
- README.md 기능표·로드맵 구조 대폭 변경
- 이 `CLAUDE.md` 자체 변경
- 브랜치 전략·스캐너 구현 우선순위 변경
- Lambda/EventBridge 등 실제 AWS 배포 관련 작업

## 절대 금지

- AWS 자격증명(`.env`, credentials) 커밋
- 실제 AWS 리소스에 대한 쓰기·삭제 API 호출 (읽기 전용만 — remediation도 스크립트 생성까지만)
- `git push --force` / `git reset --hard`
- `--no-verify`로 pre-commit hook 우회
- AI 셀프 머지 — PR 생성까지만, 머지 버튼은 반드시 사용자가 누름

---

## PR 워크플로우

```
기능 브랜치 생성 (feat/<scanner-name>)
  → 구현 + 테스트(TP/FP 둘 다)
  → 로컬 lint + pytest 통과 확인
  → PR 생성 (한국어 설명: 뭘 탐지하는지, 왜 이 기준인지, 테스트 결과)
  → 사용자 리뷰
  → 사용자 머지 (Squash 권장)
```

## 브랜치 명명 · 순서

| 브랜치 | 대상 | 상태 |
|--------|------|------|
| `feat/ec2-scanner` | EC2 보안그룹 오픈포트 탐지 | ✅ main 반영됨 |
| `feat/s3-scanner` | S3 오설정 감지 | 다음 착수 |
| `feat/iam-scanner` | IAM 과잉권한·미사용키 | IAM 정책 시맨틱 재설계 필요 |
| `feat/cloudtrail-scanner` | CloudTrail 이상탐지 | 가장 까다로움, 버퍼 필요 |
| `feat/remediation` | 자동 수정 제안 (dry-run) | 위 4개 통합 후 |
| `feat/lambda-pipeline` | Lambda + EventBridge 자동화 | 로컬 검증 끝난 후 |

---

## 설계 원칙 (README.md와 동일, 요약)

1. 읽기 전용 스캔, 쓰기는 제안까지만
2. 오탐 최소화 — 표면적 위험과 실제 노출을 구분
3. IAM은 정책 시맨틱 기반, 문자열 매칭 아님
