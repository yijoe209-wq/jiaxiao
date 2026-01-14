#!/usr/bin/env python3
"""
调试工具：查看所有注册用户
"""

import sys
import os
import hashlib

# 强制使用本地开发环境
os.environ['ENV'] = 'development'

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, init_db, Family

def hash_password(password):
    """加密密码（和 app.py 中的一致）"""
    return hashlib.sha256(password.encode()).hexdigest()

def list_users():
    """列出所有用户"""
    # 使用数据库 URL（从环境变量或默认值）
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///jiaxiao.db')

    print(f"📊 连接数据库: {database_url}")

    init_db(database_url)
    session = db.get_session()

    try:
        users = session.query(Family).all()

        if not users:
            print("❌ 数据库中没有用户")
            return

        print(f"\n📋 共有 {len(users)} 个用户：\n")
        print("=" * 80)

        for user in users:
            print(f"👤 用户ID: {user.family_id}")
            print(f"   姓名: {user.parent_name}")
            print(f"   邮箱: {user.email}")
            print(f"   密码哈希: {user.password}")
            print(f"   创建时间: {user.created_at}")
            print("=" * 80)

    finally:
        session.close()


def test_password(email, password):
    """测试密码是否正确"""
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///jiaxiao.db')
    init_db(database_url)

    session = db.get_session()

    try:
        user = session.query(Family).filter_by(email=email.lower()).first()

        if not user:
            print(f"❌ 用户不存在: {email}")
            return

        input_hash = hash_password(password)
        print(f"\n🔐 密码测试: {email}")
        print(f"   输入密码: {password}")
        print(f"   输入密码哈希: {input_hash}")
        print(f"   数据库哈希:   {user.password}")
        print(f"   匹配: {'✅ 是' if input_hash == user.password else '❌ 否'}")

    finally:
        session.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='调试用户数据库')
    parser.add_argument('--list', action='store_true', help='列出所有用户')
    parser.add_argument('--test', nargs=2, metavar=('EMAIL', 'PASSWORD'), help='测试密码')

    args = parser.parse_args()

    if args.test:
        test_password(args.test[0], args.test[1])
    elif args.list:
        list_users()
    else:
        list_users()
