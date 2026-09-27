"""Small dependency-free terminal UI for the first vertical slice."""
from __future__ import annotations

import os
import re
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


_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def color(text: str, tone: str = PAPER, bold: bool = False) -> str:
    return f"{BOLD if bold else ''}{tone}{text}{RESET}"


def visible(text: str) -> int:
    return len(_ANSI.sub("", text))


def fit(text: str, size: int) -> str:
    if visible(text) <= size:
        return text + " " * (size - visible(text))
    return _ANSI.sub("", text)[:max(0, size - 1)] + "…"


def rule(char: str = "─") -> str:
    return color(char * width(), MUTED)


def panel(title: str, rows: list[str], tone: str = CYAN) -> list[str]:
    inner = width() - 4
    result = [color("┌─ " + title + " " + "─" * max(0, width() - len(title) - 5) + "┐", tone)]
    for row in rows:
        result.append(color("│ ", tone) + fit(row, inner) + color(" │", tone))
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


def _box(title: str, rows: list[str], box_width: int, tone: str = CYAN) -> list[str]:
    """A fixed-width box used by the trading terminal dashboard."""
    inner = max(8, box_width - 4)
    top = "┌─ " + title + " " + "─" * max(0, box_width - len(title) - 5) + "┐"
    result = [color(top, tone)]
    for row in rows:
        result.append(color("│ ", tone) + fit(row, inner) + color(" │", tone))
    result.append(color("└" + "─" * (box_width - 2) + "┘", tone))
    return result


def _row(number: str, icon: str, name: str, weight: str, value: str, rarity: str, rarity_color: str) -> str:
    return (color(f"{number:>2} ", MUTED) + color(icon, PAPER) + " "
            + f"{name:<22} {weight:>4}  {value:>9}  " + color(rarity, rarity_color))


