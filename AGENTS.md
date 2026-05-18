# AGENTS.md — AI 코딩 에이전트를 위한 안내서

> 이 문서는 Claude Code · Gemini CLI · Cursor 등 AI 코딩 에이전트가 본 저장소에서 작업할 때 가장 먼저 읽어야 할 파일입니다. 사람을 위한 소개는 [README.md](README.md), 협업 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md), 상세 설계는 [docs/spec.md](docs/spec.md)를 참고하세요.

## TL;DR

대학 "자료구조와 알고리즘" 수업의 기말 프로젝트. **Python으로 구현하는 2D 그리드 턴제 던전 크롤러 RPG**. 6개 자료구조/알고리즘(BSP·Deque·heapq·Hash·A\*·AVL)을 실제 게임 문제에 적용하는 것이 목적입니다.

- **언어**: Python 3.10+
- **UI**: 터미널(rich + readchar). `pygame` 등 그래픽 확장은 가산점이 없으므로 **MVP 우선**.
- **팀**: 2인. Git 사용은 협업 효율보다는 **학습 목적**.
- **평가**: 강의실 Linux PC에서 직접 시연 + 조교 Q&A. 코드 제출 없음. **알고리즘 선택 이유**가 Q&A의 핵심.

## 빠른 시작 (Quick Start)

```bash
# 1) 가상환경
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2) 의존성 (개발용 포함)
pip install -r requirements-dev.txt

# 3) 실행 (현재는 NotImplementedError)
python main.py

# 4) 테스트 / 포맷 / 린트
pytest
ruff format .
ruff check .
```

## 디렉토리 지도

```
dungeon_crawler/
├── AGENTS.md  ← 너 (지금 읽는 파일)
├── CLAUDE.md  ← @AGENTS.md (단순 import)
├── README.md, CONTRIBUTING.md, SETUP.md
├── pyproject.toml, requirements*.txt, .gitignore, .gitattributes
├── core/             # 공통 데이터 타입 (의존 그래프 루트, 누구에게도 의존하지 않음)
│   ├── types.py      # ✅ 구현 완료. Coord, Tile, Entity, Player, Enemy, Item, Action, Record
│   ├── rng.py        # ✅ 구현 완료. seed 고정 랜덤 래퍼
│   └── events.py     # ⏳ 미구현. 이벤트 로그 큐
├── map/              # 던전 맵 / 시야
│   ├── bsp.py        # ✅ 구현 완료. BSP Tree 던전 생성 — 명세서 §4.1
│   ├── dungeon.py    # ✅ 구현 완료. Dungeon 컨테이너
│   └── fov.py        # ✅ 구현 완료. 시야(FOV) 계산
├── systems/          # 게임 시스템
│   ├── turn_manager.py # ⏳ 미구현. heapq 우선순위 큐 + lazy del — §4.3
│   ├── undo.py         # ⏳ 미구현. deque + Command 패턴 — §4.2
│   ├── inventory.py    # ⏳ 미구현. dict 해시 테이블 — §4.4
│   └── ai.py           # ✅ 구현 완료. A* 알고리즘 — §4.5

├── persistence/      # 영속화
│   ├── avl_tree.py     # ✅ 구현 완료. AVL Tree 자체 구현 — §4.6
│   └── leaderboard.py  # ✅ 구현 완료. AVL 기반 리더보드 + JSON
├── ui/
│   └── terminal.py   # ⏳ 미구현. rich + readchar 기반 렌더링/입력
├── main.py           # ⏳ 미구현. 게임 엔트리포인트 (NotImplementedError)
├── tests/            # pytest, 미구현 모듈 테스트는 pytest.mark.skip
└── docs/
    └── spec.md       # 📖 .docx 명세서의 markdown 추출본 (에이전트 참조용)
```

**의존 방향**: `core` ← `map · systems · persistence` ← `ui · main`. 역방향 import 금지. UI 계층은 추후 pygame 등으로 교체 가능해야 한다.

## 구현 상태 (2026-05-18 기준)

| 모듈 | 상태 | 다음 PR 후보 |
|------|------|--------------|
| `core/types.py`, `core/rng.py` | ✅ 구현 완료 | — |
| `map/bsp.py`, `map/dungeon.py`, `map/fov.py` | ✅ 구현 완료 | — |
| `systems/ai.py` | ✅ 구현 완료 | — |
| `persistence/avl_tree.py`, `persistence/leaderboard.py` | ✅ 구현 완료 | — |
| `systems/turn_manager.py`, `systems/undo.py`, `systems/inventory.py` | ⏳ | 사람 B 묶음 (다음 목표) |
| `ui/terminal.py`, `main.py` | ⏳ | 통합 단계 (페어) |

## 변경 시 지켜야 할 규칙 (필수)

### 1. 브랜치 + PR

`main`에 직접 push 금지. 모든 변경은 feature 브랜치 + PR을 거친다.

