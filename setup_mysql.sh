#!/bin/bash
# MySQL配置脚本

# 检查MySQL是否运行
if ! systemctl is-active --quiet mysql; then
    echo "安装并启动MySQL..."
    apt update
    apt install -y mysql-server
    systemctl start mysql
    systemctl enable mysql
fi

# 创建数据库
mysql -e "CREATE DATABASE IF NOT EXISTS family_notebook DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 设置root密码
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Test11223344@';"
mysql -e "FLUSH PRIVILEGES;"

# 导入数据库
mysql -u root -p'Test11223344@' family_notebook < /opt/family_notebook/database/schema.sql

echo "数据库配置完成"
