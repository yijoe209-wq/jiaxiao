# UI/UX Pro Max Skill - 快速开始指南

**日期**: 2026-01-14
**项目**: 家校任务助手 UI 优化

---

## 🎯 核心功能说明

UI/UX Pro Max Skill 是一个 AI 驱动的设计智能工具包，提供：

### 设计资源库
- **57+ UI 风格**: glassmorphism, minimalism, brutalism, neumorphism 等
- **95+ 配色方案**: 针对不同产品类型优化
- **96+ 产品类型**: SaaS、电商、教育等
- **56+ 字体搭配**: 包含 Google Fonts 导入代码
- **24+ 图表类型**: 适用于各种数据可视化场景

### 搜索引擎
- BM25 排名算法 + 正则表达式混合搜索
- 自动领域检测
- 支持多域搜索组合

---

## 📥 安装方法（3 种方式）

### 方式 1: 克隆 GitHub 仓库（推荐）

```bash
# 进入项目目录
cd /Volumes/data/vibe-coding-projects/jiaxiao

# 创建 skills 目录
mkdir -p .claude/skills

# 克隆仓库到临时目录
cd /tmp
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git

# 复制 skill 到项目
cp -r ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max /Volumes/data/vibe-coding-projects/jiaxiao/.claude/skills/

# 验证安装
ls -la /Volumes/data/vibe-coding-projects/jiaxiao/.claude/skills/ui-ux-pro-max/

# 测试搜索功能
cd /Volumes/data/vibe-coding-projects/jiaxiao
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "SaaS" --domain product -n 3
```

### 方式 2: 手动下载（网络不稳定时使用）

1. 访问 [GitHub Releases](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/releases)
2. 下载最新版本的 zip 文件
3. 解压后复制 `.claude/skills/ui-ux-pro-max` 到项目目录

### 方式 3: 使用项目中的安装脚本

```bash
cd /Volumes/data/vibe-coding-projects/jiaxiao
./install_ui_ux_skill.sh
```

---

## 🚀 使用示例

### 基础用法

```bash
# 搜索产品类型推荐
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "education SaaS" --domain product -n 5

# 搜索 UI 风格
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "modern minimal professional" --domain style -n 3

# 搜索配色方案
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "family friendly trust" --domain color -n 5

# 搜索字体搭配
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "readable chinese" --domain typography -n 3

# 搜索 UX 最佳实践
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "accessibility" --domain ux -n 5
```

### 家校任务助手专项搜索

```bash
# 1. 搜索教育 SaaS 产品设计建议
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "education SaaS parent student" --domain product -n 5

# 2. 搜索适合的 UI 风格
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "professional friendly clean" --domain style -n 3

# 3. 搜索配色方案
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "education family warm trust" --domain color -n 5

# 4. 搜索字体搭配
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "modern readable" --domain typography -n 3

# 5. 搜索 Tailwind CSS 最佳实践
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "responsive layout" --stack html-tailwind -n 5

# 6. 搜索 Dashboard 设计
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard statistics cards" --domain product -n 3

# 7. 搜索表单设计
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "form input validation" --domain ux -n 3

# 8. 搜索任务管理设计
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "task management list card" --domain product -n 3
```

---

## 📋 可用搜索域 (Domains)

| Domain | 用途 | 示例关键词 |
|--------|------|-----------|
| `product` | 产品类型推荐 | SaaS, e-commerce, education, healthcare, portfolio |
| `style` | UI 风格、色彩、效果 | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | 字体搭配、Google Fonts | elegant, playful, professional, modern |
| `color` | 配色方案 | saas, ecommerce, education, beauty, fintech |
| `landing` | 页面结构、CTA 策略 | hero, testimonial, pricing, social-proof |
| `chart` | 图表类型、库推荐 | trend, comparison, timeline, funnel, pie |
| `ux` | 最佳实践、反模式 | animation, accessibility, z-index, loading |
| `prompt` | AI 提示词、CSS 关键词 | (风格名称) |

---

## 🛠️ 可用技术栈 (Stacks)

| Stack | 专注点 |
|-------|--------|
| `html-tailwind` | Tailwind 工具类、响应式、可访问性（默认）|
| `react` | 状态管理、hooks、性能、模式 |
| `nextjs` | SSR、路由、图片、API 路由 |
| `vue` | Composition API、Pinia、Vue Router |
| `svelte` | Runes、stores、SvelteKit |
| `swiftui` | Views、State、Navigation、Animation |
| `react-native` | Components、Navigation、Lists |
| `flutter` | Widgets、State、Layout、Theming |

