# 快速开始指南

## 📋 前置要求

- Python 3.10 或更高版本
- pip 包管理器
- DeepSeek API Key（获取地址：https://platform.deepseek.com/）

## 🚀 5 分钟快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，最少需要配置这两项：
# LLM_API_KEY=sk-your-deepseek-api-key
# WECHAT_TOKEN=your-random-token
```

### 3. 初始化数据库

```bash
# 运行初始化脚本，选择选项 4（创建表 + 测试数据）
python init_db.py
```

### 4. 测试 LLM 解析

```bash
# 测试 AI 解析功能
python test_llm.py
```

### 5. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 6. 验证服务

```bash
# 检查服务健康状态
curl http://localhost:5000/health

# 查看系统指标
curl http://localhost:5000/metrics
```

## 📱 接入微信

### 方案 1：本地开发 + 内网穿透（测试用）

1. 安装 ngrok：`brew install ngrok` (macOS) 或访问 https://ngrok.com/

2. 启动 ngrok：
```bash
ngrok http 5000
```

3. 复制 ngrok 提供的公网 URL（如：`https://abc123.ngrok.io`）

4. 访问 [微信公众平台测试号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)

5. 配置服务器信息：
   - URL: `https://abc123.ngrok.io/wechat`
   - Token: 与 `.env` 中的 `WECHAT_TOKEN` 一致

6. 点击"提交"，验证通过后即可测试

### 方案 2：云函数部署（推荐）

详细步骤参考 [README.md](./README.md) 的部署指南。

## 🧪 测试消息发送

使用微信扫描测试号二维码，关注后发送测试消息：

```
明天请背诵《山行》古诗
```

系统会返回解析结果。

## 📊 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误
grep ERROR logs/app.log
```

## 🔧 常见问题

### Q: 提示 "LLM_API_KEY 未设置"？

A: 检查 `.env` 文件是否存在，且 `LLM_API_KEY` 已正确配置。

### Q: ngrok 每次重启域名都变？

A: ngrok 免费版确实如此，建议升级付费版或使用云函数部署。

### Q: 微信验证失败？

A: 确认三点：
1. URL 是否正确（包括 `/wechat` 后缀）
2. Token 是否与 `.env` 中一致
3. 服务器是否正常运行（访问 `/health` 检查）

### Q: LLM 解析失败？

A: 系统会自动降级到关键词匹配，查看日志了解详情：
```bash
grep "llm" logs/app.log
```

## 📚 下一步

- 阅读完整文档：[README.md](./README.md)
- 查看产品设计：[Product.md](./Product.md)
- 开发新功能：参考代码注释

## 🆘 需要帮助？

- 查看日志：`logs/app.log`
- 运行健康检查：访问 `http://localhost:5000/health`
- 查看系统指标：访问 `http://localhost:5000/metrics`
