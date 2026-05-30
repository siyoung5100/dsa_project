"""공통 데이터 타입 정의.

명세서 §3 참고. 모든 모듈이 공유하는 핵심 자료형을 한 곳에 모은다.
이 모듈은 다른 모듈에 의존하지 않는다 (의존 그래프의 루트).

포함:
- 좌표: Coord
- 타일: TileType, Tile
- 엔티티: Entity, Player, Enemy
- 아이템: ItemCategory, Item
- 행동(Command 패턴): Action, MoveAction, AttackAction, UseItemAction, PickupAction
- 기록: Record
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


# ==============================================================
# 좌표 (Coord)
# ==============================================================
@dataclass(frozen=True)
class Coord:
    """2D 격자 좌표.

    `frozen=True`로 immutable 하며 hashable 하다 → dict/set 키로 사용 가능.
    A* 의 came_from / g_score 같은 자료구조에서 키로 쓰인다.
    """

    x: int
    y: int

    def __add__(self, other: Coord) -> Coord:
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Coord) -> Coord:
        return Coord(self.x - other.x, self.y - other.y)

    def manhattan(self, other: Coord) -> int:
        """A* 휴리스틱으로 사용할 맨해튼 거리."""
        return abs(self.x - other.x) + abs(self.y - other.y)


# ==============================================================
# 타일 (TileType, Tile)
# ==============================================================
class TileType(Enum):
    """던전 타일의 종류."""

    WALL = auto()
    FLOOR = auto()
    DOOR = auto()
    STAIRS = auto()


@dataclass
class Tile:
    """던전 그리드의 한 칸.

    visible: 현재 시야 (FOV에서 매 턴 갱신).
    explored: 한 번이라도 본 적 있는가 (어둡게 표시되도록 영구 보존).
    """

    type: TileType
    visible: bool = False
    explored: bool = False

    @property
    def passable(self) -> bool:
        """이 타일을 엔티티가 통과할 수 있는가."""
        return self.type in (TileType.FLOOR, TileType.DOOR, TileType.STAIRS)


# ==============================================================
# 엔티티 (Entity, Player, Enemy)
# ==============================================================
@dataclass
class Entity:
    """플레이어·적의 공통 부모.

    `defense`는 Python 예약어 `def`와의 충돌을 피하기 위해 풀 네임 사용.
    """

    id: int
    pos: Coord
    hp: int
    max_hp: int
    atk: int
    defense: int
    speed: int
    alive: bool = True

    def take_damage(self, amount: int) -> int:
        """방어력을 적용한 실제 피해를 받고, 받은 양을 반환."""
        actual = max(0, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        if self.hp == 0:
            self.alive = False
        return actual

    def heal(self, amount: int) -> int:
        """체력 회복. 실제 회복된 양을 반환."""
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


@dataclass
class Player(Entity):
    """플레이어 캐릭터. 인벤토리·Undo·통계는 별도 시스템이 소유."""

    xp: int = 0
    level: int = 1
    stage: int = 1

    def gain_xp(self, amount: int) -> list[str]:
        """경험치를 획득하고, 필요 시 레벨 업 처리를 수행하며 변경 로그를 반환."""
        import math

        self.xp += amount
        logs = []
        while True:
            # 요구 경험치 공식: 100 * (1.5 ** (level - 1))
            req = int(100 * (1.5 ** (self.level - 1)))
            if self.xp >= req:
                self.xp -= req

                # 기존 체력 비율 저장 (현재 체력 / 최대 체력)
                ratio = self.hp / self.max_hp if self.max_hp > 0 else 0

                # 레벨업 및 스탯 상승
                self.level += 1
                self.atk += 2
                self.defense += 1
                self.max_hp += 10

                # 체력 비율 유지 올림 계산
                self.hp = math.ceil(self.max_hp * ratio)

                logs.append(f"레벨 업! {self.level}레벨이 되었습니다! 스탯이 대폭 상승했습니다.")
            else:
                break
        return logs


@dataclass
class Enemy(Entity):
    """적 엔티티.

    path_cache: 마지막 A* 결과를 보관해, 플레이어가 움직이지 않으면 재계산을 건너뛴다.
    """

    kind: str = "goblin"
    path_cache: list[Coord] = field(default_factory=list)
    xp_reward: int = 0


# ==============================================================
# 아이템 (ItemCategory, Item)
# ==============================================================
class ItemCategory(Enum):
    """인벤토리는 카테고리별 중첩 dict로 관리된다 (§4.4 참고)."""

    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    CONSUMABLE = "CONSUMABLE"


@dataclass
class Item:
    """아이템 프로토타입.

    effect 예: {"atk": 5}, {"hp": 20}, {"defense": 3}.
    프로토타입은 관례상 변경하지 않는다 (불변 강제는 하지 않음).
    """

    id: str
    name: str
    category: ItemCategory
    effect: dict[str, int] = field(default_factory=dict)


# ==============================================================
# 행동 (Action — Command 패턴)
# ==============================================================
class Action(ABC):
    """Command 패턴의 베이스.

    모든 게임 행동(이동·공격·아이템 사용·줍기)은 Action의 서브클래스로 표현된다.
    `do()` 실행 후 `undo()` 호출 시 do() 이전 상태로 *정확히* 복원되어야 한다.

    cost: TurnManager가 행동 후 다음 행동 시각을 계산할 때 사용. 기본 100 (한 턴).
          빠른 공격 등은 더 작게, 느린 행동은 더 크게 설정.
    """

    cost: int = 100

    @abstractmethod
    def do(self, world: Any) -> None:
        """행동을 실행한다. world는 게임 상태 facade (추후 정의)."""
        raise NotImplementedError

    @abstractmethod
    def undo(self, world: Any) -> None:
        """do() 의 역산을 수행한다."""
        raise NotImplementedError


@dataclass
class MoveAction(Action):
    """엔티티를 (dx, dy) 만큼 이동시킨다."""

    actor: Entity
    dx: int
    dy: int

    def do(self, world: Any) -> None:
        new_pos = self.actor.pos + Coord(self.dx, self.dy)
        if world.is_passable(new_pos):
            self.actor.pos = new_pos

    def undo(self, world: Any) -> None:
        self.actor.pos = self.actor.pos - Coord(self.dx, self.dy)


@dataclass
class WaitAction(Action):
    """아무것도 하지 않고 턴만 넘긴다."""

    actor: Entity

    def do(self, world: Any) -> None:
        pass

    def undo(self, world: Any) -> None:
        pass


@dataclass
class AttackAction(Action):
    """attacker가 target을 공격한다.

    do() 실행 시 target.hp 감소량을 _damage_dealt에 기록해두면
    undo() 가 정확히 복원할 수 있다.
    """

    attacker: Entity
    target: Entity
    _damage_dealt: int = 0  # do() 가 채워넣고 undo() 가 사용
    _pre_hp: int = 0
    _pre_xp: int = 0
    _pre_level: int = 1
    _pre_atk: int = 0
    _pre_defense: int = 0
    _pre_max_hp: int = 0

    def do(self, world: Any) -> None:
        # 백업 (공격자가 플레이어인 경우 id가 0)
        is_player_attacker = self.attacker.id == 0
        if is_player_attacker:
            self._pre_hp = self.attacker.hp
            self._pre_xp = self.attacker.xp
            self._pre_level = self.attacker.level
            self._pre_atk = self.attacker.atk
            self._pre_defense = self.attacker.defense
            self._pre_max_hp = self.attacker.max_hp

        self._damage_dealt = self.target.take_damage(self.attacker.atk)
        from core.events import events

        events.log(
            f"{self.attacker.kind if hasattr(self.attacker, 'kind') else '플레이어'}이(가) "
            f"{self.target.kind if hasattr(self.target, 'kind') else '플레이어'}에게 "
            f"{self._damage_dealt}의 피해를 입혔습니다."
        )

        # 몬스터 사망 시 처치 보상
        if not self.target.alive:
            xp_reward = getattr(self.target, "xp_reward", 0)
            if xp_reward > 0:
                events.log(f"{self.target.kind} 처치! {xp_reward} XP를 획득했습니다.")
                if is_player_attacker:
                    level_up_logs = self.attacker.gain_xp(xp_reward)
                    for log in level_up_logs:
                        events.log(log)

    def undo(self, world: Any) -> None:
        self.target.hp += self._damage_dealt
        if self.target.hp > 0:
            self.target.alive = True

        # 플레이어 스냅샷 복구
        if self.attacker.id == 0:
            self.attacker.hp = self._pre_hp
            self.attacker.xp = self._pre_xp
            self.attacker.level = self._pre_level
            self.attacker.atk = self._pre_atk
            self.attacker.defense = self._pre_defense
            self.attacker.max_hp = self._pre_max_hp


@dataclass
class UseItemAction(Action):
    """actor가 인벤토리의 item_id 아이템을 사용한다."""

    actor: Entity
    item: Item  # 명세서에는 item_id였으나 undo를 위해 Item 객체 보관 권장
    _applied_effect: dict[str, int] = field(default_factory=dict)

    def do(self, world: Any) -> None:
        # 효과 적용
        for stat, val in self.item.effect.items():
            if stat == "hp":
                recovered = self.actor.heal(val)
                self._applied_effect["hp"] = recovered
            elif stat == "atk":
                self.actor.atk += val
                self._applied_effect["atk"] = val
            elif stat == "defense":
                self.actor.defense += val
                self._applied_effect["defense"] = val

        # 인벤토리에서 제거 (카테고리 정보 필요)
        world.inventory.remove(self.item.id, self.item.category)

        from core.events import events

        events.log(
            f"{self.actor.kind if hasattr(self.actor, 'kind') else '플레이어'}이(가) "
            f"{self.item.name}을(를) 사용했습니다."
        )

    def undo(self, world: Any) -> None:
        # 효과 역산
        for stat, val in self._applied_effect.items():
            if stat == "hp":
                self.actor.hp -= val
            elif stat == "atk":
                self.actor.atk -= val
            elif stat == "defense":
                self.actor.defense -= val

        # 인벤토리에 다시 추가
        world.inventory.add(self.item)


@dataclass
class PickupAction(Action):
    """actor가 tile 위치의 item을 줍는다."""

    actor: Entity
    tile: Coord
    item: Item

    def do(self, world: Any) -> None:
        if world.inventory.add(self.item):
            world.remove_item(self.tile)
            from core.events import events

            events.log(f"{self.item.name}을(를) 주웠습니다.")
        else:
            from core.events import events

            events.log("인벤토리가 가득 찼습니다!")

    def undo(self, world: Any) -> None:
        # 인벤토리에서 제거하고 월드에 다시 놓기
        if world.inventory.remove(self.item.id, self.item.category):
            world.add_item(self.tile, self.item)


# ==============================================================
# 기록 (Record — 리더보드 항목)
# ==============================================================
@dataclass(frozen=True)
class Record:
    """리더보드 한 줄.

    AVL Tree의 정렬 키는 leaderboard.py 에서 `(-score, play_time_sec, undo_used, timestamp)`
    튜플로 만든다 (점수 내림차순 + 시간·Undo 횟수·등록순 tie-break).

    timestamp 는 ISO 8601 문자열 (예: "2026-04-28T19:00:00Z").
    """

    name: str
    score: int
    play_time_sec: int
    undo_used: int
    timestamp: str
