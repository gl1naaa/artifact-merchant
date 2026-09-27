"""Small dependency-free terminal UI for the first vertical slice."""
from __future__ import annotations

import os
import shutil

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[38;5;210m"
GREEN = "\033[38;5;114m"
YELLOW = "\033[38;5;221m"
CYAN = "\033[38;5;116m"
BLUE = "\033[38;5;110m"
PURPLE = "\033[38;5;139m"
MUTED = "\033[38;5;102m"
PAPER = "\033[38;5;255m"


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def width() -> int:
    """Return a usable layout width without overflowing narrow terminals."""
    return max(40, min(shutil.get_terminal_size((80, 24)).columns, 120))


def color(text: str, tone: str = PAPER, bold: bool = False) -> str:
    return f"{BOLD if bold else ''}{tone}{text}{RESET}"


def rule(char: str = "─") -> str:
    return color(char * width(), MUTED)


def panel(title: str, rows: list[str], tone: str = CYAN) -> list[str]:
    inner = width() - 4
    result = [color(f"┌─ {title} " + "─" * max(0, inner - len(title) - 3) + "┐", tone)]
    for row in rows:
        result.append(color("│ ", tone) + row[:inner].ljust(inner) + color(" │", tone))
    result.append(color("└" + "─" * (width() - 2) + "┘", tone))
    return result


def header(day: int, gold: int, reputation: int) -> list[str]:
    title = color("  ◈ ARTIFACT MERCHANT", YELLOW, True)
    stats = (
        color(f"DAY {day:02d}", MUTED)
        + color(f"  ◆ {gold}g", YELLOW)
        + color(f"  REP {reputation:+d}", GREEN if reputation >= 0 else RED)
    )
    if width() < 68:
        return [title, stats, rule()]
    return [title + "    " + stats, rule()]


def dashboard(day: int = 1, gold: int = 420, reputation: int = 0) -> None:
    clear()
    lines = header(day, gold, reputation)
    lines += panel("THE GILDED VEIL · SHOP FLOOR", [
        color("The bell above the door is silent. Three artifacts wait under glass.", PAPER),
        "",
        color("OPEN HOURS", MUTED) + "  morning · appraisal · customers · closing",
        color("SHOP STATUS", MUTED) + "  " + color("stable", GREEN) + "    " + color("WARDING", MUTED) + "  " + color("weak", YELLOW),
    ], CYAN)
    lines.append("")
    lines += panel("TODAY'S LEDGER", [
        color("1", YELLOW, True) + "  " + color("Suppliers", PAPER) + "        Review incoming lots",
        color("2", YELLOW, True) + "  " + color("Inventory", PAPER) + "        Inspect and manage artifacts",
        color("3", YELLOW, True) + "  " + color("Open the shop", PAPER) + "    Meet today's customers",
        color("4", YELLOW, True) + "  " + color("Research", PAPER) + "         Spend time to reveal properties",
        color("5", YELLOW, True) + "  " + color("End the day", PAPER) + "      Resolve events and save",
    ], BLUE)
    lines.append("")
    lines += panel("RECENT NOTES", [
        color("•", GREEN) + " A sealed crate arrived before dawn.",
        color("•", PURPLE) + " The Academy is buying navigation relics this week.",
        color("•", RED) + " Do not store unknown cursed items near the front room.",
    ], PURPLE)
    lines += ["", rule(), color("[1-5] choose action   [H] help   [Q] quit", MUTED)]
    print("\n".join(lines))


def help_screen() -> None:
    clear()
    print("\n".join(header(1, 420, 0)))
    print("\n".join(panel("CONTROLS", [
        color("1–5", YELLOW, True) + "  select a shop action",
        color("H", YELLOW, True) + "    show this help",
        color("Q", YELLOW, True) + "    return to desktop / quit",
        "",
        color("Design principle", MUTED),
        "Information is valuable, but never free. Every appraisal costs time, gold, or trust.",
    ], CYAN)))
    input("\nPress Enter to return...")
