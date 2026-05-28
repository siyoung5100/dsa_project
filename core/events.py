from __future__ import annotations

from collections import deque


class EventManager:
    """게임 내 메시지 로그를 관리하는 시스템.

    로직 계층에서 발생한 이벤트를 저장하고 UI 계층에서 가져갈 수 있게 한다.
    최근 N개의 메시지만 유지한다.
    """

    def __init__(self, max_logs: int = 50) -> None:
        self._logs: deque[str] = deque(maxlen=max_logs)

    def log(self, message: str) -> None:
        """메시지를 큐에 추가한다."""
        self._logs.append(message)

    def get_logs(self) -> list[str]:
        """현재 저장된 모든 메시지를 리스트로 반환한다."""
        return list(self._logs)

    def clear(self) -> None:
        """모든 메시지를 삭제한다."""
        self._logs.clear()


# 전역 인스턴스 (편의상 제공)
events = EventManager()
