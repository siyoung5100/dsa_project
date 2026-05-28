from __future__ import annotations

import pytest

from core.types import Coord, Item, ItemCategory, Player, Tile, TileType, UseItemAction
from core.world import World
from map.dungeon import Dungeon
from systems.inventory import Inventory
from systems.undo import UndoSystem


@pytest.fixture
def test_world():
    """테스트용 가상 월드 구성."""
    grid = [[Tile(TileType.FLOOR) for _ in range(5)] for _ in range(5)]
    dungeon = Dungeon(width=5, height=5, grid=grid)
    player = Player(
        id=0,
        pos=Coord(2, 2),
        hp=80,
        max_hp=100,
        atk=10,
        defense=2,
        speed=100,
    )
    inventory = Inventory(capacity_per_cat=5)
    return World(dungeon=dungeon, player=player, inventory=inventory, entities=[], items={})


def test_use_consumable_potion(test_world):
    """체력이 깎인 상태에서 HP 포션을 사용하면 체력이 정확히 회복되고 인벤토리에서 소모되어야 함."""
    player = test_world.player
    inventory = test_world.inventory

    potion = Item(
        id="red_potion", name="Red Potion", category=ItemCategory.CONSUMABLE, effect={"hp": 15}
    )
    inventory.add(potion, count=1)

    assert inventory.total() == 1
    assert player.hp == 80

    action = UseItemAction(player, potion)
    action.do(test_world)

    # 체력 회복 80 + 15 = 95
    assert player.hp == 95
    # 인벤토리 소모
    assert inventory.total() == 0


def test_use_potion_max_hp_cap(test_world):
    """최대 체력 이상으로 포션을 사용해도 max_hp를 넘지 않고, 회복량은 0이지만 소모되어야 함."""
    player = test_world.player
    inventory = test_world.inventory
    player.hp = 95  # 5만 비어있음

    potion = Item(
        id="red_potion", name="Red Potion", category=ItemCategory.CONSUMABLE, effect={"hp": 20}
    )
    inventory.add(potion, count=1)

    action = UseItemAction(player, potion)
    action.do(test_world)

    # max_hp가 100이므로 100으로 캡핑
    assert player.hp == 100
    assert inventory.total() == 0


def test_use_weapon_atk_boost(test_world):
    """무기 아이템을 사용(장착 소모)하면 공격력이 증가하고 인벤토리에서 소모되어야 함."""
    player = test_world.player
    inventory = test_world.inventory

    sword = Item(
        id="iron_sword", name="Iron Sword", category=ItemCategory.WEAPON, effect={"atk": 5}
    )
    inventory.add(sword, count=1)

    assert player.atk == 10
    action = UseItemAction(player, sword)
    action.do(test_world)

    # 공격력 10 -> 15 증가
    assert player.atk == 15
    assert inventory.total() == 0


def test_use_armor_defense_boost(test_world):
    """방어구 아이템을 사용(장착 소모)하면 방어력이 증가하고 인벤토리에서 소모되어야 함."""
    player = test_world.player
    inventory = test_world.inventory

    armor = Item(
        id="leather_armor", name="Leather Armor", category=ItemCategory.ARMOR, effect={"defense": 3}
    )
    inventory.add(armor, count=1)

    assert player.defense == 2
    action = UseItemAction(player, armor)
    action.do(test_world)

    # 방어력 2 -> 5 증가
    assert player.defense == 5
    assert inventory.total() == 0


def test_use_item_action_undo_redo(test_world):
    """아이템 사용 행동에 대한 Undo 및 Redo 시 상태(스탯, 인벤토리 수량)가 정밀 복원되어야 함."""
    player = test_world.player
    inventory = test_world.inventory
    undo_system = UndoSystem(test_world)

    # 포션, 검, 갑옷을 각각 획득 및 사용
    potion = Item(
        id="red_potion", name="Red Potion", category=ItemCategory.CONSUMABLE, effect={"hp": 20}
    )
    sword = Item(
        id="iron_sword", name="Iron Sword", category=ItemCategory.WEAPON, effect={"atk": 5}
    )

    inventory.add(potion, count=1)
    inventory.add(sword, count=1)

    # 1. 포션 사용 실행
    action_potion = UseItemAction(player, potion)
    undo_system.execute(action_potion)

    assert player.hp == 100  # 80 + 20
    assert inventory.total() == 1  # sword 만 남음

    # 2. 검 사용 실행
    action_sword = UseItemAction(player, sword)
    undo_system.execute(action_sword)

    assert player.atk == 15  # 10 + 5
    assert inventory.total() == 0

    # 3. 검 사용 취소 (Undo 1회)
    assert undo_system.undo() is True
    assert player.atk == 10  # 검 스탯 롤백
    assert inventory.total() == 1  # 검 복원
    # 복원된 아이템이 올바른 카테고리에 복원되었는지 확인
    assert len(inventory.list(ItemCategory.WEAPON)) == 1
    assert inventory.list(ItemCategory.WEAPON)[0].item.id == "iron_sword"

    # 4. 포션 사용 취소 (Undo 2회)
    assert undo_system.undo() is True
    assert player.hp == 80  # 포션 스탯 롤백
    assert inventory.total() == 2  # 포션 및 검 모두 복원
    assert len(inventory.list(ItemCategory.CONSUMABLE)) == 1

    # 5. 포션 사용 재실행 (Redo 1회)
    assert undo_system.redo() is True
    assert player.hp == 100
    assert inventory.total() == 1

    # 6. 검 사용 재실행 (Redo 2회)
    assert undo_system.redo() is True
    assert player.atk == 15
    assert inventory.total() == 0
