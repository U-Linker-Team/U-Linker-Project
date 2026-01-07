#!/bin/bash
# 代码更新部署脚本
# 用于将本地代码更新到云服务器

set -e

# 配置信息
SERVER_IP="121.89.81.18"
SERVER_USER="root"
SSH_KEY_PATH="~/.ssh/u-linker.pem"
BACKEND_DIR="/opt/u-linker-backend"
FRONTEND_DIR="/opt/u-linker-frontend"
LOCAL_BACKEND_DIR="/home/mark/u-linker-backend_yys"
LOCAL_FRONTEND_DIR="/home/mark/vsworkspace/vsworkspace_原/vue-demo"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 检查本地目录是否存在
if [ ! -d "$LOCAL_BACKEND_DIR" ]; then
    print_error "后端目录不存在: $LOCAL_BACKEND_DIR"
    exit 1
fi

if [ ! -d "$LOCAL_FRONTEND_DIR" ]; then
    print_error "前端目录不存在: $LOCAL_FRONTEND_DIR"
    exit 1
fi

echo "=" | head -c 60
echo ""
echo "代码更新部署脚本"
echo "=" | head -c 60
echo ""
echo "服务器: ${SERVER_USER}@${SERVER_IP}"
echo "后端目录: ${BACKEND_DIR}"
echo "前端目录: ${FRONTEND_DIR}"
echo ""

# 询问要更新的内容
echo "请选择要更新的内容："
echo "1) 仅更新后端代码"
echo "2) 仅更新前端代码"
echo "3) 更新前后端代码"
echo "4) 仅生成测试数据（不更新任何代码，只向数据库添加数据）"
echo "5) 数据库迁移（在更新后端代码后运行，用于更新数据库表结构）"
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        UPDATE_BACKEND=true
        UPDATE_FRONTEND=false
        GENERATE_DATA=false
        MIGRATE_DB=false
        ;;
    2)
        UPDATE_BACKEND=false
        UPDATE_FRONTEND=true
        GENERATE_DATA=false
        MIGRATE_DB=false
        ;;
    3)
        UPDATE_BACKEND=true
        UPDATE_FRONTEND=true
        GENERATE_DATA=false
        MIGRATE_DB=false
        ;;
    4)
        UPDATE_BACKEND=false
        UPDATE_FRONTEND=false
        GENERATE_DATA=true
        MIGRATE_DB=false
        ;;
    5)
        UPDATE_BACKEND=false
        UPDATE_FRONTEND=false
        GENERATE_DATA=false
        MIGRATE_DB=true
        ;;
    *)
        print_error "无效选项"
        exit 1
        ;;
esac

if [ "$UPDATE_BACKEND" = true ]; then
    print_step "步骤 1: 上传后端代码..."
    
    # 排除不需要上传的文件
    rsync -avz --progress \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude '*.md' \
        --exclude '*.sh' \
        --exclude '*.tar' \
        --exclude 'instance' \
        --exclude '*.log' \
        -e "ssh -i $SSH_KEY_PATH" \
        "$LOCAL_BACKEND_DIR/" "${SERVER_USER}@${SERVER_IP}:${BACKEND_DIR}/"
    
    if [ $? -ne 0 ]; then
        print_error "后端代码上传失败"
        exit 1
    fi
    print_info "后端代码上传成功"
    echo ""
    
    # 重启后端服务
    print_step "步骤 2: 重启后端服务..."
    ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" << 'EOF'
set -e
cd /opt/u-linker-backend

# 检测 Docker Compose 命令格式
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 停止并删除旧容器
echo "🔨 停止并删除旧容器..."
${DOCKER_COMPOSE} -f docker-compose.backend.yml stop web 2>/dev/null || true
${DOCKER_COMPOSE} -f docker-compose.backend.yml rm -f web 2>/dev/null || true
docker rm -f u-linker-web 2>/dev/null || true

# 后端 Nginx 也需要重启以应用配置变更（例如 client_max_body_size）
${DOCKER_COMPOSE} -f docker-compose.backend.yml stop nginx-backend 2>/dev/null || true
${DOCKER_COMPOSE} -f docker-compose.backend.yml rm -f nginx-backend 2>/dev/null || true
docker rm -f u-linker-nginx-backend 2>/dev/null || true

# 重新构建镜像
echo "重新构建镜像..."
${DOCKER_COMPOSE} -f docker-compose.backend.yml build web

# 启动服务
echo "启动服务..."
${DOCKER_COMPOSE} -f docker-compose.backend.yml up -d

echo "等待服务启动（10秒）..."
sleep 10

echo "服务状态："
${DOCKER_COMPOSE} -f docker-compose.backend.yml ps

echo "后端服务已重启"
EOF
    
    if [ $? -ne 0 ]; then
        print_error "后端服务重启失败"
        exit 1
    fi
    echo ""
fi

