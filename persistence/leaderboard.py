from __future__ import annotations

import json
from pathlib import Path

from core.types import Record
from persistence.avl_tree import AVLTree


def _key(r: Record) -> tuple:
    """리더보드 정렬 키 생성.
    1. 점수(score) 내림차순 (-)
    2. 소요 시간(play_time_sec) 오름차순 (+)
    3. Undo 사용 횟수(undo_used) 오름차순 (+)
    4. 등록 시각(timestamp) 오름차순 (+)
    """
    return (-r.score, r.play_time_sec, r.undo_used, r.timestamp)


class Leaderboard:
    """AVL Tree 기반 리더보드 시스템."""

    def __init__(self, path: Path):
        self.path = path
        self.tree = AVLTree()
        self.load()

    def add(self, record: Record) -> int:
        """새 기록을 추가하고 등수(1-indexed)를 반환한다."""
        key = _key(record)
        self.tree.insert(key, record)
        self.save()
        return self.tree.rank(key) + 1

    def top(self, k: int = 10) -> list[Record]:
        """상위 k개의 기록을 리스트로 반환한다."""
        out = []
        for i, node in enumerate(self.tree.in_order()):
            if i >= k:
                break
            out.append(node.value)
        return out

    def save(self) -> None:
        """JSON 파일로 리더보드 저장."""
        # AVL 트리의 in_order 순회는 정렬된 순서(오름차순)이므로
        # _key 규칙상 가장 좋은 기록부터 순회된다.
        data = [node.value.__dict__ for node in self.tree.in_order()]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        """JSON 파일에서 리더보드 불러오기."""
        if not self.path.exists():
            return

        try:
            content = self.path.read_text(encoding="utf-8")
            if not content.strip():
                return
            data = json.loads(content)
            for d in data:
                record = Record(**d)
                self.tree.insert(_key(record), record)
        except (json.JSONDecodeError, TypeError, KeyError):
            # 파일 손상 시 빈 상태로 시작 (또는 에러 로그)
            self.tree = AVLTree()
