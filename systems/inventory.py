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

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.types import Item, ItemCategory


@dataclass
class Slot:
    """인벤토리의 한 슬롯. 아이템 정보와 수량을 가진다."""
    item: "Item"
    count: int


class Inventory:
    def __init__(self, capacity_per_cat: int = 20):
        from core.types import ItemCategory
        
        self.capacity = capacity_per_cat
        # 카테고리별로 아이템 ID를 키로 하는 dict 관리
        self._by_cat: dict["ItemCategory", dict[str, Slot]] = {
            c: {} for c in ItemCategory
        }

    def add(self, item: "Item", count: int = 1) -> bool:
        """아이템을 추가한다. 성공 시 True, 용량 초과 시 False 반환."""
        bucket = self._by_cat[item.category]
        
        if item.id in bucket:
            bucket[item.id].count += count
            return True
        else:
            # 새로운 아이템 종류 추가 시 용량 확인
            if len(bucket) >= self.capacity:
                return False
            bucket[item.id] = Slot(item, count)
            return True

    def remove(self, item_id: str, category: "ItemCategory", count: int = 1) -> bool:
        """아이템 수량을 줄인다. 성공 시 True, 부족하거나 없을 시 False 반환."""
        bucket = self._by_cat[category]
        slot = bucket.get(item_id)
        
        if slot is None or slot.count < count:
            return False
        
        slot.count -= count
        if slot.count <= 0:
            del bucket[item_id]
        return True

    def list(self, category: "ItemCategory") -> list[Slot]:
        """특정 카테고리의 모든 아이템 슬롯 목록을 반환한다."""
        return list(self._by_cat[category].values())

    def total(self) -> int:
        """인벤토리 내의 모든 아이템 총 수량을 반환한다."""
        return sum(slot.count for bucket in self._by_cat.values() for slot in bucket.values())
