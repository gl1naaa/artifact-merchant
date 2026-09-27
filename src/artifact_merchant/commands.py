"""Safe command language for the terminal game and .am scripts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex

HELP = {
    "help": "показать команды",
    "inventory": "показать инвентарь",
    "market": "открыть рынок",
    "inspect <id>": "осмотреть артефакт",
    "buy <id>": "купить предмет с рынка",
    "sell <id>": "выставить предмет на продажу",
    "research <id>": "исследовать неизвестное свойство",
    "location": "информация о локации",
    "clear": "очистить экран",
    "script <file>": "выполнить .am-файл построчно",
    "quit": "выйти из игры",
}


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[str, ...] = ()


def parse(line: str) -> Command:
    try:
        parts = shlex.split(line, comments=True, posix=True)
    except ValueError:
        return Command("__parse_error__")
    if not parts:
        return Command("")
    return Command(parts[0].lower(), tuple(parts[1:]))


def load_script(path: str, root: Path | None = None) -> list[Command]:
    """Load only game commands; comments and blank lines are ignored."""
    target = Path(path)
    if root is not None:
        target = (root / target).resolve()
        if root.resolve() not in target.parents and target != root.resolve():
            raise ValueError("script must stay inside the scripts directory")
    if target.suffix.lower() != ".am":
        raise ValueError("scripts must use the .am extension")
    return [parse(line) for line in target.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
