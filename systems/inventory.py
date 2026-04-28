"""Inventory — dict 기반 해시 테이블 (카테고리별 중첩 dict).

명세서 §4.4 참고.
연산 복잡도: add/remove/lookup 평균 O(1), list(category) O(|category|).

핵심 클래스:
- Inventory
  - add(item, count=1) -> bool
  - remove(item_id, category, count=1) -> bool
  - list(category) -> list[Slot]
  - total() -> int
"""
