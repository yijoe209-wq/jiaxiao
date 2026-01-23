# 家族成员管理 API - 添加到 app.py

# 在 app.py 中添加以下 API 端点：

@app.route('/api/family/members', methods=['GET'])
def get_family_members():
    """获取家庭成员列表"""
    try:
        family_id = get_current_family_id()
        if not family_id:
            return jsonify({'error': '请先登录'}), 401

        session = db.get_session()
        from models import Parent

        # 查询家庭的所有成员
        members = session.query(Parent).filter_by(
            family_id=family_id,
            is_active=True
        ).order_by(Parent.created_at).all()

        result = {
            'members': [member.to_dict() for member in members],
            'total': len(members)
        }

        session.close()
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取家庭成员失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


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
        password = data.get('password', '')
        name = data.get('name', '').strip()

        # 验证
        if not email or '@' not in email:
            return jsonify({'error': '请输入有效的邮箱地址'}), 400

        if len(password) < 6:
            return jsonify({'error': '密码至少6位'}), 400

        if not name:
            return jsonify({'error': '请输入姓名'}), 400

        session = db.get_session()
        from models import Parent

        # 检查邮箱是否已注册
        existing = session.query(Parent).filter_by(email=email).first()
        if existing:
            session.close()
            return jsonify({'error': '该邮箱已被使用'}), 400

        # 检查家庭人数限制（可选，比如最多10个成员）
        member_count = session.query(Parent).filter_by(
            family_id=family_id,
            is_active=True
        ).count()
        if member_count >= 10:
            session.close()
            return jsonify({'error': '家庭成员数量已达上限（10人）'}), 400

        # 创建新成员
        new_member = Parent(
            family_id=family_id,
            email=email,
            password=hash_password(password),
            name=name,
            role='member'  # 新添加的成员都是普通成员
        )
        session.add(new_member)
        session.commit()

        logger.info(f"添加家庭成员: family_id={family_id}, name={name}, email={email}")

        session.close()
        return jsonify({
            'success': True,
            'message': f'成功添加成员：{name}',
            'member': new_member.to_dict()
        })

    except Exception as e:
        logger.error(f"添加家庭成员失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/family/members/<parent_id>', methods=['DELETE'])
def remove_family_member(parent_id):
    """移除家庭成员"""
    try:
        family_id = get_current_family_id()
        if not family_id:
            return jsonify({'error': '请先登录'}), 401

        # 只有管理员可以移除成员
        current_role = flask_session.get('role')
        if current_role != 'admin':
            return jsonify({'error': '只有管理员可以移除家庭成员'}), 403

        session = db.get_session()
        from models import Parent

        # 查找要移除的成员
        member = session.query(Parent).filter_by(
            parent_id=parent_id,
            family_id=family_id
        ).first()

        if not member:
            session.close()
            return jsonify({'error': '成员不存在'}), 404

        # 不能移除自己
        current_parent_id = flask_session.get('parent_id')
        if member.parent_id == current_parent_id:
            session.close()
            return jsonify({'error': '不能移除自己'}), 400

        # 不能移除其他管理员
        if member.role == 'admin':
            session.close()
            return jsonify({'error': '不能移除管理员'}), 400

        # 软删除：标记为不活跃
        member.is_active = False
        session.commit()

        logger.info(f"移除家庭成员: parent_id={parent_id}, name={member.name}")

        session.close()
        return jsonify({
            'success': True,
            'message': f'已移除成员：{member.name}'
        })

    except Exception as e:
        logger.error(f"移除家庭成员失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/family/members/<parent_id>/role', methods=['PUT'])
def update_member_role(parent_id):
    """更新成员角色（提升为管理员或降级为成员）"""
    try:
        family_id = get_current_family_id()
        if not family_id:
            return jsonify({'error': '请先登录'}), 401

        # 只有管理员可以修改角色
        current_role = flask_session.get('role')
        if current_role != 'admin':
            return jsonify({'error': '只有管理员可以修改成员角色'}), 403

        data = request.json
        new_role = data.get('role', 'member')

        if new_role not in ['admin', 'member']:
            return jsonify({'error': '无效的角色'}), 400

        session = db.get_session()
        from models import Parent

        # 查找成员
        member = session.query(Parent).filter_by(
            parent_id=parent_id,
            family_id=family_id
        ).first()

        if not member:
            session.close()
            return jsonify({'error': '成员不存在'}), 404

        # 不能修改自己的角色
        current_parent_id = flask_session.get('parent_id')
        if member.parent_id == current_parent_id:
            session.close()
            return jsonify({'error': '不能修改自己的角色'}), 400

        # 更新角色
        old_role = member.role
        member.role = new_role
        session.commit()

        logger.info(f"更新成员角色: parent_id={parent_id}, {old_role} -> {new_role}")

        session.close()
        return jsonify({
            'success': True,
            'message': f'已将 {member.name} 的角色更新为 {new_role}',
            'member': member.to_dict()
        })

    except Exception as e:
        logger.error(f"更新成员角色失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
