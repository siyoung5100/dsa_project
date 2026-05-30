from __future__ import annotations

from core.types import Record
from persistence.leaderboard import Leaderboard


def test_leaderboard_custom_name_registration(tmp_path):
    """사용자가 직접 입력한 커스텀 닉네임 레코드가 리더보드에 정상 등록되고 등수 산출이 잘 되는지 검증."""
    db_file = tmp_path / "leaderboard.json"
    lb = Leaderboard(db_file)

    # 1. 다양한 닉네임 레코드 준비
    r1 = Record(
        name="Hero_A", score=500, play_time_sec=120, undo_used=1, timestamp="2026-05-30T10:00:00"
    )
    r2 = Record(
        name="닉네임한글",
        score=1000,
        play_time_sec=100,
        undo_used=0,
        timestamp="2026-05-30T10:05:00",
    )
    r3 = Record(
        name="Spam_User",
        score=100,
        play_time_sec=300,
        undo_used=10,
        timestamp="2026-05-30T10:10:00",
    )

    # 2. 리더보드에 등록 및 순위 검증
    # 점수가 가장 높은 "닉네임한글"이 1등이어야 함
    assert lb.add(r1) == 1  # 첫 번째 삽입
    assert lb.add(r2) == 1  # 닉네임한글(1000점)이 1등으로 올라섬
    assert lb.add(r3) == 3  # Spam_User(100점)는 3등

    # 3. 순위 순서 확인
    top_records = lb.top(3)
    assert len(top_records) == 3
    assert top_records[0].name == "닉네임한글"
    assert top_records[1].name == "Hero_A"
    assert top_records[2].name == "Spam_User"

    # 4. 파일 영속화 확인 및 검증
    assert db_file.exists()

    # 5. 새 인스턴스로 다시 로드해도 이름 정보가 정확히 복원되는지 확인
    lb_loaded = Leaderboard(db_file)
    assert len(lb_loaded.tree) == 3
    loaded_top = lb_loaded.top(3)
    assert loaded_top[0].name == "닉네임한글"
    assert loaded_top[1].name == "Hero_A"
    assert loaded_top[2].name == "Spam_User"
