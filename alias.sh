# 定义脚本根目录变量
SCRIPT_ROOT="/home/jinyue/s"
# 设置镜像加速（国内用户建议添加）
export HF_ENDPOINT=https://hf-mirror.com
# 定义别名，用于选择最闲的 GPU
alias selectgpu="source $SCRIPT_ROOT/select_best_gpu.sh"
echo '选择最闲 GPU: selectgpu'
alias startA="$SCRIPT_ROOT/agentui/start.sh"
  #覆盖


# 定义其他别名
alias lsps="sudo python3 $SCRIPT_ROOT/lsps.py"
选py() {
    alias python="$1"
    echo "Python 已切换到: $1"
}
start_dify(){
	cd ~/build/dify/docker
	docker compose up -d
}
update_dify(){
	cd ~/build/dify/docker
docker compose down
git pull origin main
docker compose pull
docker compose up -d
}
down_dify(){
 cd ~/build/dify/docker
docker compose down

}
#给我写一个函数在bashrc里面 输入logdir 启动tensorboard 如果端口被占用 则自动加一 直到未被占用，然后返回端口  tb(){
tb() {
    local port=${2:-7777}  # 默认端口7777，可传入参数覆盖
    local logdir=${1:-"./logs"}  # 默认日志目录./logs，可传入参数覆盖
    
    # 检测端口是否被占用
    while netstat -ano | grep -q ":$port "; do
        echo "Port $port is occupied, trying next port..."
        ((port++))
    done
    
    echo "Starting TensorBoard on port $port with logdir: $logdir"
    tensorboard --logdir "$logdir" --port "$port" &
    echo "TensorBoard started at http://localhost:$port"
    
    return $port  # 返回最终使用的端口号
}

#docker compose down
#git pull origin main
 #docker compose pull
alias envok="python $SCRIPT_ROOT/envok.py"
echo '看看lsps 检查环境是否正常: envok'
alias 文件内找="ack -l "
# alias python="python3"
alias gput="python $SCRIPT_ROOT/torchgputest.py"
alias fq="$SCRIPT_ROOT/fq.sh"
alias sx="source ~/.bashrc"


alias U="pip install --upgrade"
alias sj="$SCRIPT_ROOT/suji.sh"
alias serv="$SCRIPT_ROOT/server.sh"
alias fqlog="cat $SCRIPT_ROOT/fanqiang/logfanqiang"
alias crlaunchjson="selectgpu && $SCRIPT_ROOT/envlaunch.sh"
forwardport() {
  local remote_port="${2:-80}"
  local hostname="$1"
  local local_port="$remote_port"

  while netstat -tuln | grep ":$local_port " > /dev/null; do
    local_port=$((local_port + 1))
  done

  ssh -L "$local_port:0.0.0.0:$remote_port" "$hostname" &
  echo "Forwarding remote port $remote_port of $hostname to local port $local_port"
}
alias f="find . -name "
alias 实际="cd -P ."
echo -e '常用命令: tb =tensorboard 实际 文件内找fq fqlog sj serv startA \n pip升级 U,source刷新 sx ;start update dify\n  f= find . -name "*tutorial*"'


alias pull_="rsync -av -e ssh"
alias pull_s="rsync -av -e ssh a800t:~/s ~/ && sx"
echo -e 'pull_ a800t:~ . pull_s crlaunchjson\n'


export HF_ENDPOINT=https://hf-mirror.com
alias hfdownload="$SCRIPT_ROOT/hf-fast.sh"

conda env list
