from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AVLNode:
    key: Any
    value: Any
    left: AVLNode | None = None
    right: AVLNode | None = None
    height: int = 1
    size: int = 1


class AVLTree:
    def __init__(self):
        self.root: AVLNode | None = None

    def search(self, key: Any) -> Any | None:
        """키 기반 값 검색. O(log N)"""
        node = self._search(self.root, key)
        return node.value if node else None

    def _search(self, node: AVLNode | None, key: Any) -> AVLNode | None:
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def insert(self, key: Any, value: Any) -> None:
        """노드 삽입. 현재는 BST 기본 동작만 수행 (균형 로직 제외)."""
        self.root = self._insert(self.root, key, value)

    def _insert(self, node: AVLNode | None, key: Any, value: Any) -> AVLNode:
        if node is None:
            return AVLNode(key, value)

        if key == node.key:
            node.value = value
        elif key < node.key:
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)

        self._update(node)
        # TODO: self._rebalance(node) 호출 필요
        return node

    def _update(self, node: AVLNode) -> None:
        """높이와 서브트리 크기 갱신."""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.size = 1 + self._get_size(node.left) + self._get_size(node.right)

    def _get_height(self, node: AVLNode | None) -> int:
        return node.height if node else 0

    def _get_size(self, node: AVLNode | None) -> int:
        return node.size if node else 0

    def __len__(self) -> int:
        return self._get_size(self.root)
