"""core/types.py 단위 테스트."""

from __future__ import annotations

import pytest

from core.types import (
    Action,
    AttackAction,
    Coord,
    Enemy,
    Entity,
    Item,
    ItemCategory,
    MoveAction,
    PickupAction,
    Player,
    Record,
    Tile,
    TileType,
    UseItemAction,
)


# ==============================================================
# Coord
# ==============================================================
class TestCoord:
    def test_arithmetic(self):
        a, b = Coord(2, 3), Coord(1, 1)
        assert a + b == Coord(3, 4)
        assert a - b == Coord(1, 2)

    def test_manhattan(self):
        assert Coord(0, 0).manhattan(Coord(3, 4)) == 7
        assert Coord(2, 5).manhattan(Coord(2, 5)) == 0

    def test_hashable_and_immutable(self):
        c = Coord(1, 2)
        # frozen=True 이므로 dict 키, set 원소로 사용 가능 — A* 의 핵심 요건
        assert {c: "ok"}[Coord(1, 2)] == "ok"
        assert Coord(1, 2) in {Coord(1, 2)}
        with pytest.raises(Exception):
            c.x = 999  # type: ignore[misc]


# ==============================================================
# Tile
# ==============================================================
class TestTile:
    @pytest.mark.parametrize(
        ("tile_type", "expected"),
        [
            (TileType.FLOOR, True),
            (TileType.DOOR, True),
            (TileType.STAIRS, True),
            (TileType.WALL, False),
        ],
    )
    def test_passable(self, tile_type, expected):
        assert Tile(type=tile_type).passable is expected

    def test_default_visibility(self):
        t = Tile(type=TileType.FLOOR)
        assert t.visible is False
        assert t.explored is False


# ==============================================================
# Entity / Player / Enemy
# ==============================================================
class TestEntity:
    def _player(self, **overrides):
        defaults = dict(
            id=1, pos=Coord(0, 0), hp=50, max_hp=50,
            atk=10, defense=5, speed=100,
        )
        defaults.update(overrides)
        return Player(**defaults)

    def test_take_damage_applies_defense(self):
        p = self._player()
        dealt = p.take_damage(20)
        assert dealt == 15  # 20 - defense(5)
        assert p.hp == 35
        assert p.alive

    def test_take_damage_floors_at_zero(self):
        p = self._player(hp=10)
        p.take_damage(1000)
        assert p.hp == 0
        assert not p.alive

    def test_take_damage_minimum_zero(self):
        p = self._player(defense=100)
        # 방어력보다 작은 공격은 0 데미지
        assert p.take_damage(5) == 0
        assert p.hp == p.max_hp

    def test_heal_caps_at_max_hp(self):
        p = self._player(hp=40)
        healed = p.heal(100)
        assert healed == 10  # 40 → 50, 실제 회복 10
        assert p.hp == 50

    def test_player_extends_entity_with_xp_level(self):
        p = self._player()
        assert p.xp == 0
        assert p.level == 1

    def test_enemy_has_kind_and_path_cache(self):
        e = Enemy(
            id=2, pos=Coord(5, 5), hp=20, max_hp=20,
            atk=8, defense=2, speed=80,
        )
        assert e.kind == "goblin"
        assert e.path_cache == []  # default_factory 가 정상 동작 (공유 X)
        assert e.alive

    def test_enemy_path_cache_is_per_instance(self):
        e1 = Enemy(id=1, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=50)
        e2 = Enemy(id=2, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=50)
        e1.path_cache.append(Coord(1, 1))
        # 두 인스턴스가 같은 리스트를 공유하면 안 됨 (default_factory 의 핵심)
        assert e2.path_cache == []


# ==============================================================
# Item / ItemCategory
# ==============================================================
class TestItem:
    def test_categories_exist(self):
        assert ItemCategory.WEAPON.value == "WEAPON"
        assert ItemCategory.ARMOR.value == "ARMOR"
        assert ItemCategory.CONSUMABLE.value == "CONSUMABLE"

    def test_item_with_effect(self):
        sword = Item(
            id="iron_sword", name="철검",
            category=ItemCategory.WEAPON, effect={"atk": 5},
        )
        assert sword.effect == {"atk": 5}

    def test_item_default_effect_is_empty(self):
        plain = Item(id="rock", name="돌멩이", category=ItemCategory.CONSUMABLE)
        assert plain.effect == {}


# ==============================================================
# Action 계층
# ==============================================================
class TestAction:
    def test_action_is_abstract(self):
        # Action은 직접 인스턴스화 불가 (do/undo 가 abstract)
        with pytest.raises(TypeError):
            Action()  # type: ignore[abstract]

    def test_move_action_constructs(self):
        actor = Player(
            id=1, pos=Coord(0, 0), hp=50, max_hp=50,
            atk=10, defense=5, speed=100,
        )
        m = MoveAction(actor=actor, dx=1, dy=0)
        assert m.actor is actor
        assert m.dx == 1 and m.dy == 0
        assert m.cost == 100  # 클래스 변수 기본값

    def test_concrete_actions_subclass_action(self):
        # 모든 concrete Action은 Action의 서브클래스여야 함 (UndoSystem 의 타입 보증)
        for cls in (MoveAction, AttackAction, UseItemAction, PickupAction):
            assert issubclass(cls, Action)

    def test_unimplemented_methods_raise(self):
        # 현재 단계에서는 do/undo 가 NotImplementedError. World 정의 후 구현 예정.
        actor = Player(id=1, pos=Coord(0, 0), hp=50, max_hp=50, atk=1, defense=0, speed=100)
        m = MoveAction(actor=actor, dx=1, dy=0)
        with pytest.raises(NotImplementedError):
            m.do(world=None)
        with pytest.raises(NotImplementedError):
            m.undo(world=None)


# ==============================================================
# Record
# ==============================================================
class TestRecord:
    def test_record_is_frozen_and_hashable(self):
        r = Record(
            name="alice", score=1000, play_time_sec=120,
            undo_used=3, timestamp="2026-04-28T19:00:00Z",
        )
        # 동일 데이터의 두 Record 는 동등
        same = Record(
            name="alice", score=1000, play_time_sec=120,
            undo_used=3, timestamp="2026-04-28T19:00:00Z",
        )
        assert r == same
        # set 에 들어갈 수 있어야 함 (frozen=True)
        assert {r, same} == {r}

    def test_record_immutable(self):
        r = Record(
            name="alice", score=1000, play_time_sec=120,
            undo_used=0, timestamp="2026-04-28T19:00:00Z",
        )
        with pytest.raises(Exception):
            r.score = 9999  # type: ignore[misc]

    def test_leaderboard_sort_key_orders_by_score_desc(self):
        # leaderboard.py 의 _key 와 동일한 규약을 직접 테스트
        a = Record("a", score=500, play_time_sec=60, undo_used=0, timestamp="t1")
        b = Record("b", score=1000, play_time_sec=60, undo_used=0, timestamp="t2")
        c = Record("c", score=500, play_time_sec=30, undo_used=0, timestamp="t3")

        def key(r: Record) -> tuple:
            return (-r.score, r.play_time_sec, r.undo_used, r.timestamp)

        ranked = sorted([a, b, c], key=key)
        assert [r.name for r in ranked] == ["b", "c", "a"]
        # b 가 1등(점수 최고), c 가 2등(같은 점수 중 시간 짧음), a 가 3등.
