# 🚀 10分钟快速测试指南

## 📋 前置检查

在开始之前，确保：

- [x] 已安装 Python 3.10+
- [x] 已配置 DeepSeek API Key
- [x] 已初始化数据库
- [x] 本地服务可以正常启动（http://localhost:5001）
- [ ] 已有微信公众号（订阅号/服务号/测试号均可）

---

## 🎯 快速测试步骤

### 第一步：启动本地服务（2分钟）

```bash
# 在项目目录下
cd /Volumes/data/vibe-coding-projects/jiaxiao

# 启动服务
python app.py
```

**看到这个提示表示成功**：
```
🚀 启动家校任务管理助手
📊 数据库: sqlite:///jiaxiao.db
🤖 LLM 模型: deepseek-chat
 * Running on http://0.0.0.0:5001
```

**保持这个终端窗口运行**，不要关闭！

---

### 第二步：安装内网穿透工具（3分钟）

#### 方法 1：使用 cpolar（推荐，国内访问快）

** macOS 安装**：
```bash
# 安装
brew tap cpolar/homebrew-tap
brew install cpolar

# 或使用下载安装
# 访问 https://www.cpolar.com/download
# 下载 macOS 版本并安装
```

**启动 cpolar**：
```bash
# 在新的终端窗口中运行
cpolar http 5001
```

**你会看到类似输出**：
```
cpolar by @bestexpresser - version 3.3.18

Tunnel Status       online
Account             xxxx@xxxx.com (Plan: Free)
Version             3.3.18
Web Interface       http://127.0.0.1:4040
Forwarding          https://abc123.cpolar.cn -> http://localhost:5001
                     https://abc123.cpolar.io -> http://localhost:5001
Forwarding          http://abc123.cpolar.cn -> http://localhost:5001
                     http://abc123.cpolar.io -> http://localhost:5001
```

**⚠️ 重要**：复制其中一个 HTTPS 地址，例如：
- `https://abc123.cpolar.cn`

这就是你的公网地址！

#### 方法 2：使用 ngrok（国外访问快）

**安装**：
```bash
# macOS
brew install ngrok

# 或下载
# 访问 https://ngrok.com/download
```

**启动 ngrok**：
```bash
ngrok http 5001
```

**复制 HTTPS 地址**（如：`https://xyz.ngrok.io`）

---

### 第三步：验证内网穿透（1分钟）

在浏览器中访问你复制的地址：

```
https://abc123.cpolar.cn
```

**应该看到**：系统监控页面

**测试健康检查**：
```
https://abc123.cpolar.cn/health
```

**应该返回**：
```json
{"status":"ok","timestamp":"2025-01-10T...","checks":{"database":"ok","llm_api":"configured"}}
```

✅ 如果能看到这个页面，说明内网穿透成功！

---

### 第四步：配置微信公众号（3分钟）

#### 1. 登录公众号后台

访问：https://mp.weixin.qq.com/

使用你的公众号账号登录

#### 2. 进入基本配置

左侧菜单：**开发** → **基本配置**

#### 3. 配置服务器地址

点击"修改配置"按钮：

| 配置项 | 填写内容 |
|--------|---------|
| **URL** | `https://abc123.cpolar.cn/wechat`<br>⚠️ 注意：使用你复制的地址 + `/wechat` |
| **Token** | 与 `.env` 文件中的 `WECHAT_TOKEN` 一致<br>（如果没有配置，先去配置） |
| **EncodingAESKey** | 随机生成（点击按钮） |
| **消息加解密方式** | 选择 **明文模式** |

#### 4. 提交配置

点击"提交"按钮

**如果配置正确**，会提示"提交成功"

**如果配置失败**，检查：
- ✅ URL 是否正确（包含 `/wechat` 后缀）
- ✅ Token 是否与 `.env` 中一致
- ✅ 本地服务是否正在运行
- ✅ cpolar 是否正在运行

#### 5. 启用服务器配置

点击"启用"按钮，使配置生效

---

### 第五步：测试功能（2分钟）

#### 方法 1：使用公众号（推荐）

1. **关注你的公众号**
   - 使用微信扫描公众号二维码
   - 或搜索公众号名称关注

2. **发送测试消息**

   发送以下内容：
   ```
   语文任务：
   1. 背诵《山行》古诗
   2. 朗读课文第三遍
   3. 完成练习册第5页
   ```

3. **查看回复**

   应该收到类似回复：
   ```
   ✅ 已识别任务

   📊 共 3 条任务
   1. 背诵《山行》古诗
   2. 朗读课文第三遍
   3. 完成练习册第5页

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   👉 点此确认任务

   在微信中打开，可直接分配给学生
   ```

4. **点击链接**

   - 长按链接，选择"在浏览器中打开"
   - 或直接点击（如果链接可点击）

5. **查看确认页面**

   - 在微信内置浏览器中打开
   - 查看所有任务详情
   - 选择学生（小明/小红）
   - 点击"确认并创建任务"

6. **验证成功**

   - 看到"✓ 任务已成功创建！"
   - 3秒后自动跳转到任务列表
   - 查看新创建的任务

#### 方法 2：使用模拟测试页面（备选）

如果公众号配置有问题，可以先使用模拟页面测试：

1. 访问：`https://abc123.cpolar.cn/simulate`

2. 点击"使用此示例"

