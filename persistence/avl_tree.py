from __future__ import annotations

from collections.abc import Iterator
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

    def kth(self, k: int) -> AVLNode | None:
        """k번째 순위의 노드 반환 (0-indexed). O(log N)"""
        return self._kth(self.root, k)

    def _kth(self, node: AVLNode | None, k: int) -> AVLNode | None:
        if node is None:
            return None

        left_size = self._get_size(node.left)
        if k < left_size:
            return self._kth(node.left, k)
        elif k > left_size:
            return self._kth(node.right, k - left_size - 1)
        else:
            return node

    def rank(self, key: Any) -> int:
        """특정 키보다 작은 노드의 개수 반환. O(log N)"""
        return self._rank(self.root, key)

    def _rank(self, node: AVLNode | None, key: Any) -> int:
        if node is None:
            return 0

        if key < node.key:
            return self._rank(node.left, key)
        elif key > node.key:
            return 1 + self._get_size(node.left) + self._rank(node.right, key)
        else:
            return self._get_size(node.left)

    def in_order(self) -> Iterator[AVLNode]:
        """정렬된 순서로 노드를 순회하는 Generator. O(N)"""
        yield from self._in_order(self.root)

    def _in_order(self, node: AVLNode | None) -> Iterator[AVLNode]:
        if node:
            yield from self._in_order(node.left)
            yield node
            yield from self._in_order(node.right)

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
        return self._rebalance(node)

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """균형을 맞추고 균형이 잡힌 새 루트 노드를 반환."""
        balance = self._get_balance(node)

        # LL Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # LR Case
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # RL Case
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z: AVLNode) -> AVLNode:
        """좌회전 수행.
             z              y
            / \\            / \
           T1  y     ->   z   T3
              / \\        / \
             T2  T3     T1  T2
        """
        y = z.right
        assert y is not None
        t2 = y.left

        y.left = z
        z.right = t2

        self._update(z)
        self._update(y)
        return y

    def _rotate_right(self, z: AVLNode) -> AVLNode:
        """우회전 수행.
               z            y
              / \\          / \
             y   T3  ->   T1  z
            / \\              / \
           T1  T2           T2  T3
        """
        y = z.left
        assert y is not None
        t2 = y.right

        y.right = z
        z.left = t2

        self._update(z)
        self._update(y)
        return y

    def _get_balance(self, node: AVLNode | None) -> int:
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

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
