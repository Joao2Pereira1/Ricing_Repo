#!/usr/bin/env python3
"""
VSCode Theme Switcher
Corre em: python vscode-theme-switcher.py

Painel esquerdo : escolhe o ficheiro CSS (injectado via extensão)
                  → substitui o bloco :root em VSC_Costumization.css

Painel direito  : escolhe o tema interno do VSCode
                  → edita "workbench.colorTheme" em settings.json

NOTA:
Depois de aplicar o tema:
Ctrl + Shift + P → "Reload Window"
"""

import re
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
CSS_THEMES_DIR = Path(r"C:\Backup\03_Themes_And_UI\vscode_themes")

TARGET_CSS = Path(r"C:\Code\VSC_Costumization.css")

VSCODE_SETTINGS = Path(
    r"C:\Users\João Pereira\AppData\Roaming\Code\User\settings.json"
)

BACKUP_DIR = Path(r"C:\Backup\03_Themes_And_UI\vscode backups")

# ── Temas internos VSCode ─────────────────────────────────────────────────────
VSCODE_THEMES: dict[str, str] = {
    "Dracula": "Dracula Theme",
    "Dracula Soft": "Dracula Theme Soft",
    "One Dark Pro": "One Dark Pro",
    "One Dark Pro Flat": "One Dark Pro Flat",
    "One Dark Pro Mix": "One Dark Pro Mix",
    "GitHub Dark": "GitHub Dark",
    "GitHub Dark Dimmed": "GitHub Dark Dimmed",
    "GitHub Light": "GitHub Light",
    "Catppuccin Mocha": "Catppuccin Mocha",
    "Catppuccin Macchiato": "Catppuccin Macchiato",
    "Catppuccin Frappe": "Catppuccin Frappe",
    "Catppuccin Latte": "Catppuccin Latte",
    "Tokyo Night": "Tokyo Night",
    "Tokyo Night Storm": "Tokyo Night Storm",
    "Tokyo Night Light": "Tokyo Night Light",
    "Monokai Pro": "Monokai Pro",
    "Monokai Pro Spectrum": "Monokai Pro (Filter Spectrum)",
    "Monokai Pro Octagon": "Monokai Pro (Filter Octagon)",
    "Nord": "Nord",
    "Gruvbox Dark Hard": "Gruvbox Dark Hard",
    "Gruvbox Dark Medium": "Gruvbox Dark Medium",
    "Gruvbox Light Medium": "Gruvbox Light Medium",
    "Ayu Dark": "Ayu Dark",
    "Ayu Mirage": "Ayu Mirage",
    "Ayu Light": "Ayu Light",
    "Solarized Dark": "Solarized Dark",
    "Solarized Light": "Solarized Light",
    "Material Theme": "Material Theme",
    "Material Theme Darker": "Material Theme Darker",
    "Material Palenight": "Material Theme Palenight",
    "Cobalt2": "Cobalt2",
    "Night Owl": "Night Owl",
    "Night Owl Light": "Night Owl (No Italics)",
    "Panda Syntax": "Panda Syntax",
    "Shades of Purple": "Shades of Purple",
    "Synthwave '84": "SynthWave '84",
    "Horizon": "Horizon",
    "Atom One Dark": "Atom One Dark",
    "Atom One Light": "Atom One Light",
    "Default Dark+": "Default Dark+",
    "Default Light+": "Default Light+",
    "High Contrast": "Default High Contrast",
}

# ── ANSI ───────────────────────────────────────────────────────────────────────
R = "\033[0m"
GREEN = "\033[1;38;5;82m"
RED = "\033[1;38;5;196m"
YELLOW = "\033[1;38;5;220m"
CYAN = "\033[38;5;51m"
TITLE = "\033[1;38;5;39m"
SEL = "\033[48;5;24m\033[1;97m"
DIM = "\033[38;5;242m"

MAX_VISIBLE = 16

# ─────────────────────────────────────────────────────────────
# ANSI ENABLE
# ─────────────────────────────────────────────────────────────

def enable_ansi():
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)

        mode = ctypes.c_ulong()

        kernel.GetConsoleMode(
            handle,
            ctypes.byref(mode)
        )

        kernel.SetConsoleMode(
            handle,
            mode.value | 0x0004
        )

# ─────────────────────────────────────────────────────────────
# KEY INPUT
# ─────────────────────────────────────────────────────────────

import msvcrt

def read_key():
    ch = msvcrt.getwch()

    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()

        if ch2 == "H":
            return "UP"

        if ch2 == "P":
            return "DOWN"

    if ch == "\r":
        return "ENTER"

    if ch == "\x1b":
        return "ESC"

    if ch in ("\x08", "\x7f"):
        return "BACKSPACE"

    return ch

# ─────────────────────────────────────────────────────────────
# FUZZY
# ─────────────────────────────────────────────────────────────

def fuzzy_match(query, text):

    if not query:
        return True

    query = query.lower()
    text = text.lower()

    pos = 0

    for ch in query:
        idx = text.find(ch, pos)

        if idx == -1:
            return False

        pos = idx + 1

    return True

# ─────────────────────────────────────────────────────────────
# RENDER SINGLE PANEL
# ─────────────────────────────────────────────────────────────

