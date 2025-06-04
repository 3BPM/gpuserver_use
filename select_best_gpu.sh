#!/bin/bash

# 帮助信息函数
show_help() {
    echo "用法: $0 [GPU索引列表]"
    echo "示例:"
    echo "  $0           # 自动选择内存最大的GPU"
    echo "  $0 3         # 指定使用GPU 3"
    echo "  $0 0,1,2,3   # 指定使用多个GPU"
    echo "  $0 -h        # 显示帮助信息"
}

# 检查是否有参数
if [ $# -ge 1 ]; then
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            # 验证参数格式
            if [[ $1 =~ ^[0-9]+(,[0-9]+)*$ ]]; then
                export CUDA_VISIBLE_DEVICES=$1
                echo "已指定 GPU: $1"
                exit 0
            else
                echo "错误: 无效的GPU索引格式" >&2
                show_help
                exit 1
            fi
            ;;
    esac
fi

# 如果没有参数，执行原有自动选择逻辑

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
    echo "已自动选择 GPU: $selected_gpu (空闲内存: ${max_free_memory}MB)"
else
    echo "没有找到空闲的 GPU。"
fi
