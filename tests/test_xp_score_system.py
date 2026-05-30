from __future__ import annotations

from core.rng import RNG
from core.types import AttackAction, Coord, Enemy, Player, Tile, TileType
from core.world import World
from map.dungeon import Dungeon
from systems.inventory import Inventory
from systems.spawner import Spawner


def test_exponential_levelup_calculations():
    """지수 함수 증가 공식에 따라 레벨업 요구 XP 차감 및 다중 레벨업 이월을 검증."""
    player = Player(id=0, pos=Coord(0, 0), hp=100, max_hp=100, atk=10, defense=2, speed=100)

    # 1레벨 -> 2레벨 요구량: 100 * (1.5**0) = 100
    # 2레벨 -> 3레벨 요구량: 100 * (1.5**1) = 150
    assert hasattr(player, "gain_xp")

    # 120 XP 획득 -> 2레벨 달성 후 20 XP 남음
    logs = player.gain_xp(120)
    assert player.level == 2
    assert player.xp == 20
    assert len(logs) == 1
    assert "레벨 업!" in logs[0]

    # 추가로 140 XP 획득 -> 총 160 XP로 2레벨 요구량 150 돌파하여 3레벨 달성 후 10 XP 남음
    logs2 = player.gain_xp(140)
    assert player.level == 3
    assert player.xp == 10
    assert len(logs2) == 1

    # 다중 레벨업 검증 (1레벨 짜리에 단번에 500 XP를 주었을 때)
    fresh_player = Player(id=0, pos=Coord(0, 0), hp=100, max_hp=100, atk=10, defense=2, speed=100)
    # 1레벨(요구 100) -> 2레벨(요구 150) -> 3레벨(요구 225) -> 4레벨(요구 337)
    # 500 XP 주면 100 차감(2레벨), 150 차감(3레벨), 남은 250 중 225 차감(4레벨) -> 4레벨 달성 후 25 XP 남음
    logs_multi = fresh_player.gain_xp(500)
    assert fresh_player.level == 4
    assert fresh_player.xp == 25
    assert len(logs_multi) == 3


def test_stat_boosts_with_ceil_hp_ratio():
    """레벨업 시 ATK+2, DEF+1, MaxHP+10 스탯 부스트 및 올림 체력 비율 비례 조정을 검증."""
    # 체력이 50/100 (비율 50%)인 반피 상태의 플레이어
    player = Player(id=0, pos=Coord(0, 0), hp=50, max_hp=100, atk=10, defense=2, speed=100)

    player.gain_xp(100)  # 2레벨업

    assert player.atk == 12
    assert player.defense == 3
    assert player.max_hp == 110

    # 110의 50% = 55 (올림 처리해도 정확히 55)
    assert player.hp == 55

    # 소수점 올림 처리가 이루어지는 애매한 체력 비율 검증
    # 체력이 35/100 (비율 35%)인 상태
    player2 = Player(id=0, pos=Coord(0, 0), hp=35, max_hp=100, atk=10, defense=2, speed=100)
    player2.gain_xp(100)  # 2레벨업 (MaxHP -> 110)
    # 110 * 0.35 = 38.5 -> 올림 적용 시 39 HP여야 함
    assert player2.hp == 39


def test_monster_stage_scaling():
    """층수(Stage)에 따른 몬스터 기본 전투 스펙 상향 및 스탯/XP 곱연산 스케일링을 검증."""
    rng = RNG(seed=42)
    spawner = Spawner(rng)

    # 1. 상향된 1층 몬스터 기본 스펙 체크 (slime, goblin, orc)
    # Spawner 내부 무작위 스폰 테스트를 위해 다량 생성 후 스탯 검증
    slimes = []
    goblins = []
    orcs = []

    for _ in range(50):
        e = spawner._create_random_enemy(Coord(0, 0), stage=1)
        if e.kind == "slime":
            slimes.append(e)
        elif e.kind == "goblin":
            goblins.append(e)
        elif e.kind == "orc":
            orcs.append(e)

    # Slime 기본 스펙 검증: HP 15, ATK 3, DEF 0, BaseXP 10
    if slimes:
        s = slimes[0]
        assert s.max_hp == 15
        assert s.atk == 3
        assert s.defense == 0
        assert s.xp_reward == 10

    # Goblin 기본 스펙 검증: HP 30, ATK 5, DEF 1, BaseXP 20
    if goblins:
        g = goblins[0]
        assert g.max_hp == 30
        assert g.atk == 5
        assert g.defense == 1
        assert g.xp_reward == 20

    # Orc 기본 스펙 검증: HP 55, ATK 10, DEF 3, BaseXP 45
    if orcs:
        o = orcs[0]
        assert o.max_hp == 55
        assert o.atk == 10
        assert o.defense == 3
        assert o.xp_reward == 45

    # 2. 2층(Stage=2) 배율 스포닝 스탯 곱연산 검증
    e_stage2 = spawner._create_random_enemy(Coord(0, 0), stage=2)
    if e_stage2.kind == "slime":
        assert e_stage2.max_hp == 30
        assert e_stage2.atk == 6
        assert e_stage2.xp_reward == 20
    elif e_stage2.kind == "goblin":
        assert e_stage2.max_hp == 60
        assert e_stage2.atk == 10
        assert e_stage2.xp_reward == 40
    elif e_stage2.kind == "orc":
        assert e_stage2.max_hp == 110
        assert e_stage2.atk == 20
        assert e_stage2.xp_reward == 90


