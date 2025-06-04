#!/bin/bash

# 检查是否有输入参数
if [ $# -ge 1 ]; then
    # 如果参数是 "0,1,2,3" 或其他组合则直接使用
    export CUDA_VISIBLE_DEVICES=$1
    free_memory=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | sed -n "${1}p")
    echo "手动选择 GPU: $1,空闲内存: ${free_memory}MB)"
else
    # 获取 GPU 信息 (原始自动选择逻辑)
    gpu_info=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null)

    # 检查nvidia-smi是否可用
    if [ $? -ne 0 ]; then
        echo "错误：无法获取GPU信息，请检查nvidia-smi"
        exit 1
    fi

    # 初始化变量
    max_free_memory=0
    selected_gpu=""

    # 遍历每个 GPU 的空闲内存
    while IFS=',' read -r index free_memory; do
        # 去除index中的空格
        index=$(echo $index | tr -d ' ')
        if (( free_memory > max_free_memory )); then
            max_free_memory=$free_memory
            selected_gpu=$index
        fi
    done <<< "$gpu_info"

    # 如果找到了空闲的 GPU，则导出环境变量
    if [ -n "$selected_gpu" ]; then
        export CUDA_VISIBLE_DEVICES=$selected_gpu
        echo "自动选择 GPU: $selected_gpu (空闲内存: ${max_free_memory}MB)"
    else
        echo "没有找到可用的 GPU。"
    fi
fi
