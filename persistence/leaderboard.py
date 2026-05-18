"""Leaderboard — AVL Tree 기반 순위표 + JSON 영속화.

정렬 키: (-score, play_time_sec, undo_used, timestamp)

핵심 클래스:
- Leaderboard(path)
  - add(record) -> int  # 등수 반환
  - top(k=10) -> list[Record]
  - save() / load()
"""

import json
import pathlib
from dataclasses import asdict
from core.types import Record
from persistence.avl_tree import AVLTree


def _make_key(r: Record) -> tuple:
    """리더보드 정렬을 위한 튜플 키 생성.
    (점수 내림차순, 플레이시간 오름차순, Undo 횟수 오름차순, 등록시간 오름차순)
    """
    return (-r.score, r.play_time_sec, r.undo_used, r.timestamp)


class Leaderboard:
    def __init__(self, path: str | pathlib.Path):
        self.path = pathlib.Path(path)
        self.tree = AVLTree()
        self.load()

    def add(self, record: Record) -> int:
        """기록을 추가하고 현재 등수를 반환한다 (0-indexed)."""
        key = _make_key(record)
        self.tree.insert(key, record)
        self.save()
        return self.tree.rank(key)

    def top(self, k: int = 10) -> list[Record]:
        """상위 k개의 기록을 반환한다."""
        results = []
        for i, node in enumerate(self.tree.in_order()):
            if i >= k:
                break
            results.append(node.value)
        return results

    def save(self) -> None:
        """데이터를 JSON 파일로 저장한다."""
        # AVL Tree의 중위 순회 결과(이미 정렬됨)를 리스트로 변환
        data = [asdict(node.value) for node in self.tree.in_order()]
        try:
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def load(self) -> None:
        """JSON 파일에서 데이터를 로드한다."""
        if not self.path.exists():
            return
        
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            # 새로 트리를 구성함 (AVL이 알아서 균형을 잡음)
            new_tree = AVLTree()
            for d in data:
                r = Record(**d)
                new_tree.insert(_make_key(r), r)
            self.tree = new_tree
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            # 손상된 파일인 경우 백업 처리 등을 할 수 있지만, 여기서는 단순히 무시
