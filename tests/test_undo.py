"""systems/undo.py 단위 테스트.

명세서 §5.2 시나리오 참고.
"""

import pytest
from dataclasses import dataclass
from core.types import Action
from systems.undo import UndoSystem

@dataclass
class CounterWorld:
    count: int = 0

class IncrementAction(Action):
    def do(self, world: CounterWorld) -> None:
        world.count += 1
    def undo(self, world: CounterWorld) -> None:
        world.count -= 1

def test_basic_undo_redo():
    world = CounterWorld()
    undo_sys = UndoSystem(world)
    
    action = IncrementAction()
    undo_sys.execute(action)
    assert world.count == 1
    
    undo_sys.undo()
    assert world.count == 0
    assert undo_sys.used == 1
    
    undo_sys.redo()
    assert world.count == 1

def test_history_limit():
    """31번 실행 시 가장 오래된 기록이 폐기되는지 확인 (limit=30)."""
    world = CounterWorld()
    undo_sys = UndoSystem(world, limit=30)
    
    actions = [IncrementAction() for _ in range(35)]
    for a in actions:
        undo_sys.execute(a)
    
    assert world.count == 35
    
    # 30번까지는 undo 가능
    for _ in range(30):
        assert undo_sys.undo() is True
    
    assert world.count == 5
    # 31번째 undo는 기록이 없어야 함
    assert undo_sys.undo() is False
    assert world.count == 5

def test_redo_clearing():
    """undo 후 새로운 행동을 하면 redo 스택이 비워지는지 확인."""
    world = CounterWorld()
    undo_sys = UndoSystem(world)
    
    undo_sys.execute(IncrementAction())
    undo_sys.undo()
    assert len(undo_sys._redo) == 1
    
    undo_sys.execute(IncrementAction())
    assert len(undo_sys._redo) == 0
    assert undo_sys.redo() is False
