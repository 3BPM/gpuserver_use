#!/bin/bash

# 文件名
filename="/home/jinyue/note"

# 检查是否接收到参数
if [ $# -eq 0 ]; then
    # 没有参数，读取文件内容并输出
    if [ -f "$filename" ]; then
        cat "$filename"
    else
        echo "文件 $filename 不存在。"
    fi
else
    # 如果参数是dd，则删除最后一行
    if [ "$1" = "dd" ]; then
        # 使用sed命令删除最后一行
        last_line=$(tail -n 1 "$filename")
        sed -i '$d' "$filename"
        echo "已删除 $filename 的最后一行: $last_line"
    elif [ "$1" = "." ]; then
        # 如果输入.，则写入当前目录路径
        pwd >> "$filename"
        # echo "当前目录路径已写入 $filename"
    else
        # 接收到参数，将参数写入文件
        echo "$1" >> "$filename"
        # echo "内容已写入 $filename"
    fi
fi

