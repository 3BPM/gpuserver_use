# ~/.bashrc - Custom Bash Configuration

# --- Basic Setup ---

# Define script root directory relative to home
# Using $HOME makes it portable across different usernames
SCRIPT_ROOT="$HOME/s"

# Set Hugging Face endpoint mirror (recommended for users in China)
export HF_ENDPOINT=https://hf-mirror.com

# --- GPU Selection ---

# Alias to source the script that selects the least busy GPU
alias selectgpu="source \"$SCRIPT_ROOT/select_best_gpu.sh\""
echo "[Info] Select least busy GPU using: selectgpu"

# --- Common Application Starters ---

# Alias to start AgentUI
alias startA="$SCRIPT_ROOT/agentui/start.sh"

# --- Dify Management Functions ---

# Function to start Dify services in detached mode
start_dify() {
    echo "Starting Dify services..."
    if command cd "$HOME/build/dify/docker"; then
        docker compose up -d
    else
        echo "Error: Could not change directory to $HOME/build/dify/docker" >&2
        return 1
    fi
}

# Function to update Dify: stop, pull changes, pull images, restart
update_dify() {
    echo "Updating Dify..."
    if command cd "$HOME/build/dify/docker"; then
        docker compose down && \
        git pull origin main && \
        docker compose pull && \
        docker compose up -d
        echo "Dify update complete."
    else
        echo "Error: Could not change directory to $HOME/build/dify/docker" >&2
        return 1
    fi
}

# Function to stop and remove Dify containers/networks
down_dify() {
    echo "Stopping Dify services..."
    if command cd "$HOME/build/dify/docker"; then
        docker compose down
    else
        echo "Error: Could not change directory to $HOME/build/dify/docker" >&2
        return 1
    fi
}

# 在 .bashrc 中只检测一次并缓存
_SUDO_CACHE_FILE="$HOME/.sudo_as_admin_successful"

# 检测并缓存结果
_check_sudo_access() {
    # 如果已经是 root
    [ "$EUID" -eq 0 ] && { echo "root"; return; }

    # 检查缓存（1小时有效）
    if [ -f "$_SUDO_CACHE_FILE" ]; then
        local cache_time=$(stat -c %Y "$_SUDO_CACHE_FILE" 2>/dev/null)
        local now=$(date +%s)
        if [ $((now - cache_time)) -lt 3600 ]; then
            cat "$_SUDO_CACHE_FILE"
            return
        fi
    fi

    # 实际检测
    if sudo -n true 2>/dev/null; then
        echo "sudo" > "$_SUDO_CACHE_FILE"
        echo "sudo"
    else
        echo "" > "$_SUDO_CACHE_FILE"
        echo ""
    fi
}

# 在 bashrc 加载时检测一次
SUDO_PREFIX="$(_check_sudo_access)"

# 定义别名
alias lsps="${SUDO_PREFIX:+sudo }python3 \"$SCRIPT_ROOT/lsps.py\""
alias lsg="${SUDO_PREFIX:+sudo }python3 \"$SCRIPT_ROOT/lsgroup.py\""
alias lsug="${SUDO_PREFIX:+sudo }python3 \"$SCRIPT_ROOT/lsuser_sgroup.py\""

# Function to switch the 'python' alias (Use with caution!)
# Example: setpy /usr/bin/python3.9
# Warning: Overriding the default 'python' can break system scripts.
# Consider using virtual environments (conda, venv) instead.
setpy() {
    if [[ -z "$1" ]]; then
        echo "Usage: setpy /path/to/python/executable" >&2
        return 1
    fi
    if [[ ! -x "$1" ]]; then
         echo "Error: '$1' is not an executable file." >&2
         return 1
    fi
    alias python="$1"
    echo "Python alias temporarily set to: $1"
    echo "Note: This only affects the current shell session."
}


