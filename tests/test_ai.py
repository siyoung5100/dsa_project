"""systems/ai.py 단위 테스트.

명세서 §5.5 시나리오 참고:
- 최단 경로 길이 검증 (장애물 없을 때)
- 장애물(벽) 회피 검증
- 도달 불가능한 경우 처리
"""

from core.types import Coord
from systems.ai import a_star, manhattan


def test_a_star_basic():
    """벽이 없는 평지에서 최단 경로 검증."""
    start = Coord(0, 0)
    goal = Coord(4, 4)

    def passable(c: Coord) -> bool:
        return True  # 모든 곳 통과 가능

    path = a_star(start, goal, passable)

    # (0,0)에서 (4,4)까지 맨해튼 거리는 8, 경로는 시작점 포함 9칸이어야 함.
    assert len(path) == 9
    assert path[0] == start
    assert path[-1] == goal


def test_a_star_obstacle():
    """벽을 피해가는지 검증.
    S . .
    # # .
    . . G
    """
    start = Coord(0, 0)
    goal = Coord(2, 2)

    walls = {Coord(0, 1), Coord(1, 1)}

    def passable(c: Coord) -> bool:
        if c.x < 0 or c.y < 0 or c.x > 2 or c.y > 2:
            return False
        return c not in walls

    path = a_star(start, goal, passable)

    # 경로는 (0,0) -> (1,0) -> (2,0) -> (2,1) -> (2,2) 여야 함.
    expected = [Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(2, 1), Coord(2, 2)]
    assert path == expected


def test_a_star_unreachable():
    """도달 불가능한 경우 빈 리스트 반환."""
    start = Coord(0, 0)
    goal = Coord(2, 2)

    # 목적지를 완전히 벽으로 둘러쌈 (4방향)
    walls = {Coord(1, 2), Coord(2, 1), Coord(3, 2), Coord(2, 3)}

    def passable(c: Coord) -> bool:
        # 영역 제한 (0~5)
        if not (0 <= c.x <= 5 and 0 <= c.y <= 5):
            return False
        return c not in walls

    path = a_star(start, goal, passable)
    assert path == []


def test_manhattan():
    assert manhattan(Coord(0, 0), Coord(3, 4)) == 7
    assert manhattan(Coord(1, 1), Coord(1, 1)) == 0


def test_enemy_ai_perception():
    """복합 몬스터 인식 로직(다른 방 차단, 같은 방 내 거리 8이내 한정) 검증."""
    from core.types import Enemy, Player, Tile, TileType
    from core.world import World
    from map.bsp import Rect
    from map.dungeon import Dungeon
    from systems.ai import EnemyAI
    from systems.inventory import Inventory

    # 15x15 빈 그리드 던전 생성
    grid = [[Tile(TileType.FLOOR) for _ in range(15)] for _ in range(15)]
    dungeon = Dungeon(width=15, height=15, grid=grid)

    # 방 2개 배치 (Room 1: (0,0)에서 5x5, Room 2: (6,0)에서 5x5)
    r1 = Rect(x=0, y=0, w=5, h=5)
    r2 = Rect(x=6, y=0, w=5, h=5)
    dungeon.rooms = [r1, r2]

    # 몬스터(Enemy)와 플레이어(Player) 생성
    enemy = Enemy(
        id=1, pos=Coord(4, 1), hp=10, max_hp=10, atk=1, defense=0, speed=100, kind="goblin"
    )
    player = Player(id=0, pos=Coord(2, 2), hp=100, max_hp=100, atk=10, defense=2, speed=100)

    world = World(dungeon=dungeon, player=player, inventory=Inventory(), entities=[enemy])
    ai = EnemyAI()

    # Case 1: 같은 방(r1)에 있고 거리가 가까울 때 (맨해튼 거리 = 3 <= 8)
    # A* 추적으로 플레이어 방향으로 접근해야 함.
    action = ai.decide(enemy, player.pos, world)
    assert action.dx != 0 or action.dy != 0

    # Case 2: 서로 다른 방에 있을 때 (플레이어는 r1(2,2), 몬스터는 r2(8,2))
    # 다른 방에 있으므로 인식하지 못하고 MoveAction(0, 0)을 반환해야 함.
    enemy.pos = Coord(8, 2)
    action = ai.decide(enemy, player.pos, world)
    assert action.dx == 0 and action.dy == 0

    # Case 3: 같은 방에 있지만 맨해튼 거리가 8을 초과할 때 (거리 = 9)
    dungeon.rooms = [Rect(x=0, y=0, w=12, h=12)]
    player.pos = Coord(1, 1)
    enemy.pos = Coord(10, 1)

    action = ai.decide(enemy, player.pos, world)
    assert action.dx == 0 and action.dy == 0


def test_ai_cache_slicing_on_movement():
    """플레이어 정지 상태(턴 소모 시)에서 몬스터가 전진할 때 캐시 슬라이싱 및 추적이 매끄러운지 검증."""
    from core.types import Enemy, Player, Tile, TileType
    from core.world import World
    from map.bsp import Rect
    from map.dungeon import Dungeon
    from systems.ai import EnemyAI
    from systems.inventory import Inventory

    grid = [[Tile(TileType.FLOOR) for _ in range(10)] for _ in range(10)]
    dungeon = Dungeon(width=10, height=10, grid=grid)
    dungeon.rooms = [Rect(x=0, y=0, w=10, h=10)]

    # 플레이어 (5,5)에 고정
    player = Player(id=0, pos=Coord(5, 5), hp=100, max_hp=100, atk=10, defense=2, speed=100)
    # 몬스터 (5,2)에서 출발 (거리 3)
    enemy = Enemy(
        id=1, pos=Coord(5, 2), hp=30, max_hp=30, atk=5, defense=1, speed=100, kind="goblin"
    )

    world = World(dungeon=dungeon, player=player, inventory=Inventory(), entities=[enemy])
    ai = EnemyAI()

    # 1. 첫 턴: A* 계산 실행 및 한 칸 전진 시도
    action1 = ai.decide(enemy, player.pos, world)
    assert action1.dx == 0
    assert action1.dy == 1  # (5,2) -> (5,3) 이동 결정

    # 몬스터 물리 이동 수행 (do)
    action1.do(world)
    assert enemy.pos == Coord(5, 3)
    assert len(enemy.path_cache) > 0

    # 2. 둘째 턴: 플레이어가 이동하지 않았더라도(대기 턴 소모 상태)
    # 몬스터가 제자리걸음(0,0) 하지 않고 다음 타일 (5,4)로 정상 추적하는지 검증
    action2 = ai.decide(enemy, player.pos, world)
    assert action2.dx == 0
    assert action2.dy == 1  # (5,3) -> (5,4) 이동 결정

    action2.do(world)
    assert enemy.pos == Coord(5, 4)


def test_monster_speed_standardization():
    """모든 종류의 몬스터 기본 속도가 100으로 통일되어 스폰되는지 검증."""
    from core.rng import RNG
    from systems.spawner import Spawner

    rng = RNG(seed=42)
    spawner = Spawner(rng)

    for _ in range(100):
        enemy = spawner._create_random_enemy(Coord(0, 0), stage=1)
        assert enemy.speed == 100
