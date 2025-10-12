import subprocess
import re
import time
import sys
import select
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# OUI数据库本地文件路径，请确保该文件存在
OUI_DB_PATH = "oui.txt"  # 请替换为实际的本地OUI文件路径


def list_interfaces():
    """列出所有可用的网络接口（排除回环接口）"""
    try:
        result = subprocess.run(['ip', '-o', 'link', 'show', 'up'], capture_output=True, text=True, check=True)
        interfaces = []
        pattern = re.compile(r': ([^:]+):')
        for line in result.stdout.splitlines():
            match = pattern.search(line)
            if match:
                iface = match.group(1)
                if  not re.match(r'^(lo|veth)', iface) and re.search(r'eth|eno|enp|ens|enx|wlan|tailscale', iface):
                    interfaces.append(iface)
        return interfaces
    except subprocess.CalledProcessError as e:
        print(f"获取网络接口失败: {e}")
        sys.exit(1)

def choose_interface():
    """让用户选择网络接口，3秒后自动选择默认接口"""
    try:
        # 获取默认路由接口
        result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
        default_iface = None
        for line in result.stdout.splitlines():
            parts = line.split()
            if parts and parts[0] == 'default':
                default_iface = parts[4]
                break

        interfaces = list_interfaces()

        if not interfaces:
            print("没有发现可用的网络接口")
            sys.exit(1)

        if len(interfaces) == 1:
            return interfaces[0]

        print(f"检测到多块网卡，请选择（3秒后自动选默认路由网卡 {default_iface}）：")
        for i, iface in enumerate(interfaces, 1):
            print(f"  {i}) {iface}")

        # 等待用户输入，3秒超时
        choice = None
        start_time = time.time()
        while time.time() - start_time < 3:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                choice = sys.stdin.readline().strip()
                break
            time.sleep(0.1)

        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(interfaces):
                return interfaces[idx]

        return default_iface
    except Exception as e:
        print(f"选择接口时出错: {e}")
        sys.exit(1)

def get_network_by_iface(iface):
    """根据选定的接口获取网段信息"""
    try:
        result = subprocess.run(['ip', '-o', '-f', 'inet', 'addr', 'show', 'dev', iface, 'scope', 'global'],
                              capture_output=True, text=True, check=True)
        cidr = None
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                cidr = parts[3]
                break
        if not cidr:
            print(f"接口 {iface} 没有 IPv4 地址")
            sys.exit(1)
        return cidr
    except subprocess.CalledProcessError:
        print(f"获取接口 {iface} 的网络信息失败")
        sys.exit(1)

def lookup_vendor(mac):
    """根据MAC地址查找厂商信息"""
    if not Path(OUI_DB_PATH).exists():
        print(f"OUI数据库文件不存在: {OUI_DB_PATH}")
        return "未知厂商"

    # 处理MAC地址，提取前6位
    try:
        oui = re.sub(r'[:-]', '', mac).upper()[:6]
        with open(OUI_DB_PATH, 'r', encoding='latin-1') as f:
            for line in f:
                if line.startswith(oui):
                    # 提取厂商信息
                    vendor = line.split('\t')[-1].strip()
                    return vendor if vendor else "未知厂商"
        return "未知厂商"
    except Exception as e:
        print(f"查找厂商信息出错: {e}")
        return "未知厂商"

def scan_network(network, iface=None):
    """
    扫描网络内的存活主机。
    - 对于普通局域网接口，优先使用 arp-scan。
    - 对于 tailscale0 接口，使用 ping。
    """
    # 如果是 tailscale 接口，或者arp-scan命令不存在，则强制使用 ping
    is_tailscale = iface and 'tailscale' in iface
    arp_scan_exists = subprocess.run(['which', 'arp-scan'], capture_output=True).returncode == 0

    if is_tailscale or not arp_scan_exists:
        # 对于 /32 的单个地址，直接 ping 即可
        if network.endswith('/32'):
            ip_to_ping = network.split('/')[0]
            print(f"正在 ping 单个地址: {ip_to_ping} ... ", end='', flush=True)
            try:
                # 使用 -c 1 (发送1个包) 和 -W 1 (超时1秒)
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip_to_ping],
                                          capture_output=True, text=True, check=True)
                print("在线")
                # 对于 Tailscale，MAC地址没有意义，可以返回一个占位符或None
                return [(ip_to_ping, 'N/A (Tailscale)')]
            except subprocess.CalledProcessError:
                print("离线或无响应")
                return []
        else:
            # 对于一个网段，执行并行 ping (这部分逻辑可以保持或根据需要调整)
            return ping_scan_subnet(network, iface)

    # 对于非 tailscale 接口，且 arp-scan 存在，使用 arp-scan
    else:
        print(f"使用 arp-scan 扫描 {network} on {iface or 'default'}...")
        try:
            cmd = ['arp-scan', '-l', '-g', '-x', '-r', '3', network] # 减少重试次数
            if iface:
                cmd.extend(['--interface', iface])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            devices = []
            pattern = re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f:]+)\s+')
            for line in result.stdout.splitlines():
                match = pattern.match(line)
                if match:
                    devices.append((match.group(1), match.group(2)))
            return devices
        except subprocess.CalledProcessError as e:
            print(f"arp-scan 扫描失败: {e.stderr}")
            return []
        except Exception as e:
            print(f"扫描网络时出现未知错误: {e}")
            return []

