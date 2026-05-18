#!/usr/bin/env python3

import json
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# PATH
# ─────────────────────────────────────────────

KOMOREBI_CONFIG = Path(
    r"C:\Users\João Pereira\komorebi.json"
)

BACKUP_DIR = Path(
    r"C:\Backup\Theme Switcher\komorebi"
)

# ─────────────────────────────────────────────
# THEMES (ONLY BORDER COLORS)
# ─────────────────────────────────────────────

THEMES = {
    "Dracula": "#bd93f9",
    "Nord": "#88c0d0",
    "Tokyo Night": "#7aa2f7",
    "Monokai Pro": "#fd5e53",
    "Crimson Blood": "#ff0033",
    "Rose Pine": "#ebbcba",
    "Apricot Dusk": "#ffb38a",
    "Apricot Ember": "#ff7a45",
    "Synthwave": "#ff00ff",
    "Everforest": "#a7c080",
    "Kanagawa": "#7e9cd8",
    "Gruvbox Dark": "#fabd2f",
    "Neon Abyss": "#00ff99"
}

THEME_KEYS = list(THEMES.keys())

# ─────────────────────────────────────────────
# ANSI UI
# ─────────────────────────────────────────────

R = "\033[0m"
CYAN = "\033[38;5;51m"
YELLOW = "\033[1;38;5;220m"
GREEN = "\033[1;38;5;82m"
RED = "\033[1;38;5;196m"

# ─────────────────────────────────────────────
# KOMOREBI RESTART (OPTIONAL BUT USEFUL)
# ─────────────────────────────────────────────

def restart_komorebi():
    try:
        subprocess.run(["komorebic", "stop", "--whkd"], check=True)
        subprocess.run(["komorebic", "start", "--whkd"], check=True)
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────
# APPLY BORDER COLOR
# ─────────────────────────────────────────────

def apply_border(color: str, name: str):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # backup
        if KOMOREBI_CONFIG.exists():
            shutil.copy2(
                KOMOREBI_CONFIG,
                BACKUP_DIR / f"komorebi_{ts}.json"
            )

        # load json
        data = json.loads(KOMOREBI_CONFIG.read_text(encoding="utf-8"))

        # change ONLY border color
        data["border_colours"]["single"] = color

        # save
        KOMOREBI_CONFIG.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        # restart komorebi so it applies instantly
        restart_komorebi()

        return True, name, color

    except Exception as e:
        return False, None, str(e)

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

def print_menu(selected: int):
    print("\033[2J\033[H")
    print(f"\n{CYAN}Komorebi Border Color Switcher{R}\n")

    for i, name in enumerate(THEME_KEYS):
        prefix = "▶" if i == selected else " "
        color = YELLOW if i == selected else R
        print(f" {color}{prefix} {name}{R}")

    print(f"\n{CYAN}↑↓ navegar | Enter aplicar | Esc sair{R}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    selected = 0

    while True:
        print_menu(selected)

        import msvcrt
        key = msvcrt.getwch()

        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()

            if key == "H":
                selected = max(0, selected - 1)

            elif key == "P":
                selected = min(len(THEME_KEYS) - 1, selected + 1)

        elif key == "\r":
            name = THEME_KEYS[selected]
            color = THEMES[name]

            ok, theme, msg = apply_border(color, name)

            print("\033[2J\033[H")

            if ok:
                print(f"\n{GREEN}✔ Aplicado:{R} {theme} -> {msg}\n")
            else:
                print(f"\n{RED}✗ Erro:{R} {msg}\n")

            input("Enter para sair...")
            break

        elif key == "\x1b":
            break


if __name__ == "__main__":
    main()
