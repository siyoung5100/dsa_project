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
