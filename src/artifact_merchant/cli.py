"""Command-line entry point for Artifact Merchant."""
from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .commands import HELP, Command, load_script, parse
from .input import read_command
from .game import GameState
from .ui import dashboard


def _completion_provider(state: GameState):
    commands = [key.split()[0] for key in HELP]
    artifact_ids = [item.id for item in state.market + state.inventory]

    def complete(text: str) -> list[str]:
        parts = text.split()
        if len(parts) <= 1:
            prefix = parts[0] if parts else ""
            return sorted({item for item in commands if item.startswith(prefix)})
        if parts[0].lower() in {"buy", "sell", "inspect", "research", "contain", "store", "cleanse"}:
            prefix = parts[-1]
            return [item for item in artifact_ids if item.startswith(prefix)]
        return []

    return complete


def _show_items(title: str, items: list) -> list[str]:
    rows = [title]
    if not items:
        return rows + ["(пусто)"]
    return rows + [f"{item.id:<20} {item.name:<24} {item.sell_price:>10,} кр." for item in items]


def execute(command: Command, state: GameState, console: list[str]) -> bool:
    """Execute a UI command. Returns False when the session should end."""
    name = command.name
    if name in {"q", "quit", "exit", "выход"}:
        console.append("До встречи, торговец.")
        return False
    if name in {"h", "help", "помощь"}:
        console.extend(["COMMANDS", "  inventory          показать инвентарь", "  market             открыть рынок", "  buy <id>           купить артефакт", "  sell <id>          продать артефакт", "  status             состояние лавки", "  journal            журнал событий", "  clear              очистить терминал", "  quit               выйти"])
    elif name in {"clear", "cls"}:
        console.clear()
    elif name == "status":
        console.append(state.status())
    elif name == "inventory":
        console.extend(_show_items("ИНВЕНТАРЬ", state.inventory))
    elif name == "market":
        console.extend(_show_items("РЫНОК", state.market))
    elif name == "journal":
        console.extend(["ЖУРНАЛ"] + [f"• {entry}" for entry in state.journal[-10:]])
    elif name == "buy":
        ok, message = state.buy(command.args[0] if command.args else "")
        console.append(f"{'OK' if ok else 'ERROR'}: {message}")
    elif name == "sell":
        ok, message = state.sell(command.args[0] if command.args else "")
        console.append(f"{'OK' if ok else 'ERROR'}: {message}")
    elif name in {"inspect", "research"}:
        item_id = command.args[0] if command.args else ""
        ok, rows = (state.inspect(item_id) if name == "inspect" else state.research(item_id))
        console.extend([f"{'OK' if ok else 'ERROR'}: {row}" for row in rows])
    elif name in {"location", "orders", "factions", "upgrades", "wait", "save", "load"}:
        console.append(f"Команда принята: {name}. Модуль будет подключён следующим срезом.")
    elif name:
        console.append(f"Неизвестная команда: {name}. Напишите help.")
    return True


def run_script(path: str, state: GameState, console: list[str]) -> None:
    root = Path.cwd() / "scripts"
    relative = Path(path)
    if relative.parts and relative.parts[0].lower() == "scripts":
        relative = Path(*relative.parts[1:])
    for command in load_script(str(relative), root):
        console.append(f"> {command.name} {' '.join(command.args)}".rstrip())
        if not execute(command, state, console):
            break


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    for line in sys.argv[1:]:
        if line == "--version":
            print(version())
            return
    state = GameState.new()
    console = ["Connected to the Gilded Veil terminal.", "Type help for available commands."]
    while True:
        dashboard(state, console)
        try:
            # The dashboard already drew the prompt row and bottom border.
            # Move into that row so input remains inside the frame.
            sys.stdout.write("\033[2A\r\033[2K│ > ")
            sys.stdout.flush()
            command = parse(read_command("", _completion_provider(state)))
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи.")
            return
        console.append(f"> {command.name} {' '.join(command.args)}".rstrip())
        if command.name == "script":
            if not command.args:
                console.append("Использование: script scripts/day.am")
            else:
                try:
                    run_script(command.args[0], state, console)
                except (OSError, ValueError) as exc:
                    console.append(f"Ошибка скрипта: {exc}")
            continue
        if not execute(command, state, console):
            return


def version() -> str:
    return f"Artifact Merchant v{__version__}"


if __name__ == "__main__":
    main()
