#!/bin/bash

COLORS_JSON="$HOME/.cache/wal/colors.json"
PLASMA_CONFIG="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"

# Extrai color4 do pywal (cor de destaque/seleção)
ACCENT_HEX=$(python3 -c "
import json
with open('$COLORS_JSON') as f:
    data = json.load(f)
print(data['colors']['color4']['hex'] if isinstance(data['colors']['color4'], dict) else data['colors']['color4'])
")

if [ -z "$ACCENT_HEX" ]; then
    echo "Erro: não foi possível ler a cor do pywal"
    exit 1
fi

# Hex para RGB
RGB=$(python3 -c "
h = '$ACCENT_HEX'.lstrip('#')
print(f'{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}')
")

echo "Cor: $ACCENT_HEX → RGB: $RGB"

# Atualiza as 3 cores na secção correta
sed -i \
    -e "s/^date_font_color=.*/date_font_color=$RGB/" \
    -e "s/^day_font_color=.*/day_font_color=$RGB/" \
    -e "s/^time_font_color=.*/time_font_color=$RGB/" \
    "$PLASMA_CONFIG"

echo "✓ Clock atualizado"

# Recarrega o Plasma
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.refreshCurrentShell 2>/dev/null \
    || echo "Nota: reinicia o Plasma para aplicar (kquitapp6 plasmashell && kstart plasmashell)"