def dashboard(state) -> None:
    """Render the workstation from the live game state."""
    clear()
    day, gold, reputation = state.day, state.gold, state.reputation
    w = width()
    compact = w < 112
    left_w = (w - 5) // 2 if not compact else w
    right_w = w - left_w - 2 if not compact else w
    lines = [
        color("  ARTIFACT TRADING TERMINAL", CYAN, True)
        + color("    Покупка   //   Продажа   //   Исследование   //   Расширение влияния", PAPER),
        color("  Локация: ", MUTED) + color("Орбитальная станция «Гелиос»", GREEN)
        + color("   |   День: ", MUTED) + color(str(day), PAPER)
        + color("   |   Кредиты: ", MUTED) + color(f"{gold:,} кр.", GREEN)
        + color("   |   Репутация: ", MUTED) + color(f"{reputation}", GREEN),
        rule(),
    ]
    icons = ["◇", "✥", "◈", "✧", "♢", "◎"]
    rarity_tones = {"легендарный": YELLOW, "эпический": PURPLE, "редкий": BLUE, "необычный": GREEN}
    inventory = [color("#    Предмет                    Вес   Ценность  Редкость", MUTED)]
    for index, item in enumerate(state.inventory, 1):
        inventory.append(_row(str(index), icons[(index - 1) % len(icons)], item.name,
                              f"{item.weight:.1f}", f"{item.sell_price:,}", item.rarity,
                              rarity_tones.get(item.rarity, PAPER)))
    if not state.inventory:
        inventory.append(color("(пусто — купите первый артефакт на рынке)", MUTED))
    market = [color("Предмет                       Покупка     Продажа   Спрос", MUTED)]
    for item in state.market:
        market.append(color(f"{item.id:<27}", YELLOW if item.rarity == "легендарный" else PAPER)
                      + f" {item.buy_price:>9,}    " + color(f"{item.sell_price:>9,}", GREEN) + "   ▲")
    if not state.market:
        market.append(color("(рынок пуст)", MUTED))
    selected = state.inventory[0] if state.inventory else (state.market[0] if state.market else None)
    selected_name = selected.name if selected else "Нет выбранного артефакта"
    selected_rarity = selected.rarity if selected else "—"
    selected_weight = f"{selected.weight:.1f} кг" if selected else "—"
    selected_value = f"{selected.sell_price:,} кр." if selected else "—"
    inspection = [
        color(selected_name, YELLOW, True) + "                 " + color(selected_rarity, YELLOW),
        rule("·")[:max(1, right_w - 2)],
        "      /\\        " + color("Вес:", MUTED) + f"                  {selected_weight}",
        "     /  \\       " + color("Базовая ценность:", MUTED) + "     " + color(selected_value, GREEN),
        "    / .  \\      " + color("Радиация:", MUTED) + "          +3 ед.",
        "    \\  . /      " + color("Стабильность:", MUTED) + "       27%",
        "     \\__/       " + color("Энергия:", MUTED) + "          87.4 ТэВ",
        "                 " + color("Происхождение:", MUTED) + "    Неизвестно",
        "                 " + color("Состояние:", MUTED) + "        " + color("Стабильное", GREEN),
        rule("·")[:max(1, right_w - 2)],
        color("Особенности:", PAPER),
        "- Искажает локальное пространство",
        "- Реагирует на сознание наблюдателя",
        "- Интересен для нескольких фракций",
    ]
    location = ["Орбитальная станция «Гелиос»", "", "Фракция:        Союз Торговцев", "Тип:             Торговый хаб", "Услуги:          Рынок, Аукцион, Склад", "Особенность:     Нейтральная территория"]
    if compact:
        for title, rows, tone in [(f"ИНВЕНТАРЬ · {len(state.inventory)}/20", inventory, GREEN), ("РЫНОК АРТЕФАКТОВ", market, CYAN), ("ОСМОТР АРТЕФАКТА", inspection, YELLOW), ("ЛОКАЦИЯ", location, BLUE)]:
            lines += _box(title, rows, w, tone) + [""]
    else:
        top = [_box(f"ИНВЕНТАРЬ · {len(state.inventory)}/20", inventory, left_w, GREEN), _box("РЫНОК АРТЕФАКТОВ", market, left_w, CYAN), _box("ОСМОТР АРТЕФАКТА", inspection, right_w, YELLOW)]
        right_top = _box("ОСМОТР АРТЕФАКТА", inspection, right_w, YELLOW)
        for i in range(max(len(top[0]), len(right_top))):
            a = top[0][i] if i < len(top[0]) else ""
            b = right_top[i] if i < len(right_top) else ""
            lines.append(fit(a, left_w) + "  " + b)
        lines.append("")
        right_bottom = _box("ЛОКАЦИЯ", location, right_w, BLUE)
        for i in range(max(len(top[1]), len(right_bottom))):
            a = top[1][i] if i < len(top[1]) else ""
            b = right_bottom[i] if i < len(right_bottom) else ""
            lines.append(fit(a, left_w) + "  " + b)
        lines.append("")
    journal = [color("События", MUTED)] + ["• " + entry for entry in state.journal[-5:]]
    lines += _box("ЖУРНАЛ СОБЫТИЙ", journal, w, BLUE)
    lines += ["", color("inventory   market   inspect <id>   buy <id>   sell <id>   help   quit", GREEN), color("> ", GREEN, True)]
    print("\n".join(lines))


def help_screen() -> None:
    clear()
    print("\n".join(header(1, 420, 0)))
    print("\n".join(panel("CONTROLS", [
        color("inventory", YELLOW, True) + "  show your artifacts",
        color("market", YELLOW, True) + "     open the artifact market",
        color("inspect <id>", YELLOW, True) + " examine a lot",
        color("buy / sell", YELLOW, True) + " trade by command",
        color("research <id>", YELLOW, True) + " reveal a property",
        color("script <file>", YELLOW, True) + " run a .am command script",
        color("help / quit", YELLOW, True) + " help or exit",
        "",
        color("Design principle", MUTED),
        "Information is valuable, but never free. Every appraisal costs time, gold, or trust.",
    ], CYAN)))
    input("\nPress Enter to return...")
