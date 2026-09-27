"""Command-line entry point for Artifact Merchant."""
from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .commands import HELP, Command, load_script, parse
from .ui import dashboard, help_screen


def execute(command: Command) -> bool:
    """Execute a UI command. Returns False when the session should end."""
    name = command.name
    if name in {"q", "quit", "exit", "выход"}:
        print("До встречи, торговец.")
        return False
    if name in {"h", "help", "помощь"}:
        help_screen()
    elif name in {"clear", "cls"}:
        return True
    elif name in {"inventory", "market", "location", "inspect", "buy", "sell", "research"}:
        subject = f" {command.args[0]}" if command.args else ""
        print(f"\n  Команда принята: {name}{subject}")
        print("  Игровая логика этого раздела будет подключена следующим вертикальным срезом.")
        input("  Enter — продолжить...")
    elif name:
        print(f"\n  Неизвестная команда: {name}. Напишите help.")
        input("  Enter — продолжить...")
    return True


def run_script(path: str) -> None:
    root = Path.cwd() / "scripts"
    for command in load_script(path, root if Path(path).parent == Path("scripts") else None):
        if not execute(command):
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
    while True:
        dashboard()
        try:
            command = parse(input("\n> "))
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
        if not execute(command):
            return


def version() -> str:
    return f"Artifact Merchant v{__version__}"


if __name__ == "__main__":
    main()
