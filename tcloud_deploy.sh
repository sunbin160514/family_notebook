#!/bin/bash
# 家庭记事本 - 腾讯云服务器部署命令
# 在服务器上执行此脚本

set -e

echo "🏠 开始部署家庭记事本..."
echo "========================"

# 更新系统
echo "📦 更新系统..."
apt update && apt upgrade -y

# 安装必要软件
echo "📦 安装必要软件..."
apt install -y git curl

# 安装Docker
echo "🐳 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 安装Docker Compose
echo "🐳 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 安装MySQL（如果未安装）
echo "🗄️  检查MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "🗄️  安装MySQL..."
    apt install -y mysql-server
    systemctl start mysql
    systemctl enable mysql

    # 创建数据库
    mysql -e "CREATE DATABASE IF NOT EXISTS family_notebook DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Test11223344@';"
    mysql -e "FLUSH PRIVILEGES;"
fi

# 创建项目目录
mkdir -p /opt/family_notebook
cd /opt/family_notebook

# 克隆代码（或手动上传）
echo "📥 下载代码..."
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/sunbin160514/family_notebook.git .
fi

# 创建环境变量文件
echo "⚙️  配置环境变量..."
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=Test11223344@
FLASK_PORT=5000
FLASK_DEBUG=False
EOF

# 导入数据库
echo "🗄️  导入数据库..."
mysql -u root -p'Test11223344@' family_notebook < database/schema.sql 2>/dev/null || true

# 创建日志目录
mkdir -p logs

# 构建并启动
echo "🔨 构建Docker镜像..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
sleep 5

# 检查状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ 部署成功！"
    echo "🌐 应用访问地址: http://43.157.55.92:5000"
    echo "📊 查看日志: docker-compose logs -f"
    echo ""
    echo "常用命令:"
    echo "  查看状态: docker-compose ps"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
else
    echo "❌ 部署失败"
    echo "查看日志: docker-compose logs"
    exit 1
fi
