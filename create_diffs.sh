for new in $(ls new/*csv); do
    new_name=$(echo $new | cut -d/ -f2)
    sample_name=$(echo $new | cut -d/ -f2 | cut -d_ -f1)

    for old in $(ls old/*csv); do
        old_name=$(echo $old | cut -d/ -f2)

        if [ "$new_name" = "$old_name" ]; then
            suffix=$(echo $old_name | cut -d_ -f3-)
            echo $sample_name"_"$suffix
            diff $new $old > diffs/$sample_name"_"$suffix
        fi
    done
done