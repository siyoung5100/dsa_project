"""Leaderboard — AVL Tree 기반 순위표 + JSON 영속화.

정렬 키: (-score, play_time_sec, undo_used, timestamp)

핵심 클래스:
- Leaderboard(path)
  - add(record) -> int  # 등수 반환
  - top(k=10) -> list[Record]
  - save() / load()
"""
