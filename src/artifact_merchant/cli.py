"""Command-line entry point for Artifact Merchant."""
from __future__ import annotations

import sys

from . import __version__
from .ui import dashboard, help_screen


def main() -> None:
    # Windows consoles may still expose cp1251/cp866; keep the Unicode UI usable.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    while True:
        dashboard()
        try:
            command = input("\n  ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи.")
            return
        if command in {"q", "quit", "выход"}:
            print("До встречи, торговец.")
            return
        if command in {"h", "help", "помощь"}:
            help_screen()
            continue
        if command in {"1", "2", "3", "4", "5"}:
            dashboard()
            labels = {"1": "Suppliers", "2": "Inventory", "3": "Shop", "4": "Research", "5": "End day"}
            print(f"\n  {labels[command]} screen will be implemented in the next slice.")
            input("  Press Enter to return...")
            continue


def version() -> str:
    return f"Artifact Merchant v{__version__}"


if __name__ == "__main__":
    main()
