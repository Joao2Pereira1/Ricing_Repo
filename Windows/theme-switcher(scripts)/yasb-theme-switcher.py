#!/usr/bin/env python3
"""
YASB Theme Switcher
Corre em: python yasb-theme-switcher.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
THEMES_DIR = Path(r"C:\Backup\03_Themes_And_UI\yasb themes")
TARGET_CSS = Path(r"C:\Users\João Pereira\.config\yasb\styles.css")
BACKUP_DIR = TARGET_CSS.parent / "backups"

# Candidatos para o executável do YASB (adiciona o teu se não estiver aqui)
YASB_PATHS = [
    Path(r"C:\Users\João Pereira\AppData\Local\Programs\yasb\yasb.exe"),
    Path(r"C:\Program Files\yasb\yasb.exe"),
    Path(r"C:\Users\João Pereira\scoop\apps\yasb\current\yasb.exe"),
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

MAX_VISIBLE = 14

# ── Terminal helpers ────────────────────────────────────────────────────────────
def enable_ansi():
    """Activa ANSI no Windows terminal."""
    if sys.platform == "win32":
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        kernel.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING

def hide_cursor():  print("\033[?25l", end="", flush=True)
def show_cursor():  print("\033[?25h", end="", flush=True)
def clear_screen(): print("\033[2J\033[H", end="", flush=True)
def move_up(n):     print(f"\033[{n}A", end="", flush=True)
def clear_line():   print("\033[2K", end="", flush=True)

# ── Leitura de teclas (Windows nativo via msvcrt) ──────────────────────────────
if sys.platform == "win32":
    import msvcrt

    def read_key():
        """Lê uma tecla. Devolve string: char normal, 'UP', 'DOWN', 'ENTER', 'ESC', 'BACKSPACE'."""
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):   # tecla especial (setas, F-keys, etc.)
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'UP'
            if ch2 == 'P': return 'DOWN'
            return None
        if ch == '\r':  return 'ENTER'
        if ch == '\x1b': return 'ESC'
        if ch in ('\x08', '\x7f'): return 'BACKSPACE'
        return ch
else:
    # Fallback Unix (para testar no Linux/Mac)
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
            if ch == '\r' or ch == '\n': return 'ENTER'
            if ch in ('\x08', '\x7f'): return 'BACKSPACE'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── Fuzzy match ────────────────────────────────────────────────────────────────
def fuzzy_match(query: str, text: str) -> bool:
    if not query:
        return True
    q = query.lower()
    t = text.lower()
    pos = 0
    for ch in q:
        idx = t.find(ch, pos)
        if idx == -1:
            return False
        pos = idx + 1
    return True

# ── Render ─────────────────────────────────────────────────────────────────────
_rendered_lines = 0

def render(filtered: list[Path], selected: int, scroll: int, query: str, total: int):
    global _rendered_lines

    lines = []

    lines.append(f"{TITLE}  ╔═══════════════════════════════════════════════╗{R}")
    lines.append(f"{TITLE}  ║   ⚡  YASB Theme Switcher                     ║{R}")
    lines.append(f"{TITLE}  ╚═══════════════════════════════════════════════╝{R}")
    lines.append("")
    lines.append(f"  {CYAN}🔍 Pesquisar:{R} {query}{YELLOW}▌{R}   {DIM}({len(filtered)}/{total} temas){R}")
    lines.append(f"  {BORDER}{'─' * 49}{R}")

    count = len(filtered)
    if count == 0:
        lines.append(f'  {DIM}  (sem resultados para "{query}"){R}')
        for _ in range(MAX_VISIBLE - 1):
            lines.append("")
    else:
        for i in range(MAX_VISIBLE):
            idx = scroll + i
            if idx >= count:
                lines.append("")
                continue
            name = filtered[idx].stem
            if idx == selected:
                lines.append(f"  {SEL_BG} ▶  {name:<44} {R}")
            else:
                lines.append(f"  {DIM}   {R}{name:<44}")

    if count > MAX_VISIBLE:
        end = min(scroll + MAX_VISIBLE, count)
        lines.append(f"  {DIM}  ↑↓ scroll  [{scroll+1}–{end} de {count}]{R}")
    else:
        lines.append("")

    lines.append(f"  {BORDER}{'─' * 49}{R}")
    lines.append(f"  {DIM}[↑↓] navegar   [Enter] aplicar   [Esc/q] sair{R}")

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

# ── Aplicar tema ───────────────────────────────────────────────────────────────
def apply_theme(src: Path):
    show_cursor()
    clear_screen()

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if TARGET_CSS.exists():
        shutil.copy2(TARGET_CSS, BACKUP_DIR / f"styles_backup_{ts}.css")

    try:
        shutil.copy2(src, TARGET_CSS)
    except Exception as e:
        print(f"\n  {RED}✗ Erro ao copiar o tema:{R} {e}")
        print(f"  {DIM}  Fonte  : {src}{R}")
        print(f"  {DIM}  Destino: {TARGET_CSS}{R}\n")
        return

    print(f"\n  {GREEN}✔  Tema aplicado com sucesso!{R}\n")
    print(f"  {CYAN}  Tema  :{R}  {src.stem}.css")
    print(f"  {CYAN}  Backup:{R}  {DIM}{BACKUP_DIR / f'styles_backup_{ts}.css'}{R}\n")

    answer = input(f"  {YELLOW}Recarregar YASB agora? [s/N]:{R} ").strip().lower()
    if answer == "s":
        print(f"  {DIM}A fechar YASB...{R}")
        subprocess.run(["taskkill", "/F", "/IM", "yasb.exe"],
                       capture_output=True)
        import time; time.sleep(1)

        yasb_exe = None
        for p in YASB_PATHS:
            if p.exists():
                yasb_exe = p
                break
        # fallback: PATH
        if not yasb_exe:
            import shutil as sh
            found = sh.which("yasb.exe") or sh.which("yasb")
            if found:
                yasb_exe = Path(found)

        if yasb_exe:
            subprocess.Popen([str(yasb_exe)],
                             creationflags=subprocess.DETACHED_PROCESS
                             if sys.platform == "win32" else 0)
            print(f"  {GREEN}✔  YASB reiniciado.{R}")
        else:
            print(f"  {YELLOW}⚠  Executável não encontrado. Adiciona o path em YASB_PATHS no script.{R}")
    print()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    enable_ansi()
    hide_cursor()

    # Carrega temas
    all_themes = sorted(THEMES_DIR.rglob("*.css"))
    if not all_themes:
        show_cursor()
        print(f"{RED}✗ Nenhum .css encontrado em: {THEMES_DIR}{R}")
        sys.exit(1)

    query    = ""
    selected = 0
    scroll   = 0
    filtered = all_themes[:]

    def refilter():
        nonlocal filtered, selected, scroll
        filtered = [t for t in all_themes if fuzzy_match(query, t.stem)]
        selected = 0
        scroll   = 0

    try:
        render(filtered, selected, scroll, query, len(all_themes))

        while True:
            key = read_key()
            if key is None:
                continue

            count = len(filtered)

            if key == 'UP':
                if selected > 0:
                    selected -= 1
                    if selected < scroll:
                        scroll = selected

            elif key == 'DOWN':
                if selected < count - 1:
                    selected += 1
                    if selected >= scroll + MAX_VISIBLE:
                        scroll = selected - MAX_VISIBLE + 1

            elif key == 'ENTER':
                if filtered:
                    show_cursor()
                    apply_theme(filtered[selected])
                    sys.exit(0)

            elif key in ('ESC', 'q', 'Q'):
                show_cursor()
                clear_screen()
                sys.exit(0)

            elif key == 'BACKSPACE':
                if query:
                    query = query[:-1]
                    refilter()

            elif isinstance(key, str) and key.isprintable() and len(key) == 1:
                query += key
                refilter()

            else:
                continue

            render(filtered, selected, scroll, query, len(all_themes))

    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
        sys.exit(0)

if __name__ == "__main__":
    main()