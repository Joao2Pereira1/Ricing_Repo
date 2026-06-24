#!/usr/bin/env bash

set -euo pipefail

USER_HOME="${HOME}"
USER_NAME="$(id -un)"

echo "=============================="
echo "   ARCH LINUX CLEANER"
echo "=============================="
echo

# Diretórios dentro de ~/.cache que NÃO devem ser apagados
PROTECTED_CACHE_DIRS=(
    "$USER_HOME/.cache/wal"
)

# Função segura para apagar conteúdo de diretórios
# Apaga ficheiros e pastas dentro do diretório, mas permite exclusões.
safe_rm() {
    local target="$1"

    [[ -d "$target" ]] || return 0

    # Caso especial: ~/.cache com exclusões
    if [[ "$target" == "$USER_HOME/.cache" ]]; then
        find "$target" -mindepth 1 \
            ! -path "$USER_HOME/.cache/wal" \
            ! -path "$USER_HOME/.cache/wal/*" \
            -exec rm -rf {} + 2>/dev/null || true
    else
        find "$target" -mindepth 1 -exec rm -rf {} + 2>/dev/null || true
    fi
}

echo "📦 Espaço antes:"
df -h /

echo
echo "🧹 Limpando cache do utilizador..."

safe_rm "$USER_HOME/.cache"
safe_rm "$USER_HOME/.config/obsidian/Cache"
safe_rm "$USER_HOME/.config/Code/Cache"
safe_rm "$USER_HOME/.config/Code/CachedExtensionVSIXs"
safe_rm "$USER_HOME/.config/Code/CachedData"

mkdir -p "$USER_HOME/.cache"
mkdir -p "$USER_HOME/.cache/wal"

echo
echo "🗑 Limpando Trash..."
TRASH_DIR="$USER_HOME/.local/share/Trash/files"
[[ -d "$TRASH_DIR" ]] && find "$TRASH_DIR" -mindepth 1 -delete

echo
echo "🧼 Limpando /tmp e /var/tmp apenas do utilizador..."
find /tmp -mindepth 1 -user "$USER_NAME" -delete 2>/dev/null || true
find /var/tmp -mindepth 1 -user "$USER_NAME" -delete 2>/dev/null || true

echo
echo "🔐 Pedindo permissões sudo uma vez..."
sudo -v

echo
echo "📚 Limpando logs antigos journalctl..."
sudo journalctl --vacuum-time=7d

echo
echo "📦 Limpando cache do pacman..."
if command -v paccache &>/dev/null; then
    sudo paccache -r
else
    echo "paccache não encontrado. Instala com: sudo pacman -S pacman-contrib"
fi

echo
echo "📦 Removendo pacotes órfãos..."
orphans="$(pacman -Qtdq 2>/dev/null || true)"
if [[ -n "$orphans" ]]; then
    sudo pacman -Rns --noconfirm $orphans
else
    echo "Nenhum pacote órfão."
fi

echo
echo "📦 Limpando cache do yay se existir..."
if command -v yay &>/dev/null; then
    yay -Sc --noconfirm
fi

echo
echo "🧹 Limpando thumbnails..."
safe_rm "$USER_HOME/.cache/thumbnails"

echo
echo "📊 Cache após limpeza:"
du -sh "$USER_HOME/.cache" 2>/dev/null || true

echo
echo "📦 Espaço depois:"
df -h /

echo
echo "✅ Limpeza concluída!"