# Function to launch TensorBoard, finding an available port
# Usage: tb [log_directory] [start_port]
# Example: tb ./my_logs 8000
# Example: tb # uses ./logs and port 7777
tb() {
    local logdir="${1:-./logs}" # Default log directory: ./logs
    local port="${2:-7777}"   # Default start port: 7777
    local max_attempts=100
    local attempts=0

    # Check if log directory exists
    if [[ ! -d "$logdir" ]]; then
        echo "Warning: Log directory '$logdir' does not exist. Creating it."
        mkdir -p "$logdir" || { echo "Error: Failed to create log directory '$logdir'" >&2; return 1; }
    fi

    # Find an available port using 'ss' (more modern than netstat)
    # ss -Htan 'sport = :port' checks for listening TCP sockets on the specified port
    while ss -Htan "sport = :$port" | grep -q 'LISTEN' && [ $attempts -lt $max_attempts ]; do
        echo "Port $port is occupied, trying next port..."
        ((port++))
        ((attempts++))
    done

    if [ $attempts -ge $max_attempts ]; then
        echo "Error: Could not find an available port after $max_attempts attempts." >&2
        return 1
    fi

    echo "Starting TensorBoard on port $port with logdir: $logdir"
    # Run in background, redirect stdout/stderr to /dev/null to avoid cluttering terminal
    #python -m tensorboard.main --logdir "$logdir" --port "$port" > /dev/null 2>&1 &
    tensorboard --logdir "$logdir" --port "$port" > /dev/null 2>&1 &
    # Give it a moment to start
    sleep 1
    echo "TensorBoard launched in background. Access at: http://localhost:$port"
    # If you need to capture the port number in a script, use command substitution:
    # local_port=$(tb mylogs 8000; echo $?) # This captures the function's *exit status*
    # To get the *port number* itself, the function would need to echo it as the *last* thing it does.
    # For interactive use, printing the URL is usually sufficient.
}

# Alias to check environment using a custom script
alias envok="python3 \"$SCRIPT_ROOT/envok.py\""
echo "[Info] Check environment status using: envok"



# Alias for quick PyTorch GPU test
alias gput="python3 \"$SCRIPT_ROOT/torchgputest.py\""

# Alias for custom network (?) script
alias fq="$SCRIPT_ROOT/fq.sh"

# Alias to view log file for fq script
alias fqlog="cat \"$SCRIPT_ROOT/fanqiang/logfanqiang\""

# Alias for custom 'suji' script
alias sj="$SCRIPT_ROOT/suji.sh"

# Alias for custom server script
alias serv="python -m http.server 8000 >> logserver 2>&1 &"


# Alias to run environment launch script after selecting GPU
alias crlaunchjson="selectgpu && \"$SCRIPT_ROOT/envlaunch.sh\""

# Function to forward a remote port via SSH, finding an available local port
# Usage: forwardport user@hostname [remote_port] [start_local_port]
# Example: forwardport myuser@remote.server 8080 9000
forwardport() {
    local remote_host="$1"
    local remote_port="${2:-80}"  # Default remote port 80
    local local_port="${3:-$remote_port}" # Default local port matches remote, or use provided start
    local max_attempts=100
    local attempts=0

    if [[ -z "$remote_host" ]]; then
        echo "Usage: forwardport user@hostname [remote_port] [start_local_port]" >&2
        return 1
    fi

    # Find an available local port
    while ss -Htan "sport = :$local_port" | grep -q 'LISTEN' && [ $attempts -lt $max_attempts ]; do
        ((local_port++))
        ((attempts++))
    done

     if [ $attempts -ge $max_attempts ]; then
        echo "Error: Could not find an available local port after $max_attempts attempts." >&2
        return 1
    fi

    echo "Attempting to forward remote port $remote_port on $remote_host to local port $local_port..."
    ssh -f -N -L "$local_port:127.0.0.1:$remote_port" "$remote_host"

    # Check if ssh tunnel was established successfully (basic check)
    if [ $? -eq 0 ]; then
       echo "Successfully forwarded remote $remote_host:$remote_port to local http://localhost:$local_port"
       echo "SSH tunnel running in the background. Use 'pkill -f \"ssh -f -N -L $local_port:127.0.0.1:$remote_port $remote_host\"' to stop it."
    else
       echo "Error: Failed to establish SSH tunnel." >&2
       return 1
    fi
}


# --- File System & Navigation ---

# Alias for find: find file by name in current directory downwards
# Usage: findname '*pattern*'
alias findname="find . -name" # Renamed from f

