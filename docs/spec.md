# 자료구조와 알고리즘 기말 프로젝트 — 구현 명세서

**Python Dungeon Crawler RPG**

*--- 구현 명세서 (Implementation Specification) ---*

**적용 자료구조/알고리즘**: BSP · Deque · Priority Queue · Hash Map · A* · AVL Tree

**최신 갱신일**: 2026-05-28

---

## 1. 문서 개요

본 문서는 DS&A 기말 프로젝트 『Dungeon Crawler RPG』의 구현 명세서이다. 앞서 제출한 계획서(후보 비교)에서 결정된 다음 6가지 자료구조/알고리즘에 대해, 모듈 구조·공통 데이터 타입·함수 시그니처·의사코드·복잡도·테스트 계획을 정의한다.

### 1.1 확정된 자료구조/알고리즘

| 구분 | 자료구조 / 알고리즘 | 핵심 복잡도 | 선정 포인트 (적용 효과) |
| :--- | :--- | :--- | :--- |
| **① 던전 생성** | BSP (Binary Space Partitioning) Tree | O(R log R) | 방 겹침이 없는 절차적 생성 및 트리 재귀 구조 활용 |
| **② Undo 시스템** | Deque (`collections.deque`, `maxlen=30`) | O(1) | 최근 30회 행동에 대한 Command 패턴 역산 처리 |
| **③ 턴 관리** | Priority Queue (`heapq` Min-Heap) | O(log K) | 속도(Speed) 반영 턴 스케줄링 및 lazy deletion 적용 |
| **④ 인벤토리** | Hash Table (카테고리별 중첩 dict) | 평균 O(1) | 고유 ID 기반 수량 관리 및 카테고리별 탐색 최적화 |
| **⑤ 적 AI** | A* 알고리즘 (맨해튼 거리 휴리스틱) | O(E log V) | 4방향 그리드 환경에서의 최단경로 추적 최적화 |
| **⑥ 리더보드** | Self-Balancing BST (AVL Tree 직접 구현) | O(log N) | 삽입, 순위(rank), k번째 원소(kth) 연산의 균형 보장 |

### 1.2 변수 및 용어 정의
- **W, H**: 던전 맵의 너비·높이 (타일 단위)
- **R**: 생성된 방(Room)의 수, **E**: 방 사이 복도 간선 수
- **V**: A*의 정점 수 (통과 가능한 타일 수, $\le W \times H$)
- **K**: 현재 턴 스케줄러에 등록되어 있는 액티브 엔티티 수
- **N**: 각 자료구조 내부 원소 수 (Undo 이력 수, 인벤토리 아이템 수, 리더보드 기록 수 등)

---

## 2. 프로젝트 디렉토리 & 모듈 구조

### 2.1 디렉토리 트리

```text
dungeon_crawler/
├── main.py                  # 게임 엔트리포인트 및 메뉴 루프
├── core/
│   ├── types.py             # Coord, Tile, Entity, Player, Enemy, Item, Action, Record
│   ├── rng.py               # seed 고정용 무작위 난수 래퍼
│   └── events.py            # 이벤트 로그 메시지 큐
├── map/
│   ├── bsp.py               # BSP 트리 절차적 던전 생성 (padding=2 방 밀착 방지)
│   ├── dungeon.py           # Dungeon 컨테이너 (타일 그리드 + 방 목록)
│   └── fov.py               # Bresenham 직선 LOS 기반 시야 연산
├── systems/
│   ├── turn_manager.py      # Min-Heap heapq 기반 턴 관리 (lazy deletion 탑재)
│   ├── undo.py              # deque + Command 패턴 기반 시간 여행 (Undo/Redo)
│   ├── inventory.py         # dict 중첩 해시 테이블 인벤토리 시스템
│   └── ai.py                # A* 알고리즘 및 방 인지 기반 적 추적 AI
├── persistence/
│   ├── avl_tree.py          # AVL 트리 직접 구현 (자가 균형, size 필드 탑재)
│   └── leaderboard.py       # AVL 기반 리더보드 관리 및 JSON 직렬화
├── ui/
│   └── terminal.py          # rich + readchar 기반 플레이어 추적 스크롤 뷰포트 UI
└── tests/                   # 단위 테스트 스위트
```

