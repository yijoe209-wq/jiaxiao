#!/bin/bash

# UI/UX Pro Max Skill 安装脚本
# 用途：为家校任务助手项目安装 UI/UX Pro Max Skill

set -e  # 遇到错误立即退出

echo "=========================================="
echo "UI/UX Pro Max Skill 安装向导"
echo "=========================================="
echo ""

# 检查 Python 环境
echo "📦 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ 找到 $PYTHON_VERSION"
echo ""

# 选择安装方式
echo "请选择安装方式："
echo "1) 项目级安装（仅用于当前项目）"
echo "2) 全局安装（所有项目可用，推荐）"
echo ""
read -p "请输入选项 [1/2]: " install_choice

if [ "$install_choice" = "1" ]; then
    # 项目级安装
    echo ""
    echo "📁 项目级安装模式"
    echo ""

    # 创建项目目录结构
    PROJECT_ROOT="/Volumes/data/vibe-coding-projects/jiaxiao"
    mkdir -p "$PROJECT_ROOT/.claude/skills"

    # 临时克隆仓库
    TEMP_DIR=$(mktemp -d)
    echo "⬇️  克隆 UI/UX Pro Max Skill 仓库到临时目录..."
    git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git "$TEMP_DIR" > /dev/null 2>&1 || {
        echo "❌ 克隆失败，请检查网络连接"
        rm -rf "$TEMP_DIR"
        exit 1
    }

    # 复制 skill 到项目
    echo "📋 复制 Skill 到项目..."
    cp -r "$TEMP_DIR/.claude/skills/ui-ux-pro-max" "$PROJECT_ROOT/.claude/skills/"

    # 清理临时目录
    rm -rf "$TEMP_DIR"

    echo "✅ 安装完成！"
    echo ""
    echo "📍 安装路径: $PROJECT_ROOT/.claude/skills/ui-ux-pro-max"
    echo ""
    echo "🧪 测试安装："
    echo "   cd $PROJECT_ROOT"
    echo "   python3 .claude/skills/ui-ux-pro-max/scripts/search.py \"SaaS\" --domain product -n 1"

elif [ "$install_choice" = "2" ]; then
    # 全局安装
    echo ""
    echo "🌍 全局安装模式"
    echo ""

    # 创建全局目录
    GLOBAL_SKILL_DIR="$HOME/.claude/skills"
    mkdir -p "$GLOBAL_SKILL_DIR"

    # 临时克隆仓库
    TEMP_DIR=$(mktemp -d)
    echo "⬇️  克隆 UI/UX Pro Max Skill 仓库到临时目录..."
    git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git "$TEMP_DIR" > /dev/null 2>&1 || {
        echo "❌ 克隆失败，请检查网络连接"
        rm -rf "$TEMP_DIR"
        exit 1
    }

    # 复制 skill 到全局目录
    echo "📋 复制 Skill 到全局目录..."
    cp -r "$TEMP_DIR/.claude/skills/ui-ux-pro-max" "$GLOBAL_SKILL_DIR/"

    # 清理临时目录
    rm -rf "$TEMP_DIR"

    echo "✅ 安装完成！"
    echo ""
    echo "📍 安装路径: $GLOBAL_SKILL_DIR/ui-ux-pro-max"
    echo ""
    echo "🧪 测试安装："
    echo "   python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py \"SaaS\" --domain product -n 1"
    echo ""
    echo "🔗 在项目中使用（可选）："
    echo "   cd /Volumes/data/vibe-coding-projects/jiaxiao"
    echo "   ln -s ~/.claude/skills/ui-ux-pro-max .claude/skills/ui-ux-pro-max"

else
    echo "❌ 无效选项"
    exit 1
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "📚 使用指南："
echo "   1. 查看集成方案文档："
echo "      cat UI_UX_PRO_MAX_INTEGRATION_PLAN.md"
echo ""
echo "   2. 搜索设计建议示例："
echo "      python3 .claude/skills/ui-ux-pro-max/scripts/search.py \"education SaaS\" --domain product -n 3"
echo ""
echo "   3. 查看所有可用命令："
echo "      python3 .claude/skills/ui-ux-pro-max/scripts/search.py --help"
echo ""