MV() {
    local src="" dest="" dry_run=false verbose=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                cat << 'EOF'
Usage: MV [OPTIONS] <source> <destination>

Simulates Windows-style "Move and Merge":
- Moves files from source to destination.
- Overwrites files in destination if they have the same name.
- KEEPS files in destination that do not exist in source (Merge).
- Deletes source files/directories after successful transfer.

Options:
  -h, --help       Show this help message and exit
  -n, --dry-run    Perform a trial run without making changes
  -v, --verbose    Show detailed output
EOF
                return 0
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -*)
                echo "Unknown option: $1" >&2
                return 1
                ;;
            *)
                if [[ -z "$src" ]]; then
                    src="$1"
                elif [[ -z "$dest" ]]; then
                    dest="$1"
                else
                    echo "Error: Too many arguments." >&2
                    return 1
                fi
                shift
                ;;
        esac
    done

    # 检查参数
    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Error: Both source and destination must be specified." >&2
        return 1
    fi

    if [[ ! -d "$src" ]]; then
        echo "Error: Source directory does not exist: $src" >&2
        return 1
    fi

    # 规范化路径：确保 src 和 dest 都以 / 结尾
    # 这对于将 src 的内容合并到 dest 内部至关重要
    src="${src%/}/"
    dest="${dest%/}/"

    # 检查目标目录
    if [[ ! -d "$dest" ]]; then
        echo "Destination directory does not exist: $dest"
        if [[ "$dry_run" == true ]]; then
            echo "(Dry-run) Would create directory: $dest"
        else
            read -p "Create it? (y/N): " confirm
            if [[ $confirm =~ ^[Yy] ]]; then
                mkdir -p "$dest"
            else
                echo "Aborted." >&2
                return 1
            fi
        fi
    fi

    # ---------------------------------------------------------
    # 构建 rsync 命令 (核心修改部分)
    # ---------------------------------------------------------
    local cmd=("rsync" "-avh"
               "--partial"
               "--info=progress2,name0"
               "--remove-source-files"  # 关键：传输成功后删除源文件
              )

    # 注意：这里去掉了 --delete-after，因为你要的是合并而不是镜像

    # 添加 verbose
    [[ "$verbose" == true ]] && cmd+=("-v")

    # 添加 dry-run
    [[ "$dry_run" == true ]] && cmd+=("--dry-run")

    # 添加排除项
    cmd+=(
        --exclude='*.tmp'
        --exclude='__pycache__'
        --exclude='*.log'
        --exclude='*.backup'
    )

    # 添加源和目标
    cmd+=("$src" "$dest")

    # 输出调试信息
    echo "---------------------------------------------------"
    echo "Mode: Move & Merge (Windows Style)"
    echo "From: $src"
    echo "To:   $dest"
    if [[ "$dry_run" == true ]]; then
        echo "⚠️  DRY RUN MODE: No files will be moved or deleted."
    fi
    echo "Running: ${cmd[*]}"
    echo "---------------------------------------------------"

    # 这里的 sleep 可以保留，给你反悔的机会
    sleep 2

    # 执行 rsync
    if "${cmd[@]}"; then
        echo "✅ File transfer complete."

        # ---------------------------------------------------------
        # 后处理：清理源目录的空骨架
        # ---------------------------------------------------------
        # rsync --remove-source-files 只删文件，不删目录。
        # 我们需要手动清理 src 中已经变空的目录。

        if [[ "$dry_run" == false ]]; then
            echo "🧹 Cleaning up empty directories in source..."
            # -depth 确保先删子目录再删父目录
            # 2>/dev/null 忽略那些因为排除文件导致目录非空的报错
            find "$src" -depth -type d -empty -delete 2>/dev/null

            # 检查源目录是否完全消失（如果所有文件都移走了）
            if [[ ! -d "$src" ]]; then
                echo "✨ Source directory removed completely."
            else
                echo "⚠️  Source directory still exists (likely contains excluded files)."
            fi
        else
            echo "(Dry-run) Would remove empty directories in: $src"
        fi

    else
        echo "❌ Failed: rsync command returned error." >&2
        return 1
    fi
}

# Alias for ack (better grep for code) - find files containing pattern
# Consider 'grep -rl PATTERN .' as a fallback if ack isn't installed
alias findinfiles="ack -l" # Renamed from 文件内找

# Alias to change to the real physical directory (resolving symlinks)
alias cdp="cd -P ." # Renamed from 实际
alias lsp="pwd -P"

# --- Package & Environment Management ---

# Alias to shorten pip upgrade
alias U="pip install --upgrade"

# Alias to reload .bashrc configuration
alias sx="source ~/.bashrc"
echo "[Info] Reload configuration using: sx"

# --- Remote Operations (rsync/ssh) ---

# Base rsync alias (might be more useful as a function if arguments vary)
alias rsync_pull="rsync -avz --progress -e ssh" # Added compression and progress
alias pull='rsync -az --info=progress2 --no-inc-recursive -e ssh'

