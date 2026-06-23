# 🏠 温馨家庭记事本

一个温馨的家庭信息管理系统，帮助您记录家人的喜好、生日和日常注意事项。

## ✨ 功能特性

- 👨‍👩‍👧‍👦 **家人管理** - 添加、查看、编辑、删除家人信息
- 🔍 **搜索功能** - 按姓名或昵称快速搜索
- 🎂 **生日提醒** - 自动检测7天内过生日的家人
- 📥 **数据导出** - 一键导出Excel文件
- 💕 **温馨设计** - 暖色调界面，营造家的氛围
- 📱 **响应式布局** - 支持电脑、平板、手机访问

## 📝 记录信息

每个家人可记录以下信息：
- 姓名、昵称
- 阳历生日、阴历生日
- 喜欢的食物、运动
- 讨厌的食物（忌口）
- 日常注意事项
- 备注

## 🚀 快速开始

### 1. 配置数据库

编辑 `.env` 文件，设置MySQL连接信息：

```bash
cp .env.example .env
# 编辑 .env 文件
```

配置示例：
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=your_password

FLASK_PORT=5000
FLASK_DEBUG=True
```

### 2. 初始化数据库

在MySQL中执行：

```bash
mysql -u root -p < database/schema.sql
```

或直接运行SQL语句创建数据库和表。

### 3. 安装依赖并启动

```bash
# 使用启动脚本
chmod +x start.sh
./start.sh

# 或手动启动
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 4. 访问应用

打开浏览器访问 http://localhost:5000

## 🎨 页面预览

- **首页** - 家人列表、生日提醒、搜索
- **添加页面** - 表单填写家人信息
- **详情页面** - 完整信息展示
- **编辑页面** - 修改家人信息

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| / | GET | 首页 |
| /api/members/<id> | DELETE | 删除家人 |
| /api/export | GET | 导出Excel |
| /health | GET | 健康检查 |

## 🔧 OpenClaw 集成

应用提供健康检查接口，便于OpenClaw自动化调用：

```bash
# 启动应用
cd family_notebook && python app.py

# 健康检查
curl http://localhost:5000/health
```

## 📦 技术栈

- **后端**: Python 3.11 + Flask
- **数据库**: MySQL
- **前端**: HTML5 + CSS3 + JavaScript
- **样式**: 自定义温馨风格CSS

## 💝 温馨配色

- 🟠 暖橙色 (#FF9A76) - 主色调
- 🟡 奶油白 (#FFF8F0) - 背景色
- 💗 珊瑚粉 - 强调色
- 所有设计元素都体现温馨、舒适的家的感觉

## 📄 许可证

MIT License
