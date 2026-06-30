#!/bin/bash
# 家庭记事本 - 故障排查脚本

echo "🔍 开始排查..."
echo "=============="

cd /opt/family_notebook 2>/dev/null || cd ~/family_notebook 2>/dev/null || cd /root/family_notebook 2>/dev/null

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到项目目录"
    echo "请确认项目位置：find / -name 'docker-compose.yml' 2>/dev/null | head -5"
    exit 1
fi

echo ""
echo "1️⃣ Docker容器状态："
docker-compose ps

echo ""
echo "2️⃣ 应用日志（最近20行）："
docker-compose logs --tail=20

echo ""
echo "3️⃣ 端口监听状态："
ss -tlnp | grep 5000 || netstat -tlnp | grep 5000 || echo "未监听5000端口"

echo ""
echo "4️⃣ 防火墙状态："
ufw status 2>/dev/null || echo "ufw未安装"
iptables -L -n | grep 5000 2>/dev/null || echo "iptables未配置5000端口"

echo ""
echo "5️⃣ 安全组检查："
echo "请登录腾讯云控制台 -> 云服务器 -> 安全组 -> 确认已开放5000端口"

echo ""
echo "6️⃣ 网络连通性测试："
curl -s http://localhost:5000/health 2>/dev/null && echo "✅ 本地访问正常" || echo "❌ 本地访问失败"

echo ""
echo "=============="
echo "如需重启服务：docker-compose restart"
echo "如需重新部署：docker-compose down && docker-compose up -d --build"