# Example Usage: rsync_pull user@host:/remote/path /local/path

# Specific alias to pull 's' directory from 'a800t' and reload bashrc
alias pull_s="rsync -avz --progress -e ssh 3090raw:~/s/ \"$HOME/s/\" && sx" # Note trailing slashes for directory content sync
alias pull_sshconfig="rsync -avz --progress -e ssh 3090raw:~/.ssh/config ~/.ssh/config"
echo "[Info] Pull ~/s from a800t and reload: pull_s_a800t"

# --- Hugging Face Downloader ---
alias hfdownload="bash $SCRIPT_ROOT/hf-fast.sh"

# --- Startup Information ---
chmod +x $SCRIPT_ROOT/chsrc-x64-linux
alias chsrc="sudo $SCRIPT_ROOT/chsrc-x64-linux"
alias showdockers="bash $SCRIPT_ROOT/showdockers.sh"
alias changemac="bash $SCRIPT_ROOT/changemac.sh"
alias showbashhistory="bash $SCRIPT_ROOT/other_bash_history.sh"
echo "-----------------------------------------------------"
echo " Bash environment initialized. Key commands:"
echo "   GPU/System/Docker: selectgpu, lsps,lsg,lsug, gput"
echo "   Dify Mgmt:  start_dify, update_dify, down_dify"
echo "   Dev Tools:  tb, setpy (use carefully!)"
echo "   Network:    chsrc,fq, fqlog,changmac, forwardport <user@host> [remote_port]"
echo "   File/Nav:   findname <pattern>,findinfiles ,cdp, lsp,l=listtime,d=lssize"
echo "   Sync:       MV,pull_s_a800t, pull <src> <dest>"
echo "   Package/Env: U <package>, sx, envok"
echo "   Misc:       startA, sj, serv, hfdownload"
echo "-----------------------------------------------------"

# List conda environments on shell startup (can be slow, uncomment if needed)
# echo "Available Conda environments:"
conda env list

c() {
    if [ $# -ne 1 ]; then
        echo "请输入环境名称"
    return 1
    fi
    if conda activate "$1"; then
        envok
    else
        echo "激活失败..."
        return 1
    fi
}
dr() {
    docker exec -it "$1" bash
}

alias l='ls -lta | tail -n +2; echo "=== 统计信息 ==="; files=$(ls -A | wc -l); dirs=$(find . -maxdepth 1 -type d ! -name "." | wc -l); echo "总条目数: $files | 文件夹: $dirs | 文件: $((files - dirs))"'

# 将此函数放入 ~/.bashrc 或 ~/.zshrc
function lt3() {
    echo "正在扫描子目录 (深度: 3)..."

    # 遍历当前目录下的每一个文件/文件夹
    for item in *; do
        # 跳过不存在的文件（处理空目录通配符情况）
        [ -e "$item" ] || continue

        # 核心逻辑：
        # 1. find "$item": 在当前item内部查找
        # 2. -maxdepth 3: 限制递归深度为3层
        # 3. -printf: 打印 "秒级时间戳(用于排序) 人类可读时间"
        # 4. sort -rn | head -n 1: 找出内部所有文件中最新的那个时间

        latest_info=$(find "$item" -maxdepth 3 -printf "%T@ %TY-%Tm-%Td_%TH:%TM:%S\n" 2>/dev/null | sort -rn | head -n 1)

        # 提取时间戳用于总排序，提取格式化时间用于显示
        # 输出格式: [时间戳] [格式化时间] [文件名/文件夹名]
        if [ -n "$latest_info" ]; then
             # 拆分 find 的结果
             timestamp=$(echo "$latest_info" | awk '{print $1}')
             humantime=$(echo "$latest_info" | awk '{print $2}')

             # 输出一行，稍后用于整体排序
             echo "$timestamp $humantime $item"
        fi
    done | sort -rn | awk '{printf "\033[32m%s\033[0m  \033[1m%s\033[0m\n", $2, $3}'
}
d() {
    for f in *; do
    du -sh "$f" | awk '{print $1}'  # 获取大小
    ls -ld --time-style=long-iso "$f" | awk '{print $6, $7, $8, $9}'  # 获取修改时间和文件名
    done | paste -d ' ' - - | sort -k1,1hr
}

#加入gpu抢卡默认1.sh
alias rs="python \"$SCRIPT_ROOT/runscript.py\""
