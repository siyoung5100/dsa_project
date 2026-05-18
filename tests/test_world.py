from core.world import World
from core.types import Coord, Player, Tile, TileType, Entity
from map.dungeon import Dungeon
from systems.inventory import Inventory

def test_world_passable():
    # 3x3 던전 (중앙은 벽)
    grid = [[Tile(TileType.FLOOR) for _ in range(3)] for _ in range(3)]
    grid[1][1] = Tile(TileType.WALL)
    dungeon = Dungeon(width=3, height=3, grid=grid)
    
    player = Player(id=0, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    world = World(dungeon=dungeon, player=player, inventory=Inventory())
    
    # 벽은 통과 불가
    assert world.is_passable(Coord(1, 1)) is False
    # 빈 공간은 통과 가능
    assert world.is_passable(Coord(0, 1)) is True
    # 플레이어 위치는 통과 불가 (다른 엔티티 입장에서)
    assert world.is_passable(Coord(0, 0)) is False

def test_world_entity_collision():
    grid = [[Tile(TileType.FLOOR) for _ in range(3)] for _ in range(3)]
    dungeon = Dungeon(width=3, height=3, grid=grid)
    player = Player(id=0, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    enemy = Entity(id=1, pos=Coord(1, 1), hp=5, max_hp=5, atk=1, defense=0, speed=100)
    
    world = World(dungeon=dungeon, player=player, inventory=Inventory(), entities=[enemy])
    
    # 적이 있는 위치는 통과 불가
    assert world.is_passable(Coord(1, 1)) is False
    
    # 죽은 적은 통과 가능해야 함 (구현에 따라 다르지만 현재는 alive 체크함)
    enemy.alive = False
    assert world.is_passable(Coord(1, 1)) is True

def test_get_entity_at():
    grid = [[Tile(TileType.FLOOR) for _ in range(3)] for _ in range(3)]
    dungeon = Dungeon(width=3, height=3, grid=grid)
    player = Player(id=0, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    enemy = Entity(id=1, pos=Coord(1, 1), hp=5, max_hp=5, atk=1, defense=0, speed=100)
    
    world = World(dungeon=dungeon, player=player, inventory=Inventory(), entities=[enemy])
    
    assert world.get_entity_at(Coord(0, 0)) == player
    assert world.get_entity_at(Coord(1, 1)) == enemy
    assert world.get_entity_at(Coord(2, 2)) is None

def test_world_items():
    from core.types import Item, ItemCategory
    grid = [[Tile(TileType.FLOOR) for _ in range(3)] for _ in range(3)]
    dungeon = Dungeon(width=3, height=3, grid=grid)
    player = Player(id=0, pos=Coord(0, 0), hp=10, max_hp=10, atk=1, defense=0, speed=100)
    world = World(dungeon=dungeon, player=player, inventory=Inventory())
    
    item = Item(id="potion", name="Potion", category=ItemCategory.CONSUMABLE)
    pos = Coord(1, 1)
    
    world.add_item(pos, item)
    assert world.get_item_at(pos) == item
    
    removed = world.remove_item(pos)
    assert removed == item
    assert world.get_item_at(pos) is None
