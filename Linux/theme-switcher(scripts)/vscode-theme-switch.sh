#!/usr/bin/env bash
# =============================================================================
# vscode-theme-switch.sh
# Muda tema do VSCode: paleta CSS + workbench.colorTheme no settings.json
# Deps: fzf, jq (opcional mas recomendado)
# Uso: ./vscode-theme-switch.sh
#      ./vscode-theme-switch.sh --list          # só listar temas disponíveis
#      ./vscode-theme-switch.sh "Blood Moon"    # aplicar diretamente sem fzf
# =============================================================================

set -euo pipefail

# ─── Configuração ─────────────────────────────────────────────────────────────

THEMES_DIR="/run/media/Windows-SSD/Backup/03_Themes_And_UI/vscode_themes"
CSS_FILE="/home/pereira/Documents/VSC_Costumization.css"
SETTINGS_FILE="${HOME}/.config/Code/User/settings.json"

# ─── Temas VSCode instalados ───────────────────────────────────────────────────
# Adiciona/remove os temas que tens instalados no VSCode.
# O nome tem de ser EXATAMENTE igual ao que aparece no settings.json
# ex: "workbench.colorTheme": "Dracula Theme"  →  "Dracula Theme"

VSCODE_THEMES=(
    # ── Os teus temas ──────────────────────────────────────────────────────────
    "Dracula Theme"
    "Dracula Theme Soft"
    "Monokai"
    "Monokai Pro"
    "One Dark Pro"
    "One Dark Pro Darker"
    "GitHub Dark"
    "Tokyo Night"
    "Tokyo Night Storm"
    "Catppuccin Mocha"
    "Catppuccin Macchiato"
    "Catppuccin Frappé"
    "Catppuccin Latte"
    "Dark Green Jungle theme"
    "Sea Green Theme"
    "Minimal Kiwi"
    "Nord"
    "Gruvbox Dark Hard"
    "Gruvbox Dark Medium"
    "Gruvbox Dark Soft"
    "Gruvbox Light Hard"
    "Gruvbox Light Medium"
    "Gruvbox Light Soft"
    "Ayu Dark"
    "Ayu Light"
    "Ayu Mirage"
    "Material Theme Ocean"
    "Synthwave '84"
    "Atom One Dark"

    # ── Rainglow (dark) ────────────────────────────────────────────────────────
    "Absent (rainglow)"
    "Allure (rainglow)"
    "Arstotzka (rainglow)"
    "Azure (rainglow)"
    "Banner (rainglow)"
    "Blink (rainglow)"
    "Bold (rainglow)"
    "Box UK (rainglow)"
    "Brave (rainglow)"
    "Carbonight (rainglow)"
    "Chocolate (rainglow)"
    "Codecourse (rainglow)"
    "Coffee (rainglow)"
    "Comrade (rainglow)"
    "Crackpot (rainglow)"
    "Crisp (rainglow)"
    "Dare (rainglow)"
    "Darkside (rainglow)"
    "Downpour (rainglow)"
    "Earthsong (rainglow)"
    "Fodder (rainglow)"
    "Frantic (rainglow)"
    "Freshcut (rainglow)"
    "Friction (rainglow)"
    "Frontier (rainglow)"
    "Github (rainglow)"
    "Glance (rainglow)"
    "Gloom (rainglow)"
    "Glowfish (rainglow)"
    "Goldfish (rainglow)"
    "Grunge (rainglow)"
    "Halflife (rainglow)"
    "Hawaii (rainglow)"
    "Heroku (rainglow)"
    "Hive (rainglow)"
    "Horizon (rainglow)"
    "Hub (rainglow)"
    "Hyrule (rainglow)"
    "Iceberg (rainglow)"
    "Isotope (rainglow)"
    "Jewel (rainglow)"
    "Jingle (rainglow)"
    "Joker (rainglow)"
    "Juicy (rainglow)"
    "Jumper (rainglow)"
    "Keen (rainglow)"
    "Kiwi (rainglow)"
    "Laracasts (rainglow)"
    "Laravel (rainglow)"
    "Lavender (rainglow)"
    "Legacy (rainglow)"
    "Lichen (rainglow)"
    "Loyal (rainglow)"
    "Mauve (rainglow)"
    "Mellow (rainglow)"
    "Mintchoc (rainglow)"
    "Monzo (rainglow)"
    "Morass (rainglow)"

    # ── Rainglow Contrast ──────────────────────────────────────────────────────
    "Absent Contrast (rainglow)"
    "Allure Contrast (rainglow)"
    "Azure Contrast (rainglow)"
    "Carbonight Contrast (rainglow)"
    "Chocolate Contrast (rainglow)"
    "Gloom Contrast (rainglow)"
    "Horizon Contrast (rainglow)"
    "Iceberg Contrast (rainglow)"
    "Isotope Contrast (rainglow)"
    "Laracasts Contrast (rainglow)"
    "Laravel Contrast (rainglow)"
    "Lichen Contrast (rainglow)"
    "Mauve Contrast (rainglow)"

    # ── Rainglow Light ─────────────────────────────────────────────────────────
    "Absent Light (rainglow)"
    "Earthsong Light (rainglow)"
    "Freshcut Light (rainglow)"
    "Github Light (rainglow)"
    "Gloom Light (rainglow)"
    "Horizon Light (rainglow)"
    "Laracasts Light (rainglow)"
    "Laravel Light (rainglow)"
)

