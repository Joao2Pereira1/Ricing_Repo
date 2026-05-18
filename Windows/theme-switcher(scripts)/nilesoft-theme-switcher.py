#!/usr/bin/env python3

import sys
import shutil
import subprocess
import time
from pathlib import Path

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────

NILESFT_TARGET = Path(
    r"C:\Program Files\Nilesoft Shell\imports\theme.nss"
)

THEMES_DIR = Path(
    r"C:\Backup\Theme Switcher\nilesoft shell themes"
)

BACKUP_DIR = Path(
    r"C:\Backup\Theme Switcher\nilesoft shell backups"
)

# ─────────────────────────────────────────────
# ANSI (simples)
# ─────────────────────────────────────────────

R = "\033[0m"
GREEN = "\033[1;38;5;82m"
RED = "\033[1;38;5;196m"
CYAN = "\033[38;5;51m"
YELLOW = "\033[1;38;5;220m"

# ─────────────────────────────────────────────
# UTIL
# ─────────────────────────────────────────────

def enable_ansi():
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)

        mode = ctypes.c_ulong()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        kernel.SetConsoleMode(handle, mode.value | 0x0004)

def list_themes():
    return sorted(THEMES_DIR.glob("*.nss"))

def print_menu(themes, selected):
    print("\033[2J\033[H")

    print(f"\n{CYAN}Nilesoft Shell Theme Switcher{R}\n")

    for i, t in enumerate(themes):
        prefix = "▶" if i == selected else " "
        color = YELLOW if i == selected else R
        print(f" {color}{prefix} {t.stem}{R}")

    print(f"\n{CYAN}↑↓ navegar | Enter aplicar | Esc sair{R}")

# ─────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────

def apply_theme(theme_path: Path):

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        if NILESFT_TARGET.exists():
            backup = BACKUP_DIR / "theme_backup.nss"
            shutil.copy2(NILESFT_TARGET, backup)

        shutil.copy2(theme_path, NILESFT_TARGET)

        return True, theme_path.stem

    except PermissionError:
        return False, "Sem permissões (executa como admin)"

    except Exception as e:
        return False, str(e)

def restart_explorer():
    try:
        # mata explorer
        subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        time.sleep(1)

        # relança explorer
        subprocess.Popen("explorer.exe")

        return True, "Explorer reiniciado"

    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():

    enable_ansi()

    themes = list_themes()

    if not themes:
        print("Nenhum tema encontrado.")
        return

    selected = 0

    while True:

        print_menu(themes, selected)

        import msvcrt
        key = msvcrt.getwch()

        if key in ("\x00", "\xe0"):
            key = msvcrt.getwch()

            if key == "H":
                selected = max(0, selected - 1)

            elif key == "P":
                selected = min(len(themes) - 1, selected + 1)

        elif key == "\r":
            ok, msg = apply_theme(themes[selected])

            print("\033[2J\033[H")

            if ok:
                print(f"\n✔ Tema aplicado: {msg}\n")

                ans = input("Reiniciar Explorer para aplicar tema? [S/n]: ").lower()

                if ans in ("", "s", "sim", "y", "yes"):
                    ok2, msg2 = restart_explorer()

                    if ok2:
                        print(f"\n✔ {msg2}\n")
                    else:
                        print(f"\n✗ Erro: {msg2}\n")

            else:
                print(f"\n✗ Erro: {msg}\n")

            input("Enter para sair...")
            break

if __name__ == "__main__":
    main()
