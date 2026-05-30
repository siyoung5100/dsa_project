"""UndoSystem — collections.deque(maxlen=30) + Command 패턴.

명세서 §4.2 참고.
연산 복잡도: execute/undo/redo 모두 O(1) + Action 본체 비용.

핵심 클래스:
- UndoSystem
  - execute(action)
  - undo() -> bool
  - redo() -> bool
  - remaining: int
  - used: int  # 누적 undo 사용 횟수 (리더보드 지표)
"""

from collections import deque
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.types import Action


class UndoSystem:
    def __init__(self, world: Any = None, limit: int = 30):
        self.world = world
        self._history: deque[Action] = deque(maxlen=limit)
        self._redo: deque[Action] = deque(maxlen=limit)
        self.used: int = 0  # 누적 undo 사용 횟수 (리더보드 지표)

    def clear(self) -> None:
        """히스토리와 레두 스택을 완전히 비운다 (스테이지 전환 시 등)."""
        self._history.clear()
        self._redo.clear()

    @property
    def history(self) -> deque["Action"]:
        return self._history

    @property
    def redo_stack(self) -> deque["Action"]:
        return self._redo

    def execute(self, action: "Action") -> None:
        """행동을 실행하고 히스토리에 기록한다."""
        action.do(self.world)
        self._history.append(action)
        self._redo.clear()  # 새로운 행동 시 redo 스택 초기화

    def undo(self) -> bool:
        """가장 최근 행동을 되돌린다."""
        if not self._history:
            return False

        action = self._history.pop()
        action.undo(self.world)
        self._redo.append(action)
        self.used += 1
        return True

    def redo(self) -> bool:
        """되돌린 행동을 다시 실행한다."""
        if not self._redo:
            return False

        action = self._redo.pop()
        action.do(self.world)
        self._history.append(action)
        return True

    @property
    def remaining(self) -> int:
        """남은 히스토리 저장 공간 (maxlen - 현재 크기)."""
        return (self._history.maxlen or 0) - len(self._history)
