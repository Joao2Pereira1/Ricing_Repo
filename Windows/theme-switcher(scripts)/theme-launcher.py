#!/usr/bin/env python3
"""
Theme Launcher — menu central para todos os theme switchers
Corre em: python theme-launcher.py
"""

import os
import sys
import subprocess
from pathlib import Path

# ── Paths dos switchers ────────────────────────────────────────────────────────
SWITCHERS_DIR = Path(r"C:\Backup\Theme Switcher")  # ajusta se necessário

SWITCHERS = [
    {
        "label":  "VSCode",
        "icon":   "💻",
        "desc":   "CSS injection + internal theme",
        "script": SWITCHERS_DIR / "vscode-theme-switcher.py",
    },
    {
        "label":  "Windows Terminal",
        "icon":   "⬛",
        "desc":   "Color scheme for all profiles",
        "script": SWITCHERS_DIR / "terminal-theme-switcher.py",
    },
    {
        "label":  "YASB",
        "icon":   "⚡",
        "desc":   "Status bar CSS theme",
        "script": SWITCHERS_DIR / "yasb-theme-switcher.py",
    },
    {
        "label":  "Nilesoft Shell",
        "icon":   "🐚",
        "desc":   "Context menu theme (.nss)",
        "script": SWITCHERS_DIR / "nilesoft-theme-switcher.py",
    },
    {
        "label":  "Komorebi",
        "icon":   "🪟",
        "desc":   "Window border color",
        "script": SWITCHERS_DIR / "komorebic-theme-switcher.py",
    },
    {
        "label":  "Apply All",
        "icon":   "🎨",
        "desc":   "Run every switcher in sequence",
        "script": None,   # tratado à parte
    },
]

# ── ANSI ───────────────────────────────────────────────────────────────────────
R      = "\033[0m"
BOLD   = "\033[1m"
SEL_BG = "\033[48;5;24m\033[1;97m"
TITLE  = "\033[1;38;5;39m"
DIM    = "\033[38;5;242m"
GREEN  = "\033[1;38;5;82m"
RED    = "\033[1;38;5;196m"
YELLOW = "\033[1;38;5;220m"
CYAN   = "\033[38;5;51m"
BORDER = "\033[38;5;240m"
PURPLE = "\033[38;5;141m"

# ── Terminal helpers ────────────────────────────────────────────────────────────
def enable_ansi():
    if sys.platform == "win32":
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        kernel.SetConsoleMode(handle, mode.value | 0x0004)

def hide_cursor(): print("\033[?25l", end="", flush=True)
def show_cursor(): print("\033[?25h", end="", flush=True)
def clear_screen(): print("\033[2J\033[H", end="", flush=True)

# ── Leitura de teclas ──────────────────────────────────────────────────────────
if sys.platform == "win32":
    import msvcrt

    def read_key():
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'UP'
            if ch2 == 'P': return 'DOWN'
            return None
        if ch == '\r':   return 'ENTER'
        if ch == '\x1b': return 'ESC'
        return ch
else:
    import tty, termios

    def read_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
                return 'ESC'
            if ch in ('\r', '\n'): return 'ENTER'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── Render ─────────────────────────────────────────────────────────────────────
_rendered_lines = 0

def render(selected: int):
    global _rendered_lines

    lines = []
    lines.append(f"{TITLE}  ╔═══════════════════════════════════════════════╗{R}")
    lines.append(f"{TITLE}  ║   🎨  Theme Launcher                          ║{R}")
    lines.append(f"{TITLE}  ╚═══════════════════════════════════════════════╝{R}")
    lines.append("")

    for i, s in enumerate(SWITCHERS):
        is_apply_all = s["script"] is None
        script_exists = is_apply_all or Path(s["script"]).exists()
        status = f"{DIM}[não encontrado]{R}" if not script_exists else ""

        if is_apply_all:
            # destaca o Apply All
            if i == selected:
                row = f"  {SEL_BG} {s['icon']}  {s['label']:<20} {DIM}{s['desc']}{R}{SEL_BG}  {R}"
            else:
                row = f"  {PURPLE}   {s['icon']}  {BOLD}{s['label']:<20}{R}  {DIM}{s['desc']}{R}"
        else:
            if i == selected:
                row = f"  {SEL_BG} {s['icon']}  {s['label']:<20} {DIM}{s['desc']}{R}{SEL_BG}  {R}"
            else:
                row = f"  {DIM}   {R}{s['icon']}  {s['label']:<20}  {DIM}{s['desc']}{R}  {status}"

        lines.append(row)

    lines.append("")
    lines.append(f"  {BORDER}{'─' * 49}{R}")
    lines.append(f"  {DIM}[↑↓] navegar   [Enter] selecionar   [Esc/q] sair{R}")

    out = []
    if _rendered_lines == 0:
        out.append("\033[2J\033[H")
        _rendered_lines = len(lines)
    else:
        out.append(f"\033[{_rendered_lines}A")

    for line in lines:
        out.append(f"\033[2K{line}\n")

    sys.stdout.write("".join(out))
    sys.stdout.flush()

# ── Lançar switcher ────────────────────────────────────────────────────────────
def launch(script: Path):
    show_cursor()
    clear_screen()
    try:
        subprocess.run([sys.executable, str(script)])
    except FileNotFoundError:
        print(f"\n  {RED}✗ Script não encontrado:{R} {script}\n")
        input("  Enter para voltar...")
    except KeyboardInterrupt:
        pass

def apply_all():
    show_cursor()
    clear_screen()

    all_scripts = [s for s in SWITCHERS if s["script"] is not None]

    print(f"\n  {TITLE}🎨  Apply All — {len(all_scripts)} switchers{R}\n")
    print(f"  {DIM}Vai executar cada switcher um a um.{R}")
    print(f"  {DIM}Cancela qualquer um com Esc/q para avançar.{R}\n")
    print(f"  {BORDER}{'─' * 49}{R}\n")

    for s in all_scripts:
        script = Path(s["script"])
        if not script.exists():
            print(f"  {YELLOW}⚠  {s['label']}: script não encontrado, a saltar.{R}")
            continue

        input(f"  {CYAN}▶  {s['icon']}  {s['label']}{R}  {DIM}— Enter para continuar...{R}")
        launch(script)

    clear_screen()
    print(f"\n  {GREEN}✔  Apply All concluído!{R}\n")
    input(f"  {DIM}Enter para voltar ao menu...{R}")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    enable_ansi()
    hide_cursor()

    selected = 0

    try:
        render(selected)

        while True:
            key = read_key()
            if key is None:
                continue

            if key == 'UP':
                if selected > 0:
                    selected -= 1

            elif key == 'DOWN':
                if selected < len(SWITCHERS) - 1:
                    selected += 1

            elif key == 'ENTER':
                s = SWITCHERS[selected]
                hide_cursor()

                if s["script"] is None:
                    # Apply All
                    apply_all()
                else:
                    script = Path(s["script"])
                    if not script.exists():
                        show_cursor()
                        clear_screen()
                        print(f"\n  {RED}✗ Script não encontrado:{R}\n  {script}\n")
                        input("  Enter para voltar...")
                    else:
                        launch(script)

                # volta ao menu
                global _rendered_lines
                _rendered_lines = 0
                hide_cursor()
                render(selected)

            elif key in ('ESC', 'q', 'Q'):
                show_cursor()
                clear_screen()
                sys.exit(0)

            else:
                render(selected)
                continue

            render(selected)

    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
        sys.exit(0)

if __name__ == "__main__":
    main()