def ping_scan_subnet(network, iface=None):
    """使用 ping 并行扫描整个子网"""
    base = ".".join(network.split('/')[0].split('.')[:3])
    print(f"使用 ping 并行扫描 {base}.1-254 ... ", end='', flush=True)

    live_hosts = []

    def ping_host(ip):
        try:
            subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return ip
        except subprocess.CalledProcessError:
            return None

    with ThreadPoolExecutor(max_workers=100) as executor:
        ips_to_scan = [f"{base}.{i}" for i in range(1, 255)]
        results = executor.map(ping_host, ips_to_scan)

        for ip in results:
            if ip:
                live_hosts.append((ip, 'N/A (Ping Scan)'))

    print(f"完成，发现 {len(live_hosts)} 台主机")
    return live_hosts


def get_network_by_iface_ipv6(iface):
    """根据选定的接口获取IPv6网段信息"""
    try:
        result = subprocess.run(['ip', '-o', '-f', 'inet6', 'addr', 'show', 'dev', iface, 'scope', 'global'],
                              capture_output=True, text=True, check=True)
        ipv6_addresses = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                ipv6_cidr = parts[3]
                ipv6_addresses.append(ipv6_cidr)
        return ipv6_addresses if ipv6_addresses else None
    except subprocess.CalledProcessError:
        print(f"获取接口 {iface} 的IPv6网络信息失败")
        return None


def ipv6_scan(iface):
    """扫描局域网内的IPv6主机"""
    try:
        devices = []
        # 使用ip命令查看指定接口的IPv6邻居表
        result = subprocess.run(['ip', '-6', 'neigh', 'show', 'dev', iface],
                              capture_output=True, text=True, check=True)
        pattern = re.compile(r'^([0-9a-f:]+)\s+lladdr\s+([0-9a-f:]+)')
        for line in result.stdout.splitlines():
            match = pattern.match(line)
            if match:
                devices.append((match.group(1), match.group(2)))
        return devices
    except Exception as e:
        print(f"扫描IPv6网络时出错: {e}")
        return []


def main(args=None):
    # 处理不同类型的参数
    if args is None:
        # 直接运行脚本的情况
        iface = choose_interface()
    elif isinstance(args, str):
        # 从lsps.py传递字符串参数的情况
        if args.lower() == 'true':
            iface = choose_interface()
        else:
            iface = args
    else:
        # 期望args有interface属性的情况
        if hasattr(args, 'interface') and args.interface:
            if str(args.interface).lower() == 'true':
                iface = choose_interface()
            else:
                iface = args.interface
        else:
            iface = choose_interface()
    # 检查必要的命令
    # need_cmd('ip')
    # need_cmd('awk')
    # need_cmd('ping')
    # need_cmd('arp')

    # 获取IPv4和IPv6网络信息
    ipv4_network = get_network_by_iface(iface)
    ipv6_networks = get_network_by_iface_ipv6(iface)

    print(f"\n已选择接口：{iface}")
    print(f"IPv4网段：{ipv4_network}")
    if ipv6_networks:
        print(f"IPv6地址：{', '.join(ipv6_networks)}")
    else:
        print("未检测到IPv6地址")
    print()

    # 检查OUI数据库文件
    if not Path(OUI_DB_PATH).exists():
        print(f"错误：OUI数据库文件不存在 - {OUI_DB_PATH}")
        print("请先下载OUI数据库文件并更新路径：")
        print("wget https://standards-oui.ieee.org/oui/oui.txt -O /path/to/local/oui.txt")
        sys.exit(1)

    # 开始IPv4扫描
    print("开始IPv4扫描 ...")
    print(f"IPv4地址\t\tMAC\t\t\t厂商")
    print("-" * 60)

    ipv4_devices =  scan_network(ipv4_network, iface)
    if ipv4_devices:
        for ip, mac in ipv4_devices:
            vendor = lookup_vendor(mac)
            print(f"{ip:15}\t{mac:17}\t{vendor}")
    else:
        print("未发现IPv4设备")

    print()

    # 开始IPv6扫描
    print("开始IPv6扫描 ...")
    print(f"IPv6地址\t\t\t\tMAC\t\t\t厂商")
    print("-" * 80)

    ipv6_devices = ipv6_scan(iface)
    if ipv6_devices:
        for ip, mac in ipv6_devices:
            vendor = lookup_vendor(mac)
            print(f"{ip:38}\t{mac:17}\t{vendor}")
    else:
        print("未发现IPv6设备")

    print()
    print(f"扫描完成，共发现 {len(ipv4_devices)} 个IPv4设备和 {len(ipv6_devices)} 个IPv6设备。")

if __name__ == "__main__":
    main()
