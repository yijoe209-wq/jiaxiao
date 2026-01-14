#!/bin/bash

echo "================================"
echo "家校任务助手 - 本地测试环境"
echo "================================"
echo ""

# 设置环境变量
export ENV=development
export DATABASE_URL='sqlite:///jiaxiao_local.db'
export SECRET_KEY='local-dev-secret-key-12345'
export UPLOAD_FOLDER='./tmp/uploads'

# 创建上传目录
mkdir -p ./tmp/uploads

echo "✅ 环境变量已设置"
echo "   - 数据库: sqlite:///jiaxiao_local.db"
echo "   - 上传目录: ./tmp/uploads"
echo ""

echo "🚀 启动 Flask 服务器..."
echo "   访问地址: http://localhost:5000"
echo "   按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python app.py
