"""FOV (Field of View) — 시야 계산 (Shadowcasting).

플레이어 주변 일정 거리 내 타일만 visible=True로 표시한다.
Recursive Shadowcasting 알고리즘을 사용하여 효율적으로 가시성을 계산한다.
"""

from __future__ import annotations

import math
from core.types import Coord, TileType
from map.dungeon import Dungeon


def compute_fov(dungeon: Dungeon, center: Coord, radius: int) -> None:
    """Shadowcasting을 사용하여 플레이어 시야를 계산하고 dungeon.grid에 반영한다.

    먼저 모든 타일의 visible을 False로 초기화하고, 
    센터에서 보이는 타일들만 True로 설정한다.
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

    # 3. 8분면(Octants) 각각에 대해 스캔 실행
    for octant in range(8):
        _scan(dungeon, center, radius, 1, 0.0, 1.0, octant)


def _scan(
    dungeon: Dungeon, 
    center: Coord, 
    radius: int, 
    depth: int, 
    start_slope: float, 
    end_slope: float, 
    octant: int
) -> None:
    """특정 8분면을 재귀적으로 스캔."""
    if depth > radius:
        return

    # 현재 깊이(depth)에서 x 범위를 결정 (슬로프에 따라)
    # shadowcasting에서 depth는 octant 좌표계의 'x' 역할을 함.
    
    # 이전에 벽이었는지 추적 (새로운 가시 영역 시작 확인용)
    prev_tile_blocked = False
    
    # depth 열의 각 행을 아래에서 위로(슬로프 기준) 스캔
    # 정수 좌표로 변환하기 위해 슬로프 활용
    
    # 8분면 좌표 변환을 위한 테이블
    # (dx, dy) = (depth, row) 변환
    # octants:
    # 0: (depth, row)   1: (row, depth)
    # 2: (-row, depth)  3: (-depth, row)
    # 4: (-depth, -row) 5: (-row, -depth)
    # 6: (row, -depth)  7: (depth, -row)

    min_row = math.floor(start_slope * depth + 0.5)
    max_row = math.ceil(end_slope * depth - 0.5)

    for row in range(min_row, max_row + 1):
        # 상대 좌표를 절대 좌표로 변환
        x, y = _transform_octant(depth, row, octant)
        abs_pos = Coord(center.x + x, center.y + y)
        
        tile = dungeon.tile_at(abs_pos)
        if not tile:
            continue

        # 거리가 반지름 이내인지 확인 (원형 시야)
        if (x * x + y * y) <= radius * radius:
            tile.visible = True
            tile.explored = True

        blocked = tile.type == TileType.WALL
        
        if prev_tile_blocked:
            if not blocked:
                # 벽 뒤의 빈 공간 시작: 새로운 슬로프로 재귀 호출
                start_slope = (row - 0.5) / depth
            else:
                # 계속 벽인 경우: pass
                pass
        else:
            if blocked:
                # 빈 공간 뒤의 벽 시작: 이전까지의 영역을 재귀 호출로 마무리
                new_end_slope = (row - 0.5) / depth
                _scan(dungeon, center, radius, depth + 1, start_slope, new_end_slope, octant)
                start_slope = (row + 0.5) / depth

        prev_tile_blocked = blocked

    # 마지막 타일이 벽이 아니었다면 다음 깊이로 계속 진행
    if not prev_tile_blocked:
        _scan(dungeon, center, radius, depth + 1, start_slope, end_slope, octant)


def _transform_octant(x: int, y: int, octant: int) -> tuple[int, int]:
    """octant 좌표계(x, y)를 상대 월드 좌표계(dx, dy)로 변환."""
    if octant == 0: return (x, y)
    if octant == 1: return (y, x)
    if octant == 2: return (-y, x)
    if octant == 3: return (-x, y)
    if octant == 4: return (-x, -y)
    if octant == 5: return (-y, -x)
    if octant == 6: return (y, -x)
    if octant == 7: return (x, -y)
    return (0, 0)