```bash
git switch -c feat/<짧은-영어-설명>     # 또는 fix/, refactor/, test/, docs/, chore/
# 작업 후
git push -u origin feat/<...>
# GitHub에서 PR 생성 → 1명 리뷰 → Squash & Merge
```

### 2. 커밋 메시지 — Conventional Commits 한국어

```
feat: A* 휴리스틱을 맨해튼 거리로 구현
fix: TurnManager에서 사망 엔티티가 다시 호출되는 문제 수정
test: AVL 무작위 1,000건 균형 검증 추가
```

타입 키워드(영어): `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`. 본문은 한국어.

### 3. 코드 스타일 — Ruff (포맷 + 린트 올인원)

`pyproject.toml`에 모든 설정이 들어 있다.

- **line-length**: 100
- **target-version**: py310
- **quote-style**: double (`"문자열"`)
- **활성 룰셋**: E/W (PEP 8), F (pyflakes), I (isort), B (bugbear), UP (pyupgrade), N (네이밍), SIM, RUF
- **무시**: E501 (line-too-long, formatter가 처리)

PR을 올리기 전 반드시:
```bash
ruff format .
ruff check .
pytest
```
세 줄 모두 통과해야 함.

### 4. 외부 라이브러리 추가 시

`requirements.txt`(런타임) 또는 `requirements-dev.txt`(개발용)에 추가하고, **`README.md`의 "사용한 외부 라이브러리" 표에 사용 이유를 한 줄 적는다.** 이게 발표 Q&A에서 그대로 답변 자료가 된다.

### 5. 테스트

- 새 코드는 가능한 한 단위 테스트와 함께 PR에 포함.
- `tests/test_<모듈>.py` 파일은 이미 stub 형태로 존재하며 `pytestmark = pytest.mark.skip`으로 표시되어 있다. 모듈 구현이 시작되면 해당 skip을 제거하고 실제 테스트를 채운다.
- 테스트 시나리오는 [docs/spec.md §5](docs/spec.md)에 정리되어 있다.

### 6. 엄격한 TDD (Test-Driven Development) 적용

본 프로젝트의 모든 신규 기능 개발은 반드시 다음의 TDD 사이클을 엄격히 준수한다. 에이전트는 한 번에 대량의 코드를 작성하는 대신, 하나의 테스트 케이스를 통과시키는 작은 단위로 작업을 쪼개어 진행해야 한다.

1.  **Red Phase (실패하는 테스트 작성)**:
    *   구현하려는 기능의 명세(`docs/spec.md`)를 확인하고, 이를 검증할 수 있는 실패하는 단위 테스트를 `tests/` 폴더에 먼저 작성한다.
    *   기존의 `pytest.mark.skip`이 있다면 제거하고, `pytest`를 실행하여 해당 테스트가 실제로 실패하는지 확인한다.
2.  **Green Phase (최소한의 구현)**:
    *   테스트를 통과시키기 위해 필요한 **최소한의 코드**만을 작성한다. 이 단계에서는 코드의 우아함보다 '테스트 통과' 자체에 집중한다.
    *   `pytest`를 실행하여 작성한 테스트와 기존 테스트가 모두 통과하는지 확인한다.
3.  **Refactor Phase (리팩터링 및 품질 개선)**:
    *   테스트 통과 상태를 유지하면서, `ruff` 가이드라인에 따라 코드를 정돈하고 중복을 제거하며 가독성을 높인다.
    *   최종적으로 `ruff format`, `ruff check`, `pytest`를 모두 통과해야 해당 단위 작업이 완료된 것으로 간주한다.

## 코드 작성 규칙 (스타일 컨벤션)

### dataclass 우선

새 데이터 타입은 `@dataclass`를 기본으로 한다.
- 변경 가능: `@dataclass`
- 변경 불가능: `@dataclass(frozen=True)` (hashable 필요 시)
- 가변 기본값: `field(default_factory=list)` 또는 `field(default_factory=dict)` (절대 `[]`, `{}`를 직접 default로 쓰지 말 것 — 인스턴스 간 공유 버그)

### 타입 힌트

`from __future__ import annotations`를 모든 모듈 최상단에 두고, 모던 문법 사용:
- `list[int]`, `dict[str, int]` (`List`, `Dict` 금지)
- `Optional[X]` 대신 `X | None`
- 외부 타입은 `TYPE_CHECKING` 가드 안에 import

### 한국어 주석 / 영어 식별자

- 함수/변수/클래스 이름은 영어 (Python 관례)
- docstring·주석은 한국어 (팀 합의)
- 식별자에 한글 사용 금지 (호환성)

### 예약어 회피

- `def_` 같은 트레일링 언더스코어 회피하고 풀 네임 사용 (예: `defense`).
- 하지만 `id`, `type` 같은 빌트인 그림자는 dataclass 필드명으로 허용 (Python 관용).

## 자주 빠지는 함정 (Gotchas)

