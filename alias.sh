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

# --- Development & Monitoring Tools ---

# Alias to list processes (requires sudo, be careful)
alias lsps="sudo python3 \"$SCRIPT_ROOT/lsps.py\""
alias lsg="sudo python3 \"$SCRIPT_ROOT/lsgroup.py\""
alias lsug="sudo python3 \"$SCRIPT_ROOT/lsuser_sgroup.py\""

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
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        echo "Usage: MV [OPTIONS]"
        echo "Wrapper for rsync with --partial and --progress enabled by default."
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message and exit"
        echo ""
        echo "Environment Variables:"
        echo "  SRC            Source directory (trailing slash recommended)"
        echo "  DEST           Destination directory (trailing slash recommended)"
        return 0
    fi

    if [[ -z "$SRC" || -z "$DEST" ]]; then
        echo "Error: Both SRC and DEST environment variables must be set." >&2
        return 1
    fi

    rsync -avh --partial --progress "$SRC/" "$DEST/"
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
alias chsrc="$SCRIPT_ROOT/chsrc-x64-linux"
alias showdockers="bash $SCRIPT_ROOT/showdockers.sh"
alias changemac="bash $SCRIPT_ROOT/changemac.sh"
alias showbashhistory="bash $SCRIPT_ROOT/other_bash_history.sh"
echo "-----------------------------------------------------"
echo " Bash environment initialized. Key commands:"
echo "   GPU/System/Docker: selectgpu, lsps,lsg,lsug, gput"
echo "   Dify Mgmt:  start_dify, update_dify, down_dify"
echo "   Dev Tools:  tb, setpy (use carefully!)"
echo "   Network:    chsrc,fq, fqlog,changmac, forwardport <user@host> [remote_port]"
echo "   File/Nav:   findname <pattern>, findinfiles ,cdp, lsp "
echo "   Sync:       pull_s_a800t, pull <src> <dest>"
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
