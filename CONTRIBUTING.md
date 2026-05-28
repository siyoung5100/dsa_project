# 기여 가이드 (Contributing Guide)

이 문서는 팀 내 협업 규칙을 정의한다. 모두 같은 규칙을 따라야 코드 리뷰·머지·페어 프로그래밍이 매끄럽게 진행된다.

## 1. 브랜치 전략

`main + feature 브랜치`를 사용한다. **`main`에 직접 push하지 않는다.**

### 브랜치 네이밍

| 종류 | 패턴 | 예시 |
|------|------|------|
| 새 기능 | `feat/<짧은 설명>` | `feat/avl-insert` |
| 버그 수정 | `fix/<짧은 설명>` | `fix/undo-desync` |
| 리팩터링 | `refactor/<설명>` | `refactor/turn-loop` |
| 문서 | `docs/<설명>` | `docs/readme-update` |
| 테스트 | `test/<설명>` | `test/avl-balance` |
| 잡일 | `chore/<설명>` | `chore/ruff-config` |

설명은 영어 kebab-case 권장 (한글 브랜치명은 일부 도구에서 깨질 수 있음).

### 작업 흐름

```bash
# 1) main을 최신화
git switch main
git pull

# 2) 새 브랜치 생성
git switch -c feat/avl-insert

# 3) 작업 + 커밋 (자주, 작게)
git add <files>
git commit -m "feat: AVL 단일 회전 구현"

# 4) 원격에 push
git push -u origin feat/avl-insert

# 5) GitHub에서 PR 생성 → 리뷰 → 머지
```

## 2. 커밋 메시지 규칙 — Conventional Commits 한국어

형식:

```
<type>: <본문은 한국어로 명료하게>
```

`<type>`은 영어 키워드(검색·도구 호환), 본문은 한국어로 작성한다.

### 타입 키워드

| 타입 | 용도 |
|------|------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 동작 변화 없이 코드 구조 개선 |
| `docs` | 문서/주석만 변경 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드, 설정, 의존성 등 잡일 |
| `style` | 포맷·세미콜론 등 (논리 변화 없음) |
| `perf` | 성능 개선 |

### 좋은 예

```
feat: A* 휴리스틱을 맨해튼 거리로 구현
fix: TurnManager에서 사망 엔티티가 다시 호출되는 문제 수정
refactor: BSP 분할 함수를 재귀에서 반복으로 변경
docs: README에 사용 라이브러리 사용 이유 명시
test: AVL 무작위 1,000건 균형 검증 추가
chore: Ruff 룰셋에 SIM 추가
```

### 나쁜 예

```
update                  # 타입 없음, 무엇을 업데이트했는지 모름
fix bug                 # 어떤 버그?
WIP                     # 절대 머지하지 말 것
대충 짰음                # 본문 부실
```

### 페어 프로그래밍 시

마지막 줄에 trailer로 공동 작성자를 기재한다:

```
feat: 인벤토리 카테고리별 정렬 추가

Co-authored-by: 홍길동 <hong@example.com>
```

## 3. Pull Request 규칙

### 크기

- **PR 하나 = 한 가지 일.** 새 기능 + 리팩터를 섞지 말 것.
- 변경 라인 ~300줄 이하를 권장. 그 이상이면 분할 검토.

### 리뷰

- **최소 1명** 승인 후 머지.
- 머지 전 다음을 통과해야 한다:
  - `ruff format .` (포맷)
  - `ruff check .` (린트)
  - `pytest` (전체 테스트)

### 머지 방식

기본은 **Squash & Merge**. PR 하나 = 커밋 하나로 정리되어 `main`의 히스토리가 깔끔하다. 단, 페어 프로그래밍으로 의미 있는 커밋이 여러 개라면 Rebase Merge도 허용.

## 4. 코드 스타일

- 포맷: `ruff format` (line-length 100, double quotes)
- 린트: `ruff check`
- 타입 힌트: 가능하면 사용 (필수는 아님)
- docstring: 모듈/공개 클래스/공개 함수에 한 줄 이상

`pyproject.toml`에 모든 설정이 들어 있다.

## 5. 테스트

- 새 기능이나 버그 수정은 가능하면 단위 테스트를 동반하여 PR을 개설합니다.
- 기존 테스트가 깨지지 않도록 무결성을 유지해야 합니다.
- 과거 미구현 모듈을 위한 `pytest.mark.skip`은 현재 모두 해제되어 전체 테스트 스펙이 가동 중입니다.

## 6. 이슈 / 작업 추적

GitHub Issues를 사용한다. 이슈 단위로 브랜치를 만들고, PR 본문에 `Closes #N`을 적으면 머지 시 자동으로 닫힌다.

## 7. 막힐 때

- 페어 프로그래밍 호출 (Discord/Zoom)
- Draft PR로 부분 구현을 올려 조기 피드백 받기
- 로컬 내의 정교한 설계 명세인 [docs/spec.md](docs/spec.md)에 관련 규칙이나 구현 형태가 기재되어 있는지 먼저 확인합니다.
