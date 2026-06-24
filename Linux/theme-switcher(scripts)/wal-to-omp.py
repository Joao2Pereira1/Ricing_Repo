#!/usr/bin/env python3
"""
wal-to-omp.py — Gera tema oh-my-posh a partir das cores do pywal.

Lê ~/.cache/wal/colors.json e gera ~/.poshthemes/wal-theme.json
Atualiza automaticamente o config.fish.

Uso:
  python3 wal-to-omp.py
  python3 wal-to-omp.py --wal ~/.cache/wal/colors.json  # path custom
  python3 wal-to-omp.py --print                         # só mostra as cores
"""

import json
import argparse
import colorsys
import sys
from pathlib import Path

POSHTHEMES_DIR = Path.home() / ".poshthemes"
FISH_CONFIG    = Path.home() / ".config/fish/config.fish"
WAL_COLORS     = Path.home() / ".cache/wal/colors.json"
THEME_FILE     = Path.home() / ".poshthemes/wal-theme.omp.json"


# ---------------------------------------------------------------------------
# Utilitários de cor
# ---------------------------------------------------------------------------

def hex_to_hsl(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    hue, l, s = colorsys.rgb_to_hls(r, g, b)
    return hue, s, l


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def lightness(hex_color: str) -> float:
    _, _, l = hex_to_hsl(hex_color)
    return l


# ---------------------------------------------------------------------------
# Leitura do pywal
# ---------------------------------------------------------------------------

def load_wal_colors(wal_path: Path) -> dict:
    if not wal_path.exists():
        print(f"Erro: {wal_path} não encontrado. Corre o pywal primeiro.", file=sys.stderr)
        sys.exit(1)
    with open(wal_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    colors = {}
    for key, val in data.get("colors", {}).items():
        colors[key] = val["hex"] if isinstance(val, dict) else val
    special = data.get("special", {})
    colors["background"] = special.get("background", colors.get("color0", "#000000"))
    colors["foreground"] = special.get("foreground", colors.get("color7", "#ffffff"))
    return colors


# ---------------------------------------------------------------------------
# Geração da palette
# ---------------------------------------------------------------------------

def pick_dominant(colors: dict) -> str:
    candidates = [colors[f"color{i}"] for i in range(1, 7)]
    hsl_list = [hex_to_hsl(c) for c in candidates]
    max_sat = max(s for _, s, _ in hsl_list)

    if max_sat < 0.35:
        hues = sorted(h for h, _, _ in hsl_list)
        median_hue = hues[len(hues) // 2]
        return min(candidates, key=lambda c: abs(hex_to_hsl(c)[0] - median_hue))

    def score(c):
        h, s, l = hex_to_hsl(c)
        l_penalty = abs(l - 0.5) * 2
        return s * (1 - l_penalty * 0.5)
    return max(candidates, key=score)


def generate_palette(colors: dict) -> dict:
    candidates = sorted(
        [colors[f"color{i}"] for i in range(1, 7)],
        key=lightness
    )

    # os: zona escura-média (índice 1) — contrasta bem com white
    os_color = candidates[1]
    # pink: zona média (índice 3)
    pink     = candidates[3]
    # lavender: zona clara (índice 5)
    lavender = candidates[5]

    # white: deriva do hue do os mas muito claro (não usa o foreground do wal)
    h, s, _ = hex_to_hsl(os_color)
    white = hsl_to_hex(h, s * 0.3, 0.92)

    # text: escuro para contrastar com pink/lavender
    text = hsl_to_hex(h, s * 0.4, 0.10)

    return {
        "os":       os_color,
        "pink":     pink,
        "lavender": lavender,
        "blue":     os_color,
        "white":    white,
        "text":     text,
    }


# ---------------------------------------------------------------------------
# Tema base
# ---------------------------------------------------------------------------

BASE_THEME = {
    "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
    "palette": {},
    "blocks": [
        {
            "alignment": "left",
            "segments": [
                {
                    "background": "p:os",
                    "foreground": "p:white",
                    "powerline_symbol": "\ue0b4",
                    "leading_diamond": "\ue0b6",
                    "style": "diamond",
                    "template": "{{.Icon}} ",
                    "type": "os"
                },
                {
                    "background": "p:os",
                    "foreground": "p:white",
                    "style": "diamond",
                    "template": " {{ .UserName }}@{{ .HostName }}",
                    "type": "session"
                },
                {
                    "background": "p:pink",
                    "foreground": "p:text",
                    "options": {
                        "folder_icon": "..\ue5fe..",
                        "home_icon": "~",
                        "style": "agnoster_short"
                    },
                    "powerline_symbol": "\ue0b4",
                    "style": "powerline",
                    "template": " {{ .Path }}",
                    "type": "path"
                },
                {
                    "background": "p:lavender",
                    "foreground": "p:text",
                    "style": "powerline",
                    "options": {
                        "branch_icon": "\ue725 ",
                        "fetch_status": False
                    },
                    "powerline_symbol": "\ue0b4",
                    "template": " {{ .HEAD }}",
                    "type": "git"
                }
            ],
            "type": "prompt"
        },
        {
            "alignment": "left",
            "newline": True,
            "segments": [
                {
                    "foreground": "p:blue",
                    "style": "plain",
                    "template": "\u276F ",
                    "type": "text"
                }
            ],
            "type": "prompt"
        }
    ],
    "final_space": True,
    "version": 4
}


# ---------------------------------------------------------------------------
# Escrita do tema
# ---------------------------------------------------------------------------

def write_theme(palette: dict) -> Path:
    POSHTHEMES_DIR.mkdir(parents=True, exist_ok=True)
    theme = dict(BASE_THEME)
    theme["palette"] = palette

    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return THEME_FILE


def update_fish_config(theme_path: Path):
    if not FISH_CONFIG.exists():
        print(f"  aviso: config.fish não encontrado em {FISH_CONFIG}", file=sys.stderr)
        return
    with open(FISH_CONFIG) as f:
        lines = f.readlines()
    new_lines = []
    changed = False
    for line in lines:
        if "oh-my-posh init fish --config" in line:
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}oh-my-posh init fish --config {theme_path} | source\n")
            changed = True
        else:
            new_lines.append(line)
    if changed:
        with open(FISH_CONFIG, "w") as f:
            f.writelines(new_lines)
        print(f"  config.fish atualizado")
    else:
        print(f"  aviso: linha oh-my-posh não encontrada em {FISH_CONFIG}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Gera tema oh-my-posh a partir das cores do pywal."
    )
    parser.add_argument(
        "--wal", "-w",
        default=str(WAL_COLORS),
        help=f"Caminho para o colors.json do pywal (default: {WAL_COLORS})",
    )
    parser.add_argument(
        "--print", "-p",
        action="store_true",
        help="Mostra a palette gerada sem modificar nenhum ficheiro.",
    )
    args = parser.parse_args()

    colors  = load_wal_colors(Path(args.wal))
    palette = generate_palette(colors)

    if args.print:
        print("Palette gerada:")
        for k, v in palette.items():
            print(f"  {k:10s} → {v}")
        return

    dest = write_theme(palette)

    print(f"✓ tema gerado: {dest}")
    print(f"  cores:")
    for k, v in palette.items():
        print(f"    {k:10s} → {v}")

    update_fish_config(dest)


if __name__ == "__main__":
    main()
