"""persistence/avl_tree.py + leaderboard.py 단위 테스트.

명세서 §5.6 시나리오 참고.
"""

import pytest
import random
from core.types import Record
from persistence.avl_tree import AVLTree
from persistence.leaderboard import Leaderboard

def test_avl_basic_insertion():
    """AVL 트리에 데이터를 넣고 순서대로 나오는지 확인."""
    tree = AVLTree()
    data = [10, 20, 30, 40, 50, 25]
    for x in data:
        tree.insert(x, f"val_{x}")
    
    # 중위 순회 결과는 정렬되어 있어야 함
    result = [node.key for node in tree.in_order()]
    assert result == sorted(data)

def test_avl_balance():
    """랜덤 데이터를 대량으로 넣어도 균형이 유지되는지 확인."""
    tree = AVLTree()
    nums = list(range(100))
    random.shuffle(nums)
    
    for x in nums:
        tree.insert(x, x)
    
    # AVL 트리의 높이는 log(N)에 비례해야 함 (N=100이면 높이 10 이하)
    # 실제 AVL 높이 공식: h < 1.44 * log2(N+2) - 1.328
    # 100이면 log2(100) ~= 6.64, 1.44 * 6.64 ~= 9.56
    def get_height(node):
        if not node: return 0
        return 1 + max(get_height(node.left), get_height(node.right))
    
    h = get_height(tree.root)
    assert h <= 10

def test_avl_rank_and_kth():
    """rank(미만 노드 수)와 kth(k번째 노드) 연산 검증."""
    tree = AVLTree()
    data = [10, 20, 30, 40, 50]
    for x in data:
        tree.insert(x, x)
    
    # rank: 30 미만은 [10, 20] 2개
    assert tree.rank(30) == 2
    assert tree.rank(10) == 0
    assert tree.rank(55) == 5
    
    # kth: 0번째는 10, 2번째는 30
    assert tree.kth(0).key == 10
    assert tree.kth(2).key == 30
    assert tree.kth(4).key == 50

def test_leaderboard_logic(tmp_path):
    """리더보드 점수 정렬 및 저장/로드 검증."""
    db_path = tmp_path / "leaderboard.json"
    lb = Leaderboard(db_path)
    
    r1 = Record("Alpha", 100, 60, 0, "2026-05-18T10:00:00Z")
    r2 = Record("Beta", 200, 50, 1, "2026-05-18T11:00:00Z")
    r3 = Record("Gamma", 150, 70, 0, "2026-05-18T12:00:00Z")
    
    lb.add(r1)
    lb.add(r2)
    lb.add(r3)
    
    top = lb.top(3)
    # 점수 높은 순서: Beta(200) > Gamma(150) > Alpha(100)
    assert top[0].name == "Beta"
    assert top[1].name == "Gamma"
    assert top[2].name == "Alpha"
    
    # 파일 저장 및 로드 확인
    lb2 = Leaderboard(db_path)
    assert lb2.top(1)[0].name == "Beta"
