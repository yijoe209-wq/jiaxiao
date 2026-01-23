# 多家长账号系统 - 测试指南

## ✅ 已完成的功能

### 1. 后端功能
- ✅ 创建 Parent 数据模型
- ✅ 修改注册/登录逻辑
- ✅ 实现拉人入家庭 API
- ✅ 数据库迁移脚本

### 2. 前端页面
- ✅ 创建 `/family-members` 页面
- ✅ 在任务中心添加入口
- ✅ 显示家庭成员列表
- ✅ 添加成员功能
- ✅ 移除成员功能

---

## 🧪 完整测试流程

### 测试前准备

#### 第 1 步：运行数据库迁移

```bash
cd /Volumes/data/vibe-coding-projects/jiaxiao
python migrate_to_multi_parent.py
```

**预期输出：**
```
🚀 开始数据库迁移：单一家长 → 多家长系统
============================================================

📋 步骤 1：检查迁移状态
⚠️  parents 表已存在...

📦 步骤 2：备份现有数据
✅ 已备份 families 表 → families_backup

🔨 步骤 3：创建 parents 表
✅ parents 表创建成功

🔄 步骤 4：迁移家长数据
✅ 成功迁移 1 个家长账号

✅ 步骤 6：验证迁移结果
📊 迁移后数据统计:
   - 家庭数量: 1
   - 家长数量: 1
   - 学生数量: 2

🎉 数据库迁移完成！
```

#### 第 2 步：启动应用

```bash
python app.py
```

应用会在 `http://localhost:5001` 启动

---

### 测试场景 1：爸爸（已有账号）登录

**操作：**
1. 访问 `http://localhost:5001/login`
2. 使用原账号密码登录
3. 进入任务中心

**预期结果：**
- ✅ 登录成功
- ✅ 可以看到任务列表
- ✅ 顶部导航栏显示用户名

**验证：**
- 检查浏览器控制台（F12），确认 session 中有 `parent_id` 和 `role`

---

### 测试场景 2：查看家庭成员

**操作：**
1. 点击顶部"家庭成员"按钮
2. 进入 `/family-members` 页面

**预期结果：**
- ✅ 显示家庭成员列表
- ✅ 显示爸爸的信息（名字、邮箱）
- ✅ 显示角色为"管理员"
- ✅ 没有删除按钮（不能删除自己）

---

### 测试场景 3：妈妈注册新账号

**操作：**
1. 打开无痕/隐私窗口（模拟妈妈）
2. 访问 `http://localhost:5001/login`
3. 点击"注册账号"
4. 填写信息：
   - 邮箱：`mom@test.com`
   - 密码：`123456`
   - 姓名：`妈妈`
5. 点击"注册"

**预期结果：**
- ✅ 注册成功
- ✅ 自动登录
- ✅ 创建了一个新家庭（family_id = B）

**注意：** 此时妈妈还看不到爸爸的孩子！

**验证：**
```python
# 查询数据库
session = db.get_session()
mom = session.query(Parent).filter_by(email='mom@test.com').first()
print(f"妈妈的 family_id: {mom.family_id}")  # 应该不同于爸爸的
print(f"妈妈的 role: {mom.role}")  # 应该是 'admin'
```

---

### 测试场景 4：爸爸拉妈妈入家庭 ⭐

**操作：**
1. 切换回爸爸的窗口
2. 点击"家庭成员"
3. 输入妈妈的邮箱：`mom@test.com`
4. 点击"拉入家庭"

**预期结果：**
- ✅ 提示：`成功将 妈妈 拉入家庭`
- ✅ 家庭成员列表显示：
  - 爸爸（管理员）
  - 妈妈（成员）

**验证：**
```python
# 查询数据库
session = db.get_session()
mom = session.query(Parent).filter_by(email='mom@test.com').first()
print(f"妈妈的 family_id: {mom.family_id}")  # 应该等于爸爸的 family_id
print(f"妈妈的 role: {mom.role}")  # 应该是 'member'
```

---

### 测试场景 5：妈妈查看爸爸的孩子 ⭐⭐⭐

**操作：**
1. 切换到妈妈的窗口
2. 刷新页面（F5）
3. 查看任务中心

**预期结果：**
- ✅ 可以看到爸爸添加的所有学生
- ✅ 可以看到所有任务
- ✅ 可以创建新任务
- ✅ 可以编辑/完成任务

**这是最关键的测试！验证多家长功能的核心价值。**

---

