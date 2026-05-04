자료구조와 알고리즘 기말 프로젝트

**Python Dungeon Crawler RPG**

*--- 구현 명세서 (Implementation Specification) ---*

BSP · Deque · Priority Queue · Hash Map · A\* · AVL Tree

작성일: 2026-04-18

언어: Python 3.10+ / 환경: 터미널(rich) → pygame 선택적 확장

**1. 문서 개요**

본 문서는 DS&A 기말 프로젝트 『Dungeon Crawler RPG』의 구현 명세서이다.
앞서 제출한 계획서(후보 비교)에서 결정된 다음 6가지 자료구조/알고리즘에
대해, 팀원이 바로 코드로 옮길 수 있도록 모듈 구조·공통 데이터 타입·함수
시그니처·의사코드·복잡도·테스트 계획을 정리한다.

**1.1 확정된 자료구조/알고리즘**

  --------------- -----------------------------------------------------
  ① 던전 생성     BSP (Binary Space Partitioning) Tree
  ② Undo 시스템   Deque (collections.deque, maxlen=30) + Command 패턴
  ③ 턴 관리       Priority Queue (heapq, Min-Heap) with lazy deletion
  ④ 인벤토리      Hash Table (Python dict) --- 카테고리별 중첩 dict
  ⑤ 적 AI         A\* 알고리즘 (맨해튼 거리 휴리스틱)
  ⑥ 리더보드      Self-Balancing BST (AVL Tree, 직접 구현)
  --------------- -----------------------------------------------------

**1.2 용어 정의**

-   W, H: 던전 맵의 너비·높이 (타일 단위)

-   R: 생성된 방(Room)의 수, E: 방 사이 복도 간선 수

-   V: A\*의 정점 수(= 통과 가능한 타일 수, ≤ W·H)

-   K: 현재 턴 스케줄에 올라가 있는 엔티티 수

-   N: 각 자료구조 내부 원소 수 (문맥에 따라 Undo 기록/인벤토리
    아이템/리더보드 기록)

**2. 프로젝트 디렉토리 & 모듈 구조**

**2.1 디렉토리 트리**

  -----------------------------------------------------------------
  dungeon\_crawler/
  ├── main.py \# 게임 엔트리포인트, 루프
  ├── core/
  │ ├── \_\_init\_\_.py
  │ ├── types.py \# Coord, Tile, Entity, Item, Action (공통 타입)
  │ ├── rng.py \# seed 고정용 랜덤 래퍼
  │ └── events.py \# 이벤트 로그 (UI용 메시지 큐)
  ├── map/
  │ ├── \_\_init\_\_.py
  │ ├── bsp.py \# BSP 던전 생성
  │ ├── dungeon.py \# Dungeon 클래스 (타일 그리드 + 방 목록)
  │ └── fov.py \# 시야 계산 (Shadowcasting)
  ├── systems/
  │ ├── \_\_init\_\_.py
  │ ├── turn\_manager.py \# heapq 기반 Priority Queue 턴 관리
  │ ├── undo.py \# deque 기반 Undo
  │ ├── inventory.py \# dict 기반 인벤토리
  │ └── ai.py \# A\* 경로 탐색
  ├── persistence/
  │ ├── \_\_init\_\_.py
  │ ├── avl\_tree.py \# AVL Tree 직접 구현
  │ └── leaderboard.py \# 리더보드(AVL 이용) + JSON 직렬화
  ├── ui/
  │ ├── \_\_init\_\_.py
  │ └── terminal.py \# rich 기반 렌더링
  └── tests/
  ├── test\_bsp.py
  ├── test\_undo.py
  ├── test\_turn\_manager.py
  ├── test\_inventory.py
  ├── test\_ai.py
  └── test\_avl\_leaderboard.py
  -----------------------------------------------------------------

**2.2 모듈 의존 관계**

기본 원칙: core는 누구에게도 의존하지 않고, map·systems·persistence는
core에만 의존한다. UI 계층(terminal.py, 추후 pygame.py)은 모든 모듈을
소비하되 로직 모듈은 UI를 모른다 --- 나중에 pygame으로 교체해도 게임
로직이 영향을 받지 않게 하기 위한 레이어링이다.

  -----------------------------------------
  ┌──────────────┐
  │ ui/ │ ← 교체 가능 (terminal ↔ pygame)
  └──────┬───────┘
  ▼
  ┌──────────────────────┐
  │ main.py (game loop) │
  └──┬─────────┬─────────┬┘
  ▼ ▼ ▼
  map/ systems/ persistence/
  │ │ │
  └─────────┴─────────┘
  ▼
  core/types.py
  -----------------------------------------

