# 添加"拉人入家庭"功能

## 需求
妈妈自己注册账号后，爸爸可以通过妈妈的邮箱将妈妈拉入自己的家庭。

## 实现方案

### 1. 修改添加成员 API

```python
@app.route('/api/family/members', methods=['POST'])
def add_family_member():
    """添加家庭成员"""
    try:
        family_id = get_current_family_id()
        if not family_id:
            return jsonify({'error': '请先登录'}), 401

        # 只有管理员可以添加成员
        current_role = flask_session.get('role')
        if current_role != 'admin':
            return jsonify({'error': '只有管理员可以添加家庭成员'}), 403

        data = request.json
        email = data.get('email', '').strip().lower()

        if not email or '@' not in email:
            return jsonify({'error': '请输入有效的邮箱地址'}), 400

        session = db.get_session()
        from models import Parent, Family

        # 检查邮箱是否已注册
        existing_parent = session.query(Parent).filter_by(email=email).first()

        if existing_parent:
            # 场景 1：用户已注册，拉入家庭
            if existing_parent.family_id == family_id:
                session.close()
                return jsonify({'error': '该成员已在你的家庭中'}), 400

            # 将用户拉入当前家庭
            old_family_id = existing_parent.family_id
            existing_parent.family_id = family_id
            existing_parent.role = 'member'  # 设为普通成员

            # 检查旧家庭是否还有成员，如果没有则删除
            old_family_members = session.query(Parent).filter_by(
                family_id=old_family_id
            ).count()

            if old_family_members == 0:
                # 删除空家庭
                old_family = session.query(Family).get(old_family_id)
                if old_family:
                    session.delete(old_family)

            session.commit()

            logger.info(f"拉入成员: email={email}, from_family={old_family_id}, to_family={family_id}")

            session.close()
            return jsonify({
                'success': True,
                'message': f'成功将 {existing_parent.name} 拉入家庭',
                'member': existing_parent.to_dict()
            })

        else:
            # 场景 2：用户未注册，需要创建新账号
            # 这里返回提示，让用户知道需要先注册
            session.close()
            return jsonify({
                'error': '该用户尚未注册',
                'needs_register': True,
                'message': '请先让该用户注册账号，然后再次输入邮箱即可拉入家庭'
            }), 400

    except Exception as e:
        logger.error(f"添加家庭成员失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
```

### 2. 前端页面

```html
<!-- 添加成员表单 -->
<div id="addMemberForm">
    <h3>添加家庭成员</h3>
    <p class="text-sm text-gray-600 mb-4">
        请输入成员的邮箱地址：
    </p>

    <form onsubmit="addMember(event)">
        <input
            type="email"
            id="memberEmail"
            placeholder="成员邮箱（如：mom@example.com）"
            required
            class="w-full px-4 py-2 border rounded-lg"
        >
        <button type="submit" class="mt-4 btn-primary">
            拉入家庭
        </button>
    </form>

    <div class="mt-4 p-4 bg-blue-50 rounded-lg">
        <p class="text-sm text-blue-800">
            💡 <strong>提示：</strong>
        </p>
        <ul class="text-sm text-blue-700 list-disc list-inside mt-2">
            <li>如果成员已注册，将直接拉入家庭</li>
            <li>如果成员未注册，请先让成员注册账号</li>
            <li>拉入后，成员可以看到家庭中所有的孩子和任务</li>
        </ul>
    </div>
</div>

<script>
async function addMember(event) {
    event.preventDefault();

    const email = document.getElementById('memberEmail').value.trim();

    const response = await fetch('/api/family/members', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email})
    });

    const data = await response.json();

    if (response.ok) {
        alert('✅ ' + data.message);
        showFamilyMembers(); // 刷新成员列表
        document.getElementById('memberEmail').value = '';
    } else {
        if (data.needs_register) {
            alert('⚠️ ' + data.message);
        } else {
            alert('❌ ' + data.error);
        }
    }
}
</script>
```

## 流程图

```
妈妈自己注册
    ↓
创建账号 (family_id = A)
    ↓
爸爸登录
    ↓
输入妈妈邮箱
    ↓
系统检测：妈妈已存在
    ↓
更新妈妈的家庭 (family_id = B)
    ↓
✅ 妈妈登录后看到爸爸的孩子
```

## 优势

- ✅ 妈妈自己设置密码（隐私）
- ✅ 爸爸不需要知道妈妈密码
- ✅ 流程简单（就像微信群拉人）
- ✅ 符合用户习惯
- ✅ 安全可靠
