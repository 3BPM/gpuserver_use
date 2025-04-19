
import json
import yaml
import base64
import os
import sys
from datetime import datetime

def convert_ssr_to_clash(ssr_links, output_file=None):
    # 创建Clash配置模板
    clash_config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": True,
        "mode": "Rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxies": [],
        "proxy-groups": [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": ["DIRECT"]
            },
            {
                "name": "Toline",
                "type": "select",
                "proxies": ["DIRECT"]
            }
        ],
        "rules": [
            "DOMAIN-SUFFIX,google.com,PROXY",
            "DOMAIN-KEYWORD,google,PROXY",
            "DOMAIN-SUFFIX,ad.com,REJECT",
            "GEOIP,CN,DIRECT",
            "MATCH,DIRECT"
        ]
    }

    proxy_names = []

    for ssr_link in ssr_links:
        try:
            # 去除前缀并解码
            base64_data = ssr_link.replace('ssr://', '')
            decoded_data = base64.urlsafe_b64decode(base64_data + '=' * (-len(base64_data) % 4)).decode('utf-8')

            # 分割数据
            server_info, params = decoded_data.split(':', 5)[:2], decoded_data.split(':', 5)[2]
            server_address, server_port, protocol, method, obfs = server_info
            server_port = int(server_port)

            # 解析参数
            param_dict = dict(pair.split('=') for pair in params.split('&') if '=' in pair)
            password = base64.urlsafe_b64decode(param_dict.get('password', '') + '=' * (-len(param_dict.get('password', '')) % 4)).decode('utf-8')
            name = base64.urlsafe_b64decode(param_dict.get('remarks', '') + '=' * (-len(param_dict.get('remarks', '')) % 4)).decode('utf-8')
            group = base64.urlsafe_b64decode(param_dict.get('group', '') + '=' * (-len(param_dict.get('group', '')) % 4)).decode('utf-8')

            # 跳过无效服务器
            if not server_address or server_address in ["0.0.0.1", "0.0.0.2"]:
                continue

            # 创建Clash代理配置
            proxy = {
                "name": name,
                "type": "ssr",
                "server": server_address,
                "port": server_port,
                "password": password,
                "cipher": method,
                "protocol": protocol,
                "obfs": obfs,
                "udp": True
            }

            # 添加到代理列表
            clash_config["proxies"].append(proxy)
            proxy_names.append(name)
        except Exception as e:
            print(f"处理 SSR 链接 {ssr_link} 时出错: {e}")

    # 更新代理组
    clash_config["proxy-groups"][0]["proxies"].extend(proxy_names)

    # 按组分类代理
    groups = {}
    for proxy in clash_config["proxies"]:
        group_name = None

        # 根据代理名称判断所属组
        if "德国" in proxy["name"]:
            group_name = "德国"
        elif "法国" in proxy["name"]:
            group_name = "法国"
        elif "荷兰" in proxy["name"]:
            group_name = "荷兰"
        elif "泰国" in proxy["name"]:
            group_name = "泰国"
        elif "英国" in proxy["name"]:
            group_name = "英国"
        elif "俄罗斯" in proxy["name"] or "白俄罗斯" in proxy["name"]:
            group_name = "俄罗斯"
        elif "澳大利亚" in proxy["name"]:
            group_name = "澳大利亚"
        elif "美国" in proxy["name"]:
            group_name = "美国"
        elif "韩国" in proxy["name"]:
            group_name = "韩国"
        elif "日本" in proxy["name"]:
            group_name = "日本"
        elif "香港" in proxy["name"]:
            group_name = "香港"
        else:
            group_name = "其他"

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(proxy["name"])

    # 添加分组到proxy-groups
    for group_name, proxies in groups.items():
        if proxies:  # 只添加非空组
            clash_config["proxy-groups"].append({
                "name": group_name,
                "type": "select",
                "proxies": proxies
            })
            # 将组添加到主选择组
            clash_config["proxy-groups"][1]["proxies"].append(group_name)

    # 添加时间戳注释
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yaml_str = f"# 由SSR配置转换为Clash配置\n# 转换时间: {timestamp}\n\n"

    # 将配置转换为YAML格式并写入文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_str)
            yaml.dump(clash_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"转换完成！Clash配置已保存到: {output_file}")
    return clash_config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ssr_to_clash.py <输出文件路径>")
        sys.exit(1)

    output_file = sys.argv[1]
    from gettoline import get_and_decode
    # 示例 SSR 链接列表，实际使用时应替换为 getoline 函数的输出
    ssr_links = get_and_decode()

    try:
        result_config = convert_ssr_to_clash(ssr_links, output_file)
        print(f"成功将 SSR 配置转换为 Clash 配置并保存到: {output_file}")
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        sys.exit(1)