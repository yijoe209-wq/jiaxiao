# Zeabur 部署详细步骤

> 📅 创建时间：2026-01-13
> 🎯 目标：将家校任务助手部署到 Zeabur 平台

---

## 📋 前置准备检查清单

在开始部署之前，请确保：

- [ ] ✅ 已注册 Zeabur 账号（https://zeabur.com）
- [ ] ✅ 代码已推送到 GitHub（https://github.com/yijoe209-wq/jiaxiao）
- [ ] ✅ 已准备好 DeepSeek API Key

---

## 🚀 第一步：登录 Zeabur 并创建项目

### 1.1 访问 Zeabur

1. 打开浏览器，访问：**https://zeabur.com**
2. 点击右上角 **"登录"** 或 **"Sign In"**
3. 使用以下方式之一登录：
   - GitHub 账号（推荐）
   - Google 账号
   - 邮箱注册

### 1.2 授权 GitHub（如果使用 GitHub 登录）

1. 登录后会提示授权 GitHub
2. 点击 **"Authorize Zeabur"**
3. 选择要授权的仓库范围（建议选择 "All repositories" 或仅选择 "yijoe209-wq/jiaxiao"）

### 1.3 创建新项目

1. 登录后进入控制台
2. 点击 **"Create New Project"** 或 **"创建新项目"**
3. 输入项目名称（可选）：`jiaxiao` 或保持默认
4. 点击 **"Create"**

---

## 🌍 第二步：导入 GitHub 仓库

### 2.1 选择导入方式

1. 在项目页面，点击 **"Deploy New Service"** 或 **"部署新服务"**
2. 选择 **"Git"** 标签
3. 选择 **"GitHub"**

### 2.2 选择仓库

1. 在仓库列表中找到并点击 **"yijoe209-wq/jiaxiao"**
2. 如果看不到仓库，点击 **"Refresh"** 刷新列表

### 2.3 选择部署区域

**重要：选择合适的区域**

| 区域 | 代码 | 推荐理由 |
|------|------|----------|
| 香港 🇭🇰 | `Hong Kong` | ✅ 推荐：国内访问速度快 |
| 新加坡 🇸🇬 | `Singapore` | ✅ 推荐：国内访问速度快 |
| 东京 🇯🇵 | `Tokyo` | ⚠️ 速度一般 |
| 美西部 🇺🇸 | `California` | ❌ 国内访问慢 |

**建议选择：Hong Kong 或 Singapore**

---

## ⚙️ 第三步：配置服务

Zeabur 会自动检测项目中的 `.zeabur.yaml` 配置文件，并创建以下服务：

### 3.1 自动创建的服务

1. **PostgreSQL 数据库** (`Postgres-JIAXIAO`)
   - 类型：PostgreSQL 15
   - 内存：256MB
   - 自动创建数据库：`jiaxiao_db`

2. **Flask 应用** (`jiaxiao`)
   - 类型：Python Flask
   - 内存：512MB
   - 启动命令：`gunicorn -w 2 -b 0.0.0.0:$PORT app:app`

### 3.2 检查服务配置

1. 点击 **jiaxiao** 服务
2. 确认以下配置正确：
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
   - **Dependencies**：依赖于 `Postgres-JIAXIAO`

---

## 🔐 第四步：配置环境变量

### 4.1 打开环境变量配置

1. 在 `jiaxiao` 服务页面
2. 找到 **"Environment Variables"** 或 **"环境变量"** 标签
3. 点击进入配置页面

### 4.2 添加必须的环境变量

#### 变量 1：LLM_API_KEY（必须）

| 字段 | 值 |
|------|-----|
| **Name** | `LLM_API_KEY` |
| **Value** | `sk-your-actual-deepseek-api-key` |

**如何获取 DeepSeek API Key：**
1. 访问：https://platform.deepseek.com
2. 登录 / 注册账号
3. 进入 **API Keys** 页面
4. 点击 **"Create API Key"**
5. 复制生成的 Key（格式：`sk-xxxxx`）
6. 粘贴到 Zeabur 的环境变量值中

⚠️ **注意：**
- API Key 以 `sk-` 开头
- 请妥善保管，不要泄露
- 如果没有 API Key，AI 解析功能将无法使用

#### 变量 2：SECRET_KEY（推荐）

| 字段 | 值 |
|------|-----|
| **Name** | `SECRET_KEY` |
| **Value** | `随机生成的32位十六进制字符串` |

**如何生成：**
```bash
# 在终端执行
python -c "import secrets; print(secrets.token_hex(32))"
```

复制生成的字符串并粘贴到环境变量中。

### 4.3 可选环境变量（微信公众号）

如果需要接入微信公众号，添加以下变量：

| Name | Value | 说明 |
|------|-------|------|
| `WECHAT_TOKEN` | `your-custom-token` | 自定义令牌（与公众号配置一致） |
| `WECHAT_APPID` | `wxXXXXXX` | 微信公众号 AppID |
| `WECHAT_SECRET` | `XXXXXX` | 微信公众号 AppSecret |

