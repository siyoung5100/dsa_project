# 최초 세팅 가이드 (팀 공통)

저장소 파일은 모두 준비되어 있다. 아래 순서로 **본인 컴퓨터에서** Git 저장소를 초기화하고 GitHub에 푸시하면 팀원이 클론해서 작업을 시작할 수 있다.

> 이 가이드는 **저장소를 만든 한 사람**이 한 번만 수행한다. 나머지 팀원은 [팀원 클론 절차](#팀원-클론-절차)를 따른다.

> ⚠️ **OneDrive 등 클라우드 동기화 폴더에는 두지 말 것.** `.git/` 내부 파일 잠금 충돌과 성능 저하가 발생한다. 동기화되지 않는 일반 폴더(예: `C:\Users\<사용자>\dev\`)로 이동한 뒤 초기화한다.

---

## 1. Git 저장소 초기화 (저장소 생성자)

```bash
cd dungeon_crawler

# 혹시 자동 생성된 빈 .git 폴더가 있으면 제거
rm -rf .git

# main 브랜치로 초기화
git init -b main

# 본인 정보 설정 (이미 글로벌로 설정되어 있으면 생략)
git config user.name  "<본인 이름>"
git config user.email "<본인 이메일>"

# 모든 파일 스테이징 후 첫 커밋
git add .
git commit -m "chore: 프로젝트 초기 골격 생성"
```

## 2. GitHub 원격 저장소 생성

브라우저에서:

1. https://github.com/new 접속
2. 저장소 이름: `dungeon-crawler` (또는 팀이 합의한 이름)
3. **README, .gitignore, License 추가는 모두 체크 해제** (이미 로컬에 있음)
4. Private/Public는 팀 합의에 따라 선택
5. Create repository

GitHub가 알려주는 원격 URL을 복사한다. 예시:
- HTTPS: `https://github.com/<사용자>/<저장소>.git`
- SSH:   `git@github.com:<사용자>/<저장소>.git`

## 3. 원격 연결 + 첫 푸시

```bash
git remote add origin <위에서 복사한 URL>
git push -u origin main
```

## 4. 팀원 초대

GitHub 저장소 → Settings → Collaborators → "Add people" → 팀원 GitHub 아이디 추가.

브랜치 보호 (선택, 권장):
- Settings → Branches → "Add rule"
- Branch name pattern: `main`
- Require pull request before merging ✓
- Require approvals: 1 ✓
- Do not allow bypassing the above settings ✓

---

## 팀원 클론 절차

```bash
# 1) 저장소 클론
git clone <REPO_URL>
cd dungeon-crawler          # 또는 dungeon_crawler

# 2) 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3) 개발용 의존성 설치
pip install -r requirements-dev.txt

# 4) 정상 동작 확인
ruff format --check .
ruff check .
pytest                       # 모든 테스트가 skip 표시되면 정상

# 5) 첫 작업 브랜치 생성
git switch -c feat/<본인-담당-모듈>
```

---

## 다음 단계 — 2인 팀, 학습 목적

본 프로젝트의 Git 사용 목적은 협업 효율보다는 **Git/PR 워크플로 학습**에 있다. 2인이라는 작은 규모이므로 일부 작업은 페어 프로그래밍이 더 자연스럽지만, 학습 가치를 살리려면 **다음 규칙을 의도적으로 따른다.**

1. 모든 변경은 feature 브랜치 + PR을 거친다. main 직접 push 금지. PR 본문에 어떤 자료구조/알고리즘을 어떻게 만들었는지 한 단락 적는다 → 발표 Q&A 자료가 자동으로 누적된다.
2. 페어 프로그래밍 시에는 commit 마지막에 `Co-authored-by: 이름 <이메일>` trailer를 넣는다 (CONTRIBUTING.md 참고).
3. 가급적 작은 PR을 자주 — rebase·squash·conflict 해결을 직접 겪어볼 기회.

### 모듈 분담 (제안)

`core/types.py`(완료)에 이어 6개 모듈을 다음과 같이 묶는다.

**1단계 — 어려운 모듈은 페어로**
- `persistence/avl_tree.py` (AVL Tree) — 회전·균형 로직이 까다로워 함께 짜는 게 안전. **PR 1: 페어 작성**.

**2단계 — 둘이 동시에**
- 사람 A: `map/`(`bsp.py`, `dungeon.py`, `fov.py`) + `systems/ai.py`(A*) → "월드와 길찾기" 묶음.
- 사람 B: `systems/`(`turn_manager.py`, `undo.py`, `inventory.py`) + `persistence/leaderboard.py` → "게임 시스템과 영속화" 묶음.
- 모듈마다 별도 PR. 서로 리뷰어로 지정.

**3단계 — 통합은 페어로**
- `ui/terminal.py` + `main.py` — 게임 루프, 키 입력, 화면 갱신. 여러 모듈을 묶는 단계라 함께 작업.

이렇게 가면 PR 약 10개 정도가 main 히스토리에 남고, 각자 4~5개씩 PR을 만들고 리뷰하는 경험을 쌓는다.

### 추가로 시도해볼 만한 Git 학습 주제

여유가 있을 때 의도적으로 한 번씩 해보면 좋다.

- `git rebase -i`로 커밋 정리 (squash, reword)
- conflict가 나는 PR을 일부러 만들어서 해결 연습
- `git stash` / `git cherry-pick`
- `git reset --soft` / `git revert`의 차이 체감
- GitHub의 PR 리뷰 (Request changes / Approve / Suggestions) 모두 사용해보기
