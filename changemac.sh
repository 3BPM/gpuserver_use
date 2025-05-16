#!/bin/bash

# 获取所有网络接口信息
interfaces=$(ip -o link show | awk -F': ' '{print $2}')

echo "可用的网络接口:"

# 显示所有接口并编号
i=1
for interface in $interfaces; do
    echo "$i) $interface"
    ((i++))
done

# 请求用户输入选择真正联网的端口
read -p "请选择代表真正联网的端口对应的数字 (例如 1): " main_interface_num

# 根据用户输入获取对应接口名
main_interface=$(echo "$interfaces" | sed -n "${main_interface_num}p")

if [[ -z "$main_interface" ]]; then
    echo "无效的选择."
    exit 1
fi

echo "你选择了 $main_interface 作为主要联网接口."

# 关闭端口并更改其MAC地址
for interface in $interfaces; do
    if [[ "$interface" == "$main_interface" ]]; then
        echo "正在处理 $interface..."

        # 关闭接口
        sudo ip link set dev "$interface" down || { echo "关闭 $interface 失败"; continue; }

        # 生成随机MAC地址 (使用本地管理地址位)
        random_mac=$(printf '02:%02x:%02x:%02x:%02x:%02x\n' $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))

        # 设置新的MAC地址
        sudo ip link set dev "$interface" address "$random_mac" || { echo "设置 $interface 的MAC地址失败"; continue; }

        # 重新激活接口
        sudo ip link set dev "$interface" up || { echo "激活 $interface 失败"; }

        echo "$interface 的MAC地址已更改为 $random_mac"
    fi
    # 移除不必要的 i++
done


echo "操作完成."