"""map/bsp.py 단위 테스트.

명세서 §5.1 시나리오 참고:
- 결정론(seed 고정 → 동일 결과)
- 방 수 범위 검증
- 모든 방의 BFS 도달성
- 방끼리 겹치지 않음
"""

from core.types import Coord
from map.bsp import generate_dungeon


def test_bsp_determinism():
    """같은 시드면 같은 결과가 나와야 함."""
    seed = 42
    d1 = generate_dungeon(40, 30, seed=seed)
    d2 = generate_dungeon(40, 30, seed=seed)

    for y in range(30):
        for x in range(40):
            assert d1.grid[y][x].type == d2.grid[y][x].type


def test_bsp_room_count():
    """방 개수가 합리적인 범위 내에 있는지 확인."""
    # max_depth=3 이면 리프는 최대 8개
    d = generate_dungeon(40, 40, max_depth=3, min_leaf=10)
    assert 1 <= len(d.rooms) <= 8


def test_bsp_no_overlap():
    """방끼리 겹치지 않아야 함."""
    d = generate_dungeon(60, 40, seed=123)
    rooms = d.rooms
    for i, r1 in enumerate(rooms):
        for j, r2 in enumerate(rooms):
            if i == j:
                continue
            assert not r1.intersects(r2)


def test_bsp_connectivity():
    """모든 방이 서로 연결되어 있어야 함 (BFS)."""
    d = generate_dungeon(50, 50, seed=777)
    if not d.rooms:
        return

    start_pos = d.rooms[0].center
    visited = set()
    queue = [start_pos]
    visited.add(start_pos)

    while queue:
        curr = queue.pop(0)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nxt = curr + Coord(dx, dy)
            if d.is_passable(nxt) and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    # 모든 방의 중심이 방문되었는지 확인
    for room in d.rooms:
        assert room.center in visited
