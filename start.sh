#!/bin/bash
# 家庭记事本启动脚本

cd "$(dirname "$0")"

echo "🏠 家庭记事本启动脚本"
echo "======================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 检查数据库配置
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 配置文件"
    echo "📝 请复制 .env.example 为 .env 并配置数据库信息"
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
    exit 1
fi

# 启动应用
echo "🚀 启动应用..."
echo "📱 应用将在 http://localhost:5000 运行"
echo "🛑 按 Ctrl+C 停止"
echo ""
python app.py
