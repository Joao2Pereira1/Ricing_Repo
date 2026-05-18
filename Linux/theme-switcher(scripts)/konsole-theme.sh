#!/usr/bin/env fish

if not command -q fzf
    echo "❌ fzf não encontrado"
    exit 1
end

set SCHEME_DIRS ~/.local/share/konsole /usr/share/konsole

set SCHEME_NAMES
set SCHEME_PATHS

# ── recolher schemes ───────────────────────────────
for dir in $SCHEME_DIRS
    if test -d $dir
        for file in (find $dir -maxdepth 1 -name "*.colorscheme" | sort)
            set name (basename $file .colorscheme)

            set SCHEME_NAMES $SCHEME_NAMES $name
            set SCHEME_PATHS $SCHEME_PATHS $file
        end
    end
end

if test (count $SCHEME_NAMES) -eq 0
    echo "❌ Nenhum tema encontrado"
    exit 1
end

# ── temp mapping para fzf preview ───────────────────
set TMPMAP (mktemp)

for i in (seq (count $SCHEME_NAMES))
    echo "$SCHEME_NAMES[$i]\t$SCHEME_PATHS[$i]" >> $TMPMAP
end

# ── escolher índice em vez de string mapping ────────
set idx (printf "%s\n" $SCHEME_NAMES | fzf \
    --prompt="🎨 tema konsole: " \
    --header="↑↓ navegar  Enter aplicar  Esc cancelar" \
    --layout=reverse \
    --border=rounded \
    --height=90%)

if test -z "$idx"
    echo "cancelado"
    exit
end

# ── encontrar posição ───────────────────────────────
set pos 1
for i in (seq (count $SCHEME_NAMES))
    if test "$SCHEME_NAMES[$i]" = "$idx"
        set pos $i
        break
    end
end

# ── aplica instantaneamente à janela atual (preview live)
konsoleprofile ColorScheme=$idx 2>/dev/null

# ── aplica ao profile para novas janelas
set PROFILE (kreadconfig5 --file konsolerc --group "Desktop Entry" --key DefaultProfile)
set PROFILE_PATH "$HOME/.local/share/konsole/$PROFILE"

if test -f "$PROFILE_PATH"
    kwriteconfig5 --file "$PROFILE_PATH" \
        --group "Appearance" \
        --key ColorScheme "$idx"

    echo "✅ Tema aplicado: $idx"
    echo "⚡ Live (janela atual) + persistente (novas janelas)"
else
    echo "❌ Profile não encontrado: $PROFILE_PATH"
end