3. 点击"模拟转发"

4. 点击"点此确认任务"

5. 选择学生并确认

---

## ✅ 验证成功的标志

### 1. 服务运行正常

```bash
# 终端1（app.py）
* Running on http://0.0.0.0:5001

# 终端2（cpolar）
Tunnel Status       online
```

### 2. 公众号配置成功

- 公众号后台显示"服务器配置已启用"
- 消息发送后能收到自动回复

### 3. 功能完整测试

- [ ] 发送消息有回复
- [ ] 回复中包含确认链接
- [ ] 点击链接能打开确认页面
- [ ] 确认页面显示任务列表
- [ ] 选择学生并确认成功
- [ ] 任务列表页面显示新任务

---

## 🔧 常见问题快速解决

### Q1: cpolar 启动失败？

**解决方法**：

```bash
# 检查是否安装成功
cpolar version

# 如果提示命令不存在，重新安装
brew reinstall cpolar
```

### Q2: 微信配置验证失败？

**检查清单**：

1. ✅ 本地服务是否运行？
   ```bash
   curl http://localhost:5001/health
   ```

2. ✅ cpolar 是否运行？
   - 查看 cpolar 窗口是否显示 "online"

3. ✅ URL 是否正确？
   - 必须是 `https://abc123.cpolar.cn/wechat`
   - 不能缺少 `/wechat` 后缀

4. ✅ Token 是否一致？
   ```bash
   # 查看 .env 中的配置
   cat .env | grep WECHAT_TOKEN
   ```

5. ✅ 消息加解密方式是否选择"明文模式"？

### Q3: 发送消息后没有回复？

**排查步骤**：

1. 查看本地服务日志
   - 在运行 `python app.py` 的终端窗口查看输出
   - 看是否有错误信息

2. 测试健康检查
   ```bash
   curl https://abc123.cpolar.cn/health
   ```

3. 检查 LLM API Key
   ```bash
   cat .env | grep LLM_API_KEY
   ```

4. 查看详细日志
   ```bash
   tail -f logs/app.log
   ```

### Q4: 点击链接打不开页面？

**可能原因**：

1. **链接已过期**
   - 待确认任务 5 分钟后过期
   - 重新发送消息获取新链接

2. **微信拦截**
   - 尝试长按链接，选择"在浏览器中打开"
   - 或复制链接到浏览器

3. **网络问题**
   - 检查 cpolar 是否还在运行
   - 重新启动 cpolar

### Q5: 如何停止测试？

```bash
# 停止 cpolar：在 cpolar 终端窗口按 Ctrl+C

# 停止 app.py：在 app.py 终端窗口按 Ctrl+C

# 或者关闭终端窗口
```

---

## 📱 测试消息示例

### 简单任务
```
明天背诵《山行》古诗
```

### 复杂任务
```
语文任务：
1.阅读打卡：
朗读《语文园地八》这课，会认字和会写字口头拼读并组词。
朗读课外读物，写阅读笔记。

2.背诵课本1--8单元要求背诵的所有内容。
背诵课本105页的成语和日积月累，录音上传小管家。

3.认真修改作业本里面的错误。
```

### 数学任务
```
数学作业：
1. 完成练习册第10-12页
2. 预习下一课内容
3. 复习乘法口诀表
```

---

## 🎉 测试成功后

### 体验完整流程

```
1. 尝试发送不同类型的老师消息
   → 查看 AI 解析效果

2. 测试任务确认流程
   → 选择不同学生

3. 查看任务管理页面
   → 访问 https://abc123.cpolar.cn/tasks

4. 标记任务完成
   → 测试任务状态更新
```

### 下一步选择

**选项 1：继续优化体验**
- 调整 AI Prompt 提高准确率
- 优化确认页面 UI
- 添加更多功能

**选项 2：部署到云服务器**
- 购买云服务器（¥50-100/月）
- 参考 [WECHAT_SETUP.md](WECHAT_SETUP.md) 的"方案A"
- 24小时稳定运行

**选项 3：分享给其他人测试**
- 邀请朋友/家人关注公众号
- 收集使用反馈
- 优化产品功能

---

## 📝 配置总结

### 你需要记录的信息

```bash
# 公网地址
外网地址: https://abc123.cpolar.cn

# 公众号配置
URL: https://abc123.cpolar.cn/wechat
Token: your-token-from-env

# 本地服务
端口: 5001
健康检查: http://localhost:5001/health
```

### 下次测试如何启动

```bash
# 终端1：启动服务
cd /Volumes/data/vibe-coding-projects/jiaxiao
python app.py

# 终端2：启动内网穿透
cpolar http 5001

# 注意：每次重启 cpolar，域名会变化
# 需要重新配置公众号服务器地址
```

---

## 🆘 需要帮助？

1. 查看日志：`tail -f logs/app.log`
2. 健康检查：访问 `/health`
3. 系统指标：访问 `/metrics`
4. 参考文档：
   - [USER_GUIDE.md](USER_GUIDE.md) - 完整使用指南
   - [WECHAT_SETUP.md](WECHAT_SETUP.md) - 详细配置指南

---

## ✨ 准备好了吗？

让我们开始配置吧！按照上面的步骤，10分钟内你就能在真实的微信公众号中体验 AI 任务管理功能。

准备好了就开始第一步吧！🚀
