from core.events import EventManager


def test_event_log_basic():
    em = EventManager(max_logs=3)
    em.log("Message 1")
    em.log("Message 2")

    logs = em.get_logs()
    assert len(logs) == 2
    assert logs[0] == "Message 1"
    assert logs[1] == "Message 2"


def test_event_log_maxlen():
    em = EventManager(max_logs=2)
    em.log("1")
    em.log("2")
    em.log("3")

    logs = em.get_logs()
    assert len(logs) == 2
    assert logs[0] == "2"
    assert logs[1] == "3"


def test_event_log_clear():
    em = EventManager()
    em.log("Test")
    em.clear()
    assert len(em.get_logs()) == 0
