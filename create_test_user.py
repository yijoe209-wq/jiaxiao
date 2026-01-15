#!/usr/bin/env python3
"""创建测试账号"""
from models import db, init_db, Family
import uuid

# 初始化数据库
init_db('sqlite:///jiaxiao.db')
session = db.get_session()

try:
    # 检查是否已存在测试账号
    existing_family = session.query(Family).filter_by(email='test@example.com').first()

    if existing_family:
        print(f"✅ 测试账号已存在:")
        print(f"   邮箱: test@example.com")
        print(f"   密码: test123")
        print(f"   Family ID: {existing_family.family_id}")
        print(f"   家长姓名: {existing_family.parent_name}")
    else:
        # 创建新的测试家庭
        family_id = str(uuid.uuid4())
        test_family = Family(
            family_id=family_id,
            parent_name='测试家长',
            email='test@example.com',
            password='test123'  # 简化处理，实际应该用哈希
        )

        session.add(test_family)
        session.commit()

        print(f"✅ 测试账号创建成功:")
        print(f"   邮箱: test@example.com")
        print(f"   密码: test123")
        print(f"   Family ID: {family_id}")
        print(f"   家长姓名: 测试家长")

    print("\n" + "=" * 50)
    print("请访问以下地址登录:")
    print("=" * 50)
    print("http://localhost:5001/login")
    print("\n登录后即可查看任务中心")

finally:
    session.close()

