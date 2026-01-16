# 🧪 测试文档目录

**家校任务管理助手 - End-to-End 测试套件**

---

## 📚 文档索引

### 1. [TEST_CHECKLIST.md](TEST_CHECKLIST.md) - 测试准备清单 ⭐ 从这里开始
**10 分钟后测试步骤指南**
- ✅ 代码修复完成清单
- 📋 分步测试流程
- 🧪 详细测试场景
- 🔧 问题处理流程

### 2. [TEST_SCENARIOS.md](TEST_SCENARIOS.md) - 用户操作测试场景
**完整的用户操作手册**
- 9 个核心测试场景
- 详细的操作步骤
- 预期结果验证
- 异常场景测试

### 3. [TEST_GUIDE.md](TEST_GUIDE.md) - Playwright 测试指南
**自动化测试技术文档**
- 环境安装步骤
- 测试运行方法
- 自定义测试
- 故障排查指南

### 4. [tests_e2e.py](tests_e2e.py) - 自动化测试脚本
**Playwright E2E 测试代码**
- 7 个测试场景
- 自动截图
- 详细日志输出
- 完整错误处理

### 5. [run_tests.sh](run_tests.sh) - 测试启动脚本
**一键运行测试**
- 自动检查依赖
- 交互式确认
- 彩色输出
- 结果统计

---

## 🚀 快速开始

### 10 分钟后执行以下命令：

```bash
# 1. 确认 Zeabur 部署完成
# 访问 https://edu-track.zeabur.app/login 确认可以访问

# 2. 安装测试依赖
pip install -r requirements-test.txt
playwright install chromium

# 3. 运行测试
./run_tests.sh
```

---

## 📋 测试覆盖范围

### ✅ 核心功能测试

- [ ] 用户注册和登录
- [ ] 添加学生信息
- [ ] AI 解析作业消息（单任务）
- [ ] AI 解析作业消息（多任务）
- [ ] 任务管理（查看、完成、编辑）
- [ ] 学生管理（添加、编辑、删除）
- [ ] 用户会话管理

### ✅ UI/UX 测试

- [ ] 日式极简设计风格
- [ ] 响应式布局
- [ ] 无 Emoji 元素
- [ ] 加载状态反馈
- [ ] 成功/错误提示

### ✅ 性能测试

- [ ] 页面加载时间 < 2秒
- [ ] API 响应时间 < 1秒
- [ ] AI 解析时间 5-15秒

---

## 📊 测试数据

### 测试账号
```
邮箱: test_<timestamp>@example.com
密码: test123456
姓名: 测试家长
```

### 测试学生
```
张三 - 三年级2班
```

### 测试任务
```
单任务:
英语：1-4单元粗体字单词一英一汉

多任务:
1.英语：1-4单元粗体字单词一英一汉
2.政治：卷子，3题不写
3.地理：第一单元卷子写完
4.历史：卷子
5.语文：文言文卷子四题写完
6.语文：卷子写完
7.数学：卷子写完
8.数学：上课写的4题研究一下
（共 10 条任务）
```

---

## 📸 测试输出

### 控制台日志
```
==============================================================
🚀 启动测试环境
==============================================================
✅ 浏览器已启动
🌐 测试环境: https://edu-track.zeabur.app

==============================================================
📝 场景 1: 新用户注册和首次使用
==============================================================

1️⃣ 访问登录页面
   ✅ 页面标题正确

2️⃣ 填写注册信息
   ✅ 表单填写成功

...
```

### 截图文件
- `test_screenshot_after_register_*.png`
- `test_screenshot_after_add_student_*.png`
- `test_screenshot_after_parse_*.png`
- `test_screenshot_task_center_*.png`
- `test_screenshot_after_complete_*.png`
- `test_screenshot_after_multi_parse_*.png`
- `test_screenshot_after_logout_*.png`

---

## 🔧 常见问题

### Q: Playwright 未安装？
```bash
pip install playwright
playwright install chromium
```

### Q: 浏览器未找到？
```bash
playwright install --with-deps chromium
```

### Q: 页面元素找不到？
- 检查 Zeabur 部署状态
- 查看浏览器截图
- 确认页面加载完成

### Q: AI 解析超时？
- 正常等待时间: 10-15秒
- 如超时 30秒，检查 LLM API 配置

### Q: 网络连接失败？
- 检查 internet 连接
- 确认 Zeabur URL 正确
- 查看 Zeabur 服务状态

---

## 📞 获取帮助

### 查看详细文档
```bash
# 测试准备清单
cat TEST_CHECKLIST.md

# 用户操作场景
cat TEST_SCENARIOS.md

# 技术指南
cat TEST_GUIDE.md
```

### 查看测试代码
```bash
# 查看测试脚本
cat tests_e2e.py

# 查看启动脚本
cat run_tests.sh
```

### 查看修复记录
```bash
# 数据库初始化修复
cat DATABASE_INIT_FIX.md

# PostgreSQL 驱动修复
cat PSYCOP_FIX.md
```

---

## ✅ 准备清单

### 已完成
- [x] 修复数据库初始化问题
- [x] 修复 PostgreSQL 驱动兼容性
- [x] 编写测试场景文档
- [x] 编写自动化测试脚本
- [x] 创建测试启动脚本
- [x] 推送代码到 GitHub

### 待执行（10 分钟后）
- [ ] 确认 Zeabur 部署完成
- [ ] 手动快速验证基本功能
- [ ] 安装测试依赖
- [ ] 运行自动化测试
- [ ] 分析测试结果
- [ ] 修复发现的问题（如有）

---

## 🎯 预期测试结果

### 成功标准
- ✅ 所有 7 个场景通过
- ✅ 无 API 错误
- ✅ 所有功能正常
- ✅ UI/UX 符合要求

### 预计耗时
- 环境准备: 3 分钟
- 测试执行: 1 分钟
- 结果分析: 1 分钟
- **总计**: 5 分钟

---

**准备完成**: ✅
**等待时间**: 10 分钟（让 Zeabur 完成部署）
**开始测试**: 运行 `./run_tests.sh`

---

**文档版本**: 1.0
**最后更新**: 2026-01-16
