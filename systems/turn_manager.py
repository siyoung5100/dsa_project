"""TurnManager — heapq 기반 우선순위 큐 + lazy deletion.

명세서 §4.3 참고.
연산 복잡도: schedule/next_actor/advance 모두 O(log K).

핵심 클래스:
- TurnManager
  - schedule(entity, at)
  - next_actor() -> Entity | None
  - advance(entity, cost=100)
  - remove(entity)   # lazy
"""
