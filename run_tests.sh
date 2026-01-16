#!/bin/bash

# Playwright E2E 测试启动脚本
# 家校任务管理助手 - 自动化测试

echo "========================================"
echo "🚀 家校任务管理助手 E2E 测试"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import playwright" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Playwright 未安装，正在安装..."
    pip3 install -r requirements-test.txt
    playwright install chromium
    echo ""
else
    echo "✅ 依赖已安装"
    echo ""
fi

# 显示测试信息
echo "========================================"
echo "📋 测试信息"
echo "========================================"
echo "测试环境: https://edu-track.zeabur.app"
echo "测试场景: 7 个"
echo "预计耗时: 60 秒"
echo ""
echo "测试场景列表:"
echo "  1. 新用户注册和首次使用"
echo "  2. 添加学生信息"
echo "  3. 快速添加任务（AI 解析）"
echo "  4. 任务中心管理"
echo "  5. 完成和编辑任务"
echo "  6. 多任务批量确认"
echo "  7. 退出登录"
echo ""
echo "========================================"
echo ""

# 询问是否继续
read -p "是否开始测试？(y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 测试已取消"
    exit 0
fi

echo ""
echo "========================================"
echo "🎬 开始测试..."
echo "========================================"
echo ""

# 运行测试
python3 tests_e2e.py

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 测试完成"
    echo "========================================"
    echo ""
    echo "📸 截图已保存到当前目录"
    echo "📝 查看截图文件: test_screenshot_*.png"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ 测试失败"
    echo "========================================"
    echo ""
    echo "📸 请查看截图文件了解详情"
    echo "🔧 检查网络连接和应用部署状态"
    echo ""
    exit 1
fi
