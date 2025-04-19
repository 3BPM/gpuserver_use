#!/bin/bash

# 获取 GPU 信息
gpu_info=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits)

# 初始化变量
max_free_memory=0
selected_gpu=""

# 遍历每个 GPU 的空闲内存
while IFS=',' read -r index free_memory; do
    if (( free_memory > max_free_memory )); then
        max_free_memory=$free_memory
        selected_gpu=$index
    fi
done <<< "$gpu_info"

# 如果找到了空闲的 GPU，则导出环境变量
if [ -n "$selected_gpu" ]; then
    export CUDA_VISIBLE_DEVICES=$selected_gpu
    echo "已选择 GPU: $selected_gpu (空闲内存: ${max_free_memory}MB)"
else
    echo "没有找到空闲的 GPU。"
fi
