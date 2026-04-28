"""Dungeon Crawler RPG — 엔트리포인트.

게임 루프 개요 (명세서 §4.3 의사코드 참고):
    1. 던전 생성 (BSP)
    2. 플레이어 + 적 + 아이템 배치
    3. 턴 매니저로부터 next_actor 가져오기
    4. 플레이어 차례 → 입력 → Action.do() → undo_system에 push
       적 차례 → AI.decide() → A* 결과 → MoveAction
    5. 반복. 종료 시 Leaderboard에 기록.
"""


def main() -> None:
    """게임 시작. 추후 구현."""
    raise NotImplementedError("아직 구현되지 않았습니다. 모듈별 구현 진행 중.")


if __name__ == "__main__":
    main()