**3. 공통 데이터 타입 (core/types.py)**

모든 모듈이 공유하는 핵심 타입을 dataclass 중심으로 정의한다. 불변성이
필요한 값은 frozen=True로 잠근다.

**3.1 좌표와 타일**

  ----------------------------------------------------------------------
  from dataclasses import dataclass, field
  from enum import Enum, auto
  from typing import Optional
  \@dataclass(frozen=True)
  class Coord:
  x: int
  y: int
  def \_\_add\_\_(self, other: \'Coord\') -\> \'Coord\':
  return Coord(self.x + other.x, self.y + other.y)
  class TileType(Enum):
  WALL = auto()
  FLOOR = auto()
  DOOR = auto()
  STAIRS = auto()
  \@dataclass
  class Tile:
  type: TileType
  visible: bool = False \# 현재 시야
  explored: bool = False \# 이전에 본 적 있음
  \@property
  def passable(self) -\> bool:
  return self.type in (TileType.FLOOR, TileType.DOOR, TileType.STAIRS)
  ----------------------------------------------------------------------

**3.2 엔티티**

  ---------------------------------------------------------------------
  \@dataclass
  class Entity:
  id: int
  pos: Coord
  hp: int
  max\_hp: int
  atk: int
  def\_: int
  speed: int \# 높을수록 자주 행동 (턴 관리에서 사용)
  alive: bool = True
  \@dataclass
  class Player(Entity):
  xp: int = 0
  level: int = 1
  \# inventory, undo\_system, stats는 별도 시스템이 소유
  \@dataclass
  class Enemy(Entity):
  kind: str = \'goblin\'
  path\_cache: list = field(default\_factory=list) \# 마지막 A\* 결과
  ---------------------------------------------------------------------

**3.3 아이템과 행동(Action)**

  ----------------------------------------------------------------------
  class ItemCategory(Enum):
  WEAPON = \'WEAPON\'
  ARMOR = \'ARMOR\'
  CONSUMABLE = \'CONSUMABLE\'
  \@dataclass(frozen=True)
  class Item:
  id: str \# ex) \'iron\_sword\'
  name: str \# 표시용
  category: ItemCategory
  effect: dict \# {\'atk\': +5} 등
  class Action:
  \'\'\'Command 패턴 베이스. do()의 역산을 undo()에 구현.\'\'\'
  def do(self, world) -\> None: \...
  def undo(self, world) -\> None: \...
  class MoveAction(Action):
  def \_\_init\_\_(self, actor: Entity, dx: int, dy: int): \...
  class AttackAction(Action):
  def \_\_init\_\_(self, attacker: Entity, target: Entity): \...
  class UseItemAction(Action):
  def \_\_init\_\_(self, actor: Entity, item\_id: str): \...
  class PickupAction(Action):
  def \_\_init\_\_(self, actor: Entity, tile: Coord, item: Item): \...
  ----------------------------------------------------------------------

**3.4 기록(Record)**

  --------------------------------------------------------------
  \@dataclass(frozen=True)
  class Record:
  name: str
  score: int
  play\_time\_sec: int
  undo\_used: int
  timestamp: str \# ISO 8601
  \# 정렬 키: (-score, play\_time\_sec, undo\_used, timestamp)
  --------------------------------------------------------------

**4. 모듈별 구현 명세**

**4.1 던전 생성 --- BSP Tree (map/bsp.py)**

**선정 이유**

-   계획서에서 '2D 배열 + 그래프 + BFS' 대신 BSP를 택한 이유: 방이
    겹치지 않으며 자연스럽게 분포하여 RPG 특유의 '방+복도' 레이아웃이
    나온다.

-   트리 자료구조를 교재 범위 안에서 활용하는 구체 사례를 확보할 수 있어
    학습 효과가 크다.

-   재귀 분할이 끝난 후, 리프의 방 중심을 형제끼리 복도로 연결하는
    방식이 명확하여 팀원 간 역할 분담이 쉽다.

**핵심 인터페이스**

  --------------------------------------------------------------------
  \# map/bsp.py
  from dataclasses import dataclass, field
  from typing import Optional
  from core.types import Coord, Tile, TileType
  from map.dungeon import Dungeon
  \@dataclass
  class Rect:
  x: int; y: int; w: int; h: int
  \@property
  def center(self) -\> Coord:
  return Coord(self.x + self.w // 2, self.y + self.h // 2)
  \@dataclass
  class BSPNode:
  rect: Rect
  left: Optional\[\'BSPNode\'\] = None
  right: Optional\[\'BSPNode\'\] = None
  room: Optional\[Rect\] = None
  def generate\_dungeon(
  width: int, height: int,
  min\_leaf: int = 8,
  max\_depth: int = 5,
  seed: Optional\[int\] = None,
  ) -\> Dungeon:
  \'\'\'BSP로 던전을 생성해 Dungeon 객체를 반환.\'\'\'
  def \_split(node: BSPNode, depth: int, rng) -\> None:
  \'\'\'node.rect를 수직 또는 수평으로 분할해 자식 생성.\'\'\'
  def \_create\_rooms(node: BSPNode, rng) -\> None:
  \'\'\'리프 노드마다 rect 안에 무작위 방 생성.\'\'\'
  def \_connect(node: BSPNode, grid: list\[list\[Tile\]\]) -\> None:
  \'\'\'좌/우 자식의 방 중심을 L자 복도로 잇고, 재귀.\'\'\'
  --------------------------------------------------------------------

**의사코드**

  ------------------------------------------------------------------------
  function generate\_dungeon(W, H, min\_leaf, max\_depth, seed):
  rng = Random(seed)
  root = BSPNode(Rect(0, 0, W, H))
  grid = \[\[Tile(WALL)\] \* W for \_ in range(H)\]
  \_split(root, 0, rng)
  \_create\_rooms(root, rng)
  carve\_rooms\_into\_grid(root, grid)
  \_connect(root, grid)
  return Dungeon(grid=grid, rooms=collect\_rooms(root))
  function \_split(node, depth, rng):
  if depth \>= max\_depth: return
  if node.rect.w \< 2\*min\_leaf and node.rect.h \< 2\*min\_leaf: return
  split\_horiz = choose\_orientation(node.rect, rng)
  if split\_horiz:
  cut = rng.randint(min\_leaf, node.rect.h - min\_leaf)
  node.left = BSPNode(top half)
  node.right = BSPNode(bottom half)
  else:
  cut = rng.randint(min\_leaf, node.rect.w - min\_leaf)
  node.left = BSPNode(left half)
  node.right = BSPNode(right half)
  \_split(node.left, depth+1, rng)
  \_split(node.right, depth+1, rng)
  function \_connect(node, grid):
  if node.left is None or node.right is None: return
  \_connect(node.left, grid); \_connect(node.right, grid)
  c1 = center\_of\_any\_room(node.left)
  c2 = center\_of\_any\_room(node.right)
  carve\_L\_corridor(grid, c1, c2) \# 먼저 수평, 다음 수직 (랜덤)
  ------------------------------------------------------------------------

**복잡도**

  ------------------------- ----------------- --------------------------------------------
  **연산**                  **시간복잡도**    **비고**
  분할 \_split(·)           O(R)              R = 2\^max\_depth 이하. 각 노드 상수 연산.
  방 생성 \_create\_rooms   O(R)              리프마다 상수.
  복도 연결 \_connect       O(R + ΣL)         L = 복도 길이. 평균 O(R · (W+H)/√R).
  전체 generate\_dungeon    O(R log R) 평균   분할 깊이 log R, 각 레벨 O(R).
  공간                      O(W·H)            타일 그리드가 지배적.
  ------------------------- ----------------- --------------------------------------------

**엣지 케이스**

-   분할 불가(너무 좁은 공간): depth 조건과 min\_leaf 조건 둘 다
    검사하여 재귀 종료.

-   복도가 기존 방을 관통할 수 있음 → 허용(자연스러운 도어로 렌더링).

-   seed가 같으면 결과가 항상 같아야 함 → rng를 인자로만 전달, 전역
    random 금지 (테스트 가능성 확보).

**4.2 Undo 시스템 --- Deque + Command (systems/undo.py)**

**선정 이유**

-   maxlen=30을 지정한 collections.deque는 한도 초과 시 popleft가 O(1)로
    자동 수행되어, 요구사항(최근 30회만 보관)을 자료구조 자체가
    강제해준다.

-   Command 패턴과 결합하면 '상태 스냅샷'이 아니라 '행동의 역산'만
    저장해 메모리가 작고 디버깅이 쉽다.

-   추후 Redo 확장 시 redo\_stack을 하나 추가하는 것만으로 끝난다.

**핵심 인터페이스**

  ----------------------------------------------------------
  \# systems/undo.py
  from collections import deque
  from core.types import Action
  class UndoSystem:
  def \_\_init\_\_(self, world, limit: int = 30):
  self.world = world
  self.\_history: deque\[Action\] = deque(maxlen=limit)
  self.\_redo: deque\[Action\] = deque(maxlen=limit)
  self.used: int = 0 \# 누적 undo 사용 횟수(리더보드 지표)
  def execute(self, action: Action) -\> None:
  action.do(self.world)
  self.\_history.append(action)
  self.\_redo.clear() \# 새 행동 시 redo 무효화
  def undo(self) -\> bool:
  if not self.\_history: return False
  action = self.\_history.pop()
  action.undo(self.world)
  self.\_redo.append(action)
  self.used += 1
  return True
  def redo(self) -\> bool:
  if not self.\_redo: return False
  action = self.\_redo.pop()
  action.do(self.world); self.\_history.append(action)
  return True
  \@property
  def remaining(self) -\> int:
  return self.\_history.maxlen - len(self.\_history)
  ----------------------------------------------------------

**복잡도**

  --------------------- ---------------- ----------------------------
  **연산**              **시간복잡도**   **비고**
  execute(action)       O(1) + do()      Action 내부 비용이 지배적.
  undo()                O(1) + undo()    스택 pop + 역산.
  redo()                O(1) + do()      동일.
  한도 초과 자동 폐기   O(1)             deque(maxlen) 내장 동작.
  공간                  O(N)             N ≤ 30.
  --------------------- ---------------- ----------------------------

**주의사항**

-   각 Action.undo()는 반드시 do() 이전의 상태로 정확히 복원되어야 한다
    (특히 RNG 사용 시 Action 내부에 결과를 기록).

-   새 execute()가 들어오면 redo 덱을 비워 '가지치기' --- 사용자 기대와
    일치.

**4.3 턴 관리 --- Priority Queue (systems/turn\_manager.py)**

**선정 이유**

-   heapq는 Python 표준 라이브러리의 Min-Heap으로 push/pop이 O(log K).
    엔티티마다 다음 행동 시각(next\_time)을 키로 하면 속도(speed) 스탯을
    자연스럽게 반영할 수 있다.

-   라운드 로빈 Queue보다 구현이 조금 더 복잡하지만 '빠른 적' 같은 RPG
    요소를 지원할 수 있어 데모 가치가 높다.

-   heapq는 원소 제거(O(N))가 약점 --- 엔티티 사망은 lazy deletion으로
    해결한다.

**핵심 인터페이스**

  --------------------------------------------------------------------
  \# systems/turn\_manager.py
  import heapq, itertools
  from core.types import Entity
  class TurnManager:
  def \_\_init\_\_(self):
  self.\_heap: list\[tuple\[int, int, Entity\]\] = \[\]
  self.\_counter = itertools.count() \# tie-break
  self.\_dead: set\[int\] = set() \# lazy 삭제
  self.\_now: int = 0
  def schedule(self, entity: Entity, at: int) -\> None:
  heapq.heappush(self.\_heap, (at, next(self.\_counter), entity))
  def next\_actor(self) -\> Entity \| None:
  while self.\_heap:
  t, \_, e = heapq.heappop(self.\_heap)
  if e.id in self.\_dead or not e.alive: continue
  self.\_now = t
  return e
  return None
  def advance(self, entity: Entity, cost: int = 100) -\> None:
  next\_t = self.\_now + max(1, cost \* 100 // max(1, entity.speed))
  self.schedule(entity, next\_t)
  def remove(self, entity: Entity) -\> None:
  self.\_dead.add(entity.id)
  --------------------------------------------------------------------

**의사코드 (메인 루프 관점)**

  ----------------------------------------------
  loop:
  actor = turn\_manager.next\_actor()
  if actor is None: break \# 모든 엔티티 사망
  if actor is player:
  action = read\_input()
  undo\_system.execute(action)
  else:
  action = ai.decide(actor, world) \# A\* 사용
  action.do(world)
  turn\_manager.advance(actor, action.cost)
  ----------------------------------------------

**복잡도**

  ------------------ ---------------- ---------------------------------------
  **연산**           **시간복잡도**   **비고**
  schedule(e, t)     O(log K)         heappush.
  next\_actor()      O(log K) 상환    평균적으로 죽은 엔티티 1\~2개만 스킵.
  advance(e, cost)   O(log K)         재삽입.
  remove(e)          O(1)             lazy: \_dead에 id 추가.
  공간               O(K)             힙 크기 = 살아있는 엔티티 수에 비례.
  ------------------ ---------------- ---------------------------------------

**주의사항**

-   entity 객체를 키로 직접 비교하지 않는다 → tuple의 두 번째 항(자동
    증가 counter)이 tie-break.

-   \_dead 집합이 무한히 커지지 않도록, 힙이 비거나 특정 주기마다
    compact() 수행 권장(선택 과제).

**4.4 인벤토리 --- Hash Table (systems/inventory.py)**

**선정 이유**

-   Python dict는 오픈 어드레싱 기반 해시 테이블로 삽입·조회·삭제 평균
    O(1). 아이템 id 기반 조회·수량 누적이 주된 연산이므로 최적.

-   카테고리별 표시는 외곽 dict로 카테고리를 키 삼아 중첩하면, 카테고리
    단위 렌더링이 O(Cat) + 카테고리 내 원소 수에 비례.

**핵심 인터페이스**

  -----------------------------------------------------------------------------------
  \# systems/inventory.py
  from dataclasses import dataclass
  from core.types import Item, ItemCategory
  \@dataclass
  class Slot:
  item: Item
  count: int
  class Inventory:
  def \_\_init\_\_(self, capacity\_per\_cat: int = 20):
  self.capacity = capacity\_per\_cat
  self.\_by\_cat: dict\[ItemCategory, dict\[str, Slot\]\] = {
  c: {} for c in ItemCategory
  }
  def add(self, item: Item, count: int = 1) -\> bool:
  bucket = self.\_by\_cat\[item.category\]
  if item.id in bucket:
  bucket\[item.id\].count += count
  else:
  if len(bucket) \>= self.capacity: return False
  bucket\[item.id\] = Slot(item, count)
  return True
  def remove(self, item\_id: str, category: ItemCategory, count: int = 1) -\> bool:
  bucket = self.\_by\_cat\[category\]
  slot = bucket.get(item\_id)
  if slot is None or slot.count \< count: return False
  slot.count -= count
  if slot.count == 0: del bucket\[item\_id\]
  return True
  def list(self, category: ItemCategory) -\> list\[Slot\]:
  return list(self.\_by\_cat\[category\].values())
  def total(self) -\> int:
  return sum(slot.count for b in self.\_by\_cat.values() for slot in b.values())
  -----------------------------------------------------------------------------------

**복잡도**

  -------------------- ---------------- --------------------------
  **연산**             **시간복잡도**   **비고**
  add(item, n)         O(1) 평균        dict 삽입.
  remove(id, cat, n)   O(1) 평균        dict 조회+삭제.
  list(cat)            O(\|cat\|)       해당 카테고리 아이템 수.
  total()              O(Σ\|cat\|)      전체 아이템 수.
  공간                 O(N)             N = 고유 아이템 수.
  -------------------- ---------------- --------------------------

**엣지 케이스**

-   동일 id 아이템 중복 획득 → count에 합산.

-   capacity 초과 시 add는 False 반환(호출자가 '가방 가득참' 메시지
    처리).

-   count=0이 되면 반드시 key를 제거해 list() 결과에서 사라지게 한다.

**4.5 적 AI --- A\* (systems/ai.py)**

**선정 이유**

-   그리드 기반 단일 출발·단일 목표 최단경로의 사실상 표준. 맨해튼 거리
    휴리스틱은 4방향 이동에서 admissible이면서도 Dijkstra 대비 탐색 타일
    수를 크게 줄여준다.

-   open set을 heapq로 관리하면 코드가 간결하며 앞서 정한
    자료구조(heap)의 재사용 사례가 된다.

-   여러 적이 매 턴 경로를 계산해야 하므로 실전 성능이 Dijkstra보다
    확실히 유리.

**핵심 인터페이스**

  --------------------------------------------------------------------------------
  \# systems/ai.py
  import heapq
  from typing import Callable, Iterable
  from core.types import Coord
  Heuristic = Callable\[\[Coord, Coord\], int\]
  def manhattan(a: Coord, b: Coord) -\> int:
  return abs(a.x - b.x) + abs(a.y - b.y)
  NEIGHBORS = (Coord(1,0), Coord(-1,0), Coord(0,1), Coord(0,-1))
  def a\_star(
  grid, start: Coord, goal: Coord,
  passable: Callable\[\[Coord\], bool\],
  h: Heuristic = manhattan,
  ) -\> list\[Coord\]:
  \'\'\'start→goal 최단경로(포함). 실패 시 \[\]. 대각선 불가.\'\'\'
  class EnemyAI:
  def decide(self, enemy, player\_pos, world) -\> \'Action\':
  if not enemy.path\_cache or enemy.path\_cache\[-1\] != player\_pos:
  enemy.path\_cache = a\_star(world.grid, enemy.pos, player\_pos,
  passable=world.is\_passable)
  if len(enemy.path\_cache) \< 2: return WaitAction(enemy)
  next\_pos = enemy.path\_cache\[1\]
  return MoveAction(enemy, next\_pos.x - enemy.pos.x, next\_pos.y - enemy.pos.y)
  --------------------------------------------------------------------------------

**의사코드**

  -------------------------------------------------------------
  function a\_star(grid, start, goal, passable, h):
  open\_heap = \[(h(start, goal), 0, start)\] \# (f, g, node)
  came\_from = {}
  g\_score = {start: 0}
  while open\_heap:
  f, g, cur = heappop(open\_heap)
  if cur == goal: return reconstruct(came\_from, cur)
  for d in NEIGHBORS:
  nxt = cur + d
  if not in\_bounds(grid, nxt) or not passable(nxt): continue
  ng = g + 1
  if ng \< g\_score.get(nxt, INF):
  g\_score\[nxt\] = ng
  came\_from\[nxt\] = cur
  heappush(open\_heap, (ng + h(nxt, goal), ng, nxt))
  return \[\] \# 도달 불가
  -------------------------------------------------------------

**복잡도**

  ------------------ ------------------- --------------------------------------
  **연산**           **시간복잡도**      **비고**
  a\_star() 평균     O(E log V)          V = 통과 가능한 타일, E ≈ 4V(4방향).
  a\_star() 최악     ≈ Dijkstra          휴리스틱이 상수면 Dijkstra와 동일.
  EnemyAI.decide()   캐시 히트 시 O(1)   플레이어 위치 미변경 시 재계산 생략.
  공간               O(V)                open set + came\_from + g\_score.
  ------------------ ------------------- --------------------------------------

**엣지 케이스**

-   목표 도달 불가(벽으로 고립) 시 빈 리스트 반환 → AI는 WaitAction으로
    폴백.

-   tie-break: f가 같으면 counter로 구분(heapq에 동일 키 충돌 방지, 턴
    매니저와 동일 기법).

-   경로 캐시는 플레이어 이동 또는 벽 변경 시 무효화.

**4.6 리더보드 --- AVL Tree (persistence/avl\_tree.py, leaderboard.py)**

**선정 이유**

-   리더보드는 삽입·정렬 순회·k번째 순위 조회가 모두 중요하다.
    Self-balancing BST는 세 연산 모두 O(log N)을 보장하여 기록이
    많아져도 안정적이다.

-   AVL은 Red-Black보다 구현이 단순하고 균형 조건이 엄격(h ≤
    log₂(N+2))해 조회 성능이 유리. 수업에서 다뤘을 가능성이 높아 학습
    효과도 크다.

-   외부 라이브러리에 의존하지 않고 '자료구조를 직접 구현했다'는 평가
    기준 측면에서 프로젝트의 하이라이트가 된다.

**정렬 키 규약**

Record 간 비교 키는 (-score, play\_time\_sec, undo\_used, timestamp)의
튜플. 점수 내림차순을 위해 score에 음수를 취한다. AVLTree는 일반적인 키
비교(\<, ==)를 사용한다.

**핵심 인터페이스**

  ---------------------------------------------------------------------------
  \# persistence/avl\_tree.py
  from dataclasses import dataclass, field
  from typing import Any, Optional, Iterator
  \@dataclass
  class AVLNode:
  key: Any
  value: Any
  left: Optional\[\'AVLNode\'\] = None
  right: Optional\[\'AVLNode\'\] = None
  height: int = 1
  size: int = 1 \# 서브트리 크기(rank 조회용)
  class AVLTree:
  def \_\_init\_\_(self): self.root: Optional\[AVLNode\] = None
  def \_\_len\_\_(self) -\> int: \...
  def insert(self, key, value) -\> None: \...
  def delete(self, key) -\> bool: \...
  def search(self, key) -\> Optional\[Any\]: \...
  def kth(self, k: int) -\> Optional\[AVLNode\]: \# 0-indexed
  \...
  def rank(self, key) -\> int: \... \# key 미만 노드 수
  def in\_order(self) -\> Iterator\[AVLNode\]: \...
  \# 내부: \_rotate\_left, \_rotate\_right, \_rebalance, \_height, \_update
  ---------------------------------------------------------------------------

  ---------------------------------------------------------------------------------
  \# persistence/leaderboard.py
  import json, pathlib
  from core.types import Record
  from persistence.avl\_tree import AVLTree
  def \_key(r: Record) -\> tuple:
  return (-r.score, r.play\_time\_sec, r.undo\_used, r.timestamp)
  class Leaderboard:
  def \_\_init\_\_(self, path: pathlib.Path):
  self.path = path
  self.tree = AVLTree()
  self.load()
  def add(self, record: Record) -\> int:
  self.tree.insert(\_key(record), record)
  self.save()
  return self.tree.rank(\_key(record)) \# 등수
  def top(self, k: int = 10) -\> list\[Record\]:
  out = \[\]
  for i, node in enumerate(self.tree.in\_order()):
  if i \>= k: break
  out.append(node.value)
  return out
  def save(self) -\> None:
  data = \[rec.\_\_dict\_\_ for rec in (n.value for n in self.tree.in\_order())\]
  self.path.write\_text(json.dumps(data, ensure\_ascii=False, indent=2))
  def load(self) -\> None:
  if not self.path.exists(): return
  for d in json.loads(self.path.read\_text()):
  r = Record(\*\*d); self.tree.insert(\_key(r), r)
  ---------------------------------------------------------------------------------

**AVL 회전 의사코드**

  ------------------------------------------------------------------
  function insert(node, key, value):
  if node is None: return AVLNode(key, value)
  if key \< node.key: node.left = insert(node.left, key, value)
  else: node.right = insert(node.right, key, value)
  \_update(node) \# height, size 갱신
  return \_rebalance(node)
  function \_rebalance(n):
  bf = balance\_factor(n) \# h(left) - h(right)
  if bf \> 1 and key \< n.left.key: return rotate\_right(n) \# LL
  if bf \> 1 and key \> n.left.key:
  n.left = rotate\_left(n.left); return rotate\_right(n) \# LR
  if bf \< -1 and key \> n.right.key: return rotate\_left(n) \# RR
  if bf \< -1 and key \< n.right.key:
  n.right = rotate\_right(n.right); return rotate\_left(n) \# RL
  return n
  ------------------------------------------------------------------

**복잡도**

  ------------------ ---------------- ---------------------------
  **연산**           **시간복잡도**   **비고**
  insert(key, val)   O(log N)         AVL 균형 보장.
  delete(key)        O(log N)         successor 교체 + 회전.
  search(key)        O(log N)         이진 탐색.
  kth(k)             O(log N)         각 노드의 size 필드 활용.
  in\_order()        O(N)             모든 기록 정렬 순회.
  공간               O(N)             노드 하나당 O(1).
  ------------------ ---------------- ---------------------------

**파일 영속화 & 엣지 케이스**

-   저장: in\_order() 결과를 JSON 배열로 직렬화. 읽기 시에는 insert
    순서가 다르므로 AVL이 재균형.

-   파일 손상(JSON 파싱 실패) 시 빈 리더보드로 초기화 + 백업
    파일(.bak)로 이동.

-   동점 처리: 정렬 키 튜플의 tie-break(시간→undo→timestamp)로 자동
    해결.

**5. 단위 테스트 계획 (tests/)**

pytest 기반. 각 모듈별로 정상 경로·경계값·실패 경로를 최소 한 개씩
포함한다. CI가 없으므로 \`pytest -q tests/\`를 main 머지 전에 각자
로컬에서 실행한다.

**5.1 test\_bsp.py**

-   generate\_dungeon(seed=42)가 항상 같은 결과를 반환한다 (결정론
    검증).

-   생성된 방 수가 \[2\^max\_depth/2, 2\^max\_depth\] 범위 안에 있다.

-   모든 방이 BFS로 서로 도달 가능하다 (연결성).

-   서로 다른 두 방의 Rect가 겹치지 않는다.

**5.2 test\_undo.py**

-   FakeAction(do/undo가 카운터 증감)으로 execute × N회 후 undo × N회 시
    초기 상태 복원 검증.

-   execute × 31회 시 가장 오래된 기록이 폐기되고 undo 가능 횟수가
    정확히 30.

-   execute 후 undo 후 새 execute → redo 덱이 비워져 있다.

**5.3 test\_turn\_manager.py**

-   speed=100, speed=200 두 엔티티에서 빠른 쪽이 단위 시간당 2배
    행동한다.

-   remove(enemy) 후 next\_actor()가 해당 enemy를 반환하지 않는다 (lazy
    deletion).

-   동일 시각 tie-break가 안정적(등록 순서 유지).

**5.4 test\_inventory.py**

-   같은 id의 아이템 add(2), add(3) 후 count == 5.

-   capacity 초과 add()가 False를 반환하며 내부 상태가 변하지 않는다.

-   remove로 count=0 도달 시 list(cat)에서 사라진다.

**5.5 test\_ai.py**

-   벽이 없는 5×5 그리드에서 a\_star((0,0),(4,4)) 길이 == 9 (맨해튼 +
    1).

-   벽으로 둘러싸인 목표는 \[\]를 반환.

-   가능한 경로가 여러 개인 경우 길이는 동일해야 한다(다양성은 허용).

**5.6 test\_avl\_leaderboard.py**

-   랜덤 1,000개 insert 후 각 노드의 balance\_factor가 \[-1, 0, 1\]에
    속한다.

-   in\_order() 결과가 정렬 키 기준 오름차순이다.

-   kth(0) == 1등, kth(k-1) == k등.

-   save() → load() 왕복 후 top(10) 결과가 동일하다.

-   손상된 JSON 로드 시 예외가 아닌 빈 리더보드로 복구된다.

**6. 구현 체크리스트 (한눈 보기)**

  ----------- ----------------------------- ---------------------- ---------------------------------------------
  **모듈**    **자료구조/알고리즘**         **핵심 연산 복잡도**   **선정 포인트(한 줄)**
  던전 생성   BSP Tree                      O(R log R)             겹침 없는 방+복도, 트리 재귀의 교과서적 예.
  Undo        deque(maxlen=30)+Command      O(1)                   한도 자동 관리 + Redo 확장 용이.
  턴 관리     heapq (Min-Heap) + lazy del   O(log K)               속도 스탯 반영 가능, heap 학습.
  인벤토리    dict (nested by category)     평균 O(1)              UI/수량 관리 모두 친화적.
  적 AI       A\* + manhattan               O(E log V)             그리드 최단경로 표준, heap 재사용.
  리더보드    AVL Tree (직접 구현)          O(log N)               insert/rank/kth 모두 균형 보장.
  ----------- ----------------------------- ---------------------- ---------------------------------------------

이 명세서는 터미널(rich) 버전의 MVP를 기준으로 작성되었다. 후속 pygame
확장 시에는 ui/pygame\_ui.py만 추가하고, systems/·map/·persistence/는
건드리지 않는 것을 원칙으로 한다.
