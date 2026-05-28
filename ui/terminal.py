from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from readchar import key, readkey
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.types import TileType

if TYPE_CHECKING:
    from core.types import Coord, Player
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

    def _has_explored_neighboring_floor(self, dungeon: Any, pos: Coord) -> bool:
        """벽 주변 8방향 중 탐험된 바닥(FLOOR, DOOR, STAIRS)이 있는지 검사합니다.

        탐험되지 않은(explored=False) 검은 공간 속에 벽만 홀로 둥둥 떠서 렌더링되는 시각적 버그를 해결합니다.
        """
        from core.types import Coord

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor_pos = pos + Coord(dx, dy)
                t = dungeon.tile_at(neighbor_pos)
                if t and t.explored and t.type != TileType.WALL:
                    return True
        return False

    def _render_map(self, world: World) -> Text:
        """던전 맵을 플레이어 중심의 스크롤링 뷰포트 및 더블 문자(정사각형)로 렌더링."""
        char_map = {
            TileType.WALL: ("██", "grey37"),
            TileType.FLOOR: ("· ", "grey19"),
            TileType.DOOR: ("++", "gold3"),
            TileType.STAIRS: (">>", "bright_magenta"),
        }

        rendered_text = Text()
        dungeon = world.dungeon
        player = world.player
        entity_positions = {e.pos: e for e in world.entities if e.alive}
        item_positions = world.items

        # 뷰포트 크기 정의 (가로 35타일, 세로 20타일)
        view_w = min(dungeon.width, 35)
        view_h = min(dungeon.height, 20)

        # 플레이어 위치를 중심으로 뷰포트 시작 오프셋 계산 (경계 밖으로 벗어나지 않도록 클램프)
        start_x = max(0, min(dungeon.width - view_w, player.pos.x - view_w // 2))
        start_y = max(0, min(dungeon.height - view_h, player.pos.y - view_h // 2))

        for y in range(start_y, start_y + view_h):
            for x in range(start_x, start_x + view_w):
                from core.types import Coord

                c = Coord(x, y)
                tile = dungeon.tile_at(c)

                if not tile:
                    rendered_text.append("  ")
                    continue

                if player.pos == c:
                    rendered_text.append("@ ", style="bold yellow")
                elif c in entity_positions and tile.visible:
                    e = entity_positions[c]
                    char = e.kind[0].upper() if hasattr(e, "kind") else "E"
                    rendered_text.append(f"{char} ", style="bold red")
                elif c in item_positions and tile.visible:
                    rendered_text.append("! ", style="bold green")
                else:
                    char, color = char_map.get(tile.type, ("??", "white"))
                    if tile.visible:
                        rendered_text.append(char, style=color)
                    elif tile.explored:
                        # 벽(WALL)일 때는 인접한 8방향 타일 중 하나라도 탐험된 바닥이 있는 경우에만 렌더링
                        should_render = True
                        if tile.type == TileType.WALL:
                            should_render = self._has_explored_neighboring_floor(dungeon, c)

                        if should_render:
                            explored_color = "grey23" if tile.type == TileType.WALL else "grey15"
                            rendered_text.append(char, style=explored_color)
                        else:
                            rendered_text.append("  ")
                    else:
                        rendered_text.append("  ")
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
        """키 입력을 대기하고 방향/액션/선택 문자열을 반환."""
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
            key.ENTER: "select",
            "\r": "select",
            "\n": "select",
            " ": "select",
        }

        return mapping.get(k, "unknown")

    def show_menu(self) -> str:
        """메인 메뉴 화면을 표시하고 선택된 메뉴명을 반환 (W/S 또는 방향키 조작, Enter 결정)."""
        options = ["Game Start", "Leaderboard", "Exit"]
        selected_idx = 0

        title_art = Text(
            """ ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
 ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
 ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
 ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
 ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
 ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝

  ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗
 ██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗
 ██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝
 ██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗
 ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║
  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝""",
            style="bold magenta",
            justify="center",
        )

        while True:
            # 메뉴 그리드: 한 열, 중앙 정렬
            grid = Table.grid(expand=True)
            grid.add_column(justify="center")

            grid.add_row(title_art)
            grid.add_row("")

            max_opt_len = max(len(o) for o in options)
            for i, opt in enumerate(options):
                label = f"[ {opt:<{max_opt_len}} ]"
                if i == selected_idx:
                    grid.add_row(Text(f"▶  {label}", style="bold cyan", justify="center"))
                else:
                    grid.add_row(Text(f"   {label}", style="grey37", justify="center"))

            grid.add_row("")
            grid.add_row(Text("─" * 50, style="grey23", justify="center"))

            # 키 안내 한 줄
            hint = Text(justify="center")
            hint.append("  이동  ", style="grey46")
            hint.append(" W ", style="bold black on white")
            hint.append(" / ", style="grey46")
            hint.append(" S ", style="bold black on white")
            hint.append("   또는   ", style="grey46")
            hint.append(" ↑ ", style="bold black on white")
            hint.append(" / ", style="grey46")
            hint.append(" ↓ ", style="bold black on white")
            hint.append("     선택  ", style="grey46")
            hint.append(" Enter ", style="bold black on white")
            hint.append("  ", style="grey46")
            grid.add_row(hint)
            grid.add_row(Text("─" * 50, style="grey23", justify="center"))

            self.console.clear()
            self.console.print(
                Panel(grid, border_style="bold magenta", expand=True, padding=(1, 4))
            )

            cmd = self.get_input()
            if cmd == "up":
                selected_idx = (selected_idx - 1) % len(options)
            elif cmd == "down":
                selected_idx = (selected_idx + 1) % len(options)
            elif cmd == "select":
                choice = options[selected_idx]
                choice_map = {"Game Start": "start", "Leaderboard": "leaderboard", "Exit": "exit"}
                return choice_map.get(choice, "exit")
            elif cmd == "quit":
                return "exit"

    def show_leaderboard(self, leaderboard: Any) -> None:
        """리더보드 목록을 rich.table로 액자처럼 그려주고 아무 키나 입력하면 메뉴로 복귀."""
        while True:
            records = leaderboard.top(10)

            table = Table(
                title="🏆 TOP 10 LEADERBOARD 🏆",
                border_style="bold yellow",
                title_style="bold yellow",
            )
            table.add_column("Rank", justify="center", style="bold cyan")
            table.add_column("Player Name", justify="center", style="bold white")
            table.add_column("Score (XP)", justify="center", style="bold green")
            table.add_column("Time Played", justify="center", style="bold magenta")
            table.add_column("Undos Used", justify="center", style="bold red")
            table.add_column("Date", justify="center", style="grey37")

            for rank_idx, record in enumerate(records):
                min_part = record.play_time_sec // 60
                sec_part = record.play_time_sec % 60
                time_str = f"{min_part:02d}m {sec_part:02d}s"

                date_str = (
                    record.timestamp.split("T")[0] if "T" in record.timestamp else record.timestamp
                )

                table.add_row(
                    f"{rank_idx + 1}",
                    record.name,
                    f"{record.score}",
                    time_str,
                    f"{record.undo_used}",
                    date_str,
                )

            back_hint = Text(
                "  ESC · Q · Enter  키를 눌러 메인 메뉴로 돌아갑니다.",
                justify="center",
                style="grey46",
            )

            self.console.clear()
            self.console.print(Align.center(table))
            self.console.print(back_hint)

            cmd = self.get_input()
            if cmd in ("select", "quit", "up", "down", "left", "right"):
                break

    # ==========================================
    # [개발자 도구] 정식 릴리즈 시 아래 메소드를 제거하세요.
    # ==========================================
    def prompt_seed(self, default_seed: int = 42) -> int:
        """게임을 시작하기 전에 개발용 난수 시드를 입력받는 프롬프트."""
        self.console.clear()

        # 안내 패널 렌더링
        grid = Table.grid(expand=True)
        grid.add_column(justify="center")
        grid.add_row(Text("🛠️ DEVELOPER TOOLS 🛠️", style="bold yellow", justify="center"))
        grid.add_row("")
        grid.add_row(
            Text("던전 생성을 위한 난수 seed 값을 입력해 주세요.", style="white", justify="center")
        )
        grid.add_row(
            Text(
                f"(아무것도 입력하지 않고 Enter를 누르면 기본값 {default_seed}가 지정됩니다.)",
                style="grey46",
                justify="center",
            )
        )
        grid.add_row("")

        self.console.print(Panel(grid, border_style="yellow", padding=(1, 4)))

        # 사용자 입력을 받기 위해 일반 콘솔 input 프롬프트 띄우기
        try:
            user_input = input("\n 👉 Seed 입력: ").strip()
            if not user_input:
                return default_seed
            return int(user_input)
        except ValueError:
            self.console.print(
                f"[bold red]경고:[/bold red] 올바른 숫자가 아닙니다. 기본값 [bold yellow]{default_seed}[/bold yellow]로 진행합니다.",
                style="red",
            )
            time.sleep(1)
            return default_seed
        except (KeyboardInterrupt, SystemExit):
            return default_seed
