"""map/fov.py 단위 테스트."""

from core.types import Coord, Tile, TileType
from map.dungeon import Dungeon
from map.fov import compute_fov


def test_fov_basic():
    """벽이 없는 곳에서 반지름만큼 보임."""
    width, height = 20, 20
    grid = [[Tile(TileType.FLOOR) for _ in range(width)] for _ in range(height)]
    d = Dungeon(width, height, grid)

    center = Coord(10, 10)
    radius = 5
    compute_fov(d, center, radius)

    # 센터는 보여야 함
    assert d.grid[10][10].visible

    # 반지름 내 타일은 보여야 함 (10, 15) -> 거리 5
    assert d.grid[15][10].visible

    # 반지름 밖 타일은 안 보여야 함 (10, 16) -> 거리 6
    assert not d.grid[16][10].visible


def test_fov_blocked():
    """벽에 의해 시야가 가려지는지 확인."""
    width, height = 10, 10
    grid = [[Tile(TileType.FLOOR) for _ in range(width)] for _ in range(height)]
    d = Dungeon(width, height, grid)

    # 플레이어 (0,0), 벽 (1,0), 뒤 (2,0)
    center = Coord(0, 0)
    d.set_tile(Coord(1, 0), TileType.WALL)

    compute_fov(d, center, radius=5)

    assert d.grid[0][0].visible
    assert d.grid[0][1].visible  # 벽
    assert not d.grid[0][2].visible  # 벽 뒤 (x=2, y=0 은 grid[0][2])
