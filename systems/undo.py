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
