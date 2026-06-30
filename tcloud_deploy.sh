#!/bin/bash
# 家庭记事本 - 腾讯云服务器部署脚本
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

# 创建项目目录
mkdir -p /opt/family_notebook
cd /opt/family_notebook

# 克隆代码（或更新）
echo "📥 下载代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/sunbin160514/family_notebook.git .
fi

# 创建环境变量文件
echo "⚙️  配置环境变量..."
cat > .env << 'EOF'
DB_HOST=db
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=Test11223344@
FLASK_PORT=5000
FLASK_DEBUG=False
FRONTEND_URL=http://43.157.55.92
EOF

# 创建日志目录
mkdir -p logs

# 停止旧服务
echo "🛑 停止旧服务..."
docker-compose -f docker-compose-v3.yml down 2>/dev/null || true

# 构建并启动
echo "🔨 构建Docker镜像..."
docker-compose -f docker-compose-v3.yml build --no-cache

echo "🚀 启动服务..."
docker-compose -f docker-compose-v3.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查状态
if docker-compose -f docker-compose-v3.yml ps | grep -q "Up"; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "🌐 访问地址:"
    echo "   前端页面: http://43.157.55.92"
    echo "   后端API: http://43.157.55.92/api"
    echo "   健康检查: http://43.157.55.92/health"
    echo ""
    echo "📊 常用命令:"
    echo "   查看状态: docker-compose -f docker-compose-v3.yml ps"
    echo "   查看日志: docker-compose -f docker-compose-v3.yml logs -f"
    echo "   停止服务: docker-compose -f docker-compose-v3.yml down"
    echo "   重启服务: docker-compose -f docker-compose-v3.yml restart"
    echo ""
    echo "⚠️  如果这是首次部署，请确保:"
    echo "   1. MySQL已安装并创建数据库"
    echo "   2. 数据库已导入 schema.sql"
    echo "   3. 服务器防火墙已开放80端口"
else
    echo "❌ 部署失败"
    echo "查看日志: docker-compose -f docker-compose-v3.yml logs"
    exit 1
fi
