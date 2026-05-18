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

import heapq
import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.types import Entity


class TurnManager:
    def __init__(self):
        # (at, tie-break, entity)
        self._heap: list[tuple[int, int, "Entity"]] = []
        self._counter = itertools.count()  # tie-break용 카운터
        self._dead: set[int] = set()       # lazy 삭제를 위한 ID 집합
        self._now: int = 0                 # 현재 "시간" 또는 "틱"

    def schedule(self, entity: "Entity", at: int) -> None:
        """엔티티를 특정 시점에 행동하도록 예약한다."""
        heapq.heappush(self._heap, (at, next(self._counter), entity))

    def next_actor(self) -> "Entity | None":
        """다음 행동할 엔티티를 반환한다. 죽은 엔티티는 건너뛴다."""
        while self._heap:
            t, _, e = heapq.heappop(self._heap)
            
            # Lazy deletion: 죽은 엔티티거나 alive 플래그가 꺼진 경우 스킵
            if e.id in self._dead or not e.alive:
                continue
            
            self._now = t
            return e
        return None

    def advance(self, entity: "Entity", cost: int = 100) -> None:
        """행동 후 비용(cost)과 엔티티 속도(speed)를 계산하여 다음 턴을 예약한다."""
        # 계산식: 다음_시점 = 현재_시점 + (cost * 100 / speed)
        # speed가 높을수록 시점 증가폭이 작아져 더 자주 행동하게 됨.
        # 최소 1의 시간은 흐르도록 보장.
        next_t = self._now + max(1, cost * 100 // max(1, entity.speed))
        self.schedule(entity, next_t)

    def remove(self, entity: "Entity") -> None:
        """엔티티를 턴 스케줄에서 제거한다 (Lazy deletion)."""
        self._dead.add(entity.id)
