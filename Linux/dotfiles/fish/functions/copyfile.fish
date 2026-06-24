function copyfile
    if test (count $argv) -eq 0
        echo "Uso: copyfile ficheiro"
        return 1
    end

    if not test -f $argv[1]
        echo "Erro: ficheiro não existe: $argv[1]"
        return 1
    end

    cat $argv[1] | clipcopy
    echo "Conteúdo copiado: $argv[1]"
end
