# Playwright E2E 测试指南

**日期**: 2026-01-16
**测试环境**: https://edu-track.zeabur.app

---

## 准备工作

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements-test.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 验证安装

```bash
# 验证 Playwright 安装
playwright --version

# 验证浏览器安装
playwright show-browsers
```

---

## 运行测试

### 方法 1: 直接运行（推荐）

```bash
# 运行完整测试套件
python tests_e2e.py
```

### 方法 2: 使用 pytest

```bash
# 运行测试（无头模式）
pytest tests_e2e.py -v

# 运行测试（显示浏览器）
pytest tests_e2e.py -v --headed

# 运行测试（慢速模式）
pytest tests_e2e.py -v --headed --slowmo=1000
```

---

## 测试场景说明

### 场景 1: 新用户注册和首次使用
- 访问登录页面
- 切换到注册标签
- 填写注册信息（自动生成随机邮箱）
- 提交注册
- 验证自动登录和跳转

### 场景 3: 添加学生信息
- 访问学生管理页面
- 点击添加学生
- 填写学生信息（张三，三年级，2班）
- 提交表单
- 验证学生信息显示

### 场景 4: 快速添加任务（AI 解析）
- 访问快速添加页面
- 输入单科作业消息
- 点击 AI 解析
- 等待解析完成（10-15秒）
- 选择学生
- 确认创建
- 验证跳转到任务中心

### 场景 5: 任务中心管理
- 访问任务中心
- 检查任务列表
- 检查筛选功能
- 截图保存

### 场景 6: 完成和编辑任务
- 访问任务中心
- 查找未完成任务
- 标记任务完成
- 验证状态更新

### 场景 7: 多任务批量确认
- 访问快速添加页面
- 输入多科目作业消息（10条任务）
- 点击 AI 解析
- 等待解析完成（10-15秒）
- 确认创建所有任务
- 验证任务创建

### 场景 9: 退出登录
- 访问退出页面
- 验证跳转到登录页
- 尝试访问受保护页面（验证重定向）

---

## 测试数据

### 自动生成的测试账号

```python
# 每次运行自动生成
test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
test_password = "test123456"
test_parent_name = "测试家长"
```

### 测试学生

```
学生1:
  姓名: 张三
  年级: 三年级
  班级: 2班
```

### 测试任务

```
单任务:
  英语：1-4单元粗体字单词一英一汉；4单元短语一英一汉；打卡

多任务:
  1.英语：1-4单元粗体字单词一英一汉；4单元短语一英一汉；打卡
  2.政治：卷子，3题不写；地理：第一单元卷子写完；历史：卷子；生物：无作业
  3.语文：文言文卷子四题写完；卷子写完
  4.数学：卷子写完；上课写的4题研究一下
```

---

## 输出说明

### 控制台输出

测试运行时会在控制台输出详细日志：

```
==============================================================
🚀 启动测试环境
==============================================================
✅ 浏览器已启动
🌐 测试环境: https://edu-track.zeabur.app

==============================================================
📝 场景 1: 新用户注册和首次使用
==============================================================

1️⃣ 访问登录页面: https://edu-track.zeabur.app/login
   页面标题: 登录 - 家校任务管理助手

2️⃣ 切换到注册标签

3️⃣ 填写注册信息
   邮箱: test_20260116_123456@example.com
   密码: test123456
   家长姓名: 测试家长

4️⃣ 提交注册
   响应状态码: 200
   ✅ 注册成功

5️⃣ 验证登录状态
   当前 URL: https://edu-track.zeabur.app/
   ✅ 自动跳转到首页

📸 截图已保存: test_screenshot_after_register_20260116_123456.png
```

### 截图保存

测试过程中的关键步骤会自动截图：

- `test_screenshot_after_register_*.png` - 注册后
- `test_screenshot_after_add_student_*.png` - 添加学生后
- `test_screenshot_after_parse_*.png` - AI 解析后
- `test_screenshot_task_center_*.png` - 任务中心
- `test_screenshot_after_complete_*.png` - 完成任务后
- `test_screenshot_after_multi_parse_*.png` - 多任务解析后
- `test_screenshot_after_logout_*.png` - 退出登录后

截图文件保存在项目根目录。

---

## 故障排查

### 问题 1: Playwright 未安装

```
错误: ModuleNotFoundError: No module named 'playwright'
解决: pip install -r requirements-test.txt
```

### 问题 2: 浏览器未安装

```
错误: Executable doesn't exist
解决: playwright install chromium
```

### 问题 3: 页面元素找不到

```
原因: 页面加载时间过长或元素选择器错误
解决:
  1. 增加 wait 时间
  2. 检查页面是否正确加载
  3. 使用浏览器开发者工具检查选择器
```

### 问题 4: 网络连接失败

```
错误: Failed to connect to edu-track.zeabur.app
解决:
  1. 检查网络连接
  2. 检查 Zeabur 部署状态
  3. 确认 URL 正确
```

### 问题 5: AI 解析超时

```
原因: LLM API 响应慢或网络问题
解决:
  1. 增加等待时间（修改 slow_mo 参数）
  2. 检查 LLM API 配置
  3. 查看应用日志
```

---

## 自定义测试

### 修改测试环境

```python
# 编辑 tests_e2e.py
test = EduTrackTest(base_url="http://localhost:5001")
```

### 修改测试数据

```python
# 编辑 tests_e2e.py
self.test_email = "custom@example.com"
self.test_password = "custom123"
```

### 添加新测试场景

```python
async def test_scenario_custom(self):
    """自定义测试场景"""
    print("\n" + "="*60)
    print("🎯 自定义测试场景")
    print("="*60)

    # 你的测试代码
    await self.page.goto(f"{self.base_url}/some-page")
    await self.wait(2)

    # 验证结果
    await self.take_screenshot("custom_test")
```

---

## 性能基准

### 预期执行时间

- 场景 1（注册）: ~5秒
- 场景 3（添加学生）: ~3秒
- 场景 4（单任务）: ~15秒（含 AI 解析）
- 场景 5（任务中心）: ~3秒
- 场景 6（完成任务）: ~3秒
- 场景 7（多任务）: ~20秒（含 AI 解析）
- 场景 9（退出登录）: ~3秒

**总计**: 约 55-60 秒

### 页面加载时间

- 登录页: < 1秒
- 任务中心: < 2秒
- 快速添加: < 1秒
- 学生管理: < 1秒

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # 每 6 小时运行一次

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          playwright install chromium

      - name: Run tests
        run: python tests_e2e.py
        env:
          BASE_URL: https://edu-track.zeabur.app

      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: screenshots
          path: test_screenshot_*.png
```

---

## 下一步

1. **等待 10 分钟** - 让 Zeabur 完成部署
2. **运行测试** - 执行 `python tests_e2e.py`
3. **查看结果** - 检查控制台输出和截图
4. **分析问题** - 如有失败，查看截图和日志
5. **提交修复** - 根据测试结果修复问题

---

**文档版本**: 1.0
**最后更新**: 2026-01-16