### 2.2 모듈 의존 관계

**의존성 설계 원칙**: `core/types.py`는 의존성 그래프의 루트로서 어떠한 모듈에도 의존하지 않는다. 로직 모듈(`map`, `systems`, `persistence`)은 `core`에만 의존하며, UI 계층(`terminal.py`)은 로직 모듈을 소비하지만 로직 모듈은 UI의 세부 사항을 알지 못한다. 이는 텍스트 UI를 차후 그래픽 UI(예: Pygame)로 유연하게 교체할 수 있도록 설계된 아키텍처이다.

```text
┌──────────────┐
│     ui/      │  ← 교체 가능 (terminal ↔ pygame)
└──────┬───────┘
       ▼
┌──────────────────────┐
│ main.py (game loop)  │
└──┬─────────┬─────────┬┘
   ▼         ▼         ▼
 map/     systems/  persistence/
   │         │         │
   └─────────┼─────────┘
             ▼
       core/types.py
```

---

## 3. 공통 데이터 타입 (core/types.py)

모든 모듈이 공유하는 핵심 타입을 `@dataclass` 중심으로 정의한다. 해시 가능성과 불변성이 필요한 데이터는 `frozen=True`로 잠금 처리한다.

### 3.1 좌표와 타일

```python
from dataclasses import dataclass
from enum import Enum, auto

@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def __add__(self, other: "Coord") -> "Coord":
        return Coord(self.x + other.x, self.y + other.y)

    def manhattan(self, other: "Coord") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

class TileType(Enum):
    WALL = auto()
    FLOOR = auto()
    DOOR = auto()
    STAIRS = auto()

@dataclass
class Tile:
    type: TileType
    visible: bool = False    # 현재 시야 범위 내 존재 여부
    explored: bool = False   # 한 번이라도 탐험(시야 확보)했는지 여부

    @property
    def passable(self) -> bool:
        return self.type in (TileType.FLOOR, TileType.DOOR, TileType.STAIRS)
```

### 3.2 엔티티 (Entity)

```python
from dataclasses import dataclass, field

@dataclass
class Entity:
    id: int
    pos: Coord
    hp: int
    max_hp: int
    atk: int
    defense: int
    speed: int             # 턴 오프셋 계산용 속도 스탯
    alive: bool = True

@dataclass
class Player(Entity):
    xp: int = 0
    level: int = 1

@dataclass
class Enemy(Entity):
    kind: str = "goblin"
    path_cache: list[Coord] = field(default_factory=list)  # A* 탐색 경로 캐시
```

### 3.3 행동 패턴 (Action)

Command 패턴 형식을 빌려 구현하며, `undo()` 메소드에 `do()`의 역산 처리를 구현하여 간결한 되돌리기를 보장한다.

```python
class Action:
    def do(self, world) -> None:
        pass

    def undo(self, world) -> None:
        pass

class MoveAction(Action):
    def __init__(self, actor: Entity, dx: int, dy: int):
        self.actor = actor
        self.dx = dx
        self.dy = dy

class AttackAction(Action):
    def __init__(self, attacker: Entity, target: Entity):
        self.attacker = attacker
        self.target = target

class PickupAction(Action):
    def __init__(self, actor: Entity, tile: Coord, item: "Item"):
        self.actor = actor
        self.tile = tile
        self.item = item
```

---

## 4. 모듈별 구현 명세

### 4.1 절차적 던전 생성 — BSP Tree (map/bsp.py)

#### 4.1.1 선정 포인트
- 방끼리 서로 불규칙하게 겹치지 않으면서도 RPG 장르에 가장 부합하는 정형화된 방과 L자 형태 복도 레이아웃을 생성하기에 매우 적절하다.
- 이진 트리의 재귀적 분할과 리프(Leaf) 노드 탐색을 실질적인 2D 공간 배치 문제에 결합함으로써 트리 자료구조의 실용성을 보증한다.
- **밀착 버그 방지**: 인접 노드 방의 외벽이 직접 닿는 현상(`##` 밀착)을 방지하기 위해 생성 시 리프 노드 테두리와 무조건 **최소 2칸의 패딩**(`padding=2`)을 유지하도록 강제화했다.

