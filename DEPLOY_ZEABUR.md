# Zeabur 部署指南

## 📋 前置准备

1. **GitHub 仓库**
   - 将项目推送到 GitHub
   - 确保仓库是公开的或 Zeabur 有访问权限

2. **Zeabur 账号**
   - 注册 Zeabur 账号：https://zeabur.com/
   - 完成邮箱验证

3. **必要的信息**
   - DeepSeek API Key
   - （可选）微信公众号配置信息

---

## 🚀 部署步骤

### 第一步：创建项目

1. 登录 Zeabur 控制台
2. 点击"创建新项目"
3. 选择"导入 Git 仓库"
4. 授权并选择你的 GitHub 仓库
5. 选择区域（推荐：香港 / 新加坡 - 国内访问快）

### 第二步：配置服务

Zeabur 会自动检测 `.zeabur.yaml` 配置文件，包含：

- **主应用服务**（Flask + Gunicorn）
- **PostgreSQL 数据库**

### 第三步：配置环境变量

在 Zeabur 控制台中配置以下环境变量：

**必须配置：**
```
LLM_API_KEY=sk-your-deepseek-api-key
```

**可选配置：**
```
WECHAT_TOKEN=your-wechat-token
WECHAT_APPID=your-appid
WECHAT_SECRET=your-secret
```

### 第四步：部署

1. 点击"部署"按钮
2. 等待构建完成（约 2-3 分钟）
3. 获取部署后的域名（如：`https://xxx.zeabur.app`）

### 第五步：初始化数据库

部署成功后，访问初始化接口：

```bash
curl https://xxx.zeabur.app/init
```

或直接在浏览器打开：
```
https://xxx.zeabur.app/init
```

选择选项 4：创建表 + 测试数据

---

## 🔧 配置说明

### 数据库配置

**开发环境（本地）：**
- 使用 SQLite
- 数据库文件：`jiaxiao.db`

**生产环境（Zeabur）：**
- 自动使用 PostgreSQL
- Zeabur 提供的环境变量：`DATABASE_URL`
- 数据持久化存储

### 环境变量优先级

1. Zeabur 控制台配置的环境变量（最高优先级）
2. `.env` 文件（不要提交到 Git）
3. 代码中的默认值（最低优先级）

### 健康检查

部署后访问健康检查接口：
```
https://xxx.zeabur.app/health
```

正常返回：
```json
{
    "status": "ok",
    "timestamp": "2025-01-13T...",
    "checks": {
        "database": "ok",
        "llm_api": "configured"
    }
}
```

---

## 🌐 访问应用

### 主页面
```
https://xxx.zeabur.app/
```

### 各功能页面
- 任务录入：`https://xxx.zeabur.app/`
- 任务中心：`https://xxx.zeabur.app/my-tasks`
- 任务确认：`https://xxx.zeabur.app/tasks`
- 学生管理：`https://xxx.zeabur.app/students`

---

## 🔒 安全说明

### 敏感信息保护

**✅ 安全的做法：**
- 所有敏感信息存储在 Zeabur 环境变量中
- 代码中不包含 API Key
- `.env` 文件不提交到 Git（已在 `.gitignore` 中）
- 使用 Zeabur 提供的 PostgreSQL（自动备份）

**❌ 避免的做法：**
- 不要在代码中硬编码 API Key
- 不要提交 `.env` 文件到 Git
- 不要在日志中打印敏感信息

### 数据持久化

**Zeabur 提供：**
- ✅ PostgreSQL 自动备份
- ✅ 数据持久化存储
- ✅ 容器重启后数据不丢失
- ✅ 免费版有足够的使用额度

**注意事项：**
- 免费版有一定资源限制
- 建议定期备份数据库
- 可以使用 Zeabur 的数据库备份功能

---

## 📱 微信公众号接入（可选）

如果你想接入微信公众号：

### 1. 配置环境变量

在 Zeabur 控制台添加：
```
WECHAT_TOKEN=your-secret-token-12345
WECHAT_APPID=your-appid
WECHAT_SECRET=your-secret
```

### 2. 配置公众号服务器

登录微信公众平台：
- 开发 → 基本配置
- 服务器地址：`https://xxx.zeabur.app/wechat`
- 令牌：与 `WECHAT_TOKEN` 一致
- 消息加解密方式：明文模式

### 3. 提交验证

点击"提交"按钮，微信会向你的服务器发送验证请求。

---

## 🔄 更新部署

### 自动部署

每次推送到 GitHub 主分支，Zeabur 会自动：
1. 检测到代码更新
2. 重新构建应用
3. 零停机部署

### 手动部署

在 Zeabur 控制台点击"重新部署"按钮。

---

## 📊 监控和日志

### 查看日志

在 Zeabur 控制台：
1. 选择你的服务
2. 点击"日志"标签
3. 查看实时日志

### 监控指标

应用会自动暴露健康检查接口：
- `/health` - 健康检查
- `/metrics` - 性能指标

---

## 🆘 常见问题

### Q1: 部署后无法访问？

**检查清单：**
1. ✅ 部署状态显示"运行中"
2. ✅ 健康检查接口正常
3. ✅ 环境变量已正确配置
4. ✅ 数据库已初始化

### Q2: 环境变量配置后还是报错？

**排查步骤：**
1. 在 Zeabur 控制台确认环境变量已添加
2. 点击"重新部署"使环境变量生效
3. 查看日志确认环境变量已加载

### Q3: 数据库连接失败？

**检查：**
1. PostgreSQL 服务状态
2. `DATABASE_URL` 环境变量是否正确
3. 依赖关系是否正确配置

### Q4: 如何升级服务？

**方式一：自动部署**
```bash
git add .
git commit -m "update: xxx"
git push
```

**方式二：手动部署**
在 Zeabur 控制台点击"重新部署"

---

## 💰 费用说明

### Zeabur 免费额度

- **CPU**: 750 小时/月（约 1 个核心全天运行）
- **内存**: 512MB
- **数据库**: PostgreSQL 256MB
- **流量**: 100GB/月
- **存储**: 10GB

### 使用建议

当前应用完全可以运行在免费额度内：
- Flask 应用：512MB 内存足够
- PostgreSQL：256MB 足够（数千条记录）
- 流量：个人使用完全够用

### 超出免费额度

如果超出免费额度：
- 按量计费
- 价格相对便宜
- 可以设置消费限制

---

## 📚 下一步

部署完成后：

1. **测试基本功能**
   - 访问主页面
   - 创建测试任务
   - 验证 AI 解析功能

2. **配置自定义域名**（可选）
   - 在 Zeabur 控制台添加域名
   - 配置 DNS 解析
   - 等待 SSL 证书自动生成

3. **接入微信公众号**（可选）
   - 配置公众号服务器
   - 测试消息接收和解析
   - 验证任务确认流程

4. **邀请使用**
   - 分享访问链接给其他家长
   - 收集使用反馈
   - 持续优化产品

---

## 🎉 完成

你的家校任务助手已成功部署到 Zeabur！

**访问地址：** `https://xxx.zeabur.app`

**特点：**
- ✅ 外网可访问
- ✅ 可在微信中打开
- ✅ 数据安全持久化
- ✅ 自动 HTTPS 加密
- ✅ 自动部署更新

祝你使用愉快！