### 4.4 保存环境变量

1. 点击 **"Save"** 或 **"保存"**
2. 点击 **"Redeploy"** 或 **"重新部署"** 使环境变量生效

---

## 🚢 第五步：开始部署

### 5.1 触发部署

1. 配置完环境变量后，服务会自动开始部署
2. 或者手动点击 **"Deploy"** / **"Redeploy"** 按钮

### 5.2 查看部署日志

1. 点击 **"Logs"** / **"日志"** 标签
2. 观察部署进度：

```
✓ Cloning repository...
✓ Installing dependencies...
  - Flask==3.0.0
  - SQLAlchemy==2.0.23
  - gunicorn==21.2.0
  ...
✓ Building application...
✓ Starting service...
  ✓ Server is running on port 5001
```

### 5.3 等待部署完成

- **预计时间**：2-3 分钟
- **状态变为**：🟢 **Running** / **运行中**

---

## 🌐 第六步：获取访问地址

### 6.1 查看域名

1. 在 `jiaxiao` 服务页面
2. 找到 **"Domains"** / **"域名"** 标签
3. 会看到一个类似这样的地址：

```
https://your-project-name.zeabur.app
```

**示例：**
```
https://jiaxiao-abc123.zeabur.app
```

### 6.2 测试访问

1. 点击域名链接
2. 应该看到家校任务助手的主页面
3. 页面标题：**"家校任务助手"**

---

## 🗄️ 第七步：初始化数据库

### 7.1 访问初始化接口

在浏览器中打开：

```
https://your-project-name.zeabur.app/init
```

**示例：**
```
https://jiaxiao-abc123.zeabur.app/init
```

### 7.2 执行初始化

页面会显示初始化选项：

```
请选择操作：
1. 检查数据库连接
2. 创建所有表
3. 创建测试数据（学生 + 任务）
4. 创建表 + 测试数据（完整初始化）
```

### 7.3 选择完整初始化

**操作步骤：**

1. 点击选项 **4**（或访问 `/init?option=4`）
2. 等待初始化完成
3. 页面会显示：

```
✅ 初始化完成！

数据库表：
✓ students (学生表)
✓ pending_tasks (待解析任务)
✓ tasks (任务表)
✓ task_images (任务图片)

测试数据：
✓ 创建学生：张三（三年级）
✓ 创建学生：李四（四年级）
✓ 创建示例任务...
```

---

## ✅ 第八步：验证部署

### 8.1 健康检查

访问健康检查接口：

```
https://your-project-name.zeabur.app/health
```

**预期返回：**

```json
{
    "status": "ok",
    "timestamp": "2026-01-13T12:00:00Z",
    "checks": {
        "database": "ok",
        "llm_api": "configured"
    }
}
```

### 8.2 测试核心功能

#### 功能 1：访问主页

打开：`https://your-project-name.zeabur.app/`

**检查项：**
- [ ] 页面正常加载
- [ ] 显示"AI 智能解析任务"界面
- [ ] 学生下拉列表显示测试学生

#### 功能 2：创建任务

1. 在主页面选择学生
2. 粘贴测试消息：
   ```
   语文作业：背诵课文第三段，明天交
   数学作业：练习册第10页，后天交
   ```
3. 点击 **"AI 智能解析并创建任务"**

**检查项：**
- [ ] 显示"AI 正在解析..."
- [ ] 显示任务已创建成功
- [ ] 显示任务数量

#### 功能 3：查看任务中心

打开：`https://your-project-name.zeabur.app/my-tasks`

**检查项：**
- [ ] 显示所有任务列表
- [ ] 可以筛选（全部/待完成/已完成）
- [ ] 可以标记任务完成

#### 功能 4：学生管理

打开：`https://your-project-name.zeabur.app/students`

**检查项：**
- [ ] 显示学生列表
- [ ] 可以添加新学生
- [ ] 可以编辑学生信息

---

## 📊 第九步：监控和日志

### 9.1 查看实时日志

1. 在 Zeabur 控制台
2. 选择 `jiaxiao` 服务
3. 点击 **"Logs"** / **"日志"**
4. 可以看到：
   - HTTP 请求日志
   - AI 解析日志
   - 错误日志

### 9.2 监控资源使用

在服务概览页面可以看到：

| 指标 | 免费额度 | 正常范围 |
|------|----------|----------|
| CPU | 750小时/月 | < 10% |
| 内存 | 512MB | < 400MB |
| 数据库 | 256MB | < 200MB |
| 流量 | 100GB/月 | < 1GB/天 |

---

## 🔄 第十步：更新应用（未来）

### 方式一：自动部署（推荐）

每次推送到 GitHub 的 `main` 分支：

```bash
git add .
git commit -m "feat: 新功能描述"
git push origin main
```

Zeabur 会自动：
1. 检测到代码更新
2. 重新构建应用
3. 零停机部署

### 方式二：手动部署

1. 在 Zeabur 控制台
2. 点击 `jiaxiao` 服务
3. 点击 **"Redeploy"** / **"重新部署"**

