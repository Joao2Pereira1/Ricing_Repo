#!/usr/bin/env python3

import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────

WT_SETTINGS = Path(
    r"C:\Users\João Pereira\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
)

BACKUP_DIR = Path(
    r"C:\Backup\Theme Switcher\windows terminal backups"
)

# ─────────────────────────────────────────────
# THEMES
# ─────────────────────────────────────────────

TERMINAL_THEMES = {
    "Monokai Pro": "Monokai Pro",
    "Ubuntu": "Ubuntu-24.04-ColorScheme",
    "One Half Dark": "One Half Dark",
    "Dracula": "Dracula",
    "Tokyo Night": "Tokyo Night",

    # 🌙 Modern popular themes
    "Catppuccin Mocha": "Catppuccin Mocha",
    "Nord": "Nord",
    "Rose Pine": "Rose Pine",
    "Kanagawa": "Kanagawa",
    "Gruvbox Dark": "Gruvbox Dark",
    "Everforest": "Everforest",

    # ⚡ Neon / Cyber themes
    "Synthwave": "Synthwave",
    "Neon Abyss Pulse": "Neon Abyss Pulse",
    "Neon Abyss Deep": "Neon Abyss Deep",

    # 🟣 Purple / aesthetic themes
    "Amethyst Void": "Amethyst Void",
    "Amethyst Glow": "Amethyst Glow",

    # 🍑 Warm / Apricot tones
    "Apricot Ember": "Apricot Ember",
    "Apricot Dusk": "Apricot Dusk",

    # 🧿 Organic / green dark themes
    "Ant Forest": "Ant Forest",
    "Ant Night Moss": "Ant Night Moss",

    # 🔴 Red / aggressive themes
    "Crimson Blood": "Crimson Blood",

    # 🐧 Ubuntu variants
    "Ubuntu 22.04": "Ubuntu-22.04-ColorScheme",
    "Ubuntu 24.04": "Ubuntu-24.04-ColorScheme"
}

THEME_KEYS = list(TERMINAL_THEMES.keys())

# ─────────────────────────────────────────────
# ANSI COLORS
# ─────────────────────────────────────────────

R = "\033[0m"
GREEN = "\033[1;38;5;82m"
RED = "\033[1;38;5;196m"
CYAN = "\033[38;5;51m"
YELLOW = "\033[1;38;5;220m"

# ─────────────────────────────────────────────
# ANSI ENABLE (Windows)
# ─────────────────────────────────────────────

def enable_ansi():
    if sys.platform == "win32":
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)

        mode = ctypes.c_ulong()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        kernel.SetConsoleMode(handle, mode.value | 0x0004)

# ─────────────────────────────────────────────
# APPLY THEME
# ─────────────────────────────────────────────

TARGET_PROFILES = {
    "Git Bash",
    "PowerShell",
    "Windows PowerShell"
}

POWERSHELL_CORE_SOURCE = "Windows.Terminal.PowershellCore"
POWERSHELL_5_SOURCE = "Microsoft.PowerShell"
GIT_BASH_SOURCE = "Git"


def apply_terminal_theme(theme_name: str):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        if WT_SETTINGS.exists():
            shutil.copy2(
                WT_SETTINGS,
                BACKUP_DIR / f"wt_backup_{ts}.json"
            )

        data = json.loads(WT_SETTINGS.read_text(encoding="utf-8"))

        # ─────────────────────────────
        # 1. defaults
        # ─────────────────────────────
        if "profiles" in data and "defaults" in data["profiles"]:
            data["profiles"]["defaults"]["colorScheme"] = theme_name

        # ─────────────────────────────
        # 2. individual profiles
        # ─────────────────────────────
        for profile in data.get("profiles", {}).get("list", []):
            name = profile.get("name", "")
            source = profile.get("source", "")

            # Git Bash
            if name == "Git Bash" or source == GIT_BASH_SOURCE:
                profile["colorScheme"] = theme_name

            # PowerShell 7 (Windows Terminal Core)
            elif source == POWERSHELL_CORE_SOURCE or name == "PowerShell":
                profile["colorScheme"] = theme_name

            # PowerShell 5 (classic Windows PowerShell)
            elif name == "Windows PowerShell":
                profile["colorScheme"] = theme_name

        # ─────────────────────────────
        # write back
        # ─────────────────────────────
        WT_SETTINGS.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        return True, theme_name

    except PermissionError:
        return False, "Sem permissões (executa como admin)"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

def print_menu(selected: int):
    print("\033[2J\033[H")
    print(f"\n{CYAN}Windows Terminal Theme Switcher{R}\n")

    for i, name in enumerate(THEME_KEYS):
        prefix = "▶" if i == selected else " "
        color = YELLOW if i == selected else R
        print(f" {color}{prefix} {name}{R}")

    print(f"\n{CYAN}↑↓ navegar | Enter aplicar | Esc sair{R}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    enable_ansi()

    selected = 0

    while True:
        print_menu(selected)

        import msvcrt
        key = msvcrt.getwch()

        # setas
        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()

            if key == "H":  # up
                selected = max(0, selected - 1)

            elif key == "P":  # down
                selected = min(len(THEME_KEYS) - 1, selected + 1)

        # enter
        elif key == "\r":
            theme_name = TERMINAL_THEMES[THEME_KEYS[selected]]
            ok, msg = apply_terminal_theme(theme_name)

            print("\033[2J\033[H")

            if ok:
                print(f"\n{GREEN}✔ Tema aplicado:{R} {msg}\n")
            else:
                print(f"\n{RED}✗ Erro:{R} {msg}\n")

            input("Enter para sair...")
            break

        # esc
        elif key == "\x1b":
            break


if __name__ == "__main__":
    main()
