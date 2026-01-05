# U-Linker Project

U-Linker 是一款基于前后端分离架构的校园技能交换平台。

## 🛠 技术栈 (Tech Stack)

### 前端 (Frontend)
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Router**: Vue Router 4
- **HTTP Client**: Axios
- **UI Framework**: Tailwind CSS
- **Language**: JavaScript

### 后端 (Backend)
- **Framework**: Flask
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy
- **WSGI Server**: Gunicorn
- **Language**: Python 3.11+

## 📂 项目结构

```
U-Linker/
├── Frontend/                    # Vue3 前端项目
│   ├── src/                    # 源代码目录
│   │   ├── api/                # API接口
│   │   ├── assets/             # 静态资源
│   │   ├── components/         # Vue组件
│   │   ├── constants/          # 常量定义
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia状态管理
│   │   ├── utils/              # 工具函数
│   │   ├── views/              # 页面视图
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口文件
│   ├── public/                 # 公共资源
│   ├── Dockerfile              # Docker构建文件（多阶段构建）
│   ├── Dockerfile.simple       # 简单Dockerfile（推荐，用于已构建的前端）
│   ├── docker-compose.frontend-simple.yml  # Docker Compose配置（推荐）
│   ├── docker-compose.frontend.yml         # Docker Compose配置（完整构建）
│   ├── nginx.conf              # Nginx配置
│   ├── package.json            # 项目配置
│   ├── package-lock.json       # 依赖锁定文件
│   ├── vite.config.js          # Vite配置
│   ├── tailwind.config.js      # Tailwind CSS配置
│   ├── postcss.config.js       # PostCSS配置
│   └── index.html              # HTML入口
│
└── Backend/                    # Flask 后端项目
    ├── routes/                 # 路由模块
    │   ├── auth.py             # 认证路由
    │   ├── market.py           # 市场路由
    │   ├── transaction.py      # 交易路由
    │   ├── recommendation.py   # 推荐系统路由
    │   ├── chat.py             # 聊天路由
    │   ├── admin.py            # 管理员路由
    │   └── debug.py            # 调试路由
    ├── utils/                  # 工具函数
    │   └── response.py         # 统一响应格式
    ├── static/                 # 静态文件（头像等）
    ├── uploads/                # 上传文件目录
    ├── instance/               # 实例配置目录
    ├── Dockerfile              # Docker构建文件
    ├── docker-compose.backend.yml  # Docker Compose配置
    ├── nginx.backend.conf      # Nginx配置
    ├── requirements.txt        # Python依赖
    ├── .env.example            # 环境变量示例
    ├── models.py               # 数据模型
    ├── extensions.py           # 扩展模块（数据库等）
    └── app.py                  # 应用入口
```

## 🚀 快速开始 (Quick Start)

### 前置要求

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Node.js** >= 20.19.0 或 >= 22.12.0 (仅本地开发需要)
- **Python** >= 3.11 (仅本地开发需要)

---

## 🐳 Docker 部署（推荐）

这是推荐的生产环境部署方式，使用Docker可以确保环境一致性。

### 1. 克隆项目

```bash
git clone https://github.com/U-Linker-Team/U-Linker-Project.git
#进入后端
cd U-Linker-Backend
#进入前端
cd U-Linker-Frontend
```

### 2. 后端部署

#### 2.1 配置环境变量

进入后端目录，复制环境变量示例文件：

```bash
cd  U-Linker-Backend
cp .env.example .env
```

编辑 `.env` 文件，配置数据库等信息：

```env
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
FLASK_APP=app.py

# 数据库配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=u_linker_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=u_linker_db
```

#### 2.2 启动后端服务

```bash
cd U-Linker-Backend
docker compose -f docker-compose.backend.yml up -d
```

#### 2.3 验证后端服务

```bash
# 检查容器状态
docker compose -f docker-compose.backend.yml ps

# 检查本地环境健康状态
curl http://localhost:8000/health
```

**预期响应**：
```json
{
  "status": "ok",
  "service": "backend",
  "database": "connected"
}
```

---

### 3. 前端部署

#### 3.1 本地构建（推荐）

```bash
cd  U-Linker-Frontend

# 安装依赖
npm install

# 构建前端
npm run build
```

#### 3.2 使用Docker部署前端

```bash
cd U-Linker-Frontend

# 使用简单Dockerfile（推荐，使用已构建的dist目录）
docker compose -f docker-compose.frontend.yml up -d

# 或者使用完整构建（在Docker中构建，不推荐）
# docker compose -f docker-compose.frontend.yml up -d
```

#### 3.3 验证前端服务

```bash
# 检查容器状态
docker compose -f docker-compose.frontend.yml ps

# 检查健康状态
curl http://localhost/health
```

**预期响应**：
```json
{
  "status": "ok",
  "service": "frontend"
}
```

---

