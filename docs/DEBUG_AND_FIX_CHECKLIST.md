# 问题诊断与修复清单

**日期**: 2026-01-15
**状态**: 进行中
**优先级**: 🔥 高

---

## 📋 用户反馈的问题

1. **页面风格不统一** - my-tasks 页面显示旧的蓝橙配色，而不是日式极简风格
2. **确认流程复杂** - 确认任务时还需要选择学生
3. **任务不显示** - 创建任务后在任务中心看不到

---

## 🔍 问题诊断

### 问题 1: 页面显示旧设计风格

**原因**: 浏览器缓存了旧版本的 CSS 和 HTML

**证据**:
- my-tasks.html 已经更新为日式极简设计（23K，597行）
- 浏览器可能缓存了旧版本

**解决方案**:
- 在所有页面的 `<head>` 中添加缓存控制
- 在 HTML 中添加版本号参数
- 建议用户强制刷新（Ctrl+Shift+R / Cmd+Shift+R）

### 问题 2: 确认任务需要选择学生

**原因**: confirm.html 的逻辑允许在URL中没有student_id时显示学生选择列表

**旧代码逻辑** (825行):
```javascript
if (preselectedStudentId) {
    // 自动选中
    selectedStudent = preselectedStudent.student_id;
} else {
    // 显示学生选择列表（这是问题）
    document.getElementById('studentSelectCard').style.display = 'block';
}
```

**解决方案**:
- ✅ 已修复：重写 confirm.html（352行）
- 去掉学生选择逻辑，强制要求 URL 中有 student_id
- 如果没有 student_id，显示错误提示

### 问题 3: 创建任务后在任务中心不显示

**原因分析**:

1. **数据库正常** ✅
   - 最新任务已创建：Task ID `4fd946da...`
   - 所属家庭：`704bb093...` (易先生)
   - 该家庭有 11 个任务

2. **可能的原因**:
   - 当前登录的用户不是"易先生"（alves820@live.cn）
   - Session 过期或混乱
   - API 返回数据过滤有问题

**验证步骤**:
```bash
# 检查当前登录用户
curl -c /tmp/cookies.txt http://localhost:5001/login
# 登录
curl -b /tmp/cookies.txt -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alves820@live.cn","password":"YOUR_PASSWORD"}'
# 查看任务
curl -b /tmp/cookies.txt http://localhost:5001/api/tasks
```

---

## ✅ 已完成的修复

### 1. confirm.html 全面重写 ✅

**修改**: 825行 → 352行（减少57%）

**改进**:
- ✅ 日式极简设计（黑白灰配色）
- ✅ 去掉学生选择逻辑
- ✅ 简化代码结构
- ✅ 更好的错误处理
- ✅ 响应式设计

**新特性**:
```javascript
// 直接从 URL 获取参数，无需选择
const studentId = urlParams.get('student_id');

// 如果没有 student_id，显示错误
if (!studentId) {
    showError('缺少学生信息');
    return;
}
```

### 2. 数据库统一 ✅

**修改文件**:
- [config.py](config.py:19-20) - DATABASE_URL 统一为 `jiaxiao.db`
- [models.py](models.py:239) - default_db 统一为 `jiaxiao.db`

**数据迁移**:
- 用户: 7
- 学生: 23
- 任务: 21

---

## 🔄 待完成的修复

### 高优先级

#### 1. 清除浏览器缓存

**方案 A**: HTML Meta 标签
```html
<head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
</head>
```

**方案 B**: CSS/JS 版本号
```html
<link href="/styles.css?v=2.0" rel="stylesheet">
<script src="/app.js?v=2.0"></script>
```

**方案 C**: 用户操作
- Chrome/Firefox: `Ctrl+Shift+R` (Windows) / `Cmd+Shift+R` (Mac)
- Safari: `Cmd+Option+E` 清除缓存，然后刷新

#### 2. 更新其他页面为日式极简设计

需要更新的页面：
- [ ] simulate.html - AI 智能解析页面（30K）
- [ ] auth.html - 登录/注册页面（9.9K）
- [ ] students.html - 学生管理页面（18K）
- [ ] index.html - 首页（13K）

**统一设计系统**:
```css
/* 配色 */
--zen-bg: #ffffff;
--zen-text: #1a1a1a;
--zen-textLight: #999999;
--zen-border: #f0f0f0;

/* 字体 */
font-family: 'Noto Sans SC', 'Inter', sans-serif;

/* 圆角 */
border-radius: 8px (小元素)
border-radius: 12px (按钮)
border-radius: 16px (卡片)
border-radius: 24px (大卡片)
```

#### 3. 修复任务显示问题

**排查步骤**:
1. 确认当前登录用户
2. 检查 Flask session
3. 验证 API 返回数据
4. 确认前端渲染逻辑

**调试代码**:
```python
# app.py - 在 get_all_tasks 中添加日志
logger.info(f"Current family_id: {family_id}")
logger.info(f"Tasks count: {len(tasks)}")
```

