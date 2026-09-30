r"""Format the Huli Markdown files.

Markdown joins two adjacent non-empty text lines into one paragraph.
The script ends the first of them with `\` (a rendered line break)
and strips trailing spaces that may have served as a break.
Headings, lists, tables, quotes and code blocks are left untouched.

Usage:
    python format_md.py            # format the files listed in FILES
    python format_md.py a.md b.md  # format the given files
    python format_md.py --check    # only report what would change
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
    verb = "needs formatting" if check else "formatted"
    for name in changed:
        print(f"{verb}: {name}")
    return 1 if check and changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
