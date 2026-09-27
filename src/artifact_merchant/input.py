"""Tiny cross-platform command line editor with Tab completion."""
from __future__ import annotations

import os
import sys

from .commands import HELP


def _complete(prefix: str) -> list[str]:
    word = prefix.split()[-1] if prefix.split() else ""
    return [name for name in HELP if name.startswith(word)]


def read_command(prompt: str = "> ") -> str:
    """Read one line and complete command names with Tab."""
    if os.name != "nt":
        try:
            import readline
            readline.set_completer(lambda text, state: (_complete(text) + [None])[state])
            readline.parse_and_bind("tab: complete")
        except ImportError:
            pass
        return input(prompt)

    import msvcrt
    sys.stdout.write(prompt)
    sys.stdout.flush()
    text = ""
    matches: list[str] = []
    match_index = 0
    while True:
        key = msvcrt.getwch()
        if key in ("\r", "\n"):
            print()
            return text
        if key == "\003":
            raise KeyboardInterrupt
        if key == "\x08":
            if text:
                text = text[:-1]
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            matches = []
            continue
        if key == "\t":
            if not matches:
                matches = _complete(text)
                match_index = 0
            if matches:
                replacement = matches[match_index % len(matches)]
                match_index += 1
                typed = text.split()[-1] if text.split() else ""
                suffix = replacement[len(typed):]
                text += suffix
                sys.stdout.write(suffix)
                sys.stdout.flush()
            continue
        if key in ("\x00", "\xe0"):
            msvcrt.getwch()  # ignore function/arrows for now
            continue
        if key.isprintable():
            text += key
            sys.stdout.write(key)
            sys.stdout.flush()
            matches = []
