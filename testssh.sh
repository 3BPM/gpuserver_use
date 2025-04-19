#!/bin/bash

# 提取所有全局 IPv6 地址（排除链路本地地址 fe80::）
# IPV6_LIST=$(ip -6 addr show dev enp129s0f0 | grep 'inet6 2400' | awk '{print $2}' | cut -d'/' -f1)
IPV6_LIST="2400:dd01:103a:4007:1488:2bd7:9e2f:2cf2
2400:dd01:103a:4007:d4ec:df8e:c689:fc3a
2400:dd01:103a:4007:cc93:514b:c5ab:13cc
2400:dd01:103a:4007:1e8d:50fe:f8db:86c4
2400:dd01:103a:4007:c0ab:46ad:1250:b4d5"

	# inet6 2400:dd01:103a:4007:8c4:ee95:8b6:c0ad prefixlen 64 autoconf secured
	# inet6 2400:dd01:103a:4007:ed3c:2f8f:6ef:b1f9 prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:a41f:cc57:ca75:3438 prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:7438:47c7:6ba:25e4 prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:9cea:ec3a:22f3:cf42 prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:814d:778f:73:8d60 prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:4cf2:49ed:47e6:a49c prefixlen 64 deprecated autoconf temporary
	# inet6 2400:dd01:103a:4007:d855:8ad4:aaf1:e2ef prefixlen 64 autoconf temporary
# 定义 SSH 端口和超时时间
SSH_PORT=22097
TIMEOUT=2

# 遍历所有地址测试 SSH
for ip6 in $IPV6_LIST; do
  echo -n "Testing $ip6 ... "
  ssh -6 -o "StrictHostKeyChecking=no" -o "ConnectTimeout=$TIMEOUT" -p $SSH_PORT user@$ip6 exit 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "SUCCESS"
    echo "$ip6" >> success_ips.txt
  else
    echo "FAILED"
    echo "$ip6" >> failed_ips.txt
  fi
done
