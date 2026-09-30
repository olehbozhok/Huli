r"""Форматує Markdown-файли Huli.

Якщо два непорожні рядки тексту йдуть підряд, Markdown зливає їх в один абзац.
Скрипт ставить у кінці першого з них `\` (перенос рядка в рендері)
і прибирає кінцеві пробіли, які теж могли слугувати переносом.
Заголовки, списки, таблиці, цитати й блоки коду не чіпає.

Запуск:
    python format_md.py            # форматувати файли зі списку FILES
    python format_md.py a.md b.md  # форматувати вказані файли
    python format_md.py --check    # лише показати, що змінилося б
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ["consolidated_rules.md", "to_translate.md"]

BREAK = "\\"
BLOCK = re.compile(r"^\s*(#|[-*+] |\d+\. |\||>|```)")


def is_text(line: str) -> bool:
    return bool(line.strip()) and not BLOCK.match(line)


def format_text(text: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    in_code = False
    for i, line in enumerate(lines[:-1]):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if is_text(line) and is_text(lines[i + 1]):
            lines[i] = line.rstrip().rstrip(BREAK).rstrip() + BREAK
    return newline.join(lines)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    names = [a for a in argv if a != "--check"] or FILES
    changed = []
    for name in names:
        path = Path(name) if Path(name).is_absolute() else ROOT / name
        with open(path, encoding="utf-8", newline="") as f:
            old = f.read()
        new = format_text(old)
        if new == old:
            continue
        changed.append(name)
        if not check:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
    verb = "потрібно відформатувати" if check else "відформатовано"
    for name in changed:
        print(f"{verb}: {name}")
    return 1 if check and changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
