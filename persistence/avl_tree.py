"""AVL Tree — Self-balancing BST 자체 구현.

명세서 §4.6 참고.
연산 복잡도: insert/delete/search/kth/rank 모두 O(log N).
공간복잡도: O(N).
"""

from dataclasses import dataclass
from typing import Any, Iterator, Optional


@dataclass
class AVLNode:
    """AVL 트리의 노드."""
    key: Any
    value: Any
    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None
    height: int = 1
    size: int = 1  # 서브트리 크기 (rank/kth 조회용)


class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def __len__(self) -> int:
        return self._get_size(self.root)

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_size(self, node: Optional[AVLNode]) -> int:
        return node.size if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update(self, node: AVLNode) -> None:
        """노드의 높이와 크기를 자식 노드 정보를 기반으로 갱신."""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.size = 1 + self._get_size(node.left) + self._get_size(node.right)

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """우회전 수행.
             y            x
            / \          / \
           x   T3  ->   T1  y
          / \              / \
         T1  T2           T2  T3
        """
        x = y.left
        assert x is not None
        t2 = x.right

        x.right = y
        y.left = t2

        self._update(y)
        self._update(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """좌회전 수행.
           x                y
          / \              / \
         T1  y      ->    x   T3
            / \          / \
           T2  T3       T1  T2
        """
        y = x.right
        assert y is not None
        t2 = y.left

        y.left = x
        x.right = t2

        self._update(x)
        self._update(y)
        return y

    def insert(self, key: Any, value: Any) -> None:
        """트리에 키-값 쌍을 삽입하고 균형을 맞춘다."""
        self.root = self._insert(self.root, key, value)

    def _insert(self, node: Optional[AVLNode], key: Any, value: Any) -> AVLNode:
        if not node:
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # 키가 이미 존재하면 값만 업데이트
            node.value = value
            return node

        self._update(node)
        return self._rebalance(node, key)

    def _rebalance(self, node: AVLNode, key: Any) -> AVLNode:
        balance = self._get_balance(node)

        # LL Case
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)

        # RR Case
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)

        # LR Case
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RL Case
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: Any) -> Optional[Any]:
        """키에 해당하는 값을 검색한다."""
        curr = self.root
        while curr:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def rank(self, key: Any) -> int:
        """해당 키보다 작은 키를 가진 노드의 수를 반환한다."""
        return self._rank(self.root, key)

    def _rank(self, node: Optional[AVLNode], key: Any) -> int:
        if not node:
            return 0
        
        if key == node.key:
            return self._get_size(node.left)
        elif key < node.key:
            return self._rank(node.left, key)
        else:
            return 1 + self._get_size(node.left) + self._rank(node.right, key)

    def kth(self, k: int) -> Optional[AVLNode]:
        """k번째(0-indexed) 작은 키를 가진 노드를 반환한다."""
        if k < 0 or k >= len(self):
            return None
        return self._kth(self.root, k)

    def _kth(self, node: Optional[AVLNode], k: int) -> Optional[AVLNode]:
        if not node:
            return None
        
        left_size = self._get_size(node.left)
        if k == left_size:
            return node
        elif k < left_size:
            return self._kth(node.left, k)
        else:
            return self._kth(node.right, k - left_size - 1)

    def in_order(self) -> Iterator[AVLNode]:
        """중위 순회(키 오름차순)를 수행하는 이터레이터."""
        yield from self._in_order(self.root)

    def _in_order(self, node: Optional[AVLNode]) -> Iterator[AVLNode]:
        if node:
            yield from self._in_order(node.left)
            yield node
            yield from self._in_order(node.right)
