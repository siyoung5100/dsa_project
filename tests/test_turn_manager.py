"""systems/turn_manager.py 단위 테스트.

명세서 §5.3 시나리오 참고.
"""

from core.types import Coord, Entity
from systems.turn_manager import TurnManager


def test_speed_difference():
    """speed 스탯에 따라 행동 빈도가 달라지는지 확인."""
    tm = TurnManager()
    # e1은 속도 100, e2는 속도 200
    e1 = Entity(id=1, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    e2 = Entity(id=2, pos=Coord(0, 1), hp=10, max_hp=10, atk=1, defense=0, speed=200)

    # 두 엔티티를 시간 0에 예약
    tm.schedule(e1, 0)
    tm.schedule(e2, 0)

    # 턴 순서 확인: 같은 시간 0이면 먼저 등록된 e1, 그 다음 e2
    assert tm.next_actor() == e1
    tm.advance(e1, 100)  # e1 다음 턴: 0 + (100*100/100) = 100

    assert tm.next_actor() == e2
    tm.advance(e2, 100)  # e2 다음 턴: 0 + (100*100/200) = 50

    # 이제 e2가 50으로 e1(100)보다 빠르므로 먼저 나와야 함
    assert tm.next_actor() == e2
    tm.advance(e2, 100)  # e2 다음 턴: 50 + 50 = 100

    # 이제 e1(100)과 e2(100)이 같은데, e1이 먼저 힙에 있었으므로 e1이 나옴 (itertools.count 덕분)
    assert tm.next_actor() == e1


def test_lazy_deletion():
    """remove() 호출 후 해당 엔티티가 스케줄에서 제외되는지 확인."""
    tm = TurnManager()
    e1 = Entity(id=1, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)

    tm.schedule(e1, 0)
    tm.remove(e1)

    assert tm.next_actor() is None


def test_alive_flag_skip():
    """alive=False 인 엔티티가 스케줄에서 건너뛰어지는지 확인."""
    tm = TurnManager()
    e1 = Entity(id=1, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)

    tm.schedule(e1, 0)
    e1.alive = False

    assert tm.next_actor() is None


def test_tie_break_stability():
    """동일한 시각일 때 등록 순서가 유지되는지 확인 (itertools.count 검증)."""
    tm = TurnManager()
    entities = [
        Entity(id=i, pos=Coord(i, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
        for i in range(5)
    ]

    for e in entities:
        tm.schedule(e, 10)

    for i in range(5):
        actor = tm.next_actor()
        assert actor == entities[i]
