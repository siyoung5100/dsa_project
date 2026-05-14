"""systems/ai.py 단위 테스트.

명세서 §5.5 시나리오 참고:
- 최단 경로 길이 검증 (장애물 없을 때)
- 장애물(벽) 회피 검증
- 도달 불가능한 경우 처리
"""

import pytest
from core.types import Coord
from systems.ai import a_star, manhattan


def test_a_star_basic():
    """벽이 없는 평지에서 최단 경로 검증."""
    start = Coord(0, 0)
    goal = Coord(4, 4)
    
    def passable(c: Coord) -> bool:
        return True # 모든 곳 통과 가능

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
    expected = [Coord(0,0), Coord(1,0), Coord(2,0), Coord(2,1), Coord(2,2)]
    assert path == expected


def test_a_star_unreachable():
    """도달 불가능한 경우 빈 리스트 반환."""
    start = Coord(0, 0)
    goal = Coord(2, 2)
    
    # 목적지를 완전히 벽으로 둘러쌈 (4방향)
    walls = {
        Coord(1, 2), Coord(2, 1), 
        Coord(3, 2), Coord(2, 3)
    }
    
    def passable(c: Coord) -> bool:
        # 영역 제한 (0~5)
        if not (0 <= c.x <= 5 and 0 <= c.y <= 5):
            return False
        return c not in walls

    path = a_star(start, goal, passable)
    assert path == []


def test_manhattan():
    assert manhattan(Coord(0,0), Coord(3,4)) == 7
    assert manhattan(Coord(1,1), Coord(1,1)) == 0
