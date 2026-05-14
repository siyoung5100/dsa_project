"""persistence/avl_tree.py + leaderboard.py 단위 테스트.

명세서 §5.6 시나리오 참고.
"""

import pytest
from persistence.avl_tree import AVLTree

# 1단계: BST 기초 및 검색 테스트 (Red Phase)
def test_avl_basic_insert_search():
    tree = AVLTree()
    tree.insert(10, "ten")
    tree.insert(20, "twenty")
    tree.insert(5, "five")

    assert tree.search(10) == "ten"
    assert tree.search(20) == "twenty"
    assert tree.search(5) == "five"
    assert tree.search(30) is None

def test_avl_empty_search():
    tree = AVLTree()
    assert tree.search(10) is None

def test_avl_insert_overwrite():
    tree = AVLTree()
    tree.insert(10, "ten")
    tree.insert(10, "new ten")
    assert tree.search(10) == "new ten"

def test_avl_balance_factor():
    # 1, 2, 3 순서로 삽입 시 RR 상황 -> 좌회전 필요
    tree = AVLTree()
    for i in range(1, 8):  # 1~7 삽입
        tree.insert(i, str(i))
    
    # 균형이 잡혔다면 높이는 log2(7) 근처인 3이어야 함 (루트 기준)
    # 미구현 시에는 7이 됨
    assert tree.root.height <= 3

def test_avl_kth_rank():
    tree = AVLTree()
    # 10, 20, 30, 40, 50 삽입
    for i in range(1, 6):
        tree.insert(i * 10, f"v{i*10}")
    
    # kth (0-indexed)
    # 0: 10, 1: 20, 2: 30, 3: 40, 4: 50
    assert tree.kth(0).key == 10
    assert tree.kth(2).key == 30
    assert tree.kth(4).key == 50
    assert tree.kth(5) is None
    
    # rank (key 미만 노드 수)
    assert tree.rank(10) == 0
    assert tree.rank(30) == 2
    assert tree.rank(50) == 4
    assert tree.rank(100) == 5
