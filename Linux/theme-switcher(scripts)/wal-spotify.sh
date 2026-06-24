#!/bin/bash
# spicetify-wal.sh — Atualiza o tema spicetify com as cores do pywal
# Cria o tema "wal" em ~/.config/spicetify/Themes/wal/
# e aplica com spicetify apply.

COLORS_JSON="$HOME/.cache/wal/colors.json"
THEME_DIR="$HOME/.config/spicetify/Themes/wal"
COLOR_INI="$THEME_DIR/color.ini"
USER_CSS="$THEME_DIR/user.css"

if [ ! -f "$COLORS_JSON" ]; then
    echo "Erro: $COLORS_JSON não encontrado. Corre o pywal primeiro."
    exit 1
fi

# Extrai cores do pywal (remove o # do hex)
get_color() {
    python3 -c "
import json
with open('$COLORS_JSON') as f:
    data = json.load(f)
key = '$1'
if key in ('background', 'foreground', 'cursor'):
    val = data['special']['$1']
else:
    val = data['colors']['$1']
    if isinstance(val, dict):
        val = val['hex']
print(val.lstrip('#'))
"
}

background=$(get_color background)
foreground=$(get_color foreground)
color0=$(get_color color0)
color4=$(get_color color4)
color7=$(get_color color7)
color8=$(get_color color8)
color12=$(get_color color12)

# player: mistura de background com color8 (ligeiramente mais claro que o fundo)
player=$(python3 -c "
import colorsys
def h2rgb(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(c1, c2, t):
    r1,g1,b1 = h2rgb(c1); r2,g2,b2 = h2rgb(c2)
    return '{:02X}{:02X}{:02X}'.format(int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))
print(mix('$background', '$color8', 0.3))
")

echo "Cores geradas:"
echo "  main/sidebar → #$background"
echo "  player       → #$player"
echo "  card         → #$color8"
echo "  button       → #$color4"
echo "  text         → #$foreground"

# Cria a pasta do tema se não existir
mkdir -p "$THEME_DIR"

# Escreve o color.ini
cat > "$COLOR_INI" << EOF
[Base]
main           = $background
sidebar        = $color0
player         = $player
card           = $color8
shadow         = $color0
selected-row   = $color8
button         = $color4
button-active  = $color12
text           = $foreground
subtext        = $color7
EOF

# Cria user.css vazio se não existir (obrigatório pelo spicetify)
if [ ! -f "$USER_CSS" ]; then
    touch "$USER_CSS"
fi

echo "✓ color.ini escrito em $COLOR_INI"

# Define o tema wal no spicetify e aplica
spicetify config current_theme wal color_scheme Base
spicetify apply --no-restart

echo "✓ Spicetify atualizado com tema wal"