# Cores para output no terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ─── Funções utilitárias ───────────────────────────────────────────────────────

die() { echo -e "${RED}✗ ERRO:${RESET} $*" >&2; exit 1; }
ok()  { echo -e "${GREEN}✓${RESET} $*"; }
info(){ echo -e "${CYAN}→${RESET} $*"; }
warn(){ echo -e "${YELLOW}⚠${RESET} $*"; }

# ─── Verificações iniciais ─────────────────────────────────────────────────────

check_deps() {
    command -v fzf >/dev/null 2>&1 || die "fzf não encontrado. Instala com: sudo pacman -S fzf  ou  sudo apt install fzf"
    [[ -d "$THEMES_DIR" ]]    || die "Pasta de temas não encontrada: $THEMES_DIR"
    [[ -f "$CSS_FILE" ]]      || die "Ficheiro CSS não encontrado: $CSS_FILE"
    [[ -f "$SETTINGS_FILE" ]] || die "settings.json não encontrado: $SETTINGS_FILE"
}

# ─── Parse dos temas da pasta ─────────────────────────────────────────────────
# Cada ficheiro .css pode ter múltiplos blocos :root precedidos por comentário
# com o nome do tema ex: /* 12. BLOOD MOON  */
# Suporta também um tema por ficheiro onde o nome é o filename

get_themes() {
    # Retorna: "Nome do Tema|/caminho/para/ficheiro.css|numero_do_bloco"
    local file theme_name block_num
    while IFS= read -r -d '' file; do
        block_num=0
        while IFS= read -r line; do
            # Detecta linhas tipo: /* 12. BLOOD MOON */  ou  /* DRACULA */
            if [[ "$line" =~ ^[[:space:]]*/\*[[:space:]]*([0-9]+\.[[:space:]]+)?([A-Z][^*]+[A-Z0-9])[[:space:]]*\*/ ]]; then
                theme_name="${BASH_REMATCH[2]}"
                # Limpa espaços extra e converte para Title Case simples
                theme_name="$(echo "$theme_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')"
                echo "${theme_name}|${file}|${block_num}"
                ((block_num++)) || true
            fi
        done < "$file"
        # Se não encontrou nenhum bloco nomeado, usa o nome do ficheiro
        if [[ $block_num -eq 0 ]]; then
            theme_name="$(basename "${file%.*}")"
            echo "${theme_name}|${file}|0"
        fi
    done < <(find "$THEMES_DIR" -maxdepth 2 -name "*.css" -print0 | sort -z)
}

# ─── Extrai o bloco :root de um ficheiro (por índice) ─────────────────────────

extract_root_block() {
    local file="$1"
    local block_index="${2:-0}"
    python3 - "$file" "$block_index" <<'EOF'
import sys, re

file_path = sys.argv[1]
target_block = int(sys.argv[2])

with open(file_path, 'r') as f:
    content = f.read()

# Encontra todos os blocos :root {...}
pattern = r'(:root\s*\{[^}]*\})'
blocks = re.findall(pattern, content, re.DOTALL)

if target_block < len(blocks):
    print(blocks[target_block])
else:
    # fallback: primeiro bloco
    if blocks:
        print(blocks[0])
    else:
        sys.exit(1)
EOF
}


# ─── Aplica a paleta CSS ───────────────────────────────────────────────────────

apply_css_palette() {
    local file="$1"
    local block="$2"

    local new_root
    new_root="$(extract_root_block "$file" "$block")" || die "Não foi possível extrair bloco :root de: $file"

    # Faz backup do CSS
    cp "$CSS_FILE" "${CSS_FILE}.bak"

    # Substitui o primeiro bloco :root no ficheiro CSS alvo
    python3 - "$CSS_FILE" "$new_root" <<'EOF'
import sys, re

css_file = sys.argv[1]
new_root = sys.argv[2]

with open(css_file, 'r') as f:
    content = f.read()

# Substitui o primeiro :root {...} pelo novo
pattern = r':root\s*\{[^}]*\}'
result = re.sub(pattern, new_root, content, count=1, flags=re.DOTALL)

with open(css_file, 'w') as f:
    f.write(result)

print("CSS atualizado")
EOF
}

# ─── Atualiza o colorTheme no settings.json ───────────────────────────────────

apply_vscode_theme() {
    local theme_name="$1"

    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"

    python3 - "$SETTINGS_FILE" "$theme_name" <<'PY'
import re
import sys

path = sys.argv[1]
theme = sys.argv[2]

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r'(^[ \t]*"workbench\.colorTheme"[ \t]*:[ \t]*")[^"]*("[ \t]*,?[ \t]*$)'

new_content, count = re.subn(
    pattern,
    rf'\1{theme}\2',
    content,
    count=1,
    flags=re.MULTILINE
)

if count == 0:
    raise SystemExit("ERRO: workbench.colorTheme não encontrado como chave principal")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)
