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
    result = [color(fit(f"┌─ {title} " + "─" * max(0, inner - len(title) - 3) + "┐", width()), tone)]
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
    top = "┌─ " + title + " " + "─" * max(0, inner - len(title) - 3) + "┐"
    result = [color(fit(top, box_width), tone)]
    for row in rows:
        result.append(color("│ ", tone) + fit(row, inner) + color(" │", tone))
    result.append(color("└" + "─" * (box_width - 2) + "┘", tone))
    return result


def _row(number: str, icon: str, name: str, weight: str, value: str, rarity: str, rarity_color: str) -> str:
    return (color(f"{number:>2} ", MUTED) + color(icon, PAPER) + " "
            + f"{name:<22} {weight:>4}  {value:>9}  " + color(rarity, rarity_color))


def dashboard(day: int = 42, gold: int = 248750, reputation: int = 68) -> None:
    """Render the main workstation in the style of the supplied mockup."""
    clear()
    w = width()
    compact = w < 112
    left_w = (w - 5) // 2 if not compact else w
    right_w = w - left_w - 3 if not compact else w
    lines = [
        color("  ARTIFACT TRADING TERMINAL", CYAN, True)
        + color("    Покупка   //   Продажа   //   Исследование   //   Расширение влияния", PAPER),
        color("  Локация: ", MUTED) + color("Орбитальная станция «Гелиос»", GREEN)
        + color("   |   День: ", MUTED) + color(str(day), PAPER)
        + color("   |   Кредиты: ", MUTED) + color(f"{gold:,} кр.", GREEN)
        + color("   |   Репутация: ", MUTED) + color(f"{reputation}", GREEN),
        rule(),
    ]
    inventory = [
        color("#    Предмет                    Вес   Ценность  Редкость", MUTED),
        _row("1", "◇", "Осколок Пустоты", "0.5", "12,000", "Легендарный", YELLOW),
        _row("2", "✥", "Древний Компас", "1.2", "8,500", "Редкий", BLUE),
        _row("3", "◈", "Коготь Наблюдателя", "0.8", "6,200", "Необычный", GREEN),
        _row("4", "✧", "Сердце Пепла", "1.5", "9,800", "Редкий", BLUE),
        _row("5", "♢", "Шепчущий Идол", "0.7", "15,000", "Эпический", PURPLE),
        _row("6", "◎", "Квантовый Стабилизатор", "2.1", "22,000", "Обычный", PAPER),
    ]
    market = [
        color("Предмет                       Покупка     Продажа   Спрос", MUTED),
        color("◇  Осколок Пустоты", YELLOW) + "             420,000    " + color("575,000", GREEN) + "   ▲▲▲",
        "✥  Древний Компас              95,000    " + color("132,000", GREEN) + "   ▲▲",
        "◈  Слеза Архонта              210,000    " + color("295,000", GREEN) + "   ▲▲▲",
        "◈  Коготь Наблюдателя          48,000    " + color("71,000", GREEN) + "   ▼",
        "✧  Сердце Пепла               110,000    " + color("160,000", GREEN) + "   ▲▲",
        "♢  Шепчущий Идол              250,000    " + color("340,000", GREEN) + "   ▲▲",
    ]
    inspection = [
        color("Осколок Пустоты", YELLOW, True) + "                 " + color("Легендарный", YELLOW),
        rule("·")[:max(1, right_w - 2)],
        "      /\\        " + color("Вес:", MUTED) + "                  0.5 кг",
        "     /  \\       " + color("Базовая ценность:", MUTED) + "     " + color("575,000 кр.", GREEN),
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
        for title, rows, tone in [("ИНВЕНТАРЬ · 6/20", inventory, GREEN), ("РЫНОК АРТЕФАКТОВ", market, CYAN), ("ОСМОТР АРТЕФАКТА", inspection, YELLOW), ("ЛОКАЦИЯ", location, BLUE)]:
            lines += _box(title, rows, w, tone) + [""]
    else:
        top = [_box("ИНВЕНТАРЬ · 6/20", inventory, left_w, GREEN), _box("РЫНОК АРТЕФАКТОВ", market, left_w, CYAN), _box("ОСМОТР АРТЕФАКТА", inspection, right_w, YELLOW)]
        for a, b in zip(top[0], top[2]): lines.append(fit(a, left_w) + "  " + b)
        lines.append("")
        for a, b in zip(top[1], _box("ЛОКАЦИЯ", location, right_w, BLUE)): lines.append(fit(a, left_w) + "  " + b)
        lines.append("")
    journal = [color("Время       Операция       Предмет                  Цена        Итог", MUTED), "[14:12]     " + color("Продажа", GREEN) + "        Сердце Пепла             158,000     " + color("+158,000", GREEN), "[13:47]     " + color("Покупка", GREEN) + "        Коготь Наблюдателя        46,000     " + color("-92,000", RED), "[12:31]     " + color("Продажа", GREEN) + "        Древний Компас            128,000     " + color("+128,000", GREEN)]
    lines += _box("ЖУРНАЛ СДЕЛОК", journal, w, BLUE)
    lines += ["", color("[1] Инвентарь   [2] Рынок   [3] Контракты   [4] Аукцион   [5] Склад   [6] Локация   [I] Осмотр   [H] Помощь   [Q] Выход", GREEN), color("> buy void_shard ▮", GREEN, True)]
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
