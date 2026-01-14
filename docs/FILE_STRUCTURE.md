# 项目文件结构

## 主要页面（正在使用的）

| 页面 | 文件 | 路由 | 状态 |
|------|------|------|------|
| 登录/注册 | `templates/auth.html` | `/login` | ✅ 使用中 |
| 首页（创建任务） | `templates/simulate.html` | `/` | ✅ 使用中 |
| 任务中心 | `templates/my-tasks.html` | `/my-tasks` | ✅ 使用中 |

## 其他页面（可能已废弃）

| 页面 | 文件 | 路由 | 说明 |
|------|------|------|------|
| 旧首页 | `templates/index.html` | - | 可能已被 simulate.html 替代 |
| 任务确认 | `templates/confirm.html` | `/confirm` | 微信内打开时使用 |
| 学生管理 | `templates/students.html` | `/students` | 功能已集成到其他页面 |
| 任务列表 | `templates/tasks.html` | `/tasks` | 可能已被 my-tasks.html 替代 |
| 微信模拟 | `templates/wechat-simulate.html` | - | 测试页面 |

## 关键文件

### 后端
- `app.py` - Flask 主应用，所有 API 和路由
- `models.py` - 数据库模型
- `llm_parser.py` - AI 解析逻辑
- `config.py` - 配置文件

### 前端模板
- `templates/auth.html` - 登录注册页面
- `templates/simulate.html` - 首页（创建任务）
- `templates/my-tasks.html` - 任务中心

### 工具和文档
- `run_local.sh` - 本地启动脚本
- `LOCAL_TEST_GUIDE.md` - 本地测试指南
- `TEST_REPORT_FINAL.md` - 测试报告

---

**当前核心页面只有 3 个：auth.html, simulate.html, my-tasks.html**
