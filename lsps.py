import psutil
import argparse
import os
from typing import List, Dict
def get_process_info(pid=None, cmd_name=None, proc_directory=None):
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
            elif proc_directory and proc.info['cwd'] is not None and os.path.commonpath([proc.info['cwd'], proc_directory]) == os.path.abspath(proc_directory):
                processes.append(proc.info)
                """  # 这里的逻辑是检查进程的当前工作目录是否与给定目录匹配
                    📌 说明：
                os.path.commonpath([a, b]) 返回两个路径的最长公共前缀。
                如果 cwd 是 proc_directory 的子目录，那么公共路径就应该是 proc_directory。
                使用 os.path.abspath 确保路径标准化，避免相对路径干扰判断。
                ✅ 示例：
                cwd	proc_directory	匹配？
                /data/dir1	/data/dir1	✅ 是自身
                /data/dir1/app	/data/dir1	✅ 是子目录
                /data/dir2	/data/dir1	❌ 不匹配
                /data/dir1/../dir2	/data/dir1	❌ 实际路径不在其下

                """
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


def find_processes_using_directory(directory: str) -> List[Dict]:
    """
    查找所有打开了指定目录中文件的进程。

    参数:
        directory (str): 要检查的目录路径。

    返回:
        List[Dict]: 包含匹配进程信息的列表，每个元素为：
            {
                'pid': int,
                'name': str,
                'username': str,
                'open_files': List[str]
            }
    """
    directory = os.path.abspath(directory)
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            # 获取当前进程打开的所有文件路径
            open_files = [f.path for f in proc.open_files()]
            if not open_files:
                continue

            # 筛选属于目标目录的文件
            matched_files = [
                f for f in open_files
                if os.path.commonpath([f, directory]) == directory
            ]

            if matched_files:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'username': proc.info['username'],
                    'open_files': matched_files
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes

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
    打印监听端口信息，并显示对应的命令行信息。
    """
    if not ports:
        print("没有找到监听的端口。")
        return

    print("PID\tPort\tIP\t\tStatus\t\tCommand Line")
    print("-" * 60)
    for port_info in ports:
        try:
            # 获取进程对象并读取 cmdline
            proc = psutil.Process(port_info['pid'])
            cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else "无命令行信息"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            cmdline = "无法获取命令行信息"

        print(f"{port_info['pid']}\t{port_info['port']}\t{port_info['ip']}\t{port_info['status']}\t{cmdline}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="通过 PID、命令名或进程名查找进程")
    parser.add_argument("-id", "--pid", type=int, help="进程 ID")
    parser.add_argument("-c", "--cmd", type=str, help="命令名或命令行的一部分")#,default="python"
    parser.add_argument("-du", "--directory_use", type=str, help="进程占用目录")

    parser.add_argument("-d", "--directory", type=str, help="进程运行目录")
    # 修改 -l 参数，使其可以接受可选的端口号
    parser.add_argument("-p", "--listening", nargs='?', const=True, type=int,
                       help="查看监听的端口。不带参数时显示所有端口，带数字参数时显示指定端口的进程信息")
    args = parser.parse_args()
    if args.directory:
        # 将传入的目录转换为绝对路径
        args.directory = os.path.abspath(args.directory)
        print(f"目录参数已转换为绝对路径：{args.directory}")

    if args.directory_use:
        # 将传入的目录转换为绝对路径
        args.directory_use = os.path.abspath(args.directory_use)
        print(f"目录参数已转换为绝对路径：{args.directory_use}")

    if args.listening is not None:
        if isinstance(args.listening, bool):
            # 不带参数的 -p，显示所有端口
            ports = get_listening_ports()
            print_listening_ports(ports)
        else:
            # 带端口参数的 -p，查找对应端口的进程
            ports = get_listening_ports()
            matching_ports = [p for p in ports if p['port'] == args.listening]
            if matching_ports:
                for port_info in matching_ports:
                    processes = get_process_info(pid=port_info['pid'])
                    print(f"\n监听端口 {args.listening} 的进程信息：")
                    print_process_info(processes)
            else:
                print(f"未找到监听端口 {args.listening} 的进程。")
    elif args.directory_use is not None:
        # 处理 -du 参数
        result = find_processes_using_directory(args.directory_use)
        if not result:
            print(f"没有进程占用目录 {args.directory_use}")
        else:
            print(f"以下进程占用了目录 {args.directory_use}：")
            for p in result:
                print(f"PID: {p['pid']}, Name: {p['name']}, User: {p['username']}")
                print("占用文件:")
                for f in p['open_files']:
                    print(f"  - {f}")
                print("-" * 40)
    else:
        if not any([args.pid, args.cmd, args.directory]):
            args.cmd = "python"
        processes = get_process_info(pid=args.pid, cmd_name=args.cmd, proc_directory=args.directory)
        print_process_info(processes)
if __name__ == "__main__":
    main()
