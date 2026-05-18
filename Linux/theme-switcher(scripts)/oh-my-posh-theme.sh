#!/usr/bin/env fish

set THEMES_DIR ~/.poshthemes

if not command -q fzf
    echo "❌ fzf não encontrado"
    exit 1
end

if not test -d $THEMES_DIR
    echo "❌ pasta não existe: $THEMES_DIR"
    exit 1
end

# ── recolher temas ───────────────────────────────
set THEME_NAMES
set THEME_PATHS

for file in (find $THEMES_DIR -name "*.omp.json" | sort)
    set name (basename $file)
    set THEME_NAMES $THEME_NAMES $name
    set THEME_PATHS $THEME_PATHS $file
end

if test (count $THEME_NAMES) -eq 0
    echo "❌ nenhum tema encontrado"
    exit 1
end

# ── temp mapping para fzf preview ───────────────────
set TMPMAP (mktemp)

for i in (seq (count $THEME_NAMES))
    echo "$THEME_NAMES[$i]\t$THEME_PATHS[$i]" >> $TMPMAP
end


# ── menu fzf ────────────────────────────────────────
set CHOSEN (printf "%s\n" $THEME_NAMES | fzf \
    --prompt="🎨 oh-my-posh: " \
    --header="↑↓ navegar  Enter aplicar  Esc cancelar" \
    --layout=reverse \
    --border=rounded \
    --height=90%)

rm -f $TMPMAP

if test -z "$CHOSEN"
    echo "cancelado"
    exit 0
end

# ── encontrar path ─────────────────────────────────
set pos 1
for i in (seq (count $THEME_NAMES))
    if test "$THEME_NAMES[$i]" = "$CHOSEN"
        set pos $i
        break
    end
end

set THEME_PATH $THEME_PATHS[$pos]

# ── atualizar config.fish ─────────────────────────
set CONFIG "$HOME/.config/fish/config.fish"

if test -f $CONFIG
    sed -i '/oh-my-posh init fish/d' $CONFIG

    echo "oh-my-posh init fish --config $THEME_PATH | source" >> $CONFIG

    # aplicar tema
    functions -e fish_prompt 2>/dev/null
    functions -e _omp_hook 2>/dev/null
    oh-my-posh init fish --config $THEME_PATH | source
    commandline -f repaint

    echo "🔄 a reiniciar shell para aplicar tema..."
    sleep 0.3
    # única forma real de aplicar imediato
    exec fish

    echo ""
    echo "Tema aplicado: $CHOSEN"
else
    echo "❌ config.fish não encontrado"
end
