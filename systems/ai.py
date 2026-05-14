"""적 AI — A* 알고리즘 (맨해튼 거리 휴리스틱).

명세서 §4.5 참고.
시간복잡도: 평균 O(E log V), V = 통과 가능 타일 수, E ≈ 4V.

핵심 함수/클래스:
- a_star(grid, start, goal, passable, h=manhattan) -> list[Coord]
- EnemyAI.decide(enemy, player_pos, world) -> Action
"""

from __future__ import annotations

import heapq
import itertools
from collections.abc import Callable
from typing import Any

from core.types import Action, Coord, Enemy, MoveAction


def manhattan(a: Coord, b: Coord) -> int:
    """맨해튼 거리 휴리스틱."""
    return abs(a.x - b.x) + abs(a.y - b.y)


def a_star(
    start: Coord,
    goal: Coord,
    passable: Callable[[Coord], bool],
    h: Callable[[Coord, Coord], int] = manhattan,
) -> list[Coord]:
    """start -> goal 최단경로를 반환 (시작점 포함). 도달 불가 시 [].

    heapq를 사용하여 F = G + H 가 가장 낮은 노드를 우선 탐색한다.
    동률(tie) 처리를 위해 counter를 사용한다.
    """
    if start == goal:
        return [start]

    # (f_score, counter, current_coord)
    counter = itertools.count()
    open_heap = [(h(start, goal), next(counter), start)]

    came_from: dict[Coord, Coord | None] = {start: None}
    g_score: dict[Coord, int] = {start: 0}

    while open_heap:
        _, _, curr = heapq.heappop(open_heap)

        if curr == goal:
            # 경로 복원
            path = []
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            return path[::-1]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = curr + Coord(dx, dy)

            # goal 인 경우 passable 체크를 우회하거나(적 위치 등),
            # 호출자가 goal이 passable한지 확인했다고 가정한다.
            # 여기서는 goal이면 무조건 체크하거나 통과 가능해야 한다.
            if not passable(neighbor) and neighbor != goal:
                continue

            new_g = g_score[curr] + 1
            if neighbor not in g_score or new_g < g_score[neighbor]:
                g_score[neighbor] = new_g
                priority = new_g + h(neighbor, goal)
                heapq.heappush(open_heap, (priority, next(counter), neighbor))
                came_from[neighbor] = curr

    return []


class EnemyAI:
    """적 엔티티의 의사결정을 담당하는 클래스."""

    def decide(self, enemy: Enemy, player_pos: Coord, world: Any) -> Action:
        """현재 상태에서 적이 취할 최선의 행동을 결정.

        1. 플레이어와 인접하면 공격 (AttackAction - 추후 구현)
        2. 아니면 A*로 추적
        3. 경로 캐시를 활용해 연산 절약
        """
        dist = manhattan(enemy.pos, player_pos)

        # 공격 사거리 안 (상하좌우 인접)
        if dist == 1:
            # TODO: AttackAction 구현 후 교체. 현재는 WaitAction이나 Move(0,0) 개념
            from core.types import AttackAction

            return AttackAction(enemy, world.player)  # world.player 가 있다고 가정

        # 경로 재계산 필요 여부 확인
        # 캐시가 비었거나, 플레이어가 캐시의 목적지와 다르면 재계산
        if not enemy.path_cache or enemy.path_cache[-1] != player_pos:
            enemy.path_cache = a_star(enemy.pos, player_pos, passable=world.is_passable)

        # 경로를 찾은 경우 이동
        if len(enemy.path_cache) > 1:
            next_step = enemy.path_cache[1]
            dx = next_step.x - enemy.pos.x
            dy = next_step.y - enemy.pos.y

            # 다음 칸에 다른 적이 있는지 등은 MoveAction.do() 에서 체크하거나
            # 여기서 추가 체크 가능. 일단 MoveAction 반환.
            return MoveAction(enemy, dx, dy)

        # 아무것도 할 수 없으면 대기 (Move(0,0) 등으로 표현 가능)
        return MoveAction(enemy, 0, 0)