#### 4.1.2 핵심 인터페이스

```python
@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> Coord:
        return Coord(self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: "Rect") -> bool:
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )

@dataclass
class BSPNode:
    rect: Rect
    left: "BSPNode" | None = None
    right: "BSPNode" | None = None
    room: Rect | None = None
```

```python
def generate_dungeon(
    width: int,
    height: int,
    min_leaf: int = 8,
    max_depth: int = 5,
    seed: int | None = None,
) -> Dungeon:
    """BSP 절차적 생성 알고리즘에 의해 던전을 생성합니다."""
    pass

def _split(node: BSPNode, depth: int, min_leaf: int, max_depth: int, rng: RNG) -> None:
    """재귀적으로 공간을 이진 분할합니다."""
    pass

def _create_rooms(node: BSPNode, rng: RNG, min_leaf: int) -> None:
    """리프 노드의 바운더리 안쪽에 최소 2칸의 여백(padding=2)을 두고 방을 무작위 생성합니다."""
    pass
```

#### 4.1.3 핵심 연산 복잡도

| 연산 | 시간복잡도 | 설명 |
| :--- | :--- | :--- |
| **이진 공간 분할** | $O(R)$ | $R = 2^{depth}$ 최대 노드 개수만큼 순차 분할 수행 |
| **방 생성** | $O(R)$ | 리프 노드의 수에 비례하여 방 할당 및 경계 패딩 연산 수행 |
| **복도 연결** | $O(R + \sum L)$ | 자식 노드의 방 중심점 간의 L자 형태 복도 연결 (L = 복도 타일 수) |
| **전체 생성** | $O(R \log R)$ 평균 | 트리 구조에 따른 분할 깊이 및 복도 선로 조각 배치 시간 소요 |

---

### 4.2 Undo 시스템 — Deque (systems/undo.py)

#### 4.2.1 선정 포인트
- 되돌리기 이력 한계를 상한 `limit = 30`으로 고정한 `collections.deque`를 채택했다. 이는 덱의 크기가 30을 초과할 경우 내부적으로 가장 먼저 일어났던 행동 데이터가 $O(1)$ 시간 만에 자동으로 폐기(`popleft`)되므로 추가적인 수작업 관리가 일절 필요치 않다.
- Command 패턴에 따른 역연산 데이터(Action)만 큐에 푸시하여 메모리 풋프린트를 최소화하고 상태 복원의 정확성을 확보했다.

#### 4.2.2 핵심 인터페이스

```python
class UndoSystem:
    def __init__(self, world, limit: int = 30):
        self.world = world
        self._history = deque(maxlen=limit)
        self._redo = deque(maxlen=limit)
        self.used = 0  # 총 사용 횟수 (리더보드 감점 패널티용)

    def execute(self, action: Action) -> None:
        """새로운 명령을 실행하고 Undo 이력에 추가하며, Redo 스택을 초기화합니다."""
        pass

    def undo(self) -> bool:
        """최근 실행한 명령을 역연산하여 이전 상태로 복구하고 Redo 목록으로 이관합니다."""
        pass

    def redo(self) -> bool:
        """취소했던 명령을 재실행합니다."""
        pass
```

#### 4.2.3 핵심 연산 복잡도

| 연산 | 시간복잡도 | 비고 |
| :--- | :--- | :--- |
| **명령 실행 (`execute`)** | $O(1)$ | 덱 삽입 자체는 항상 상수 시간 |
| **되돌리기 (`undo`)** | $O(1)$ | 덱의 `pop` 및 Action에 저장된 이전 값 역할당 적용 |
| **다시 실행 (`redo`)** | $O(1)$ | Redo 덱 pop 및 재실행 |
| **공간 복잡도** | $O(N)$ | 최대 되돌리기 한도인 $N \le 30$ 크기에 비례 |

---

### 4.3 턴 관리 시스템 — Priority Queue (systems/turn_manager.py)

