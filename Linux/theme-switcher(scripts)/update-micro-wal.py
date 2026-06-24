#!/usr/bin/env python3

import json
from pathlib import Path

wal_json = Path.home() / ".cache/wal/colors.json"
micro_dir = Path.home() / ".config/micro/colorschemes"
output = micro_dir / "wal.micro"

with open(wal_json, "r", encoding="utf-8") as f:
    data = json.load(f)

special = data["special"]
colors = data["colors"]

bg = special.get("background", colors["color0"])
fg = special.get("foreground", colors["color15"])

c0  = colors["color0"]
c1  = colors["color1"]
c2  = colors["color2"]
c3  = colors["color3"]
c4  = colors["color4"]
c5  = colors["color5"]
c6  = colors["color6"]
c7  = colors["color7"]
c8  = colors["color8"]
c9  = colors["color9"]
c10 = colors["color10"]
c11 = colors["color11"]
c12 = colors["color12"]
c13 = colors["color13"]
c14 = colors["color14"]
c15 = colors["color15"]

scheme = f'''# Auto-generated from pywal
# Source: ~/.cache/wal/colors.json

color-link default "{fg},{bg}"
color-link comment "{c8},{bg}"

color-link identifier "{c12},{bg}"
color-link constant "{c13},{bg}"
color-link constant.string "{c10},{bg}"
color-link constant.string.char "{c10},{bg}"

color-link statement "{c1},{bg}"
color-link symbol "{fg},{bg}"
color-link preproc "{c5},{bg}"
color-link type "{c6},{bg}"
color-link special "{c14},{bg}"
color-link underlined "{c13},{bg}"

color-link error "bold {c9},{bg}"
color-link todo "bold {c11},{bg}"

color-link hlsearch "{bg},{c3}"
color-link statusline "{bg},{fg}"
color-link tabbar "{bg},{fg}"

color-link indent-char "{c8},{bg}"
color-link line-number "{c8},{c0}"
color-link current-line-number "{c11},{bg}"

color-link diff-added "{c10}"
color-link diff-modified "{c11}"
color-link diff-deleted "{c9}"

color-link gutter-error "{c9},{bg}"
color-link gutter-warning "{c11},{bg}"

color-link cursor-line "{c0}"
color-link color-column "{c0}"

color-link type.extended "default"
color-link symbol.tag "{c13},{bg}"
color-link match-brace "{bg},{c12}"

color-link tab-error "{c9}"
color-link trailingws "{c9}"
'''

micro_dir.mkdir(parents=True, exist_ok=True)
output.write_text(scheme, encoding="utf-8")

print(f"Generated: {output}")