### 测试场景 6：妈妈尝试添加成员

**操作：**
1. 妈妈点击"家庭成员"
2. 尝试输入邮箱添加成员

**预期结果：**
- ❌ 提示：`只有管理员可以添加家庭成员`
- ✅ 权限控制正常工作

---

### 测试场景 7：错误处理

#### 7.1 添加不存在的邮箱

**操作：**
- 爸爸输入：`nonexist@test.com`

**预期结果：**
- ℹ️ 提示：`该用户尚未注册，请先让该用户注册账号`

#### 7.2 重复添加成员

**操作：**
- 爸爸再次输入：`mom@test.com`

**预期结果：**
- ❌ 提示：`该成员已在你的家庭中`

#### 7.3 添加自己

**操作：**
- 爸爸输入自己的邮箱

**预期结果：**
- ❌ 提示：`该成员已在你的家庭中`

---

## 🎯 测试检查清单

### 功能测试

- [ ] 爸爸可以正常登录
- [ ] 爸爸可以查看家庭成员
- [ ] 妈妈可以注册账号
- [ ] 爸爸可以拉妈妈入家庭
- [ ] **妈妈可以看到爸爸的孩子** ⭐⭐⭐
- [ ] 妈妈可以管理任务
- [ ] 妈妈不能添加成员（权限控制）
- [ ] 爸爸可以移除妈妈
- [ ] 移除后妈妈无法查看孩子

### 数据一致性

- [ ] 拉入家庭后，妈妈的 family_id 更新
- [ ] 妈妈的原家庭如果为空，自动删除
- [ ] 所有学生属于同一个家庭
- [ ] 所有任务正确关联到学生

### UI/UX

- [ ] 家庭成员页面正常显示
- [ ] 角色徽章正确显示
- [ ] 加载状态正常
- [ ] 错误提示友好
- [ ] 响应式设计（手机端）

---

## 🐛 常见问题

### Q1: 数据库迁移失败

**解决方法：**
```bash
# 检查备份
sqlite3 jiaxiao.db "SELECT * FROM families_backup"

# 手动回滚
python migrate_to_multi_parent.py --rollback
```

### Q2: 妈妈看不到孩子

**排查步骤：**
```python
# 检查妈妈的 family_id
session = db.get_session()
mom = session.query(Parent).filter_by(email='mom@test.com').first()
print(f"妈妈 family_id: {mom.family_id}")

# 检查爸爸的 family_id
dad = session.query(Parent).filter_by(email='dad@test.com').first()
print(f"爸爸 family_id: {dad.family_id}")

# 检查学生
students = session.query(Student).filter_by(family_id=dad.family_id).all()
print(f"学生数量: {len(students)}")
for s in students:
    print(f"  - {s.name}")
```

### Q3: 页面 404

**检查：**
- 确认 app.py 中有 `/family-members` 路由
- 确认 templates/family-members.html 存在
- 重启应用

---

## 📊 测试报告模板

```markdown
# 多家长账号系统测试报告

## 测试环境
- 日期：2025-01-23
- 测试人：xxx
- 数据库：PostgreSQL / SQLite

## 测试结果

### ✅ 通过的测试
- [x] 场景 1：爸爸登录
- [x] 场景 2：查看家庭成员
- [x] 场景 3：妈妈注册
- [x] 场景 4：爸爸拉妈妈入家庭
- [x] 场景 5：妈妈查看孩子（核心功能）
- [x] 场景 6：权限控制

### ❌ 失败的测试
- [ ] ...

### 🐛 发现的问题
1. ...
2. ...

### 💡 改进建议
1. ...
2. ...
```

---

## 🚀 测试完成后

### 提交代码

```bash
git add .
git commit -m "feat: 多家长账号系统 + 家庭成员管理页面

## 功能
- 支持多个家长独立账号
- 家庭成员管理页面
- 拉人入家庭功能
- 权限系统（admin/member）

## 修复
- 修复任务列表学生信息显示'未知'的问题

## 页面
- 新增 /family-members 页面
- 在任务中心添加'家庭成员'入口"
```

### 部署到 Zeabur

```bash
git push
```

Zeabur 会自动部署，无需额外操作。

---

## ✨ 开始测试

准备好了吗？让我们开始测试！

```bash
# 第 1 步：迁移数据库
python migrate_to_multi_parent.py

# 第 2 步：启动应用
python app.py

# 第 3 步：打开浏览器
open http://localhost:5001
```

**祝测试顺利！** 🎉
