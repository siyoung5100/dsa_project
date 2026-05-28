"""persistence/avl_tree.py + leaderboard.py 단위 테스트.

명세서 §5.6 시나리오 참고.
"""

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
        tree.insert(i * 10, f"v{i * 10}")

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


def test_avl_delete_basic():
    tree = AVLTree()
    for i in [10, 20, 5, 15, 25]:
        tree.insert(i, str(i))

    # 잎 노드 삭제 (15)
    assert tree.delete(15) is True
    assert tree.search(15) is None
    assert len(tree) == 4

    # 자식이 하나인 노드 삭제 (20)
    assert tree.delete(20) is True
    assert tree.search(20) is None
    assert tree.search(25) == "25"
    assert len(tree) == 3

    # 자식이 둘인 노드 삭제 (10 - 루트)
    assert tree.delete(10) is True
    assert tree.search(10) is None
    assert len(tree) == 2

    # 존재하지 않는 키 삭제
    assert tree.delete(100) is False


def test_avl_random_stress():
    import random

    tree = AVLTree()
    keys = list(range(100))
    random.shuffle(keys)

    # 100개 삽입
    for k in keys:
        tree.insert(k, str(k))

    assert len(tree) == 100
    assert tree.root.height <= 8  # log2(100) approx 6.6

    # 정렬 확인
    sorted_keys = sorted(keys)
    tree_keys = [node.key for node in tree.in_order()]
    assert tree_keys == sorted_keys

    # 50개 삭제
    delete_keys = keys[:50]
    for k in delete_keys:
        assert tree.delete(k) is True

    assert len(tree) == 50
    # 삭제 후에도 균형 확인
    assert tree.root.height <= 7

    # 다시 정렬 확인
    remaining_keys = sorted(keys[50:])
    tree_keys = [node.key for node in tree.in_order()]
    assert tree_keys == remaining_keys


def test_leaderboard_sorting_and_rank():
    import pathlib

    from core.types import Record
    from persistence.leaderboard import Leaderboard

    # 임시 파일 경로 (실제 파일은 쓰지 않도록 처리하거나 tmp_path 활용)
    lb = Leaderboard(pathlib.Path("dummy.json"))
    lb.tree = AVLTree()  # 초기화 (load 방지)

    r1 = Record("Alice", 1000, 120, 5, "2026-05-01T10:00:00")
    r2 = Record("Bob", 1000, 100, 2, "2026-05-01T10:00:00")  # 같은 점수, 더 좋은 기록
    r3 = Record("Charlie", 500, 200, 10, "2026-05-01T10:00:00")  # 낮은 점수

    # 랭킹 확인 (1-indexed)
    assert lb.add(r1) == 1
    assert lb.add(r2) == 1  # Bob이 Alice를 밀어냄
    assert lb.add(r3) == 3

    # 전체 순서 확인
    top = lb.top(3)
    assert top[0].name == "Bob"
    assert top[1].name == "Alice"
    assert top[2].name == "Charlie"


def test_leaderboard_persistence(tmp_path):
    from core.types import Record
    from persistence.leaderboard import Leaderboard

    db_file = tmp_path / "leaderboard.json"
    lb = Leaderboard(db_file)

    r1 = Record("Alice", 1000, 120, 5, "2026-05-01T10:00:00")
    lb.add(r1)

    # 파일에 저장되었는지 확인 (add 내부에서 save 호출 기대)
    assert db_file.exists()

    # 새 인스턴스에서 불러오기
    lb2 = Leaderboard(db_file)
    assert len(lb2.tree) == 1
    assert lb2.top(1)[0].name == "Alice"
