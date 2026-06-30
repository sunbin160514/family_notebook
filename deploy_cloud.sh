#!/bin/bash
# 家庭记事本 - 腾讯云一键部署脚本
# 创建时间: 2026-06-30

set -e

echo "========================================"
echo "🏠 家庭记事本 - 腾讯云部署脚本"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 权限运行此脚本"
    exit 1
fi

# 项目配置
PROJECT_DIR="/opt/family_notebook"
GITHUB_REPO="https://github.com/sunbin160514/family_notebook.git"
SERVER_IP="43.157.55.92"

log_info "开始部署流程..."

# 1. 安装必要软件
log_info "步骤 1/8: 安装必要软件..."
apt update > /dev/null 2>&1
apt install -y git curl net-tools > /dev/null 2>&1
log_info "✓ 软件安装完成"

# 2. 安装Docker
log_info "步骤 2/8: 检查并安装Docker..."
if ! command -v docker &> /dev/null; then
    log_warn "Docker未安装，开始安装..."
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl start docker
    systemctl enable docker > /dev/null 2>&1
    log_info "✓ Docker安装完成"
else
    log_info "✓ Docker已安装"
fi

# 3. 安装Docker Compose
log_info "步骤 3/8: 检查并安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    log_warn "Docker Compose未安装，开始安装..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose > /dev/null 2>&1
    chmod +x /usr/local/bin/docker-compose
    log_info "✓ Docker Compose安装完成"
else
    log_info "✓ Docker Compose已安装"
fi

# 4. 创建项目目录并拉取代码
log_info "步骤 4/8: 拉取项目代码..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

if [ -d ".git" ]; then
    log_info "更新现有代码..."
    git reset --hard HEAD
    git pull origin main > /dev/null 2>&1
else
    log_info "克隆新代码..."
    rm -rf $PROJECT_DIR/*
    git clone $GITHUB_REPO . > /dev/null 2>&1
fi
log_info "✓ 代码拉取完成"

# 5. 创建环境变量文件
log_info "步骤 5/8: 配置环境变量..."
cat > $PROJECT_DIR/.env << EOF
DB_HOST=db
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=Test11223344@
FLASK_PORT=5000
FLASK_DEBUG=False
FRONTEND_URL=http://$SERVER_IP
EOF
log_info "✓ 环境变量配置完成"

# 6. 停止旧服务
log_info "步骤 6/8: 停止旧服务..."
docker-compose -f docker-compose-v3.yml down > /dev/null 2>&1 || true
docker system prune -f > /dev/null 2>&1 || true
log_info "✓ 旧服务已清理"

# 7. 构建并启动服务
log_info "步骤 7/8: 构建Docker镜像（这可能需要几分钟）..."
log_warn "正在构建前端镜像，请耐心等待..."
cd $PROJECT_DIR
docker-compose -f docker-compose-v3.yml build --no-cache > /tmp/docker-build.log 2>&1
if [ $? -ne 0 ]; then
    log_error "镜像构建失败，查看日志: /tmp/docker-build.log"
    tail -50 /tmp/docker-build.log
    exit 1
fi
log_info "✓ 镜像构建完成"

log_info "启动服务..."
docker-compose -f docker-compose-v3.yml up -d > /dev/null 2>&1
log_info "✓ 服务已启动"

# 8. 等待服务启动并检查状态
log_info "步骤 8/8: 等待服务启动..."
sleep 15

echo ""
echo "========================================"
log_info "📊 服务状态检查:"
echo "========================================"
docker-compose -f docker-compose-v3.yml ps

echo ""
echo "========================================"

# 检查服务是否健康
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo ""
    echo "🌐 访问地址:"
    echo "   主页面: http://$SERVER_IP"
    echo "   健康检查: http://$SERVER_IP/health"
    echo ""
    echo "📊 常用命令:"
    echo "   查看状态: cd $PROJECT_DIR && docker-compose -f docker-compose-v3.yml ps"
    echo "   查看日志: cd $PROJECT_DIR && docker-compose -f docker-compose-v3.yml logs -f"
    echo "   重启服务: cd $PROJECT_DIR && docker-compose -f docker-compose-v3.yml restart"
    echo "   停止服务: cd $PROJECT_DIR && docker-compose -f docker-compose-v3.yml down"
    echo ""
    echo "⚠️  如果无法访问，请检查:"
    echo "   1. 腾讯云安全组是否开放80端口"
    echo "   2. 服务器防火墙是否允许80端口"
    echo "      ufw allow 80"
    echo "      systemctl stop firewalld"
    echo ""
else
    log_error "⚠️  服务可能未正常启动 (HTTP状态: $HEALTH_STATUS)"
    echo ""
    log_info "查看日志排查问题:"
    echo "   tail -100 /tmp/docker-build.log"
    echo "   cd $PROJECT_DIR && docker-compose -f docker-compose-v3.yml logs"
    echo ""
    exit 1
fi

echo "========================================"
