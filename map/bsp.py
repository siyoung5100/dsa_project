"""BSP (Binary Space Partitioning) 기반 던전 생성.

명세서 §4.1 참고.
시간복잡도: O(R log R) 평균 (R = 방 수, max_depth로 상한 설정)
공간복잡도: O(W·H)
"""

from __future__ import annotations

from dataclasses import dataclass

from core.rng import RNG
from core.types import Coord, Tile, TileType
from map.dungeon import Dungeon


@dataclass
class Rect:
    """직사각형 영역."""

    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> Coord:
        """중심 좌표 반환."""
        return Coord(self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: Rect) -> bool:
        """다른 Rect와 겹치는지 확인."""
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )


@dataclass
class BSPNode:
    """BSP 트리의 노드."""

    rect: Rect
    left: BSPNode | None = None
    right: BSPNode | None = None
    room: Rect | None = None


def generate_dungeon(
    width: int,
    height: int,
    min_leaf: int = 8,
    max_depth: int = 5,
    seed: int | None = None,
) -> Dungeon:
    """BSP로 던전을 생성해 Dungeon 객체를 반환."""
    rng = RNG(seed)
    root = BSPNode(Rect(0, 0, width, height))

    # 1. 재귀 분할
    _split(root, 0, min_leaf, max_depth, rng)

    # 2. 방 생성
    _create_rooms(root, rng, min_leaf)

    # 3. 그리드 초기화 (벽으로 채움)
    grid = [[Tile(TileType.WALL) for _ in range(width)] for _ in range(height)]
    dungeon = Dungeon(width, height, grid)

    # 4. 방을 그리드에 파냄
    rooms = []
    _carve_rooms(root, dungeon, rooms)

    # 5. 복도 연결
    _connect(root, dungeon, rng)

    dungeon.rooms = rooms
    return dungeon


def _split(node: BSPNode, depth: int, min_leaf: int, max_depth: int, rng: RNG) -> None:
    """node.rect를 수직 또는 수평으로 분할해 자식 생성."""
    if depth >= max_depth:
        return

    # 분할 가능한지 체크
    can_split_h = node.rect.h >= min_leaf * 2
    can_split_v = node.rect.w >= min_leaf * 2

    if not can_split_h and not can_split_v:
        return

    # 분할 방향 결정
    split_horiz = False
    if can_split_h and can_split_v:
        split_horiz = rng.random() < 0.5
    elif can_split_h:
        split_horiz = True
    else:
        split_horiz = False

    # 너무 길쭉한 경우 보정
    if node.rect.w > node.rect.h * 1.5:
        split_horiz = False
    elif node.rect.h > node.rect.w * 1.5:
        split_horiz = True

    if split_horiz:
        # 수평 분할 (가로로 자름 -> 위아래)
        split_pos = rng.randint(min_leaf, node.rect.h - min_leaf)
        node.left = BSPNode(Rect(node.rect.x, node.rect.y, node.rect.w, split_pos))
        node.right = BSPNode(
            Rect(node.rect.x, node.rect.y + split_pos, node.rect.w, node.rect.h - split_pos)
        )
    else:
        # 수직 분할 (세로로 자름 -> 좌우)
        split_pos = rng.randint(min_leaf, node.rect.w - min_leaf)
        node.left = BSPNode(Rect(node.rect.x, node.rect.y, split_pos, node.rect.h))
        node.right = BSPNode(
            Rect(node.rect.x + split_pos, node.rect.y, node.rect.w - split_pos, node.rect.h)
        )

    _split(node.left, depth + 1, min_leaf, max_depth, rng)
    _split(node.right, depth + 1, min_leaf, max_depth, rng)


def _create_rooms(node: BSPNode, rng: RNG, min_leaf: int) -> None:
    """리프 노드마다 rect 안에 무작위 방 생성."""
    if node.left or node.right:
        if node.left:
            _create_rooms(node.left, rng, min_leaf)
        if node.right:
            _create_rooms(node.right, rng, min_leaf)
        return

    # 리프 노드: 방 생성
    # 최소 크기는 3x3 정도로 보장 (min_leaf가 작을 수 있으므로)
    min_w, min_h = 4, 4
    if node.rect.w < min_w or node.rect.h < min_h:
        return

    w = rng.randint(min_w, node.rect.w - 1)
    h = rng.randint(min_h, node.rect.h - 1)
    x = rng.randint(node.rect.x + 1, node.rect.x + node.rect.w - w)
    y = rng.randint(node.rect.y + 1, node.rect.y + node.rect.h - h)

    node.room = Rect(x, y, w, h)


def _carve_rooms(node: BSPNode, dungeon: Dungeon, rooms: list[Rect]) -> None:
    """생성된 방을 그리드에 실제로 기록."""
    if node.room:
        rooms.append(node.room)
        for y in range(node.room.y, node.room.y + node.room.h):
            for x in range(node.room.x, node.room.x + node.room.w):
                dungeon.set_tile(Coord(x, y), TileType.FLOOR)

    if node.left:
        _carve_rooms(node.left, dungeon, rooms)
    if node.right:
        _carve_rooms(node.right, dungeon, rooms)


def _connect(node: BSPNode, dungeon: Dungeon, rng: RNG) -> None:
    """좌/우 자식의 방 중심을 L자 복도로 잇고, 재귀."""
    if not node.left or not node.right:
        return

    _connect(node.left, dungeon, rng)
    _connect(node.right, dungeon, rng)

    # 각 자식 트리에서 무작위 방 하나씩 선택
    c1 = _get_random_room_center(node.left, rng)
    c2 = _get_random_room_center(node.right, rng)

    if c1 and c2:
        _carve_corridor(dungeon, c1, c2, rng)


def _get_random_room_center(node: BSPNode, rng: RNG) -> Coord | None:
    """해당 노드(및 자식)의 리프 방들 중 하나를 골라 중심 반환."""
    rooms = []

    def _collect(n: BSPNode):
        if n.room:
            rooms.append(n.room)
        if n.left:
            _collect(n.left)
        if n.right:
            _collect(n.right)

    _collect(node)
    if not rooms:
        return None
    return rng.choice(rooms).center


def _carve_corridor(dungeon: Dungeon, c1: Coord, c2: Coord, rng: RNG) -> None:
    """두 좌표를 L자 형태로 연결하는 복도를 팜."""
    x1, y1 = c1.x, c1.y
    x2, y2 = c2.x, c2.y

    if rng.random() < 0.5:
        # 수평 먼저, 그다음 수직
        _draw_h_line(dungeon, x1, x2, y1)
        _draw_v_line(dungeon, y1, y2, x2)
    else:
        # 수직 먼저, 그다음 수평
        _draw_v_line(dungeon, y1, y2, x1)
        _draw_h_line(dungeon, x1, x2, y2)


def _draw_h_line(dungeon: Dungeon, x1: int, x2: int, y: int) -> None:
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon.set_tile(Coord(x, y), TileType.FLOOR)


def _draw_v_line(dungeon: Dungeon, y1: int, y2: int, x: int) -> None:
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon.set_tile(Coord(x, y), TileType.FLOOR)
