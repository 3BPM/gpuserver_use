#!/bin/bash

# 遍历当前目录下所有 .sh 文件
for file in *.sh; do
    # 检查文件是否存在（避免没有 .sh 文件时报错）
    if [[ -f "$file" ]]; then
        # 添加可执行权限
        chmod +x "$file"
        echo "已添加可执行权限: $file"
    else
        echo "未找到 .sh 文件"
    fi
done