def render_panel(
    title,
    items,
    selected,
    query,
    total,
):

    print("\033[2J\033[H", end="")

    print()
    print(f"  {TITLE}{title}{R}")
    print()

    print(
        f"  {CYAN}🔍 Pesquisa:{R} {query}"
        f"  {DIM}({len(items)}/{total}){R}"
    )

    print()

    visible = items[:MAX_VISIBLE]

    for i, item in enumerate(visible):

        if isinstance(item, Path):
            name = item.stem
        else:
            name = item

        if i == selected:
            print(f"  {SEL} ▶ {name} {R}")
        else:
            print(f"    {name}")

    print()
    print(
        f"  {DIM}[↑↓] navegar  [Enter] selecionar"
        f"  [ESC] sair{R}"
    )

# ─────────────────────────────────────────────────────────────
# SELECT MENU
# ─────────────────────────────────────────────────────────────

def select_menu(title, all_items):

    query = ""
    selected = 0

    filtered = all_items[:]

    while True:

        render_panel(
            title,
            filtered,
            selected,
            query,
            len(all_items),
        )

        key = read_key()

        if key == "ESC":
            sys.exit(0)

        elif key == "UP":
            if selected > 0:
                selected -= 1

        elif key == "DOWN":
            if selected < len(filtered) - 1:
                selected += 1

        elif key == "BACKSPACE":

            if query:
                query = query[:-1]

                filtered = [
                    x for x in all_items
                    if fuzzy_match(
                        query,
                        x.stem if isinstance(x, Path) else x
                    )
                ]

                selected = 0

        elif key == "ENTER":

            if filtered:
                return filtered[selected]

        elif isinstance(key, str) and key.isprintable():

            query += key

            filtered = [
                x for x in all_items
                if fuzzy_match(
                    query,
                    x.stem if isinstance(x, Path) else x
                )
            ]

            selected = 0

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────

def extract_root_block(css_path):

    text = css_path.read_text(
        encoding="utf-8"
    )

    m = re.search(
        r':root\s*\{[^}]*\}',
        text,
        re.DOTALL
    )

    return m.group(0) if m else None

def replace_root_block(target, new_root):

    text = target.read_text(
        encoding="utf-8"
    )

    new_text, count = re.subn(
        r':root\s*\{[^}]*\}',
        new_root,
        text,
        count=1,
        flags=re.DOTALL
    )

    if count == 0:
        new_text = new_root + "\n\n" + text

    target.write_text(
        new_text,
        encoding="utf-8"
    )

# ─────────────────────────────────────────────────────────────
# APPLY CSS
# ─────────────────────────────────────────────────────────────

def apply_css_theme(src):

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ts = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    if TARGET_CSS.exists():

        shutil.copy2(
            TARGET_CSS,
            BACKUP_DIR / f"css_backup_{ts}.css"
        )

    root = extract_root_block(src)

    if root is None:
        return False, "Sem bloco :root"

    try:
        replace_root_block(
            TARGET_CSS,
            root
        )

        return True, src.stem

    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────────────────────
# APPLY INTERNAL THEME
# ─────────────────────────────────────────────────────────────

def apply_internal_theme(theme_id):

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:

        # Backup do ficheiro original
        if VSCODE_SETTINGS.exists():
            shutil.copy2(
                VSCODE_SETTINGS,
                BACKUP_DIR / f"settings_backup_{ts}.json"
            )

        text = VSCODE_SETTINGS.read_text(
            encoding="utf-8"
        )

        # ─────────────────────────────
        # REMOVE APENAS A LINHA DO TEMA
        # ─────────────────────────────

        # remove linha workbench.colorTheme inteira
        text = re.sub(
            r'^\s*"workbench\.colorTheme"\s*:\s*".*?"\s*,?\s*$',
            '',
            text,
            flags=re.MULTILINE
        )

        # ─────────────────────────────
        # INSERE NOVO TEMA NO FINAL DO BLOCO
        # ─────────────────────────────

        insert = f'\n\t"workbench.colorTheme": "{theme_id}",\n'

        # insere antes da última }
        text = re.sub(
            r'}\s*$',
            insert + "}",
            text
        )

        # guardar
        VSCODE_SETTINGS.write_text(
            text,
            encoding="utf-8"
        )

        return True, theme_id

    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():

    enable_ansi()

    css_files = sorted(
        CSS_THEMES_DIR.rglob("*.css")
    )

    internal_names = list(
        VSCODE_THEMES.keys()
    )

    # ─────────────────────────────
    # PANEL 1 - CSS
    # ─────────────────────────────

    css_selected = select_menu(
        "💉 CSS Injection Theme",
        css_files
    )

    ok, msg = apply_css_theme(
        css_selected
    )

    print("\033[2J\033[H")

    if ok:
        print(
            f"\n  {GREEN}✔ CSS aplicado:{R} {msg}\n"
        )
    else:
        print(
            f"\n  {RED}✗ Erro CSS:{R} {msg}\n"
        )

    input("  ENTER para continuar...")

    # ─────────────────────────────
    # PANEL 2 - INTERNAL THEME
    # ─────────────────────────────

    theme_selected = select_menu(
        "🎨 VSCode Internal Theme",
        internal_names
    )

    theme_id = VSCODE_THEMES[
        theme_selected
    ]

    ok, msg = apply_internal_theme(
        theme_id
    )

    print("\033[2J\033[H")

    if ok:
        print(
            f"\n  {GREEN}✔ Tema aplicado:{R} {msg}\n"
        )

        print(
            f"  {CYAN}Valor escrito no settings.json:{R}"
        )

        print(
            f'  "workbench.colorTheme": "{theme_id}"\n'
        )

    else:
        print(
            f"\n  {RED}✗ Erro tema:{R} {msg}\n"
        )

    print(
        f"  {YELLOW}Agora no VSCode:{R}"
    )

    print(
        "  Ctrl+Shift+P → Reload Window\n"
    )

if __name__ == "__main__":
    main()
