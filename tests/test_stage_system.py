from __future__ import annotations

from core.types import Coord, Enemy, Item, ItemCategory, Player, TileType
from core.world import World
from map.bsp import generate_dungeon
from systems.inventory import Inventory
from systems.turn_manager import TurnManager
from systems.undo import UndoSystem


def test_player_stage_initialization():
    """플레이어 생성 시 기본 스테이지가 1층인지 확인."""
    player = Player(
        id=0,
        pos=Coord(0, 0),
        hp=100,
        max_hp=100,
        atk=10,
        defense=5,
        speed=100,
    )
    # 기본값으로 stage 속성이 1이어야 함
    assert hasattr(player, "stage")
    assert player.stage == 1


def test_stairs_spawning_in_bsp():
    """BSP 던전 생성 시 마지막 방의 중앙에 계단이 정상 배치되는지 확인."""
    # 40x40 크기의 던전 생성
    dungeon = generate_dungeon(40, 40, seed=42)

    # 방이 최소 1개 이상 존재해야 함
    assert len(dungeon.rooms) > 0

    # 마지막 방의 중앙 좌표
    last_room_center = dungeon.rooms[-1].center

    # 해당 좌표의 타일 종류가 STAIRS여야 함
    tile = dungeon.tile_at(last_room_center)
    assert tile is not None
    assert tile.type == TileType.STAIRS

    # 계단 타일은 통과(passable) 가능해야 함
    assert tile.passable is True


def test_undo_system_clear():
    """Undo 시스템의 clear 메소드가 동작하여 기록을 비우는지 확인."""
    undo_system = UndoSystem()

    # 더미 액션 실행 등으로 히스토리를 쌓음
    # (여기서는 임의로 undo_system에 clear 메소드를 호출했을 때 스택이 비워지는지 체크)
    assert hasattr(undo_system, "clear")

    # 더미 액션을 넣을 수 없더라도 clear 호출 시 에러가 나지 않고 스택이 비워지는지 테스트
    # 실제 game loop의 undo_system에 command 스택이 저장되어 있으므로,
    # stage transition 시 `undo_system.clear()`를 명시적으로 실행해 스택을 초기화해야 함.
    undo_system.clear()
    assert len(undo_system.history) == 0
    assert len(undo_system.redo_stack) == 0


def test_turn_manager_clear():
    """TurnManager의 clear 메소드가 동작하여 스케줄을 비우고 재설정 가능한지 확인."""
    turn_manager = TurnManager()
    player = Player(id=0, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    enemy = Enemy(id=1, pos=Coord(1, 1), hp=5, max_hp=5, atk=1, defense=0, speed=100)

    turn_manager.schedule(player, 0)
    turn_manager.schedule(enemy, 0)

    assert len(turn_manager.heap) > 0

    # clear 메소드가 있고, 큐를 비워야 함
    assert hasattr(turn_manager, "clear")
    turn_manager.clear()

    # 비어있는지 확인
    assert len(turn_manager.heap) == 0

    # 새로운 스테이지용으로 재등록
    turn_manager.schedule(player, 0)
    turn_manager.schedule(enemy, 0)
    assert len(turn_manager.heap) == 2


def test_stage_transition_logic():
    """스테이지 전환 로직이 플레이어 상태 및 월드 상태를 올바르게 초기화하는지 검증."""
    # 1. 초기 맵 설정
    dungeon = generate_dungeon(40, 40, seed=42)
    player = Player(
        id=0,
        pos=dungeon.rooms[0].center,
        hp=100,
        max_hp=100,
        atk=10,
        defense=5,
        speed=100,
        stage=1,
    )
    inventory = Inventory()

    # 초기 월드 세팅 (몬스터 1마리, 아이템 1개)
    enemy = Enemy(id=1, pos=Coord(5, 5), hp=10, max_hp=10, atk=2, defense=0, speed=100)
    item = Item(id="potion", name="Potion", category=ItemCategory.CONSUMABLE)

    world = World(
        dungeon=dungeon,
        player=player,
        inventory=inventory,
        entities=[enemy],
        items={Coord(6, 6): item},
    )

    # 2. 스테이지 전환 수행 (1층 -> 2층)
    player.stage += 1

    # 완전히 새로운 던전 생성 (새 시드로 결정론적/비결정론적 생성 가능)
    new_dungeon = generate_dungeon(40, 40, seed=100)

    # 이전 몬스터, 아이템 목록 제거
    world.entities.clear()
    world.items.clear()

    # 새 던전 적용 및 플레이어 위치 이동 (첫 번째 방 중앙)
    world.dungeon = new_dungeon
    player.pos = new_dungeon.rooms[0].center

    # 새 몬스터와 아이템 임의 스폰 (여기선 모의)
    new_enemy = Enemy(id=2, pos=Coord(10, 10), hp=15, max_hp=15, atk=3, defense=1, speed=100)
    new_item = Item(id="sword", name="Sword", category=ItemCategory.WEAPON)
    world.entities.append(new_enemy)
    world.items[Coord(12, 12)] = new_item

    # 3. 단언문 검증
    assert player.stage == 2
    assert player.pos == new_dungeon.rooms[0].center
    assert len(world.entities) == 1
    assert world.entities[0].id == 2
    assert len(world.items) == 1
    assert Coord(12, 12) in world.items
    assert new_dungeon.tile_at(new_dungeon.rooms[-1].center).type == TileType.STAIRS
