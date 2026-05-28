from __future__ import annotations

from typing import TYPE_CHECKING

from readchar import readkey, key
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

from core.types import TileType

if TYPE_CHECKING:
    from core.types import Player, Entity
    from map.dungeon import Dungeon
    from core.world import World


class TerminalUI:
    """터미널 UI 핸들러. rich와 readchar를 사용한다."""

    def __init__(self) -> None:
        self.console = Console()
        self.layout = Layout()
        self._setup_layout()
        self.live = Live(self.layout, console=self.console, screen=True, auto_refresh=False)

    def _setup_layout(self) -> None:
        """기본 레이아웃 구성."""
        self.layout.split_row(
            Layout(name="map", ratio=2),
            Layout(name="side", ratio=1),
        )
        self.layout["side"].split_column(
            Layout(name="status", ratio=1),
            Layout(name="logs", ratio=1),
        )

    def __enter__(self) -> TerminalUI:
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.live.stop()

    def render(
        self,
        world: World,
        messages: list[str],
    ) -> None:
        """전체 화면을 렌더링한다."""
        self.layout["map"].update(Panel(self._render_map(world), title="Dungeon"))
        self.layout["status"].update(Panel(self._render_status(world.player), title="Status"))
        self.layout["logs"].update(Panel(self._render_logs(messages), title="Log"))
        self.live.refresh()

    def _render_map(self, world: World) -> Text:
        """던전 맵을 Text 객체로 렌더링."""
        char_map = {
            TileType.WALL: ("#", "grey37"),
            TileType.FLOOR: (".", "grey19"),
            TileType.DOOR: ("+", "gold3"),
            TileType.STAIRS: (">", "bright_magenta"),
        }

        rendered_text = Text()
        dungeon = world.dungeon
        player = world.player
        entity_positions = {e.pos: e for e in world.entities if e.alive}
        item_positions = world.items

        for y in range(dungeon.height):
            for x in range(dungeon.width):
                from core.types import Coord
                c = Coord(x, y)
                tile = dungeon.tile_at(c)
                
                if not tile:
                    rendered_text.append(" ")
                    continue

                if player.pos == c:
                    rendered_text.append("@", style="bold yellow")
                elif c in entity_positions and tile.visible:
                    e = entity_positions[c]
                    char = e.kind[0].upper() if hasattr(e, 'kind') else 'E'
                    rendered_text.append(char, style="bold red")
                elif c in item_positions and tile.visible:
                    rendered_text.append("!", style="bold green")
                else:
                    char, color = char_map.get(tile.type, ("?", "white"))
                    if tile.visible:
                        rendered_text.append(char, style=color)
                    elif tile.explored:
                        rendered_text.append(char, style="grey11")
                    else:
                        rendered_text.append(" ")
            rendered_text.append("\n")
        
        return rendered_text

    def _render_status(self, player: Player) -> Table:
        """플레이어 상태 정보 테이블 및 HP 바 생성."""
        table = Table.grid(padding=(0, 1))
        table.add_column("Stat", style="cyan", width=8)
        table.add_column("Value", style="white")

        # HP Bar
        hp_percent = player.hp / player.max_hp if player.max_hp > 0 else 0
        bar_width = 15
        filled = int(hp_percent * bar_width)
        hp_bar = Text("[", style="white")
        hp_bar.append("=" * filled, style="bold green" if hp_percent > 0.3 else "bold red")
        hp_bar.append("-" * (bar_width - filled), style="grey23")
        hp_bar.append("]", style="white")
        hp_bar.append(f" {player.hp}/{player.max_hp}", style="white")

        table.add_row("HP", hp_bar)
        table.add_row("Level", str(player.level))
        table.add_row("ATK", str(player.atk))
        table.add_row("DEF", str(player.defense))
        table.add_row("XP", str(player.xp))
        table.add_row("Pos", f"({player.pos.x}, {player.pos.y})")
        
        return table

    def _render_logs(self, messages: list[str]) -> Text:
        """최근 메시지 로그 렌더링 및 색상 스타일링."""
        styled_logs = Text()
        for msg in messages[-8:]:
            if "막혔습니다" in msg or "할 수 없는" in msg:
                styled_logs.append(msg + "\n", style="yellow")
            elif "입장" in msg:
                styled_logs.append(msg + "\n", style="bold cyan")
            elif "종료" in msg:
                styled_logs.append(msg + "\n", style="bold red")
            elif "발견" in msg:
                styled_logs.append(msg + "\n", style="bold green")
            else:
                styled_logs.append(msg + "\n", style="white")
        return styled_logs

    def get_input(self) -> str:
        """키 입력을 대기하고 방향/액션 문자열을 반환."""
        try:
            k = readkey()
        except OverflowError:
            return "unknown"
        
        mapping = {
            key.UP: "up",
            "w": "up",
            key.DOWN: "down",
            "s": "down",
            key.LEFT: "left",
            "a": "left",
            key.RIGHT: "right",
            "d": "right",
            "g": "pickup",
            "u": "undo",
            "r": "redo",
            "i": "inventory",
            key.ESC: "quit",
            "q": "quit",
        }
        
        return mapping.get(k, "unknown")
