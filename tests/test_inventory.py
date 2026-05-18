"""systems/inventory.py 단위 테스트.

명세서 §5.4 시나리오 참고.
"""

import pytest
from core.types import Item, ItemCategory
from systems.inventory import Inventory

def test_item_accumulation():
    """같은 ID의 아이템이 합산되는지 확인."""
    inv = Inventory()
    potion = Item(id="hp_potion", name="Potion", category=ItemCategory.CONSUMABLE)
    
    inv.add(potion, 2)
    inv.add(potion, 3)
    
    slots = inv.list(ItemCategory.CONSUMABLE)
    assert len(slots) == 1
    assert slots[0].count == 5
    assert inv.total() == 5

def test_capacity_limit():
    """카테고리별 용량 제한 확인."""
    inv = Inventory(capacity_per_cat=2)
    
    item1 = Item(id="w1", name="W1", category=ItemCategory.WEAPON)
    item2 = Item(id="w2", name="W2", category=ItemCategory.WEAPON)
    item3 = Item(id="w3", name="W3", category=ItemCategory.WEAPON)
    
    assert inv.add(item1) is True
    assert inv.add(item2) is True
    # 세 번째 다른 아이템은 실패해야 함
    assert inv.add(item3) is False
    assert len(inv.list(ItemCategory.WEAPON)) == 2

def test_remove_to_deletion():
    """수량이 0이 되면 목록에서 사라지는지 확인."""
    inv = Inventory()
    sword = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
    
    inv.add(sword, 1)
    assert len(inv.list(ItemCategory.WEAPON)) == 1
    
    # 1개 제거
    assert inv.remove("sword", ItemCategory.WEAPON, 1) is True
    assert len(inv.list(ItemCategory.WEAPON)) == 0
    
    # 없는 아이템 제거 시도
    assert inv.remove("sword", ItemCategory.WEAPON, 1) is False

def test_remove_partial():
    """일부 수량만 제거 확인."""
    inv = Inventory()
    arrow = Item(id="arrow", name="Arrow", category=ItemCategory.CONSUMABLE)
    
    inv.add(arrow, 10)
    assert inv.remove("arrow", ItemCategory.CONSUMABLE, 4) is True
    
    slots = inv.list(ItemCategory.CONSUMABLE)
    assert slots[0].count == 6
