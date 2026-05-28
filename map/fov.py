"""FOV (Field of View) — 시야 계산 (Bresenham 직선 기반 LOS).

플레이어 주변 일정 거리 내 타일만 visible=True로 표시한다.

[알고리즘 선택 이유]
기존 Recursive Shadowcasting 구현에서 슬로프 계산식의 반올림 오차가
좁은 복도를 통해 볼 때 반대 방 전체가 보이는 "코너 커팅(corner-cutting)" 버그를
야기했다. 이를 수정하는 대신, 정확성이 증명된 Bresenham 직선 알고리즘 기반
LOS(Line Of Sight) 방식으로 교체한다.

Bresenham 방식은 각 타일마다 출발점에서 그 타일까지의 직선 경로를 추적하여
중간에 벽이 있으면 차단한다. 복잡한 슬로프 수학 없이 복도 벽이 자연스럽게
시야를 막는다. 물리적으로 올바른 LOS를 보장한다.

시간복잡도: O(radius^2 * radius) — radius=8 기준 약 1,600회 타일 점검.
공간복잡도: O(1) — 추가 자료구조 불필요.
"""

from __future__ import annotations

from core.types import Coord, TileType
from map.dungeon import Dungeon


def compute_fov(dungeon: Dungeon, center: Coord, radius: int) -> None:
    """Bresenham 직선 기반으로 플레이어 시야를 계산하여 dungeon.grid에 반영한다.

    먼저 모든 타일의 visible을 False로 초기화하고,
    센터에서 반경 radius 이내의 각 타일에 대해 직선 시야(LOS)를 확인하여 True로 설정한다.
    """
    # 1. 초기화: 모든 타일을 비가시 상태로 설정
    for y in range(dungeon.height):
        for x in range(dungeon.width):
            dungeon.grid[y][x].visible = False

    # 2. 플레이어 위치는 항상 보임
    start_tile = dungeon.tile_at(center)
    if start_tile:
        start_tile.visible = True
        start_tile.explored = True

    # 3. 반경 내 모든 타일에 대해 Bresenham LOS 확인
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            # 원형 시야: 반경 밖은 건너뜀
            if dx * dx + dy * dy > radius * radius:
                continue
            target = Coord(center.x + dx, center.y + dy)
            if _has_los(dungeon, center, target):
                tile = dungeon.tile_at(target)
                if tile:
                    tile.visible = True
                    tile.explored = True


def _has_los(dungeon: Dungeon, origin: Coord, target: Coord) -> bool:
    """Bresenham 직선 알고리즘으로 origin에서 target까지 시야가 통하는지 확인한다.

    경로 중간에 벽이 있으면 False를 반환한다.
    target 타일 자체는 벽이어도 시야가 닿은 것으로 처리한다 (벽 자체는 보임).
    """
    x0, y0 = origin.x, origin.y
    x1, y1 = target.x, target.y

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1
    err = dx - dy

    x, y = x0, y0

    while True:
        # 목표 지점 도달 → 시야 통함
        if x == x1 and y == y1:
            return True

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

        # 중간 타일이 벽이면 차단 (목표 지점 자체는 제외 → 벽 타일도 보임)
        if (x, y) != (x1, y1):
            tile = dungeon.tile_at(Coord(x, y))
            if tile is None or tile.type == TileType.WALL:
                return False
