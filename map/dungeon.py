"""Dungeon — 타일 그리드 + 방 목록을 보유하는 컨테이너.

is_passable(coord), in_bounds(coord), tile_at(coord) 같은 조회 API를
제공한다. 다른 모듈(A*, FOV 등)은 이 인터페이스에만 의존한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any  # Rect 타입을 위해 Any 사용 (bsp와 순환 참조 방지용)

from core.types import Coord, Tile, TileType


@dataclass
class Dungeon:
    """던전 맵 상태를 보유하는 클래스.

    grid: [y][x] 순서의 Tile 2차원 리스트.
    rooms: 생성된 방들의 Rect 목록 (map/bsp.py의 Rect와 동일 구조).
    """

    width: int
    height: int
    grid: list[list[Tile]]
    rooms: list[Any] = field(default_factory=list)

    def in_bounds(self, pos: Coord) -> bool:
        """좌표가 던전 영역 안에 있는지 확인."""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def tile_at(self, pos: Coord) -> Tile | None:
        """특정 좌표의 타일 반환. 영역 밖이면 None."""
        if not self.in_bounds(pos):
            return None
        return self.grid[pos.y][pos.x]

    def is_passable(self, pos: Coord) -> bool:
        """특정 좌표를 통과할 수 있는지 확인 (통행 가능 타일 + 영역 안)."""
        tile = self.tile_at(pos)
        return tile is not None and tile.passable

    def set_tile(self, pos: Coord, tile_type: TileType) -> None:
        """특정 좌표의 타일 종류를 변경 (생성 시 사용)."""
        if self.in_bounds(pos):
            self.grid[pos.y][pos.x].type = tile_type

    def get_neighbors(self, pos: Coord) -> list[Coord]:
        """인접한 4방향 좌표 반환."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nxt = pos + Coord(dx, dy)
            if self.in_bounds(nxt):
                neighbors.append(nxt)
        return neighbors