```javascript
// my-tasks.html - 在 loadTasks 中添加日志
console.log('Loaded tasks:', tasks.length);
console.log('Tasks data:', tasks);
```

### 中优先级

#### 4. 简化其他复杂页面

- tasks.html (28K) - 可能可以删除或合并
- wechat-simulate.html (16K) - 测试页面，可以简化

#### 5. 添加版本号到静态资源

```python
# app.py
@app.context_processor
def inject_version():
    return {'version': '2.0'}
```

```html
<!-- templates -->
<link rel="stylesheet" href="/style.css?v={{ version }}">
```

---

## 📊 文件大小对比

| 文件 | 修改前 | 修改后 | 变化 |
|------|--------|--------|------|
| confirm.html | 30K (825行) | - | 重写为352行 |
| my-tasks.html | - | 23K (597行) | 日式极简 |
| config.py | - | - | 已修复 |
| models.py | - | - | 已修复 |

---

## 🧪 测试计划

### 测试场景 1: 完整任务创建流程

**步骤**:
1. 访问 http://localhost:5001
2. 登录账号（alves820@live.cn）
3. 选择学生（学生 a）
4. 输入任务："准备好语文试卷"
5. 上传图片（可选）
6. 点击"AI 智能解析"
7. 跳转到确认页面
8. 确认学生信息自动显示（无需选择）
9. 点击"确认创建任务"
10. 跳转到任务中心
11. **验证**: 新任务出现在列表中

**预期结果**:
- ✅ 所有页面显示日式极简设计
- ✅ 确认页面不需要选择学生
- ✅ 任务立即显示在任务中心

### 测试场景 2: 多学生家庭

**步骤**:
1. 登录有多个学生的账号
2. 为不同学生创建任务
3. **验证**: 每个任务都关联到正确的学生

### 测试场景 3: 浏览器缓存

**步骤**:
1. 正常使用
2. 修改某个页面的设计
3. 刷新页面（F5）
4. **验证**: 显示新设计

如果未显示：
- 强制刷新（Ctrl+Shift+R）
- 清除浏览器缓存
- 使用无痕模式测试

---

## 🎯 立即行动项

### 现在（高优先级）

1. **测试 confirm.html 修复**
   - [ ] 创建一个新任务
   - [ ] 确认不需要选择学生
   - [ ] 验证任务创建成功

2. **清除浏览器缓存**
   - [ ] 在 Chrome/Edge 中按 Ctrl+Shift+R
   - [ ] 在 Safari 中按 Cmd+Shift+R
   - [ ] 或使用无痕模式测试

3. **验证任务显示**
   - [ ] 登录 alves820@live.cn
   - [ ] 查看任务中心是否有 11 个任务
   - [ ] 创建新任务，立即刷新查看

### 今天内（中优先级）

4. **更新其他页面设计**
   - [ ] simulate.html
   - [ ] auth.html
   - [ ] students.html

5. **添加缓存控制**
   - [ ] 所有页面添加 Meta 标签
   - [ ] CSS/JS 添加版本号

### 本周内（低优先级）

6. **代码清理**
   - [ ] 删除未使用的页面
   - [ ] 统一设计系统文档
   - [ ] 添加单元测试

---

## 📝 备注

### 浏览器缓存问题

浏览器缓存是导致"页面显示旧设计"的最可能原因。即使我们更新了 HTML 文件，浏览器可能仍然使用缓存的版本。

**强制刷新方法**:
- Windows: `Ctrl + F5` 或 `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`
- 移动端: 清除浏览器缓存或使用无痕模式

### Session 管理

Flask session 默认存储在客户端 cookie 中，使用 SECRET_KEY 签名。

**检查 session**:
```python
from flask import session
print(session)  # 查看当前 session 内容
```

**清除 session**:
```python
session.clear()
```

### 数据库查询

所有任务查询都应该基于 `family_id`：

```python
# 正确 ✅
tasks = session.query(Task).join(Student).filter(
    Student.family_id == family_id
).all()

# 错误 ❌
tasks = session.query(Task).filter_by(
    student_id=student_id  # 只查一个学生的任务
).all()
```

---

## 📞 需要用户反馈的问题

1. **您当前登录的账号是什么？**
   - 邮箱: ___________
   - 是否是 alves820@live.cn?

2. **任务中心显示几个任务？**
   - 预期: 11个任务（易先生账号）
   - 实际: _____个

3. **是否尝试过强制刷新？**
   - [ ] 是，还是旧设计
   - [ ] 否，尝试后显示新设计

4. **创建新任务后？**
   - [ ] 立即显示在任务中心
   - [ ] 需要刷新才显示
   - [ ] 刷新后也不显示

5. **确认页面？**
   - [ ] 需要选择学生
   - [ ] 自动显示学生信息（新版本）

---

**生成时间**: 2026-01-15 08:45
**下次更新**: 完成所有修复后
