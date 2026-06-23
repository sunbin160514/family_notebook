#!/bin/bash
# 家庭记事本 - 腾讯云部署脚本

set -e

echo "🏠 家庭记事本部署脚本"
echo "======================"

# 检查环境
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到.env文件"
    echo "请先配置环境变量: cp .env.example .env && vim .env"
    exit 1
fi

# 安装Docker（如果未安装）
if ! command -v docker &> /dev/null; then
    echo "📦 安装Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 安装Docker Compose（如果未安装）
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 创建日志目录
mkdir -p logs

# 停止旧容器
echo "🛑 停止旧服务..."
docker-compose down 2>/dev/null || true

# 构建并启动
echo "🔨 构建镜像..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 检查状态
sleep 3
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ 部署成功！"
    echo "🌐 应用访问地址: http://$(curl -s ifconfig.me):5000"
    echo "📊 查看日志: docker-compose logs -f"
else
    echo "❌ 部署失败，请检查日志: docker-compose logs"
    exit 1
fi