# 更新前端
if [ "$UPDATE_FRONTEND" = true ]; then
    print_step "步骤 3: 构建前端..."
    
    # 注意：前端容器使用 Dockerfile.simple 在构建镜像时 COPY dist
    # 如果 dist 存在但内容是旧的，部署后页面也会一直是旧的
    # 因此这里默认建议重新构建，确保 src 的改动能进入 dist
    if [ -d "$LOCAL_FRONTEND_DIR/dist" ]; then
        print_warn "检测到 dist 目录已存在，但可能是旧构建产物"
        read -p "是否重新构建前端以确保代码生效？(Y/n): " build_choice
        if [ "$build_choice" != "n" ] && [ "$build_choice" != "N" ]; then
            cd "$LOCAL_FRONTEND_DIR"
            print_info "正在重新构建前端..."
            npm run build
            if [ $? -ne 0 ]; then
                print_error "前端构建失败"
                exit 1
            fi
            print_info "前端构建成功"
        else
            print_warn "跳过重新构建，将直接使用当前 dist 进行部署（若 dist 旧，页面仍不会更新）"
        fi
    else
        print_warn "未找到 dist 目录，需要先构建前端"
        cd "$LOCAL_FRONTEND_DIR"
        print_info "正在构建前端..."
        npm run build
        if [ $? -ne 0 ]; then
            print_error "前端构建失败"
            exit 1
        fi
        print_info "前端构建成功"
    fi
    
    print_step "步骤 4: 上传前端代码..."
    
    # 上传 dist 目录和 nginx.conf
    rsync -avz --progress \
        -e "ssh -i $SSH_KEY_PATH" \
        "$LOCAL_FRONTEND_DIR/dist/" "${SERVER_USER}@${SERVER_IP}:${FRONTEND_DIR}/dist/"
    
    rsync -avz --progress \
        -e "ssh -i $SSH_KEY_PATH" \
        "$LOCAL_FRONTEND_DIR/nginx.conf" "${SERVER_USER}@${SERVER_IP}:${FRONTEND_DIR}/"
    
    if [ $? -ne 0 ]; then
        print_error "前端代码上传失败"
        exit 1
    fi
    print_info "前端代码上传成功"
    echo ""
    
    # 重新构建并重启前端服务
    print_step "步骤 5: 重新构建并重启前端服务..."
    ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" << 'EOF'
set -e
cd /opt/u-linker-frontend

# 检测 Docker Compose 命令格式
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 前端代码在容器内（构建时复制），需要重新构建镜像
echo "停止并删除旧容器..."
docker stop u-linker-frontend 2>/dev/null || true
docker rm u-linker-frontend 2>/dev/null || true

echo "重新构建前端镜像（使用新的 dist 目录）..."
${DOCKER_COMPOSE} -f docker-compose.frontend-simple.yml build frontend

echo "启动新容器..."
${DOCKER_COMPOSE} -f docker-compose.frontend-simple.yml up -d frontend

echo "等待服务启动（5秒）..."
sleep 5

echo "前端服务状态："
docker ps --filter "name=u-linker-frontend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "前端服务已重新构建并启动"
EOF
    
    if [ $? -ne 0 ]; then
        print_error "前端服务重启失败"
        exit 1
    fi
    echo ""
fi

# 生成测试数据（不需要更新代码，只需要运行脚本）
if [ "$GENERATE_DATA" = true ]; then
    print_step "生成测试数据（不更新代码）..."
    
    # 检查脚本是否已存在于服务器上，如果不存在才上传
    print_info "检查数据生成脚本是否存在..."
    script_exists=$(ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" \
        "test -f ${BACKEND_DIR}/generate_test_data.py && echo 'exists' || echo 'not_exists'")
    
    if [ "$script_exists" = "not_exists" ]; then
        print_info "脚本不存在，正在上传..."
        rsync -avz --progress \
            -e "ssh -i $SSH_KEY_PATH" \
            "$LOCAL_BACKEND_DIR/generate_test_data.py" "${SERVER_USER}@${SERVER_IP}:${BACKEND_DIR}/"
    else
        print_info "脚本已存在，跳过上传（如需更新脚本，请选择选项 1 或 3）"
    fi
    
    # 在服务器上运行数据生成脚本（不需要更新代码）
    ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" << 'EOF'
set -e
cd /opt/u-linker-backend

# 检查脚本是否存在
if [ ! -f "generate_test_data.py" ]; then
    echo "错误：generate_test_data.py 不存在"
    exit 1
fi

# 在容器内运行数据生成脚本（只生成数据，不修改代码）
echo "正在生成测试数据..."
echo "注意：此操作只生成数据，不会更新前后端代码"
docker exec u-linker-web python3 /app/generate_test_data.py

echo "测试数据生成完成"
EOF
    
    if [ $? -ne 0 ]; then
        print_error "测试数据生成失败"
        exit 1
    fi
    echo ""
fi

# 数据库迁移
if [ "$MIGRATE_DB" = true ]; then
    print_step "数据库迁移..."
    
    # 上传迁移脚本（如果不存在）
    print_info "检查迁移脚本是否存在..."
    script_exists=$(ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" \
        "test -f ${BACKEND_DIR}/migrate_database.py && echo 'exists' || echo 'not_exists'")
    
    if [ "$script_exists" = "not_exists" ]; then
        print_info "脚本不存在，正在上传..."
        rsync -avz --progress \
            -e "ssh -i $SSH_KEY_PATH" \
            "$LOCAL_BACKEND_DIR/migrate_database.py" "${SERVER_USER}@${SERVER_IP}:${BACKEND_DIR}/"
    else
        print_info "脚本已存在，跳过上传"
    fi
    
    # 在服务器上运行数据库迁移脚本
    ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" << 'EOF'
set -e
cd /opt/u-linker-backend

# 检查脚本是否存在
if [ ! -f "migrate_database.py" ]; then
    echo "错误：migrate_database.py 不存在"
    exit 1
fi

# 检查容器是否运行
if ! docker ps | grep -q u-linker-web; then
    echo "错误：后端容器未运行，请先启动服务"
    exit 1
fi

# 在容器内运行数据库迁移脚本
echo "正在运行数据库迁移..."
docker exec u-linker-web python /app/migrate_database.py

echo "数据库迁移完成"
EOF
    
    if [ $? -ne 0 ]; then
        print_error "数据库迁移失败"
        exit 1
    fi
    print_info "数据库迁移成功"
    echo ""
fi

print_info "部署完成！"
echo ""
print_info "访问地址："
print_info "前端: http://${SERVER_IP}"
print_info "后端 API: http://${SERVER_IP}/api/"
echo ""

