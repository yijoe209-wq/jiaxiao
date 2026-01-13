@echo off
REM 安全配置环境变量脚本 (Windows)
REM 此脚本会创建 .env 文件，并确保不会被提交到 Git

echo ==========================================
echo 家校任务管理助手 - 环境配置
echo ==========================================
echo.

REM 检查 .env 是否已存在
if exist .env (
    echo ⚠️  .env 文件已存在
    echo 是否要重新配置？^(yes/no^)
    set /p confirm=
    if not "%confirm%"=="yes" (
        echo 取消配置
        exit /b 0
    )
    REM 备份现有配置
    set backup=.env.backup.%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%%time:~3,2%%time:~6,2%
    ren .env %backup%
    echo ✅ 已备份现有配置到 %backup%
)

echo.
echo 请输入 DeepSeek API Key：
echo 提示：从 https://platform.deepseek.com/ 获取
echo 格式：sk-xxxxxxxxxxxxxxxx
set /p DEEPSEEK_API_KEY=

REM 简单验证 API Key 格式
echo %DEEPSEEK_API_KEY% | findstr /B /C:"sk-" >nul
if errorlevel 1 (
    echo ❌ API Key 格式不正确，应该以 'sk-' 开头
    pause
    exit /b 1
)

echo.
echo 请输入微信 Token（用于服务器验证）：
echo 提示：可以自定义一个随机字符串，如：jiaxiao-2024-token
set /p WECHAT_TOKEN=

echo.
echo 正在创建 .env 文件...

(
echo # Flask 配置
echo SECRET_KEY=auto-generated-secret-key
echo DEBUG=True
echo.
echo # 数据库配置
echo DATABASE_URL=sqlite:///jiaxiao.db
echo.
echo # 微信配置
echo WECHAT_TOKEN=%WECHAT_TOKEN%
echo WECHAT_APP_ID=
echo WECHAT_APP_SECRET=
echo WECHAT_ENCODING_AES_KEY=
echo.
echo # LLM 配置 ^(DeepSeek^)
echo LLM_API_KEY=%DEEPSEEK_API_KEY%
echo LLM_API_BASE=https://api.deepseek.com/v1
echo LLM_MODEL=deepseek-chat
echo LLM_TEMPERATURE=0.3
echo LLM_MAX_TOKENS=500
echo.
echo # OCR 配置（可选）
echo OCR_SECRET_ID=
echo OCR_SECRET_KEY=
echo OCR_REGION=ap-beijing
echo.
echo # 异步任务配置
echo CELERY_BROKER_URL=redis://localhost:6379/0
echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
echo.
echo # 日志配置
echo LOG_LEVEL=INFO
echo LOG_DIR=logs
echo.
echo # 告警配置（可选）
echo ALERT_WEBHOOK_URL=
echo ALERT_ERROR_THRESHOLD=10
echo.
echo # 业务配置
echo TASK_CONFIRM_TIMEOUT=86400
echo DEFAULT_REMINDER_TIME=17:00
) > .env

echo ✅ .env 文件创建成功
echo.

REM 验证 .gitignore 中是否有 .env
findstr /B /C:".env" .gitignore >nul
if errorlevel 1 (
    echo ⚠️  警告：.gitignore 中没有 .env 规则
    echo 正在添加...
    echo .env >> .gitignore
    echo ✅ 已添加到 .gitignore
)

echo.
echo ==========================================
echo 配置完成！
echo ==========================================
echo.
echo 🔒 安全提醒：
echo 1. .env 文件已添加到 .gitignore，不会被提交到 Git
echo 2. 请妥善保管你的 API Key，不要分享给他人
echo 3. 定期更换 API Key 以保证安全
echo.
echo 📝 下一步：
echo 1. 测试 API 连接：python test_llm.py
echo 2. 初始化数据库：python init_db.py
echo 3. 启动服务：python app.py
echo.
pause
