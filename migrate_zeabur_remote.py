#!/usr/bin/env python3
"""
远程迁移 Zeabur 数据库
从本地连接 Zeabur PostgreSQL，执行迁移
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def get_db_url():
    """获取数据库连接URL"""
    db_url = os.getenv('DATABASE_URL')
    if 'postgresql+psycopg://' in db_url:
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    return db_url

def migrate_remote_database():
    """远程迁移 Zeabur 数据库"""
    print("🚀 开始远程迁移 Zeabur 数据库...")
    print("=" * 60)

    try:
        # 1. 连接数据库
        print("\n📡 步骤 1: 连接 Zeabur 数据库")
        db_url = get_db_url()
        print(f"数据库: {db_url.split('@')[1] if '@' in db_url else 'unknown'}")

        # 使用 SQLAlchemy 创建引擎
        from sqlalchemy import create_engine
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # 2. 检查当前状态
            print("\n📊 步骤 2: 检查数据库状态")

            # 检查 families 表结构（PostgreSQL 用 information_schema）
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'families'
                ORDER BY ordinal_position
            """))
            columns = [row[0] for row in result.fetchall()]
            print(f"families 表字段: {columns}")

            # 统计数据
            family_count = conn.execute(text("SELECT COUNT(*) FROM families")).scalar()
            parent_count = conn.execute(text("SELECT COUNT(*) FROM parents")).scalar()

            print(f"families 记录数: {family_count}")
            print(f"parents 记录数: {parent_count}")

            # 3. 检查是否有旧数据（families 表有 email 字段）
            has_email = 'email' in columns
            has_password = 'password' in columns
            has_parent_name = 'parent_name' in columns

            if has_email and has_password:
                print("\n✅ 检测到旧版本 families 表（有 email/password 字段）")
                print("🔄 步骤 3: 迁移家长数据")

                # 迁移数据
                migrate_sql = text("""
                    INSERT INTO parents (parent_id, family_id, email, password, name, role, is_active, created_at)
                    SELECT
                        family_id,
                        family_id,
                        email,
                        password,
                        parent_name,
                        'admin' as role,
                        true as is_active,
                        created_at
                    FROM families
                    WHERE NOT EXISTS (
                        SELECT 1 FROM parents WHERE parents.email = families.email
                    )
                """)

                result = conn.execute(migrate_sql)
                migrated_count = result.rowcount
                conn.commit()

                print(f"✅ 成功迁移 {migrated_count} 个家长账号")

            else:
                print("\n⚠️  families 表已是新版本（无 email/password 字段）")
                print("ℹ️  无需迁移，请直接注册新账号")

                # 检查是否有任何家长账号
                if parent_count == 0:
                    print("\n❌ 数据库中没有家长账号")
                    print("💡 请在 https://edu-track.zeabur.app 注册新账号")
                    return False

            # 4. 验证迁移结果
            print("\n✅ 步骤 4: 验证迁移结果")

            new_parent_count = conn.execute(text("SELECT COUNT(*) FROM parents")).scalar()
            print(f"parents 表记录数: {new_parent_count}")

            if new_parent_count > 0:
                # 显示迁移的账号
                result = conn.execute(text("SELECT email, name, role FROM parents"))
                parents = result.fetchall()
                print("\n📋 家长账号列表:")
                for p in parents:
                    print(f"  ✉ {p[0]} ({p[1]}, {p[2]})")

            print("\n" + "=" * 60)
            print("🎉 迁移完成！")
            print("\n💡 现在可以使用以下账号登录:")
            print("   https://edu-track.zeabur.app/login")

            return True

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_remote_database()
    sys.exit(0 if success else 1)
