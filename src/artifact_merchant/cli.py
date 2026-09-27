"""Command-line entry point for Artifact Merchant."""
from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .commands import HELP, Command, load_script, parse
from .input import read_command
from .game import GameState
from .ui import console_bottom, console_prompt_end, dashboard, help_screen


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
    elif name in {"location", "orders", "factions", "upgrades", "wait", "save", "load", "inspect", "research"}:
        console.append(f"Команда принята: {name}. Модуль будет подключён следующим срезом.")
    elif name:
        console.append(f"Неизвестная команда: {name}. Напишите help.")
    return True


def run_script(path: str) -> None:
    root = Path.cwd() / "scripts"
    state = GameState.new()
    console: list[str] = []
    for command in load_script(path, root if Path(path).parent == Path("scripts") else None):
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
            command = parse(read_command("│ > "))
            print(console_prompt_end() + "\n" + console_bottom())
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи.")
            return
        console.append(f"> {command.name} {' '.join(command.args)}".rstrip())
        if command.name == "script":
            if not command.args:
                print("\n  Использование: script scripts/day.am")
                input("  Enter — продолжить...")
            else:
                try:
                    run_script(command.args[0])
                except (OSError, ValueError) as exc:
                    print(f"\n  Ошибка скрипта: {exc}")
                    input("  Enter — продолжить...")
            continue
        if not execute(command, state, console):
            return


def version() -> str:
    return f"Artifact Merchant v{__version__}"


if __name__ == "__main__":
    main()
