function clipcopy
    if command -q wl-copy
        wl-copy
    else if command -q xclip
        xclip -selection clipboard
    else if command -q xsel
        xsel --clipboard --input
    else
        echo "Erro: instala wl-clipboard, xclip ou xsel" >&2
        return 1
    end
end
