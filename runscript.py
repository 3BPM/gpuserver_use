#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import argparse

def get_gpu_memory():
    """获取GPU显存信息，返回总显存和空闲显存（单位：GB）"""
    try:
        # 使用nvidia-smi命令获取显存信息
        result = subprocess.run([
            'nvidia-smi',
            '--query-gpu=memory.total,memory.free',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, check=True)

        # 解析输出，处理多GPU情况
        lines = result.stdout.strip().split('\n')
        gpu_info = []

        for i, line in enumerate(lines):
            parts = line.split(', ')
            if len(parts) >= 2:
                total_mem = int(parts[0])
                free_mem = int(parts[1])
                total_gb = total_mem / 1024  # 转换为GB
                free_gb = free_mem / 1024    # 转换为GB
                gpu_info.append({
                    'gpu_id': i,
                    'total_gb': total_gb,
                    'free_gb': free_gb,
                    'usage_percent': (total_mem - free_mem) / total_mem * 100
                })

        return gpu_info

    except subprocess.CalledProcessError as e:
        print(f"执行nvidia-smi命令失败: {e}")
        return None
    except FileNotFoundError:
        print("未找到nvidia-smi命令，请确保NVIDIA驱动已安装")
        return None
    except Exception as e:
        print(f"获取GPU信息时发生错误: {e}")
        return None

def wait_for_gpu_memory(required_free_gb=60, check_interval=30, max_wait_time=None):
    """
    等待直到有GPU的空闲显存大于指定值
    """
    start_time = time.time()
    last_print_time = 0
    print_interval = 300  # 每5分钟打印一次状态

    print(f"等待GPU空闲显存 >= {required_free_gb}GB...")
    print(f"检查间隔: {check_interval}秒")
    if max_wait_time:
        print(f"最大等待时间: {max_wait_time}秒")

    while True:
        current_time = time.time()

        # 检查最大等待时间
        if max_wait_time and (current_time - start_time) > max_wait_time:
            print(f"达到最大等待时间 {max_wait_time}秒，退出等待")
            return False

        gpu_info = get_gpu_memory()
        if not gpu_info:
            print("无法获取GPU信息，等待10秒后重试...")
            time.sleep(10)
            continue

        # 打印状态（每5分钟或第一次）
        if current_time - last_print_time >= print_interval or last_print_time == 0:
            print("\n" + "="*50)
            print(f"GPU显存状态检查 (时间: {time.strftime('%Y-%m-%d %H:%M:%S')})")
            print("="*50)

            for gpu in gpu_info:
                status = "✓ 满足" if gpu['free_gb'] >= required_free_gb else "✗ 不满足"
                print(f"GPU {gpu['gpu_id']}: 总显存{gpu['total_gb']:.1f}GB, "
                      f"空闲{gpu['free_gb']:.1f}GB, 使用率{gpu['usage_percent']:.1f}% - {status}")

            last_print_time = current_time

        # 检查是否有满足条件的GPU
        suitable_gpus = [gpu for gpu in gpu_info if gpu['free_gb'] >= required_free_gb]

        if suitable_gpus:
            # 选择空闲显存最多的GPU
            best_gpu = max(suitable_gpus, key=lambda x: x['free_gb'])
            print(f"\n🎉 找到满足条件的GPU {best_gpu['gpu_id']}!")
            print(f"   空闲显存: {best_gpu['free_gb']:.1f}GB >= 要求的{required_free_gb}GB")
            print(f"   总等待时间: {current_time - start_time:.1f}秒")

            # 设置环境变量，让后续脚本知道使用哪个GPU
            os.environ['CUDA_VISIBLE_DEVICES'] = str(best_gpu['gpu_id'])

            return True

        # 显示简短的等待提示（每30秒）
        wait_time = current_time - start_time
        hours = int(wait_time // 3600)
        minutes = int((wait_time % 3600) // 60)
        seconds = int(wait_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        max_free = max(gpu['free_gb'] for gpu in gpu_info)
        print(f"[{time_str}] 最大空闲显存: {max_free:.1f}GB/{required_free_gb}GB, 继续等待...")

        time.sleep(check_interval)

def run_target_script(script_path):
    """运行目标脚本"""

    # 检查脚本是否存在
    if not os.path.exists(script_path):
        print(f"❌ 目标脚本不存在: {script_path}")
        return False

    print(f"\n🚀 开始运行脚本: {script_path}")
    print("="*60)

    try:
        # 运行脚本
        result = subprocess.run(
            ['bash', script_path],
            check=True
        )
        print(f"\n✅ 脚本执行成功!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 脚本执行失败，退出码: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ 运行脚本时发生错误: {e}")
        return False

def main():
    """主函数"""
    # 配置参数
    CHECK_INTERVAL = 30    # 检查间隔（秒）
    MAX_WAIT_TIME = 24 * 3600  # 最大等待24小时
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='GPU显存监控并运行指定脚本')
    parser.add_argument('script_path', nargs='?', default='./1.sh',
                        help='要运行的脚本路径 (默认: ./1.sh)')
    # 修改: 添加显存参数
    parser.add_argument('--memory', type=int, default=50,
                        help='需要的空闲显存大小(GB) (默认: 50GB)')
    args = parser.parse_args()
    script_path = args.script_path
    REQUIRED_FREE_GB = args.memory

    print("="*60)
    print("GPU显存监控脚本")
    print("="*60)
    print(f"目标: 等待GPU空闲显存 >= {REQUIRED_FREE_GB}GB")
    print(f"然后运行: {script_path}")
    print("="*60)

    # 首先检查一次当前状态
    gpu_info = get_gpu_memory()
    if gpu_info:
        print("当前GPU状态:")
        for gpu in gpu_info:
            print(f"  GPU {gpu['gpu_id']}: {gpu['free_gb']:.1f}GB/{gpu['total_gb']:.1f}GB 空闲")

    # 等待满足条件的GPU
    if wait_for_gpu_memory(REQUIRED_FREE_GB, CHECK_INTERVAL, MAX_WAIT_TIME):
        # 运行目标脚本
        success = run_target_script(script_path)
        sys.exit(0 if success else 1)
    else:
        print("❌ 等待超时，未找到满足条件的GPU")
        sys.exit(1)

if __name__ == "__main__":
    main()
