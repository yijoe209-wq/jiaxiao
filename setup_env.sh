#!/bin/bash
# 安全配置环境变量脚本
# 此脚本会创建 .env 文件，并确保不会被提交到 Git

echo "=========================================="
echo "家校任务管理助手 - 环境配置"
echo "=========================================="
echo ""

# 检查 .env 是否已存在
if [ -f .env ]; then
    echo "⚠️  .env 文件已存在"
    echo "是否要重新配置？(yes/no)"
    read -r confirm
    if [ "$confirm" != "yes" ]; then
        echo "取消配置"
        exit 0
    fi
    # 备份现有配置
    cp .env .env.backup.$(date +%Y%m%d%H%M%S)
    echo "✅ 已备份现有配置到 .env.backup.$(date +%Y%m%d%H%M%S)"
fi

echo ""
echo "请输入 DeepSeek API Key："
echo "提示：从 https://platform.deepseek.com/ 获取"
echo "格式：sk-xxxxxxxxxxxxxxxx"
read -r DEEPSEEK_API_KEY

# 验证 API Key 格式
if [[ ! $DEEPSEEK_API_KEY =~ ^sk- ]]; then
    echo "❌ API Key 格式不正确，应该以 'sk-' 开头"
    exit 1
fi

echo ""
echo "请输入微信 Token（用于服务器验证）："
echo "提示：可以自定义一个随机字符串，如：jiaxiao-2024-token"
read -r WECHAT_TOKEN

# 生成随机 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

echo ""
echo "正在创建 .env 文件..."

cat > .env << EOF
# Flask 配置
SECRET_KEY=$SECRET_KEY
DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///jiaxiao.db

# 微信配置
WECHAT_TOKEN=$WECHAT_TOKEN
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_ENCODING_AES_KEY=

# LLM 配置 (DeepSeek)
LLM_API_KEY=$DEEPSEEK_API_KEY
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=500

# OCR 配置（可选）
OCR_SECRET_ID=
OCR_SECRET_KEY=
OCR_REGION=ap-beijing

# 异步任务配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs

# 告警配置（可选）
ALERT_WEBHOOK_URL=
ALERT_ERROR_THRESHOLD=10

# 业务配置
TASK_CONFIRM_TIMEOUT=86400
DEFAULT_REMINDER_TIME=17:00
EOF

echo "✅ .env 文件创建成功"
echo ""

# 验证 .gitignore 中是否有 .env
if ! grep -q "^\.env$" .gitignore; then
    echo "⚠️  警告：.gitignore 中没有 .env 规则"
    echo "正在添加..."
    echo ".env" >> .gitignore
    echo "✅ 已添加到 .gitignore"
fi

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "🔒 安全提醒："
echo "1. .env 文件已添加到 .gitignore，不会被提交到 Git"
echo "2. 请妥善保管你的 API Key，不要分享给他人"
echo "3. 定期更换 API Key 以保证安全"
echo ""
echo "📝 下一步："
echo "1. 测试 API 连接：python test_llm.py"
echo "2. 初始化数据库：python init_db.py"
echo "3. 启动服务：python app.py"
echo ""
