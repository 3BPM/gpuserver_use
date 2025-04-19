#要在后台运行 ./clash -d . 并将错误输出重定向到 fanqianglog 文件中，可以使用以下命令：

#~/a/fanqiang/clash -d . 2> fanqianglog &
#2>: 这是重定向标准错误流（文件描述符 2）的语法。


#&: 将命令放到后台运行。  &：

#如果需要将标准输出和标准错误都重定向到同一个文件：
#!/bin/bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"

cd /home/jinyue/s/fanqiang/

# 执行命令并将输出重定向到 fanqianglog
# 检查端口 7890 是否被占用
if ! lsof -i :7890 -sTCP:LISTEN > /dev/null 2>&1; then
    echo "端口 7890 未被占用，正在启动 clash..."
    echo "$(date '+%Y-%m-%d %H:%M:%S') 开始" > logfanqiang    # 启动 clash 程序，并将输出重定向到日志文件
    ./clash -d . >> logfanqiang 2>&1 &
    PID=$!
    echo "进程的 PID: $PID"
    echo "clash 已启动，日志输出到 logfanqiang 文件。"
else
    echo "端口 7890 已被占用，无法启动 clash。"
    lsof -i :7890 -sTCP:LISTEN

fi
# 输出进程的 PID

#2>&1: 将标准错误重定向到标准输出（即 fanqianglog）。


#查看后台任务：如果你想查看后台运行的任务，可以使用 jobs 命令：

#jobs
#将任务带回前台：如果你想将后台任务带回前台运行，可以使用 fg 命令：

#fg
#停止后台任务：如果你想停止后台任务，可以先将其带回前台（使用 fg），然后按 Ctrl+C，或者直接使用 kill 命令终止进程：
#!/bin/bash

# 输出 Bash 形式的环境变量设置
cat  logfanqiang
echo '已经执行'
echo 'export HTTP_PROXY="http://127.0.0.1:7890"'
echo 'export HTTPS_PROXY="http://127.0.0.1:7890"'
echo '<<<<<<<<<<<<<<<<<<<<'
# # 输出 CMD 形式的环境变量设置
# echo 'CMD 形式:'
# echo 'set HTTP_PROXY=http://127.0.0.1:7890'
# echo 'set HTTPS_PROXY=http://127.0.0.1:7890'
