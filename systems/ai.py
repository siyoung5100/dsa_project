"""적 AI — A* 알고리즘 (맨해튼 거리 휴리스틱).

명세서 §4.5 참고.
시간복잡도: 평균 O(E log V), V = 통과 가능 타일 수, E ≈ 4V.

핵심 함수/클래스:
- a_star(grid, start, goal, passable, h=manhattan) -> list[Coord]
- EnemyAI.decide(enemy, player_pos, world) -> Action
"""
