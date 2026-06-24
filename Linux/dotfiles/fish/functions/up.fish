function up
    set levels 1
    if test (count $argv) -gt 0
        set levels $argv[1]
    end

    for i in (seq $levels)
        cd ..
    end
end