---

## 📚 完整工作流程示例

### 场景：优化家校任务助手的任务中心页面

```bash
# Step 1: 了解产品类型
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "education SaaS task management" --domain product -n 3

# Step 2: 确定 UI 风格
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "modern minimal professional dashboard" --domain style -n 3

# Step 3: 选择配色方案
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "education family trust warm" --domain color -n 5

# Step 4: 选择字体
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "readable professional modern" --domain typography -n 3

# Step 5: 搜索 Dashboard 最佳实践
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard statistics cards filters" --domain product -n 3

# Step 6: 搜索数据可视化建议
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "task completion progress chart" --domain chart -n 3

# Step 7: 搜索 UX 指南
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "accessibility animation hover" --domain ux -n 5

# Step 8: 搜索技术栈指南
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "responsive layout components" --stack html-tailwind -n 5
```

**然后**：
1. 综合所有搜索结果
2. 提取关键设计元素
3. 创建设计令牌（colors、fonts、spacing）
4. 实施到具体页面

---

## 🎨 家校任务助手设计系统建议

### 推荐配置

基于项目特点（教育、家庭、任务管理），推荐以下设计方向：

#### 1. 产品类型
- **Education SaaS** - 专业且友好
- **Dual-user** - 家长和学生双端用户

#### 2. UI 风格
- **Modern Minimalism** - 现代极简主义
- **Soft UI** - 柔和界面
- 关键词: clean, professional, friendly, trustworthy

#### 3. 配色方案
```css
/* 主色 - 温暖橙色（活力、友好）*/
--primary: #F59E0B;

/* 辅色 - 专业蓝色（信任、稳定）*/
--secondary: #3B82F6;

/* 成功色 - 绿色（完成、成就）*/
--success: #10B981;

/* 警告色 - 琥珀色（提醒、注意）*/
--warning: #F59E0B;

/* 危险色 - 红色（逾期、重要）*/
--danger: #EF4444;

/* 中性色 - 灰色系（文本、边框）*/
--neutral: #6B7280;
```

#### 4. 字体搭配
```html
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<!-- CSS -->
<style>
  body {
    font-family: 'Noto Sans SC', 'Inter', sans-serif;
  }
  .heading {
    font-family: 'Noto Sans SC', sans-serif;
  }
  .number {
    font-family: 'Inter', sans-serif;
  }
</style>
```

#### 5. 设计原则
- **清晰优先** - 信息层级分明
- **友好亲和** - 温暖的色彩和圆角
- **专业可信** - 保持视觉一致性
- **高效操作** - 减少点击步骤

---

## 🔧 常见问题

### Q1: 搜索速度慢怎么办？
**A**:
- 使用更具体的关键词
- 减少 `-n` 参数（返回结果数量）
- 使用 `--domain` 精确搜索域

### Q2: 搜索结果不匹配？
**A**:
- 尝试不同的关键词组合
- 使用 `--domain` 指定搜索域
- 查看相似风格的产品

### Q3: 如何应用到项目中？
**A**:
1. 搜索相关设计指南
2. 提取关键设计元素
3. 创建设计令牌文件
4. 更新 Tailwind 配置
5. 应用到具体组件

### Q4: 可以离线使用吗？
**A**:
- 可以！所有数据都是本地 CSV 文件
- 无需网络连接即可搜索
- Python 是唯一依赖

---

## 📖 进一步学习

### 官方资源
- [GitHub 仓库](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [Live Demo](https://ui-ux-pro-max-skill.nextlevelbuilder.io/)
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)

### 社区资源
- [深度解析（腾讯云）](https://cloud.tencent.com/developer/article/2616211)
- [完整指南（Reddit）](https://www.reddit.com/r/journalcollector/comments/1pii7zo/uiux_pro_max_skill_complete_guide_design_skills/)
- [My 3-Step Claude Skill（YouTube）](https://www.youtube.com/watch?v=nDHXLnwlIaY)

---

## ✅ 下一步行动

1. **立即行动**：
   ```bash
   # 安装 Skill
   cd /Volumes/data/vibe-coding-projects/jiaxiao
   ./install_ui_ux_skill.sh
   ```

2. **短期目标**：
   - 运行示例搜索命令
   - 记录适合项目的设计指南
   - 创建设计令牌文件

3. **长期目标**：
   - 建立完整的设计系统
   - 创建可复用的组件库
   - 应用到其他项目

---

**文档版本**: v1.0
**创建日期**: 2026-01-14
**作者**: Claude
