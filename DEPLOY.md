# 🚀 腾讯云部署指南

## 📋 部署前准备

### 1. 腾讯云服务器要求
- **系统**: CentOS 7/8 或 Ubuntu 20.04+
- **配置**: 建议 2核4G 以上
- **带宽**: 建议 3Mbps 以上
- **安全组**: 开放 5000 端口（或自定义端口）

### 2. 安装基础软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y  # Ubuntu
# 或
sudo yum update -y  # CentOS

# 安装Git
sudo apt install git -y  # Ubuntu
sudo yum install git -y  # CentOS
```

## 🚀 部署步骤

### 方式一：Docker部署（推荐）

#### 1. 连接服务器并上传代码

```bash
# 在本地打包代码（排除.env）
cd family_notebook
tar -czvf family_notebook.tar.gz --exclude='venv' --exclude='__pycache__' --exclude='.git' .

# 上传到服务器
scp family_notebook.tar.gz root@你的服务器IP:/root/
```

#### 2. 在服务器上部署

```bash
# 连接服务器
ssh root@你的服务器IP

# 解压代码
cd /root
mkdir -p family_notebook
cd family_notebook
tar -xzvf ../family_notebook.tar.gz

# 配置环境变量
cp .env.example .env
vim .env  # 编辑配置，设置腾讯云数据库信息

# 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 方式二：手动部署

```bash
# 1. 连接服务器
ssh root@你的服务器IP

# 2. 安装Python和依赖
sudo apt install python3 python3-pip python3-venv -y

# 3. 上传代码并启动
cd /root
# 上传代码后...
cd family_notebook
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
vim .env  # 编辑数据库配置

# 5. 启动（使用nohup后台运行）
nohup python app.py > logs/app.log 2>&1 &
```

## 🗄️ 数据库配置

### 选项1：腾讯云MySQL（推荐）

1. 购买腾讯云MySQL实例
2. 创建数据库 `family_notebook`
3. 配置安全组，允许服务器IP访问
4. 在 `.env` 中配置：

```
DB_HOST=你的腾讯云MySQL内网地址
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=你的密码
```

### 选项2：服务器本地MySQL

```bash
# 安装MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# 创建数据库
sudo mysql -e "CREATE DATABASE family_notebook DEFAULT CHARACTER SET utf8mb4;"

# 配置.env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=family_notebook
DB_USER=root
DB_PASSWORD=你的密码
```

### 选项3：Docker MySQL

```yaml
# 在docker-compose.yml中添加
services:
  db:
    image: mysql:8.0
    container_name: family_mysql
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: family_notebook
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - family_network

  app:
    # ... 原有配置
    depends_on:
      - db
    environment:
      - DB_HOST=db  # 使用服务名作为主机名
      # ... 其他配置

volumes:
  mysql_data:
```

## 🔒 安全配置

### 1. 使用Nginx反向代理（推荐）

```bash
# 安装Nginx
sudo apt install nginx -y

# 配置
sudo vim /etc/nginx/sites-available/family_notebook
```

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/family_notebook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. 配置HTTPS（SSL证书）

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 你的域名
```

### 3. 防火墙设置

```bash
# 开放80和443端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

## 📊 常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码后重新部署
git pull
docker-compose up -d --build
```

## 🔄 自动部署（CI/CD）

可以使用GitHub Actions自动部署到腾讯云：

```yaml
# .github/workflows/deploy.yml
name: Deploy to Tencent Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: root
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /root/family_notebook
          git pull
          docker-compose up -d --build
```

## 🆘 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
sudo lsof -i :5000
# 杀死进程
sudo kill -9 <PID>
```

### 2. 数据库连接失败
- 检查安全组规则
- 检查MySQL用户权限
- 确认 `.env` 配置正确

### 3. 内存不足
```bash
# 添加Swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 联系支持

如有问题，请查看GitHub Issues或联系开发者。