PY
}

# ─── Menu de seleção do workbench theme (lista estática) ──────────────────────

pick_vscode_extension_theme() {
    local current_theme
    current_theme="$(grep '"workbench.colorTheme"' "$SETTINGS_FILE" 2>/dev/null \
                     | sed 's/.*"workbench.colorTheme"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')"

    # Constrói string para fzf (marca o tema atual com ►)
    local themes_list=""
    for t in "${VSCODE_THEMES[@]}"; do
        if [[ "$t" == "$current_theme" ]]; then
            themes_list+="► $t (atual)"$'\n'
        else
            themes_list+="  $t"$'\n'
        fi
    done

    local selected
    selected="$(echo "$themes_list" | grep -v '^$' | fzf \
        --height=40% \
        --border=rounded \
        --prompt="  VSCode Theme > " \
        --header="Tema atual: ${current_theme:-desconhecido}  |  ESC para manter" \
        --color='header:italic:yellow,prompt:cyan,pointer:green,marker:green' \
        --query="" \
        )" || { echo "$current_theme"; return; }

    # Remove o prefixo "► " e " (atual)" se presente
    selected="$(echo "$selected" | sed 's/^[► ]*//;s/ (atual)$//')"
    echo "$selected"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    check_deps

    # Modo --list
    if [[ "${1:-}" == "--list" ]]; then
        info "Temas disponíveis em: $THEMES_DIR"
        get_themes | awk -F'|' '{print "  •", $1, "→", $2}'
        exit 0
    fi

    # Recolhe todos os temas
    info "A ler temas de ${BOLD}$THEMES_DIR${RESET}..."
    local all_themes
    all_themes="$(get_themes)"

    if [[ -z "$all_themes" ]]; then
        die "Nenhum tema encontrado em: $THEMES_DIR"
    fi

    local total
    total="$(echo "$all_themes" | wc -l)"
    ok "Encontrados ${BOLD}$total${RESET} temas"
    echo ""

    # Modo direto: nome passado como argumento
    if [[ -n "${1:-}" ]]; then
        local query="$1"
        local match
        match="$(echo "$all_themes" | awk -F'|' -v q="$query" 'tolower($1) ~ tolower(q) {print; exit}')"
        [[ -z "$match" ]] && die "Tema '$query' não encontrado. Usa --list para ver disponíveis."
        selected="$match"
    else
        # Seleção interativa com fzf
        selected="$(echo "$all_themes" \
            | fzf \
                --height=80% \
                --layout=reverse \
                --border=rounded \
                --prompt="  Paleta CSS > " \
                --header="↑↓ navegar  Enter aplicar  Esc cancelar" \
                --color='header:italic:cyan,prompt:green,pointer:yellow,info:dim' \
                --delimiter='|' \
                --with-nth=1 \
            )" || { warn "Cancelado."; exit 0; }
    fi

    local palette_name palette_file palette_block
    IFS='|' read -r palette_name palette_file palette_block <<< "$selected"

    echo ""
    info "Paleta selecionada: ${BOLD}$palette_name${RESET}"
    echo ""

    # ── Passo 1: Aplica paleta CSS ──
    info "A aplicar paleta CSS em ${DIM}$CSS_FILE${RESET}..."
    apply_css_palette "$palette_file" "$palette_block"
    ok "Paleta CSS aplicada  ${DIM}(backup: ${CSS_FILE}.bak)${RESET}"

    # ── Passo 2: Escolhe tema VSCode ──
    echo ""
    echo -e "${YELLOW}╔══════════════════════════════════════════╗${RESET}"
    echo -e "${YELLOW}║  Agora escolhe o tema VSCode instalado   ║${RESET}"
    echo -e "${YELLOW}╚══════════════════════════════════════════╝${RESET}"
    echo ""

    local vscode_theme
    vscode_theme="$(pick_vscode_extension_theme)"

    if [[ -n "$vscode_theme" ]]; then
        info "A atualizar workbench.colorTheme → ${BOLD}$vscode_theme${RESET}..."
        apply_vscode_theme "$vscode_theme"
        ok "settings.json atualizado  ${DIM}(backup: ${SETTINGS_FILE}.bak)${RESET}"
    else
        warn "Nenhum tema VSCode selecionado, settings.json não modificado."
    fi

    echo ""
    echo -e "${GREEN}${BOLD}✓ Tema '$palette_name' aplicado com sucesso!${RESET}"
    echo -e "${DIM}  Reinicia o VSCode ou usa Ctrl+Shift+P → 'Developer: Reload Window' para ver as mudanças.${RESET}"
    echo -e "${DIM}  Reinicia o a extensão Reload Custom CSS JS para ver as mudanças.${RESET}"
    echo ""
}

# ─── Entry point ──────────────────────────────────────────────────────────────

main "${@}"
