for new in $(ls new/*csv); do
    new_name=$(echo $new | cut -d/ -f2)

    for old in $(ls old/*csv); do
        old_name=$(echo $old | cut -d/ -f2)

        if [ "$new_name" = "$old_name" ]; then
            suffix=$(echo $old_name | cut -d_ -f3-)
            diff $new $old > $suffix
        fi
    done
done