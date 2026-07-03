from nvitop import Device
import psutil

for dev in Device.all():
    gpu_id = dev.index
    gpu_procs = dev.processes()
    if not gpu_procs:
        print(f"GPU{gpu_id}: 无占用进程\n")
        continue

    print(f"===== GPU {gpu_id} 进程列表 =====")
    for pid, proc in gpu_procs.items():
        print(f"PID: {pid}")

        # 1. 修复用户名：username() 是方法，必须加括号
        try:
            user = proc.username()
        except Exception:
            user = "未知(权限不足)"
        print(f"用户: {user}")

        # 2. 捕获cwd权限拒绝异常
        try:
            work_dir = proc.cwd()
        except psutil.AccessDenied:
            work_dir = "无权限读取cwd"
        except Exception as e:
            work_dir = f"读取失败: {str(e)}"
        print(f"工作目录: {work_dir}")

        # 命令行一般很少权限报错，简单兜底
        try:
            cmd_list = proc.cmdline()
            full_cmd = proc.command()
        except Exception:
            cmd_list = []
            full_cmd = "无法读取命令"

        print(f"完整命令行数组: {cmd_list}")
        print(f"拼接完整命令: {full_cmd}")
        print(f"显存占用: {proc.gpu_memory_human()}")
        print("-" * 100)