#### 4.3.1 선정 포인트
- 플레이어와 적 몬스터들의 속도 스탯(Speed)에 따라 다음 턴 행동 가동 시각을 가중치 분배하기 위해 `heapq` (Min-Heap) 자료구조를 채택했다.
- 몬스터 사망 시 힙 트리 중심에서 원소를 강제로 찾아 지우는 비용($O(K)$)을 절감하기 위해, 지연 삭제 기법인 **Lazy Deletion** 방식을 도입하여 힙의 장점을 퇴색시키지 않고 $O(\log K)$ 성능을 유지하도록 보장했다.

#### 4.3.2 핵심 인터페이스

```python
class TurnManager:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()  # 비교 동률 방지 타이 브레이커용 카운터
        self._dead = set()  # 사망 엔티티 Lazy Deletion 대기 셋
        self._now = 0       # 글로벌 게임 누적 시간 프레임

    def schedule(self, entity: Entity, at: int) -> None:
        """Min-Heap에 턴 순서를 스케줄링합니다."""
        heapq.heappush(self._heap, (at, next(self._counter), entity))

    def next_actor(self) -> Entity | None:
        """사망 플래그를 스킵하며 최우선 턴 행동권을 지닌 엔티티를 반환합니다."""
        pass

    def advance(self, entity: Entity, cost: int = 100) -> None:
        """엔티티의 속도 스탯을 반영해 다음 행동 시각을 가중 계산하고 재스케줄링합니다."""
        pass
```

#### 4.3.3 핵심 연산 복잡도

| 연산 | 시간복잡도 | 설명 |
| :--- | :--- | :--- |
| **스케줄 추가 (`schedule`)** | $O(\log K)$ | Heap 트리 원소 정렬 삽입 |
| **다음 액터 팝 (`next_actor`)** | $O(\log K)$ 상환 | 사망한 엔티티는 상환 비용 하에서 O(1) 수준으로 빠르게 버려짐 |
| **비교 정합성 보장** | $O(1)$ | 동일 시각 원소 충돌 시 내부 시퀀스 카운터로 정렬 결정 보장 |

---

### 4.4 인벤토리 시스템 — Hash Table (systems/inventory.py)

#### 4.4.1 선정 포인트
- 고유한 아이템 ID 및 카테고리를 키로 수량 및 정보를 다이렉트 매핑하기 위해 파이썬의 해시 테이블 기반 `dict`를 이중 중첩 형식(`dict[ItemCategory, dict[str, Slot]]`)으로 적용했다.
- 카테고리별 분할 렌더링에 적절하게 대응하며 고속 아이템 조회를 완벽하게 충족한다.

#### 4.4.2 핵심 인터페이스

```python
@dataclass
class Slot:
    item: Item
    count: int

class Inventory:
    def __init__(self, capacity_per_cat: int = 20):
        self.capacity = capacity_per_cat
        self._by_cat = {c: {} for c in ItemCategory}

    def add(self, item: Item, count: int = 1) -> bool:
        """인벤토리 카테고리 슬롯에 아이템을 누적 합산합니다."""
        pass

    def remove(self, item_id: str, category: ItemCategory, count: int = 1) -> bool:
        """아이템 수량을 감소시키고 0이 될 경우 맵에서 완벽히 삭제합니다."""
        pass
```

---

### 4.5 적 AI 알고리즘 — A* Search (systems/ai.py)

#### 4.5.1 선정 포인트
- 대각선 이동을 배제하고 상하좌우 4방향 이동만 지원하는 격자 던전 환경에 부합하도록 가장 검증되고 admissible한 맨해튼 거리(Manhattan Distance)를 휴리스틱 함수로 적용했다.
- 최단거리 탐색의 오픈 셋(Open Set) 갱신 시 `heapq` 기반의 힙 연산을 적극 재사용하여 불필요한 연산 오버헤드를 극적으로 최소화했다.
- **방 소속 기반 몬스터 인식**: 연산의 최적화 및 자연스러운 레벨 디자인을 보장하기 위해, 플레이어가 몬스터와 **동일한 방(Room) 구역에 속해 있고 맨해튼 거리가 8칸 이하**일 때에만 인지 판정이 일어나 추적하도록 복합 트리거를 연동했다.

#### 4.5.2 핵심 인터페이스

