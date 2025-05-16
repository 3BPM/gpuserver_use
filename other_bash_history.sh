#!/bin/bash

# 指定目标目录
target_dir="other_bash_history"

# 确保目标目录存在
mkdir -p "$target_dir"

# 遍历所有用户的家目录并复制 .bash_history 文件
for user_home in /home/*
do
    username=$(basename "$user_home")
    history_file="$user_home/.bash_history"

    if [ -f "$history_file" ]
    then
        cp "$history_file" "$target_dir/${username}_bash_history"
        echo "Copied $username's .bash_history"
    else
        echo "$username does not have a .bash_history file."
    fi
done
