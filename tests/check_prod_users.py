#!/usr/bin/env python3
"""
检查生产环境数据库中的用户
需要提供 DATABASE_URL
"""

import sys
import os
import hashlib

# 从环境变量或参数获取数据库 URL
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ 请提供 DATABASE_URL 环境变量")
    print("\n使用方法:")
    print("  export DATABASE_URL='postgresql://...'")
    print("  python check_prod_users.py")
    sys.exit(1)

print(f"📊 连接数据库: {database_url}")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import db, init_db, Family

def hash_password(password):
    """加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

init_db(database_url)
session = db.get_session()

try:
    users = session.query(Family).all()

    if not users:
        print("\n❌ 数据库中没有用户")
        print("\n💡 建议:")
        print("   1. 访问 https://edu-track.zeabur.app/login 注册新账号")
        print("   2. 检查 Zeabur 控制台的 PostgreSQL 服务配置")
    else:
        print(f"\n📋 共有 {len(users)} 个用户：\n")
        print("=" * 80)

        for user in users:
            print(f"👤 用户ID: {user.family_id}")
            print(f"   姓名: {user.parent_name}")
            print(f"   邮箱: {user.email}")
            print(f"   创建时间: {user.created_at}")
            print("=" * 80)

        print("\n💡 提示:")
        print("   如果你的账号不在此列表中,说明数据已丢失")
        print("   请重新注册: https://edu-track.zeabur.app/login")

finally:
    session.close()
