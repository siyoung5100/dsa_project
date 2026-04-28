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

## 다음 단계

1. **모듈 분담을 정한다** — 명세서 §4의 6개 모듈을 4명에게 나누어 할당.
2. **첫 모듈은 `core/types.py`** — 모든 모듈의 의존성 루트이므로 한 명이 먼저 끝내고 main에 머지.
3. 그 후 4명이 동시에 분담 모듈을 작업.

권장 분담 (조합 예시):
- A: `map/`(BSP, dungeon, fov)
- B: `systems/`(turn_manager, undo, inventory)
- C: `persistence/`(avl_tree, leaderboard) — AVL이 까다로우니 일찍 시작
- D: `systems/ai.py`(A*) + `ui/terminal.py` + `main.py` 통합
