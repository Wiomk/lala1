#!/bin/bash

MAC="$(echo $1 | sed 's/ //g' | sed 's/-//g' | sed 's/://g' | cut -c1-6)";

result="$(grep -i -A 4 ^$MAC ./oui.txt)";

if [ "$result" ]; then
    echo "Для MAC $1 найдена следующая информация:"
    echo "$result"
else
    echo "MAC $1 не найден в базе данных."
fi
