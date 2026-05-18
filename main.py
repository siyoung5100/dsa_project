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
from core.types import Coord, Player
from core.events import events
from core.world import World
from map.bsp import generate_dungeon
from map.fov import compute_fov
from ui.terminal import TerminalUI


def main() -> None:
    """게임 시작. 기초적인 플레이어 이동 루프 구현."""
    
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
    
    # 3. 월드 초기화
    world = World(dungeon=dungeon, player=player, entities=[])
    
    # 4. UI 및 초기 설정
    events.log("던전에 입장했습니다! (WASD: 이동, Q: 종료)")
    
    with TerminalUI() as ui:
        # 5. 게임 루프
        while True:
            # 시야 계산
            compute_fov(world.dungeon, world.player.pos, radius=8)
            
            # 렌더링
            ui.render(world.dungeon, world.player, entities=world.entities, messages=events.get_logs())
            
            # 입력 대기
            action_key = ui.get_input()
            
            if action_key == "quit":
                events.log("게임을 종료합니다.")
                break
                
            # 이동 처리 (기초 구현)
            dx, dy = 0, 0
            if action_key == "up":
                dy = -1
            elif action_key == "down":
                dy = 1
            elif action_key == "left":
                dx = -1
            elif action_key == "right":
                dx = 1
                
            if dx != 0 or dy != 0:
                new_pos = world.player.pos + Coord(dx, dy)
                # 월드 레벨에서 이동 가능 여부 체크
                if world.is_passable(new_pos):
                    world.player.pos = new_pos
                else:
                    events.log("이동할 수 없는 곳입니다.")


if __name__ == "__main__":
    main()
