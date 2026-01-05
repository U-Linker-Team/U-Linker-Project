# 多阶段构建：第一阶段 - 构建 Vue 应用
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production=false

# 复制项目文件
COPY . .

# 构建应用（生成 dist 目录）
RUN npm run build

# 第二阶段 - 使用 Nginx 提供静态文件
FROM nginx:alpine

# 复制构建好的文件到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# Nginx 会自动启动，不需要 CMD

