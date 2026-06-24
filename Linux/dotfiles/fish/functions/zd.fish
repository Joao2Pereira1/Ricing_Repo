function zd
    set steps 1

    if test (count $argv) -gt 0
        if string match -qr '^[0-9]+$' -- $argv[1]
            set steps $argv[1]
        else
            echo "Uso: zu [numero]"
            return 1
        end
    end

    for i in (seq $steps)
        nextd
    end
end
