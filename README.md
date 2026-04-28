# Dungeon Crawler RPG

> 자료구조와 알고리즘 기말 프로젝트 — Python으로 구현하는 2D 그리드 턴제 던전 크롤러 RPG

수업에서 배운 6가지 자료구조/알고리즘을 실제 게임 문제에 적용하고, Big-O 기반 근거로 선택을 정당화한다.

## 사용한 자료구조 / 알고리즘

| 모듈 | 자료구조 / 알고리즘 | 핵심 복잡도 | 선택 이유 |
|------|--------------------|------------|----------|
| 던전 생성 | BSP Tree | O(R log R) | 방 겹침 없는 절차적 생성, 트리 재귀 활용 |
| Undo 시스템 | Deque + Command | O(1) | `maxlen=30` 자동 관리, Redo 확장 용이 |
| 턴 관리 | Priority Queue (heapq) | O(log K) | Speed 스탯 반영, lazy deletion 적용 |
| 인벤토리 | Hash Table (dict) | 평균 O(1) | id 기반 수량 관리 + 카테고리별 UI 친화 |
| 적 AI | A\* (Manhattan) | O(E log V) | 그리드 최단경로 표준, heap 자료구조 재사용 |
| 리더보드 | AVL Tree (자체 구현) | O(log N) | insert/rank/kth 모두 균형 보장 |

자세한 설계 근거는 `../DSA_구현_명세서.docx` 참고.

## 사용한 외부 라이브러리

평가 정책상 외부 라이브러리는 사용 이유를 답변할 수 있어야 한다. 본 프로젝트는 다음 둘만 사용한다.

- **rich** — 터미널에서 색상·박스·테이블·라이브 갱신을 선언적으로 다루기 위해.
- **readchar** — OS 무관(특히 Linux) 비차단 단일 키 입력. `rich`는 입력 처리를 제공하지 않는다.

(개발 편의용으로 `pytest`, `ruff`를 추가로 사용. 시연 PC에는 설치 불필요.)

## 설치 및 실행

```bash
# 1) 저장소 클론
git clone <REPO_URL>
cd dungeon_crawler

# 2) 가상환경 생성 (권장)
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 3) 런타임 의존성 설치
pip install -r requirements.txt

# 4) (개발자) 개발 의존성까지 설치
pip install -r requirements-dev.txt

# 5) 실행
python main.py

# 6) 테스트
pytest

# 7) 포맷 + 린트
ruff format .
ruff check .
```

## 디렉토리 구조

```
dungeon_crawler/
├── main.py                  # 게임 엔트리포인트
├── core/                    # 공통 데이터 타입 (의존 그래프의 루트)
│   ├── types.py
│   ├── rng.py
│   └── events.py
├── map/                     # 던전 생성 / 그리드 / 시야
│   ├── bsp.py               # BSP 던전 생성
│   ├── dungeon.py
│   └── fov.py
├── systems/                 # 게임 시스템
│   ├── turn_manager.py      # heapq 기반 우선순위 큐
│   ├── undo.py              # deque + Command
│   ├── inventory.py         # dict 해시 테이블
│   └── ai.py                # A*
├── persistence/             # 영속화
│   ├── avl_tree.py          # 자체 구현 AVL
│   └── leaderboard.py
├── ui/                      # 터미널 (rich + readchar)
│   └── terminal.py
├── tests/                   # pytest
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

의존 방향: `core` → `map · systems · persistence` → `ui`. 로직 모듈은 UI를 모르도록 분리되어 있어 추후 pygame 등으로 UI를 교체할 여지가 있다.

## 팀 협업 규칙

- **브랜치**: `main` + `feat/*`, `fix/*` 브랜치 (자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md))
- **커밋**: Conventional Commits 한국어 (`feat: A* 휴리스틱 추가` 등)
- **PR**: 1명 이상 리뷰 후 머지
- **포맷·린트**: Ruff (`ruff format && ruff check`) 통과 필수

## 라이선스

수업 과제로 작성됨. 외부 공개 시 라이선스는 팀 협의 후 결정.