def test_attack_action_xp_gain_and_undo_rollback():
    """AttackAction 실행 시 처치 XP 획득과 Undo 호출 시 스탯 스냅샷 롤백 동작을 검증."""
    # 3x3 던전
    grid = [[Tile(TileType.FLOOR) for _ in range(3)] for _ in range(3)]
    dungeon = Dungeon(width=3, height=3, grid=grid)

    # HP 50/100, ATK 10인 플레이어
    player = Player(id=0, pos=Coord(0, 0), hp=50, max_hp=100, atk=10, defense=2, speed=100)
    # HP 10, DEF 0, xp_reward 35(Base 35 * 1)인 몬스터
    enemy = Enemy(
        id=1,
        pos=Coord(1, 1),
        hp=10,
        max_hp=10,
        atk=2,
        defense=0,
        speed=100,
        kind="orc",
        xp_reward=35,
    )

    world = World(dungeon=dungeon, player=player, inventory=Inventory(), entities=[enemy])

    # 1. 몬스터 타격 및 처치 (공격 1회로 처치)
    action = AttackAction(player, enemy)
    action.do(world)

    # 몬스터 사망 확인
    assert enemy.alive is False
    # 플레이어 XP 획득 확인 (35 XP 획득)
    assert player.xp == 35
    assert player.level == 1  # 100 XP 미만이므로 레벨은 여전히 1

    # 2. 되돌리기 (Undo) 검증
    action.undo(world)

    # 몬스터 생존 및 체력 복구 확인
    assert enemy.alive is True
    assert enemy.hp == 10
    # 플레이어 XP 회수 확인 (35 XP -> 0 XP)
    assert player.xp == 0

    # 3. 레벨업 유발 처치 및 Undo 롤백 검증
    # 플레이어의 XP를 80으로 세팅 ( Orc 처치 시 35 XP를 얻어 115 XP로 레벨업 기대 )
    player.xp = 80
    enemy.hp = 10
    enemy.alive = True

    action2 = AttackAction(player, enemy)
    action2.do(world)

    # 레벨업 완료 확인
    assert player.level == 2
    assert player.xp == 15  # 80 + 35 - 100 = 15
    assert player.max_hp == 110
    assert player.hp == 55  # 50/100(50%) -> 55/110(50%) 비율 보정
    assert player.atk == 12

    # Undo 수행
    action2.undo(world)

    # 스냅샷 복원으로 이전 시점으로 완전히 복원되는지 검증
    assert player.level == 1
    assert player.xp == 80
    assert player.max_hp == 100
    assert player.hp == 50
    assert player.atk == 10
    assert player.defense == 2


def test_weighted_score_formula():
    """가중치 리더보드 점수 계산식과 0점 하한 제약이 올바르게 틱 작동하는지 검증."""
    from main import calculate_score

    # 플레이어 1: 2레벨, 50 XP, 3층 도달, Undo 4회 사용
    # Score = 2 * 1000 + 50 + (3 - 1) * 1000 - 4 * 100 = 2000 + 50 + 2000 - 400 = 3650
    player1 = Player(
        id=0,
        pos=Coord(0, 0),
        hp=100,
        max_hp=100,
        atk=10,
        defense=2,
        speed=100,
        stage=3,
        xp=50,
        level=2,
    )
    score1 = calculate_score(player1, undo_used=4)
    assert score1 == 3650

    # 플레이어 2: 1레벨, 10 XP, 1층 도달, Undo 20회 사용 (점수가 음수로 떨어질 위기)
    # Score = 1 * 1000 + 10 + 0 - 2000 = -990 -> max(0, -990) = 0
    player2 = Player(
        id=0,
        pos=Coord(0, 0),
        hp=100,
        max_hp=100,
        atk=10,
        defense=2,
        speed=100,
        stage=1,
        xp=10,
        level=1,
    )
    score2 = calculate_score(player2, undo_used=20)
    assert score2 == 0
