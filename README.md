# 家校信息智能管家

基于 AI 的微信群消息智能解析与任务管理工具，帮助家长和学生高效管理作业和通知。

## 🎯 核心功能

- ✅ **批量转发**：支持一次转发多条微信群消息
- 🤖 **AI 解析**：自动识别作业/通知，提取科目、时间、内容
- 👨‍👩‍👧 **多学生支持**：一个家庭管理多个学生的任务
- ✅ **任务确认**：AI 解析结果需用户确认后入库，避免误识别
- 🔔 **智能提醒**：每日定时推送未完成任务清单
- 📊 **任务看板**：按学生分类展示待办列表

## 🏗️ 技术架构

- **后端框架**：Python 3.10+ + Flask
- **数据库**：SQLite (开发) / PostgreSQL (生产)
- **AI 模型**：DeepSeek API (性价比高)
- **部署方式**：云函数 (推荐) / 云服务器

## 📦 项目结构

```
jiaxiao/
├── app.py                  # Flask 主应用
├── config.py               # 配置管理
├── models.py               # 数据库模型
├── llm_parser.py           # LLM 解析器
├── requirements.txt        # 依赖清单
├── utils/
│   ├── __init__.py
│   ├── logger.py           # 日志工具
│   ├── metrics.py          # 指标收集
│   └── fallback.py         # 降级策略
├── logs/                   # 日志目录
├── scf_app/                # 云函数配置
├── .env.example            # 环境变量示例
├── Product.md              # 产品与技术文档
└── README.md               # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd jiaxiao

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要配置
# 必须配置：
# - LLM_API_KEY (DeepSeek API Key)
# - WECHAT_TOKEN (微信测试号 Token)
```

### 3. 初始化数据库

```bash
python -c "from models import init_db; init_db()"
```

### 4. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 5. 微信接入配置

1. 访问 [微信公众平台测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 配置服务器地址：
   - URL: `http://your-domain.com/wechat`（需公网可访问）
   - Token: 与 `.env` 中的 `WECHAT_TOKEN` 一致
3. 提交配置，通过验证

## 📱 使用流程

### 家长操作流程

1. **转发消息**：在微信群中长按老师消息 → 转发给"AI 家校管家"
2. **查看解析**：AI 自动解析并返回结果卡片
3. **确认任务**：点击卡片，选择归属学生，确认后入库
4. **管理任务**：在小程序中查看、标记完成任务

### 学生操作流程

1. **登录小程序**：使用微信登录
2. **查看任务**：查看自己的待办列表
3. **标记完成**：完成后打钩标记

## 🔧 核心 API

### 微信消息接口

- **URL**: `/wechat`
- **方法**: GET/POST
- **说明**: 微信服务器回调接口

### 任务确认接口

- **URL**: `/api/confirm`
- **方法**: POST
- **参数**:
  ```json
  {
    "pending_id": "xxx",
    "student_id": "xxx"
  }
  ```

### 获取任务列表

- **URL**: `/api/tasks/<student_id>`
- **方法**: GET
- **返回**: 任务列表

### 标记任务完成

- **URL**: `/api/tasks/<task_id>/complete`
- **方法**: POST

### 健康检查

- **URL**: `/health`
- **方法**: GET
- **返回**: 系统状态

### 指标监控

- **URL**: `/metrics`
- **方法**: GET
- **返回**: 系统指标（调用次数、响应时间等）

## 🔐 数据安全

- 所有敏感信息存储在环境变量中
- 数据库密码不提交到代码仓库
- `.env` 文件加入 `.gitignore`

## 📊 数据库设计

### 核心表结构

- **families**：家庭表（家长信息）
- **students**：学生表（关联家庭）
- **tasks**：任务表（关联学生）
- **pending_tasks**：待确认任务临时表

详细设计参考 [Product.md](./Product.md)

## 🛠️ 开发指南

### 添加新功能

1. 在 `app.py` 中添加路由
2. 在 `models.py` 中定义数据模型（如需要）
3. 在 `utils/` 中添加工具函数（如需要）
4. 更新文档

### 运行测试

```bash
# 单元测试（待实现）
pytest tests/
```

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log
```

## 🚀 部署指南

### 云函数部署（推荐）

1. 安装腾讯云 CLI
2. 配置云函数
3. 上传代码包
4. 配置环境变量
5. 测试

详细步骤参考 [Product.md](./Product.md) 第 5 节。

### 云服务器部署

1. 购买云服务器（腾讯云/阿里云）
2. 安装 Python 环境
3. 拉取代码
4. 配置 Nginx 反向代理
5. 使用 Supervisor/Gunicorn 运行

## 📝 开发路线图

### Phase 1: 基础设施 ✅
- [x] 项目框架搭建
- [x] 数据库模型定义
- [x] 微信消息接收

### Phase 2: AI 解析 ✅
- [x] LLM API 接入
- [x] Prompt 工程
- [x] 降级策略

### Phase 3: 用户确认
- [x] 任务确认接口
- [ ] 模板消息推送
- [ ] 小程序开发

### Phase 4: 多学生支持
- [x] 家庭/学生管理
- [ ] 任务分配功能
- [ ] 权限控制

### Phase 5: 体验优化
- [ ] OCR 图片识别
- [ ] 定时任务提醒
- [ ] 批量消息处理

## 🐛 常见问题

### Q: 微信验证失败？
A: 检查 `.env` 中的 `WECHAT_TOKEN` 是否与微信公众平台配置一致。

### Q: LLM 解析失败？
A:
1. 检查 `LLM_API_KEY` 是否正确
2. 查看日志 `logs/app.log`
3. 系统会自动降级到关键词匹配

### Q: 数据库连接失败？
A: 检查 `DATABASE_URL` 是否正确，SQLite 文件路径是否存在。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请查看 [Product.md](./Product.md) 或提交 Issue。