### 4. 访问应用

- **前端**: http://localhost
- **后端API**: http://localhost/api/
- **后端健康检查**: http://localhost/api/health

---

## 💻 本地开发

### 后端开发

```bash
cd U-Linker-Backend
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 启动开发服务器
python app.py
```

后端服务将运行在: http://localhost:8000

**注意**：本地开发时，确保MySQL服务已启动，或者修改`.env`使用SQLite（开发环境）。

---

### 前端开发

```bash
cd U-Linker-Frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器将运行在: http://localhost:5173

**注意**：前端开发时，Vite会自动代理API请求到后端服务（配置在 `vite.config.js` 中）。

---

## 📋 环境变量配置

### 后端环境变量

创建 `Backend/.env` 文件：

```env
# Flask配置
FLASK_ENV=development  # 开发环境使用 development，生产环境使用 production
SECRET_KEY=your-secret-key-here
FLASK_APP=app.py

# 数据库配置
MYSQL_HOST=localhost  # 本地开发使用 localhost，Docker使用 mysql
MYSQL_PORT=3306
MYSQL_USER=u_linker_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=u_linker_db

# CORS配置（可选，用逗号分隔多个源）
CORS_ORIGINS=http://localhost:5173,http://localhost:8080
```

### 前端环境变量（可选）

如果需要，创建 `Frontend/.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🔧 常用命令

### Docker命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs u-linker-backend
docker logs u-linker-frontend

# 重启服务
docker restart u-linker-backend
docker restart u-linker-frontend

# 停止服务
docker compose -f docker-compose.backend.yml down
docker compose -f docker-compose.frontend.yml down

# 查看资源使用
docker stats
```

### 后端命令

```bash
# 进入后端容器
docker exec -it u-linker-web bash

# 查看后端日志
docker logs -f u-linker-web

# 重启后端
docker restart u-linker-web
```

### 前端命令

```bash
# 进入前端容器
docker exec -it u-linker-frontend sh

# 查看前端日志
docker logs -f u-linker-frontend

# 重启前端
docker restart u-linker-frontend
```

---

## 📝 API文档

### 健康检查

- **前端**: `GET /health`
- **后端**: `GET /api/health`

### 主要API端点

- `/api/auth/` - 认证相关
- `/api/market/` - 市场相关
- `/api/transaction/` - 交易相关
- `/api/recommendation/` - 推荐系统
- `/api/chat/` - 聊天功能
- `/api/admin/` - 管理员功能

详细API文档请参考代码注释或API文档。

---

## 🗄️ 数据库

### 数据库初始化

使用Docker Compose部署时，数据库会自动初始化。

### 手动初始化（本地开发）

```bash
cd U-Linker-Backend
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 创建管理员账户

```bash
cd U-Linker-Backend

# 使用交互式脚本
python create_admin.py

# 或使用非交互式脚本（适合Docker环境）
python create_admin_noninteractive.py
```

---

## 🛠️ 开发工具

### 代码格式化

**前端**:
```bash
npm run format  # 如果配置了格式化脚本
```

**后端**:
```bash
# 使用 black (如果安装)
black .
```

### 代码检查

**前端**:
```bash
npm run lint  # 如果配置了lint脚本
```

---

## 📦 项目依赖

### 后端主要依赖

- Flask 3.0.3
- SQLAlchemy 2.0.44
- Flask-CORS 5.0.0
- PyMySQL 1.1.0
- Gunicorn 21.2.0
- Pandas >= 2.2.0

完整依赖列表请查看 `Backend/requirements.txt`

### 前端主要依赖

- Vue 3.5.22
- Vue Router 4.6.4
- Pinia 3.0.4
- Axios 1.13.2
- Tailwind CSS 3.4.0
- Vite 7.1.11

完整依赖列表请查看 `Frontend/package.json`

---

## 🔒 安全注意事项

1. **环境变量**: 不要将 `.env` 文件提交到Git仓库
2. **密钥**: 生产环境使用强密钥（SECRET_KEY）
3. **数据库密码**: 使用强密码，不要使用默认密码
4. **CORS**: 生产环境配置正确的CORS源
5. **HTTPS**: 生产环境建议使用HTTPS

---

## 🐛 故障排查

### 后端无法启动

1. 检查数据库连接配置
2. 检查端口是否被占用
3. 查看日志: `docker logs u-linker-web`

### 前端无法访问后端API

1. 检查后端服务是否运行
2. 检查Nginx配置
3. 检查CORS配置
4. 查看浏览器控制台错误

### 数据库连接失败

1. 检查数据库服务是否运行
2. 检查环境变量配置
3. 检查网络连接（Docker网络）

---

## 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 许可证。

---

## 👥 贡献者 (Contributors)

感谢所有为本项目做出贡献的开发者！

---

## 📞 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**Happy Coding! 🚀**
