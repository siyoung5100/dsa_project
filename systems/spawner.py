from __future__ import annotations

from typing import TYPE_CHECKING

from core.types import Coord, Enemy, Item, ItemCategory

if TYPE_CHECKING:
    from core.rng import RNG
    from core.world import World


class Spawner:
    """몬스터와 아이템을 던전에 배치하는 유틸리티."""

    def __init__(self, rng: RNG) -> None:
        self.rng = rng
        self._entity_id_counter = 100  # 플레이어(0)와 겹치지 않게

    def spawn_monsters(self, world: World, count_per_room: int = 1) -> None:
        """각 방에 몬스터를 생성."""
        stage = getattr(world.player, "stage", 1)
        for room in world.dungeon.rooms:
            for _ in range(count_per_room):
                # 방 내부 무작위 좌표 선택
                x = self.rng.randint(room.x, room.x + room.w - 1)
                y = self.rng.randint(room.y, room.y + room.h - 1)
                pos = Coord(x, y)

                # 플레이어 위치나 이미 엔티티가 있는 곳은 피함
                if pos == world.player.pos or world.get_entity_at(pos):
                    continue

                enemy = self._create_random_enemy(pos, stage)
                world.entities.append(enemy)

    def spawn_items(self, world: World, count_per_room: int = 1) -> None:
        """각 방에 아이템을 생성."""
        for room in world.dungeon.rooms:
            for _ in range(count_per_room):
                x = self.rng.randint(room.x, room.x + room.w - 1)
                y = self.rng.randint(room.y, room.y + room.h - 1)
                pos = Coord(x, y)

                # 아이템이 이미 있는 곳은 피함
                if world.get_item_at(pos):
                    continue

                item = self._create_random_item()
                world.add_item(pos, item)

    def _create_random_enemy(self, pos: Coord, stage: int = 1) -> Enemy:
        """무작위 적 생성."""
        # kinds = [ (kind, base_hp, base_atk, defense, speed, base_xp) ]
        kinds = [
            ("goblin", 30, 5, 1, 100, 20),
            ("orc", 55, 10, 3, 100, 45),
            ("slime", 15, 3, 0, 100, 10),
        ]
        kind, hp, atk, defense, speed, base_xp = self.rng.choice(kinds)

        hp = int(hp * stage)
        atk = int(atk * stage)
        xp_reward = int(base_xp * stage)

        enemy = Enemy(
            id=self._entity_id_counter,
            pos=pos,
            hp=hp,
            max_hp=hp,
            atk=atk,
            defense=defense,
            speed=speed,
            kind=kind,
            xp_reward=xp_reward,
        )
        self._entity_id_counter += 1
        return enemy

    def _create_random_item(self) -> Item:
        """무작위 아이템 생성."""
        items = [
            ("red_potion", "Red Potion", ItemCategory.CONSUMABLE, {"hp": 20}),
            ("iron_sword", "Iron Sword", ItemCategory.WEAPON, {"atk": 5}),
            ("leather_armor", "Leather Armor", ItemCategory.ARMOR, {"defense": 2}),
        ]
        item_id, name, cat, effect = self.rng.choice(items)
        return Item(id=item_id, name=name, category=cat, effect=effect)
