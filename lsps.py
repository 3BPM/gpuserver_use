import psutil
import argparse

def get_process_info(pid=None, cmd_name=None, proc_name=None):
    """
    根据 PID、命令名或进程名查找匹配的进程。

    参数：
        pid (int): 进程 ID
        cmd_name (str): 命令名（部分命令行字符串）
        proc_name (str): 进程名

    返回：
        list: 包含匹配进程信息的列表
    """

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'cwd']):
        try:
            if pid and proc.info['pid'] == pid:  # Changed 'in' to '=='
                processes.append(proc.info)
            elif cmd_name and cmd_name in ' '.join(proc.info['cmdline'] or []):
                processes.append(proc.info)
            elif proc_name and proc.info['name'] in proc_name:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def print_process_info(processes):
    """
    打印进程的详细信息。

    参数：
        processes (list): 包含进程信息的列表
    """
    if not processes:
        print("未找到匹配的进程。")
        return

    for proc in processes:
        pid = proc['pid']
        try:
            cwd = proc['cwd']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            cwd = "权限不足"

        cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else "无命令行信息"
        username = proc['username'] if proc['username'] else "未知用户"

        print(f"PID: {pid}")
        print(f"CWD: {cwd}")
        print(f"具体命令: {cmdline}")
        print(f"用户: {username}")
        print("-" * 40)

def get_listening_ports(max_port=10000):
    """
    获取所有监听中的端口，默认返回10000以下的端口

    参数：
        max_port (int): 最大端口号

    返回：
        list: 包含监听端口信息的列表
    """
    listening_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.laddr.port < max_port:
            listening_ports.append({
                'pid': conn.pid,
                'port': conn.laddr.port,
                'ip': conn.laddr.ip,
                'status': conn.status
            })
    return sorted(listening_ports, key=lambda x: x['port'], reverse=True)
def print_listening_ports(ports):
    """
    打印监听端口信息

    参数：
        ports (list): 包含端口信息的列表
    """
    if not ports:
        print("没有找到监听的端口。")
        return

    print("PID\tPort\tIP\t\tStatus")
    print("-" * 40)
    for port_info in ports:
        print(f"{port_info['pid']}\t{port_info['port']}\t{port_info['ip']}\t{port_info['status']}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="通过 PID、命令名或进程名查找进程")
    parser.add_argument("-id", "--pid", type=int, help="进程 ID")
    parser.add_argument("-c", "--cmd", type=str, help="命令名或命令行的一部分")
    parser.add_argument("-n", "--name", type=str, help="进程名")
    # 修改 -l 参数，使其可以接受可选的端口号
    parser.add_argument("-p", "--listening_port", nargs='?', const=True, type=int,
                       help="查看监听的端口。不带参数时显示所有端口，带数字参数时显示指定端口的进程信息")
    args = parser.parse_args()

    if args.listening is not None:
        if isinstance(args.listening, bool):
            # 不带参数的 -l，显示所有端口
            ports = get_listening_ports()
            print_listening_ports(ports)
        else:
            # 带端口参数的 -l，查找对应端口的进程
            ports = get_listening_ports()
            matching_ports = [p for p in ports if p['port'] == args.listening]
            if matching_ports:
                for port_info in matching_ports:
                    processes = get_process_info(pid=port_info['pid'])
                    print(f"\n监听端口 {args.listening} 的进程信息：")
                    print_process_info(processes)
            else:
                print(f"未找到监听端口 {args.listening} 的进程。")
    else:
        # 原有逻辑保持不变
        if not any([args.pid, args.cmd, args.name]):
            args.cmd = "python"
        processes = get_process_info(pid=args.pid, cmd_name=args.cmd, proc_name=args.name)
        print_process_info(processes)
if __name__ == "__main__":
    main()
