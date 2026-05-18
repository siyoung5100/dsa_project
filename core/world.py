from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from map.dungeon import Dungeon
    from core.types import Player, Entity, Coord


@dataclass
class World:
    """게임의 전체 상태를 보유하는 객체.
    
    Action.do(world) 및 AI.decide(actor, world)에서 사용된다.
    """
    dungeon: Dungeon
    player: Player
    entities: list[Entity] = field(default_factory=list)

    def is_passable(self, pos: Coord) -> bool:
        """해당 좌표로 이동 가능한지 확인 (벽 및 다른 엔티티 체크)."""
        # 1. 벽 체크
        if not self.dungeon.is_passable(pos):
            return False
        
        # 2. 다른 엔티티 체크 (플레이어 포함)
        if self.player.pos == pos:
            return False
            
        for entity in self.entities:
            if entity.alive and entity.pos == pos:
                return False
                
        return True

    def get_entity_at(self, pos: Coord) -> Entity | None:
        """해당 좌표에 있는 엔티티 반환."""
        if self.player.pos == pos:
            return self.player
        
        for entity in self.entities:
            if entity.alive and entity.pos == pos:
                return entity
        return None