1. **dataclass 상속 + default 값 순서**: 부모 클래스에 default 있는 필드가 있으면, 자식 클래스의 새 필드도 모두 default 값을 가져야 한다. Player(Entity), Enemy(Entity)는 이 규칙을 이미 지키고 있다.

2. **`frozen=True` + 가변 필드**: frozen은 *필드 재할당*만 막고, dict/list 같은 가변 객체의 *내부 변경*은 막지 않는다. `Item.effect: dict[str, int]`는 관례상 변경하지 않으나 강제력 없음.

3. **heapq에 비교 불가능 객체**: `(priority, entity)` 튜플을 heappush 하면 동률 시 entity끼리 비교를 시도해 TypeError가 난다. **항상 tie-break용 카운터를 끼워 (priority, counter, entity) 형태로 사용** (TurnManager 명세 참고).

4. **`map/` 패키지 이름**: Python 빌트인 `map()`을 그림자 처리하지만 패키지 import에서는 문제없다. `import map` 같은 문장만 피하면 된다 (`from map.bsp import generate_dungeon` OK).

5. **OneDrive에 git 저장소 두지 말 것**: `.git/objects/`가 동기화 잠금과 충돌해 손상 위험. 일반 폴더(예: `C:\Claude\` 또는 `~/dev/`)에 두라.

6. **줄바꿈**: `.gitattributes`로 모든 텍스트 파일을 LF로 강제. Windows 사용자가 작업해도 저장소 내부는 LF로 통일.

## 명세서 (docs/spec.md) 빠른 참조

스텁 파일들의 docstring에 등장하는 §번호는 [docs/spec.md](docs/spec.md)의 섹션을 가리킨다.

- §1 — 문서 개요, 변수 정의 (W, H, R, E, V, K, N)
- §2 — 디렉토리 + 의존 그래프
- §3 — 공통 데이터 타입 (이미 `core/types.py`에 구현됨)
- §4.1 — BSP 던전 생성 (재귀 분할, L자 복도)
- §4.2 — Undo: deque + Command
- §4.3 — Turn Manager: heapq + lazy deletion
- §4.4 — Inventory: 카테고리 중첩 dict
- §4.5 — A*: 맨해튼 휴리스틱, 경로 캐시
- §4.6 — AVL Tree: 회전, size 필드, kth/rank
- §5 — 단위 테스트 시나리오 (각 모듈별)
- §6 — 한눈 보기 체크리스트

## 발표·시연 컨텍스트 (중요)

평가는 강의실 Linux PC에서 **직접 시연 + 조교 Q&A** 방식이다. 다음을 의식하면 좋다.

1. **Q&A의 초점은 알고리즘 선택 이유.** 코드 디테일을 깊게 묻지 않는다. 따라서:
   - 각 모듈 구현 시 docstring에 "왜 이 자료구조를 골랐나"를 한 단락 적어두면 발표 자료가 자동으로 누적된다.
   - 외부 라이브러리는 사용 이유를 명확히 답할 수 있어야 한다 (현재는 `rich`, `readchar`만 사용 — 사유는 README.md에 명시).

2. **시연 환경**: Linux + Python 3.10+ + `pip install` 가능. RTX 30 + 64GB RAM이라 성능 걱정 0.

3. **가산점 없음**: 기본 요구사항(6개 알고리즘) 외 추가 기능에 가산점이 없다. 시간을 코드 품질·테스트·발표 연습에 쓰는 것이 합리적.

## 디버깅 팁

- 게임 루프에서 `print()`는 화면을 깨므로, 로그는 파일로 (`logs/debug.log`, .gitignore에 등록됨).
- pytest에서 `-s` 플래그로 print 출력 보기, `-v`로 자세한 결과.
- BSP 생성 결과를 콘솔에 그려보고 싶으면 `python -c "from map.bsp import generate_dungeon; ..."` 식의 스크립트 사용.

## 에이전트가 모르면 물어볼 것

작업 전 확실하지 않은 결정이 있으면, 사람에게 물어본다 (특히 이런 것들):

- 새 외부 라이브러리 도입 — 사용 이유를 명세할 수 있어야 도입 가능
- 명세서 §4와 다른 자료구조 선택 — 발표 답변에 영향
- 게임 디자인 디테일 (HP 수치, 던전 크기, 적 종류 등) — PPT 초안과 일치하는 합리적 기본값 사용 후 사람이 검토
- 테스트 케이스 추가 — 새 케이스의 의도를 한 줄로 설명

## 관련 문서

- [README.md](README.md) — 사람용 프로젝트 소개
- [CONTRIBUTING.md](CONTRIBUTING.md) — 협업 규칙 상세 (Conventional Commits 한국어, PR 룰)
- [SETUP.md](SETUP.md) — 최초 git init / GitHub 푸시 / 팀원 클론 절차
- [docs/spec.md](docs/spec.md) — 구현 명세서 전문 (markdown)
- 부모 폴더의 `.docx` 4개 — 인간 제출용 (계획서, 명세서, 중간점검, 원본 PPT)
