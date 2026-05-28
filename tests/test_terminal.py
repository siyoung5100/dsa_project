"""ui/terminal.py 단위 테스트.

TDD 규칙에 따라 뷰포트 카메라 및 더블 캐릭터 렌더링 기능을 검증합니다.
"""

from core.types import Coord, Player, Tile, TileType
from core.world import World
from map.dungeon import Dungeon
from ui.terminal import TerminalUI


def test_viewport_bounds_clamping():
    """플레이어가 던전 경계 구석에 있을 때 뷰포트 오프셋 계산이 완벽하게 가두어지는지 검증."""
    ui = TerminalUI()
    width, height = 60, 25
    grid = [[Tile(TileType.FLOOR) for _ in range(width)] for _ in range(height)]
    dungeon = Dungeon(width, height, grid)
    player = Player(id=0, pos=Coord(0, 0), hp=100, max_hp=100, atk=10, defense=2, speed=100)
    world = World(dungeon=dungeon, player=player, inventory=None, entities=[])

    # 1. 좌상단 코너 (0, 0)
    # view_w = 35, view_h = 20 이므로 플레이어를 중심으로 두려 하면
    # start_x = 0 - 17 = -17 -> clamp에 의해 0
    # start_y = 0 - 10 = -10 -> clamp에 의해 0
    # 뷰포트 함수가 반환하는 렌더링에 적절하게 반영되는지 간접 검사
    text = ui._render_map(world)
    assert len(text.plain.splitlines()) == 20

    # 2. 우하단 코너 (59, 24)
    player.pos = Coord(59, 24)
    # start_x = 59 - 17 = 42 -> clamp에 의해 dungeon.width - view_w = 60 - 35 = 25
    # start_y = 24 - 10 = 14 -> clamp에 의해 dungeon.height - view_h = 25 - 20 = 5
    text_corner = ui._render_map(world)
    lines = text_corner.plain.splitlines()
    assert len(lines) == 20
    assert all(len(line) == 70 for line in lines)  # 가로 35 * 2 = 70글자 고정


def test_viewport_double_character_rendering():
    """더블 캐릭터 매핑(██, · )이 올바르게 출력되는지 검증."""
    ui = TerminalUI()
    width, height = 10, 10  # 뷰포트보다 작은 던전
    grid = [[Tile(TileType.WALL) for _ in range(width)] for _ in range(height)]
    # (2, 2)에 바닥 설치
    grid[2][2] = Tile(TileType.FLOOR)
    grid[2][2].visible = True  # 직접 보임 처리

    dungeon = Dungeon(width, height, grid)
    player = Player(id=0, pos=Coord(0, 0), hp=100, max_hp=100, atk=10, defense=2, speed=100)
    world = World(dungeon=dungeon, player=player, inventory=None, entities=[])

    text = ui._render_map(world)
    lines = text.plain.splitlines()

    # 뷰포트 크기가 던전보다 크면 던전 전체 크기만큼 렌더링되거나 패딩 처리됩니다.
    # 뷰포트 내부에서 (2,2) 좌표의 타일을 찾을 수 있어야 함.
    # (0,0)의 플레이어는 "@ "로 렌더링되어야 함.
    assert "@ " in lines[0]
    # (2,2)의 FLOOR는 "· "로 렌더링되어야 함.
    assert "· " in lines[2]
