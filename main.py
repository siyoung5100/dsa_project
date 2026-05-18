"""Dungeon Crawler RPG — 엔트리포인트.

게임 루프 개요 (명세서 §4.3 의사코드 참고):
    1. 던전 생성 (BSP)
    2. 플레이어 + 적 + 아이템 배치
    3. 턴 매니저로부터 next_actor 가져오기
    4. 플레이어 차례 → 입력 → Action.do() → undo_system에 push
       적 차례 → AI.decide() → A* 결과 → MoveAction
    5. 반복. 종료 시 Leaderboard에 기록.
"""


import sys
import time
from datetime import datetime
from pathlib import Path
from core.types import Coord, Player, MoveAction, AttackAction, PickupAction, Record
from core.events import events
from core.world import World
from core.rng import RNG
from map.bsp import generate_dungeon
from map.fov import compute_fov
from ui.terminal import TerminalUI
from systems.spawner import Spawner
from systems.turn_manager import TurnManager
from systems.undo import UndoSystem
from systems.inventory import Inventory
from systems.ai import EnemyAI
from persistence.leaderboard import Leaderboard


def main() -> None:
    """게임 시작. 정식 턴제 루프 및 시스템 통합."""
    
    # 0. 초기화
    rng = RNG(seed=42)
    turn_manager = TurnManager()
    inventory = Inventory()
    ai = EnemyAI()
    leaderboard = Leaderboard(Path("leaderboard.json"))
    start_time = time.time()
    
    # 1. 던전 생성
    width, height = 50, 25
    dungeon = generate_dungeon(width, height, seed=42)
    
    # 2. 플레이어 생성 및 배치
    if not dungeon.rooms:
        print("에러: 던전에 방이 생성되지 않았습니다.")
        sys.exit(1)
        
    start_pos = dungeon.rooms[0].center
    player = Player(
        id=0,
        pos=start_pos,
        hp=100,
        max_hp=100,
        atk=10,
        defense=2,
        speed=100
    )
    
    # 3. 월드 및 시스템 설정
    world = World(dungeon=dungeon, player=player, inventory=inventory, entities=[])
    undo_system = UndoSystem(world)
    spawner = Spawner(rng)
    spawner.spawn_monsters(world, count_per_room=1)
    spawner.spawn_items(world, count_per_room=1)
    
    # 4. 턴 스케줄링 (플레이어 + 적)
    turn_manager.schedule(player, 0)
    for entity in world.entities:
        turn_manager.schedule(entity, 0)
    
    # 5. UI 및 초기 설정
    events.log("던전에 입장했습니다! (WASD: 이동, G: 줍기, U: Undo, R: Redo, Q: 종료)")
    
    with TerminalUI() as ui:
        while True:
            actor = turn_manager.next_actor()
            if actor is None or not player.alive:
                play_time = int(time.time() - start_time)
                events.log(f"게임 오버! 최종 점수: {player.xp} (Q를 눌러 종료)")
                
                # 리더보드 저장
                record = Record(
                    name="Player",
                    score=player.xp,
                    play_time_sec=play_time,
                    undo_used=undo_system.used,
                    timestamp=datetime.now().isoformat()
                )
                rank = leaderboard.add(record)
                events.log(f"리더보드 등록 완료! 현재 순위: {rank + 1}등")
                
                # 사망 후에도 화면은 볼 수 있게 루프 유지
                ui.render(world, messages=events.get_logs())
                while ui.get_input() != "quit":
                    pass
                break

            if actor == player:
                # 시야 계산 및 렌더링 (플레이어 턴에만)
                compute_fov(world.dungeon, player.pos, radius=8)
                ui.render(world, messages=events.get_logs())
                
                # 입력 대기 및 행동 결정
                action = None
                while action is None:
                    cmd = ui.get_input()
                    
                    if cmd == "quit":
                        return
                    elif cmd == "undo":
                        if undo_system.undo():
                            events.log("시간을 되돌렸습니다.")
                            ui.render(world, messages=events.get_logs())
                        continue
                    elif cmd == "redo":
                        if undo_system.redo():
                            events.log("미래를 다시 썼습니다.")
                            ui.render(world, messages=events.get_logs())
                        continue
                    elif cmd == "pickup":
                        item = world.get_item_at(player.pos)
                        if item:
                            action = PickupAction(player, player.pos, item)
                        else:
                            events.log("발밑에 아무것도 없습니다.")
                            continue
                        
                    dx, dy = 0, 0
                    if cmd == "up": dy = -1
                    elif cmd == "down": dy = 1
                    elif cmd == "left": dx = -1
                    elif cmd == "right": dx = 1
                    
                    if dx != 0 or dy != 0:
                        new_pos = player.pos + Coord(dx, dy)
                        target = world.get_entity_at(new_pos)
                        
                        if target and target != player:
                            action = AttackAction(player, target)
                        elif world.dungeon.is_passable(new_pos):
                            action = MoveAction(player, dx, dy)
                        else:
                            events.log("벽에 막혔습니다!")
                
                # 플레이어 행동 실행
                undo_system.execute(action)
                turn_manager.advance(player, action.cost)
                
            else:
                # 적 AI 턴
                action = ai.decide(actor, player.pos, world)
                
                dist = actor.pos.manhattan(player.pos)
                if dist == 1:
                    action = AttackAction(actor, player)
                
                action.do(world)
                turn_manager.advance(actor, action.cost)


if __name__ == "__main__":
    main()
