#!/bin/bash
# 数据库备份脚本
# 用于在迁移前备份数据库

set -e

# 配置信息
SERVER_IP="121.89.81.18"
SERVER_USER="root"
SSH_KEY_PATH="~/.ssh/u-linker.pem"
BACKEND_DIR="/opt/u-linker-backend"

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

echo "=" | head -c 60
echo ""
echo "数据库备份脚本"
echo "=" | head -c 60
echo ""

# 在服务器上执行备份
print_step "正在备份数据库..."
ssh -i "$SSH_KEY_PATH" "${SERVER_USER}@${SERVER_IP}" << 'EOF'
set -e

# 进入后端目录，读取环境变量
cd /opt/u-linker-backend

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "错误：.env文件不存在，无法获取数据库密码"
    exit 1
fi

# 读取环境变量
source .env

# 检查必要的环境变量
if [ -z "$MYSQL_ROOT_PASSWORD" ] && [ -z "$MYSQL_PASSWORD" ]; then
    echo "错误：无法获取数据库密码（MYSQL_ROOT_PASSWORD 或 MYSQL_PASSWORD）"
    exit 1
fi

# 生成备份文件名
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
BACKUP_PATH="/root/${BACKUP_FILE}"

echo "备份文件: ${BACKUP_FILE}"

# 检查MySQL容器是否运行
if ! docker ps | grep -q u-linker-mysql; then
    echo "错误：MySQL容器未运行"
    exit 1
fi

# 使用root用户备份（推荐，root用户有所有权限）
if [ -n "$MYSQL_ROOT_PASSWORD" ]; then
    echo "使用root用户备份..."
    docker exec u-linker-mysql mysqldump \
        -u root \
        -p"${MYSQL_ROOT_PASSWORD}" \
        u_linker_db > "${BACKUP_PATH}"
else
    # 如果没有root密码，使用普通用户
    echo "使用普通用户备份..."
    docker exec u-linker-mysql mysqldump \
        -u u_linker_user \
        -p"${MYSQL_PASSWORD}" \
        u_linker_db > "${BACKUP_PATH}"
fi

# 检查备份是否成功
if [ $? -eq 0 ] && [ -f "${BACKUP_PATH}" ]; then
    # 压缩备份文件（可选）
    gzip "${BACKUP_PATH}" 2>/dev/null || true
    if [ -f "${BACKUP_PATH}.gz" ]; then
        BACKUP_FILE="${BACKUP_FILE}.gz"
        BACKUP_PATH="${BACKUP_PATH}.gz"
    fi
    
    # 获取文件大小
    FILE_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
    echo "✅ 备份成功！"
    echo "   文件: ${BACKUP_FILE}"
    echo "   大小: ${FILE_SIZE}"
    echo "   路径: ${BACKUP_PATH}"
else
    echo "❌ 备份失败"
    exit 1
fi
EOF

if [ $? -eq 0 ]; then
    print_info "数据库备份完成！"
    print_info "备份文件已保存在服务器 /root/ 目录下"
    print_info "如需下载到本地，请使用以下命令："
    echo ""
    echo "scp -i ${SSH_KEY_PATH} \\"
    echo "  ${SERVER_USER}@${SERVER_IP}:/root/backup_*.sql* \\"
    echo "  ~/backups/"
    echo ""
else
    print_error "数据库备份失败"
    exit 1
fi

