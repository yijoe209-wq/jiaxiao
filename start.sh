#!/bin/bash

# 家校任务管理助手 - 开发服务器启动脚本

echo "🚀 正在启动家校任务管理助手..."

# 设置开发环境变量
export ENV=development
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动 Flask 服务器
python3 app.py
