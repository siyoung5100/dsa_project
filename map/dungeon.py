"""Dungeon — 타일 그리드 + 방 목록을 보유하는 컨테이너.

is_passable(coord), in_bounds(coord), tile_at(coord) 같은 조회 API를
제공한다. 다른 모듈(A*, FOV 등)은 이 인터페이스에만 의존한다.
"""
