# 多家长账号系统 - 完整文档

## 🎉 功能已实现

### 1. 数据模型 ✅
- 创建 `Parent` 模型
- 修改 `Family` 模型关系
- 支持一个家庭多个家长

### 2. 后端 API ✅
- ✅ 修改注册逻辑（创建 Family + Parent）
- ✅ 修改登录逻辑（查询 Parent 表）
- ✅ 添加家庭成员管理 API：
  - `GET /api/family/members` - 获取成员列表
  - `POST /api/family/members` - 添加成员
  - `DELETE /api/family/members/<id>` - 移除成员
  - `PUT /api/family/members/<id>/role` - 修改角色

### 3. 权限系统 ✅
- `admin` - 管理员（家庭创建者）
- `member` - 普通成员
- 只有管理员可以添加/移除成员

---

## 🚀 使用指南

### 步骤 1：运行数据库迁移

```bash
python migrate_to_multi_parent.py
```

**迁移会做什么：**
1. 创建 `parents` 表
2. 将现有 `families` 表的家长数据迁移到 `parents`
3. 保留原数据作为备份

### 步骤 2：测试登录

使用原来的账号密码登录，应该能正常工作。

### 步骤 3：添加家庭成员（妈妈）

有两种方式：

#### 方式 A：通过 API

```bash
curl -X POST https://edu-track.zeabur.app/api/family/members \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mom@example.com",
    "password": "password123",
    "name": "妈妈"
  }'
```

#### 方式 B：创建管理页面（推荐）

在任务中心页面添加一个"家庭成员"按钮：

```html
<!-- 在 my-tasks.html 的导航栏中添加 -->
<button onclick="showFamilyMembers()" class="btn-secondary">
    👨‍👩‍👧‍👦 家庭成员
</button>

<!-- 添加模态框 -->
<div id="familyMembersModal" class="modal hidden">
    <div class="modal-content">
        <h2>家庭成员管理</h2>
        <div id="membersList"></div>
        <hr>
        <h3>添加成员</h3>
        <form id="addMemberForm">
            <input type="text" id="memberName" placeholder="姓名" required>
            <input type="email" id="memberEmail" placeholder="邮箱" required>
            <input type="password" id="memberPassword" placeholder="密码" required>
            <button type="submit">添加</button>
        </form>
    </div>
</div>

<script>
// 显示家庭成员
async function showFamilyMembers() {
    const response = await fetch('/api/family/members');
    const data = await response.json();

    const list = document.getElementById('membersList');
    list.innerHTML = data.members.map(member => `
        <div class="member-item">
            <div>
                <strong>${member.name}</strong>
                <span class="role-badge">${member.role === 'admin' ? '管理员' : '成员'}</span>
            </div>
            ${member.role !== 'admin' ? `
                <button onclick="removeMember('${member.parent_id}', '${member.name}')">
                    移除
                </button>
            ` : ''}
        </div>
    `).join('');

    document.getElementById('familyMembersModal').classList.remove('hidden');
}

// 添加成员
document.getElementById('addMemberForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('memberName').value;
    const email = document.getElementById('memberEmail').value;
    const password = document.getElementById('memberPassword').value;

    const response = await fetch('/api/family/members', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password})
    });

    if (response.ok) {
        alert('添加成功！');
        showFamilyMembers();
        document.getElementById('addMemberForm').reset();
    } else {
        const data = await response.json();
        alert('添加失败：' + data.error);
    }
});

// 移除成员
async function removeMember(parentId, name) {
    if (!confirm(`确定要移除 ${name} 吗？`)) return;

    const response = await fetch(`/api/family/members/${parentId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        alert('移除成功！');
        showFamilyMembers();
    } else {
        const data = await response.json();
        alert('移除失败：' + data.error);
    }
}
</script>
```

---

## 📊 数据库结构

### families 表
```sql
family_id VARCHAR(50) PRIMARY KEY
family_name VARCHAR(100) -- 可选
created_at DATETIME
```

### parents 表（新增）
```sql
parent_id VARCHAR(50) PRIMARY KEY
family_id VARCHAR(50) -- 外键到 families
email VARCHAR(100) UNIQUE -- 登录凭证
password VARCHAR(100) -- 加密密码
name VARCHAR(50) -- 家长姓名
role VARCHAR(20) -- admin 或 member
is_active BOOLEAN -- 是否激活
created_at DATETIME
last_login DATETIME
```

### students 表
```sql
student_id VARCHAR(50) PRIMARY KEY
family_id VARCHAR(50) -- 外键到 families
name VARCHAR(50)
grade VARCHAR(20)
-- ...
```

---

## 🔐 权限说明

| 操作 | Admin | Member |
|------|-------|--------|
| 查看任务 | ✅ | ✅ |
| 创建任务 | ✅ | ✅ |
| 编辑任务 | ✅ | ✅ |
| 删除任务 | ✅ | ✅ |
| 添加成员 | ✅ | ❌ |
| 移除成员 | ✅ | ❌ |
| 修改角色 | ✅ | ❌ |

---

## 🧪 测试场景

### 场景 1：爸爸添加妈妈
1. 爸爸登录
2. 进入"家庭成员管理"
3. 填写妈妈的信息（邮箱、密码、姓名）
4. 点击"添加"
5. 妈妈收到通知后登录

### 场景 2：妈妈查看任务
1. 妈妈使用自己的账号登录
2. 可以看到所有孩子的任务
3. 可以创建、编辑、完成任务

### 场景 3：权限控制
1. 妈妈尝试添加成员
2. 系统提示"只有管理员可以添加"
3. 妈妈无法添加

---

## 📝 API 文档

### 获取家庭成员
```http
GET /api/family/members

Response:
{
  "members": [
    {
      "parent_id": "xxx",
      "family_id": "yyy",
      "email": "dad@example.com",
      "name": "爸爸",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-01-23T...",
      "last_login": "2025-01-23T..."
    }
  ],
  "total": 1
}
```

### 添加成员
```http
POST /api/family/members
Content-Type: application/json

{
  "email": "mom@example.com",
  "password": "password123",
  "name": "妈妈"
}

Response:
{
  "success": true,
  "message": "成功添加成员：妈妈",
  "member": {...}
}
```

### 移除成员
```http
DELETE /api/family/members/<parent_id>

Response:
{
  "success": true,
  "message": "已移除成员：妈妈"
}
```

### 更新角色
```http
PUT /api/family/members/<parent_id>/role
Content-Type: application/json

{
  "role": "admin"
}

Response:
{
  "success": true,
  "message": "已将 妈妈的角色更新为 admin",
  "member": {...}
}
```

---

## ✨ 完成清单

- [x] 创建 Parent 数据模型
- [x] 修改注册逻辑
- [x] 修改登录逻辑
- [x] 添加家庭成员管理 API
- [x] 创建数据库迁移脚本
- [x] 编写完整文档
- [ ] 前端管理页面（可选，可以通过 API 操作）
- [ ] 测试所有功能
- [ ] 部署到 Zeabur

---

## 🚀 下一步

1. **运行迁移脚本**
   ```bash
   python migrate_to_multi_parent.py
   ```

2. **测试登录**
   - 使用原账号登录
   - 验证功能正常

3. **添加妈妈账号**
   - 通过 API 或前端页面
   - 测试妈妈登录

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 实现多家长账号系统"
   git push
   ```

5. **部署到 Zeabur**
   - 自动部署
   - 测试生产环境

---

**🎉 多家长账号系统已完成！现在爸爸和妈妈都可以独立登录管理孩子的任务了！**
