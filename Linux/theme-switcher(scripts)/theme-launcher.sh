#!/usr/bin/env fish
# ╔══════════════════════════════════════════════════════════════════════╗
# ║              THEME LAUNCHER  ·  TUI unificado                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

# ── Paths dos scripts ─────────────────────────────────────────────────────────
# Ajusta estes paths para onde tens os scripts guardados
set SCRIPT_VSCODE   "$HOME/scripts/vscode-theme-switch.sh"
set SCRIPT_KONSOLE  "$HOME/scripts/konsole-theme.sh"
set SCRIPT_OMP      "$HOME/scripts/oh-my-posh-theme.sh"

# ── Helpers ───────────────────────────────────────────────────────────────────
function _err
    echo -e "\e[0;31m✗\e[0m $argv"
end

function _check_script
    if not test -f $argv[1]
        _err "Script não encontrado: $argv[1]"
        return 1
    end
    if not test -x $argv[1]
        chmod +x $argv[1]
    end
end

# ── Banner ────────────────────────────────────────────────────────────────────
function _banner
    clear
    echo ""
    echo -e "\e[0;35m\e[1m"
    echo "  ████████╗██╗  ██╗███████╗███╗   ███╗███████╗"
    echo "     ██╔══╝██║  ██║██╔════╝████╗ ████║██╔════╝"
    echo "     ██║   ███████║█████╗  ██╔████╔██║█████╗  "
    echo "     ██║   ██╔══██║██╔══╝  ██║╚██╔╝██║██╔══╝  "
    echo "     ██║   ██║  ██║███████╗██║ ╚═╝ ██║███████╗"
    echo "     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝"
    echo -e "\e[0m"
    echo -e "\e[2m  Launcher TUI  ·  VSCode · Konsole · Oh-My-Posh\e[0m"
    echo ""
end

# ── Menu principal ────────────────────────────────────────────────────────────
function _main_menu
    _banner

    set options \
        "  VSCode      ·  Paleta CSS + workbench theme" \
        "  Konsole     ·  Colorscheme" \
        "  Oh-My-Posh  ·  Prompt theme" \
        "  Sair"

    set chosen (printf "%s\n" $options | fzf \
        --prompt="  Theme Launcher › " \
        --header="↑↓ navegar  Enter selecionar  Esc sair" \
        --layout=reverse \
        --border=rounded \
        --height=40% \
        --no-sort \
        --color="header:italic:cyan,prompt:magenta,pointer:yellow,info:dim")

    switch $chosen
        case "*VSCode*"
            _check_script $SCRIPT_VSCODE; and bash $SCRIPT_VSCODE

        case "*Konsole*"
            _check_script $SCRIPT_KONSOLE; and fish $SCRIPT_KONSOLE

        case "*Oh-My-Posh*"
            _check_script $SCRIPT_OMP; and fish $SCRIPT_OMP
            # oh-my-posh-theme.sh faz exec fish, não volta ao menu
            return

        case "*Sair*" ""
            echo -e "\e[2m  Até logo.\e[0m"
            echo ""
            return 0
    end

    echo ""
    read -l -P "  Prima Enter para voltar ao menu... " _
    _main_menu
end

# ── Entry point ───────────────────────────────────────────────────────────────

if not command -q fzf
    _err "fzf não encontrado. Instala com: sudo pacman -S fzf  ou  sudo apt install fzf"
    exit 1
end

_main_menu