```python
def manhattan(a: Coord, b: Coord) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)

def a_star(
    grid: list[list[Tile]],
    start: Coord,
    goal: Coord,
    passable: Callable[[Coord], bool],
) -> list[Coord]:
    """A* 알고리즘을 사용해 출발지에서 목적지까지의 최단 노드 리스트를 반환합니다."""
    pass
```

---

### 4.6 리더보드 시스템 — AVL Tree (persistence/leaderboard.py)

#### 4.6.1 선정 포인트
- 외부 영속화 및 리더보드 랭킹 산출 성능을 보장하기 위해 자가 균형 이진 탐색 트리인 **AVL 트리**를 어떠한 서드파티 라이브러리 없이 순수 파이썬으로 구현했다.
- 회전 연산(LL, LR, RL, RR)을 완벽하게 수립하고, 각 노드 내부에 자신을 루트로 하는 서브트리 노드의 전체 개수(`size`) 필드를 지속 트래킹하게 커스텀하여 **임의 노드의 랭킹(Rank) 조회 및 k번째 랭커 조회(kth)** 연산을 전부 안정적으로 최적화했다.

#### 4.6.2 핵심 인터페이스

```python
@dataclass
class AVLNode:
    key: Any
    value: Any
    left: "AVLNode" | None = None
    right: "AVLNode" | None = None
    height: int = 1
    size: int = 1  # 랭킹 순위 합산용 서브트리 크기 필드

class AVLTree:
    def insert(self, key: Any, value: Any) -> None:
        pass

    def delete(self, key: Any) -> bool:
        pass

    def kth(self, k: int) -> AVLNode | None:
        """서브트리의 size 필드를 참조하여 정확히 k번째(0-indexed)에 해당하는 순위 노드를 획득합니다."""
        pass

    def rank(self, key: Any) -> int:
        """지정된 정렬 키보다 크거나 작은 위치에 있는 원소의 개수를 세어 순위를 역산합니다."""
        pass
```

#### 4.6.3 정렬 키 우선순위 규약
랭킹 정렬 및 갱신은 다음 우선순위 튜플 키에 입각하여 수행된다:
`(-score, play_time_sec, undo_used, timestamp)`
(점수가 높을수록, 플레이 시간이 짧을수록, Undo 사용 횟수가 적을수록, 더 먼저 등록된 일자일수록 고순위를 점유한다.)

---

## 5. 단위 테스트 계획 및 검증 (tests/)

TDD(Test-Driven Development) 원칙을 엄수하여 신규 기능 구현 전에 실패하는 테스트를 선배치하고 이를 완전히 패스시키는 단계적 신뢰성 수립 프로세스를 전면 준수하고 있다.

### 5.1 test_terminal.py (신규 검증)
- `test_viewport_bounds_clamping`: 맵 경계 구석 `(0, 0)` 또는 `(59, 24)`에서 플레이어가 탐험 시 뷰포트 시작 오프셋이 경계 밖으로 이탈하지 않고 `(0, 0)` 및 `(25, 5)`로 완벽하게 락이 걸리는지 뷰포트 물리 클램핑을 검증한다.
- `test_viewport_rendered_dimensions`: 플레이어의 모든 이동 변수를 추적하여 콘솔에 렌더링을 시도할 때, 출력 해상도가 가로 70열(더블 문자화), 세로 20라인의 고정폭 해상도를 일관되게 유지하는지 뷰포트 규격의 고정 안전성을 검증한다.
- `test_viewport_double_character_rendering`: 벽(`██`), 바닥(`· `), 플레이어(`@ `) 등이 2글자 너비로 깨짐 현상 없이 완벽하게 대체 렌더링을 완수하는지 시각 정합성을 검증한다.

### 5.2 전체 테스트 무결성
- `pytest` 가동 시 신설된 시야 및 뷰포트 테스트 스위트를 아우른 **총 65개 전체 단위 테스트가 100% 정상 통과(Green)** 상태를 충족해야 합격으로 간주한다.
- `ruff check .` 및 `ruff format .` 구동 시 일체의 린트 에러나 미조율 공백 경고 없이 패스하는 것을 보증해야 마스터 브랜치 머지가 허용된다.
