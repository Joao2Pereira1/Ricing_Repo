
# caso precisares basta descomentar
# export PATH="$PATH:/opt/nvim-linux-x86_64/bin"

# placa pic32 para ac
# if test -d /opt/pic32mx/bin
#    set -gx PATH $PATH /opt/pic32mx/bin
# end

# alias
alias ls="eza --icons"
alias ll="eza --icons -all"
alias cdir='copydir'
alias cfile='copyfile'

# pacman alias
alias s="sudo pacman -Ss"
alias i="sudo pacman -S"
alias r="sudo pacman -R"

# alias themes
alias ot="~/scripts/oh-my-posh-theme.sh"
alias kt="~/scripts/konsole-theme.sh"
alias vt="~/scripts/vscode-theme-switch.sh"
alias tl="~/scripts/theme-launcher.sh"
alias ow="python3 ~/scripts/wal-to-omp.py" # oh-my-posh com pywal

# config alias
alias fs="micro ~/.config/fish/config.fish"
alias omp="micro ~/.poshthemes/wal-theme.omp.json"

# alias directories
alias uni="cd /run/media/Windows-SSD/Universidade"
alias notes="cd /run/media/Windows-SSD/Universidade/MarkdownNotes"
alias coding="cd /run/media/Windows-SSD/Code"
alias backup="cd /run/media/Windows-SSD/Backup"

# alias launch apps
alias vivaldi='vivaldi-stable --ozone-platform=x11 --password-store=basic'
alias marktext='marktext --disable-gpu --ozone-platform=x11'
alias obsidian='obsidian --ozone-platform=x11'

# alias other
alias cpp="wl-copy"
alias chmox="chmod +x"
alias mc="micro"
alias as="aur-scan"

# linha de espaco ao iniciar shell
if status is-interactive
    echo
end

# remover keybinding para kill alt + d padrao do fish, para usar para terminal panes
bind --erase --preset \es
bind --erase --preset \ed

# tens uma funcao para subir diretorios up
# depois zu sobe x posicoes no historico de diretorio
# depois zd desce x posicoes no historico de diretorio
# zh ve historico de diretorios
alias zh="dirh"
alias src='source ~/.config/fish/config.fish'

# Set up fzf key bindings
fzf --fish | source
zoxide init fish | source
thefuck --alias | source 

# tema oh-my-posh
oh-my-posh init fish --config /home/pereira/.poshthemes/wal-theme.omp.json | source
