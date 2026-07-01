#!/bin/bash
# 腾讯云部署 - 执行此脚本完成部署

set -e

echo "🏠 开始云部署..."

# 1. 登录服务器并执行以下命令：
cat << 'DEPLOY_COMMANDS'

================================================================
请在腾讯云服务器上执行以下命令：
================================================================

# 1. SSH登录服务器（在本地终端执行）
ssh root@43.157.55.92

# 2. 进入项目目录
cd /opt/family_notebook

# 3. 拉取最新代码
git pull origin main

# 4. 检查并安装Docker（如未安装）
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 5. 安装Docker Compose（如未安装）
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 6. 创建环境变量文件
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

# 7. 停止旧服务
docker-compose -f docker-compose-v3.yml down 2>/dev/null || true

# 8. 构建并启动服务
docker-compose -f docker-compose-v3.yml build --no-cache
docker-compose -f docker-compose-v3.yml up -d

# 9. 等待服务启动
sleep 15

# 10. 检查状态
echo ""
echo "📊 服务状态："
docker-compose -f docker-compose-v3.yml ps

echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址：http://43.157.55.92"

DEPLOY_COMMANDS
