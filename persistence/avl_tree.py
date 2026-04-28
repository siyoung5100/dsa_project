"""AVL Tree — Self-balancing BST 자체 구현.

명세서 §4.6 참고.
연산 복잡도: insert/delete/search/kth/rank 모두 O(log N).
공간복잡도: O(N).

핵심 클래스:
- AVLNode(key, value, left, right, height, size)
- AVLTree
  - insert(key, value)
  - delete(key) -> bool
  - search(key) -> value | None
  - kth(k) -> AVLNode | None     # 0-indexed
  - rank(key) -> int             # key 미만 노드 수
  - in_order() -> Iterator[AVLNode]
"""