---

## 🆘 常见问题排查

### 问题 1：部署失败

**症状：** 部署状态显示 ❌ Failed

**排查步骤：**

1. **查看日志**
   - 点击 "Logs" 标签
   - 查找错误信息

2. **常见错误：依赖安装失败**
   ```
   ERROR: Could not find a version that satisfies the requirement...
   ```
   **解决：** 检查 [requirements.txt](requirements.txt) 中的版本号

3. **常见错误：端口绑定失败**
   ```
   Error: Address already in use
   ```
   **解决：** 确保使用 `$PORT` 环境变量

### 问题 2：访问 404 或 500 错误

**症状：** 访问域名返回 404 或 500

**排查步骤：**

1. **检查服务状态**
   - 服务状态应为 🟢 Running
   - 如果是 🔴 Stopped，点击 "Start"

2. **检查环境变量**
   - 确认 `LLM_API_KEY` 已配置
   - 重新部署使环境变量生效

3. **查看日志**
   - 查看是否有 Python 错误堆栈

### 问题 3：AI 解析不工作

**症状：** 创建任务时提示 "AI 解析失败"

**排查步骤：**

1. **检查 API Key**
   ```
   curl https://your-project.zeabur.app/health
   ```
   确认返回 `"llm_api": "configured"`

2. **验证 API Key 有效性**
   - 登录 DeepSeek 平台
   - 检查 API Key 是否有效
   - 检查余额是否充足

3. **查看详细日志**
   - 在 Zeabur 日志中查找 API 请求详情

### 问题 4：数据库连接失败

**症状：** 页面提示 "数据库连接失败"

**排查步骤：**

1. **检查 PostgreSQL 服务**
   - 确认 `Postgres-JIAXIAO` 服务状态为 🟢 Running
   - 如果停止，重新启动

2. **检查依赖关系**
   - `jiaxiao` 服务应该依赖于 `Postgres-JIAXIAO`
   - 如果没有，重新添加依赖

3. **重新初始化数据库**
   ```
   访问：https://your-project.zeabur.app/init?option=2
   ```

---

## 💰 费用说明

### 免费额度（当前套餐）

| 资源 | 额度 | 本项目使用 |
|------|------|-----------|
| CPU | 750小时/月 | ~50小时/月 ✅ |
| 内存 | 512MB | ~200MB ✅ |
| PostgreSQL | 256MB | ~50MB ✅ |
| 流量 | 100GB/月 | ~1GB/月 ✅ |
| 存储 | 10GB | ~100MB ✅ |

**结论：完全在免费额度内**

### 何时会产生费用？

- ⚠️ 流量超过 100GB/月
- ⚠️ 需要更大内存或 CPU
- ⚠️ 需要更多数据库存储

**建议：**
- 定期查看账单页面
- 设置消费限制
- 监控资源使用情况

---

## 🎯 部署完成检查清单

完成所有步骤后，确认：

- [ ] ✅ Zeabur 项目已创建
- [ ] ✅ GitHub 仓库已导入
- [ ] ✅ 环境变量已配置（LLM_API_KEY）
- [ ] ✅ 服务状态为 🟢 Running
- [ ] ✅ 可以访问主域名
- [ ] ✅ 数据库已初始化（包含测试数据）
- [ ] ✅ 健康检查接口返回正常
- [ ] ✅ 可以创建任务（AI 解析正常）
- [ ] ✅ 可以查看任务中心
- [ ] ✅ 可以管理学生

---

## 📱 下一步：接入微信（可选）

如果想通过微信公众号使用：

### 1. 配置环境变量

在 Zeabur 中添加：
```
WECHAT_TOKEN=your-secret-token
WECHAT_APPID=wxXXXXXXXX
WECHAT_SECRET=XXXXXXXX
```

### 2. 配置微信公众号

登录微信公众平台：
- 服务器地址：`https://your-project.zeabur.app/wechat`
- 令牌：与 `WECHAT_TOKEN` 一致
- 加密方式：明文模式

### 3. 验证

点击"提交"按钮，微信会向你的服务器发送验证请求。

---

## 🎉 恭喜！

你的家校任务助手已成功部署到 Zeabur！

**访问地址：** `https://your-project-name.zeabur.app`

**主要功能：**
- ✅ 外网可访问（任何地方）
- ✅ 微信中可直接打开
- ✅ 数据安全持久化（PostgreSQL）
- ✅ 自动 HTTPS 加密
- ✅ 自动部署更新（Git push）

**分享链接：**
- 将域名发送给其他家长
- 在微信中直接打开使用
- 无需安装任何应用

---

## 📞 需要帮助？

如果遇到问题：

1. **查看文档**：[DEPLOY_ZEABUR.md](DEPLOY_ZEABUR.md)
2. **查看日志**：Zeabur 控制台 → Logs
3. **健康检查**：`/health` 接口
4. **重新部署**：Zeabur 控制台 → Redeploy

---

祝你使用愉快！🎊
