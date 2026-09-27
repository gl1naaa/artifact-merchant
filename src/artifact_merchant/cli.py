"""Command-line entry point for Artifact Merchant."""
from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .commands import HELP, Command, load_script, parse
from .input import read_command
from .game import GameState
from .ui import dashboard, help_screen


def _show_items(title: str, items: list) -> None:
    print(f"\n  {title}")
    if not items:
        print("  (пусто)")
    for item in items:
        print(f"  {item.id:<20} {item.name:<24} {item.sell_price:>10,} кр.")


def execute(command: Command, state: GameState) -> bool:
    """Execute a UI command. Returns False when the session should end."""
    name = command.name
    if name in {"q", "quit", "exit", "выход"}:
        print("До встречи, торговец.")
        return False
    if name in {"h", "help", "помощь"}:
        help_screen()
    elif name in {"clear", "cls"}:
        return True
    elif name == "status":
        print(f"\n  {state.status()}")
        input("  Enter — продолжить...")
    elif name == "inventory":
        _show_items("ИНВЕНТАРЬ", state.inventory)
        input("  Enter — продолжить...")
    elif name == "market":
        _show_items("РЫНОК", state.market)
        input("  Enter — продолжить...")
    elif name == "journal":
        print("\n  ЖУРНАЛ")
        print("\n".join(f"  • {entry}" for entry in state.journal[-10:]))
        input("  Enter — продолжить...")
    elif name == "buy":
        ok, message = state.buy(command.args[0] if command.args else "")
        print(f"\n  {'OK' if ok else 'ERROR'}: {message}")
        input("  Enter — продолжить...")
    elif name == "sell":
        ok, message = state.sell(command.args[0] if command.args else "")
        print(f"\n  {'OK' if ok else 'ERROR'}: {message}")
        input("  Enter — продолжить...")
    elif name in {"location", "orders", "factions", "upgrades", "wait", "save", "load", "inspect", "research"}:
        print(f"\n  Команда принята: {name}. Этот модуль будет подключён следующим срезом.")
        input("  Enter — продолжить...")
    elif name:
        print(f"\n  Неизвестная команда: {name}. Напишите help.")
        input("  Enter — продолжить...")
    return True


def run_script(path: str) -> None:
    root = Path.cwd() / "scripts"
    state = GameState.new()
    for command in load_script(path, root if Path(path).parent == Path("scripts") else None):
        if not execute(command, state):
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
    while True:
        dashboard(state.day, state.gold, state.reputation)
        try:
            command = parse(read_command("\n> "))
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи.")
            return
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
        if not execute(command, state):
            return


def version() -> str:
    return f"Artifact Merchant v{__version__}"


if __name__ == "__main__":
    main()
