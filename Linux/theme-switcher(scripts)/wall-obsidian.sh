#!/usr/bin/env bash

VAULT="/run/media/Windows-SSD/Universidade/MarkdownNotes/.obsidian"

APPEARANCE="$VAULT/appearance.json"
STYLE_SETTINGS="$VAULT/plugins/obsidian-style-settings/data.json"

# Escolhe a cor do pywal
# Podes trocar color4 por color5, color6, etc.
ACCENT=$(jq -r '.colors.color5' ~/.cache/wal/colors.json)

# fallback caso dê erro
[ -z "$ACCENT" ] || [ "$ACCENT" = "null" ] && exit 1

# appearance.json
tmp=$(mktemp)
jq --arg color "$ACCENT" '
  .accentColor = $color
' "$APPEARANCE" > "$tmp" && mv "$tmp" "$APPEARANCE"

# style-settings data.json
tmp=$(mktemp)
jq --arg color "$ACCENT" '
  ."Appearance-dark@@accent-dark" = $color |
  ."Appearance-dark@@color-red-rgb@@dark" = $color
' "$STYLE_SETTINGS" > "$tmp" && mv "$tmp" "$STYLE_SETTINGS"

echo "Obsidian accent atualizado para $ACCENT"
