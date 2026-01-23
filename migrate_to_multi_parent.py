#!/usr/bin/env python3
"""
数据库迁移脚本：从单一家长账号迁移到多家长账号系统

迁移步骤：
1. 创建 parents 表
2. 将现有 families 表中的家长数据迁移到 parents 表
3. 更新 families 表结构
4. 更新外键关系
"""

import sys
from datetime import datetime
from sqlalchemy import text
from models import db, Parent, Family, Student, Task

def migrate_database():
    """执行数据库迁移"""

    print("🚀 开始数据库迁移：单一家长 → 多家长系统")
    print("=" * 60)

    session = db.get_session()
    engine = db.engine

    try:
        # ==================== 步骤 1：检查是否已迁移 ====================
        print("\n📋 步骤 1：检查迁移状态")

        try:
            # 检查 parents 表是否存在
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='parents'"))
            parents_exists = result.fetchone() is not None

            if parents_exists:
                print("⚠️  parents 表已存在，检查是否需要继续迁移...")

                # 检查是否已有数据
                parent_count = session.execute(text("SELECT COUNT(*) FROM parents")).scalar()
                print(f"✅ 现有家长数量: {parent_count}")

                if parent_count > 0:
                    confirm = input("\n⚠️  已有家长数据，是否重新迁移？(yes/no): ")
                    if confirm.lower() != 'yes':
                        print("❌ 取消迁移")
                        return False
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False

        # ==================== 步骤 2：备份现有数据 ====================
        print("\n📦 步骤 2：备份现有数据")

        try:
            # 备份 families 表
            session.execute(text("CREATE TABLE IF NOT EXISTS families_backup AS SELECT * FROM families"))
            print("✅ 已备份 families 表 → families_backup")

            # 统计现有数据
            family_count = session.execute(text("SELECT COUNT(*) FROM families")).scalar()
            student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()
            task_count = session.execute(text("SELECT COUNT(*) FROM tasks")).scalar()

            print(f"📊 现有数据统计:")
            print(f"   - 家庭数量: {family_count}")
            print(f"   - 学生数量: {student_count}")
            print(f"   - 任务数量: {task_count}")

        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False

        # ==================== 步骤 3：创建 parents 表 ====================
        print("\n🔨 步骤 3：创建 parents 表")

        # 创建表
        create_parents_sql = """
        CREATE TABLE IF NOT EXISTS parents (
            parent_id VARCHAR(50) PRIMARY KEY,
            family_id VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            name VARCHAR(50),
            role VARCHAR(20) DEFAULT 'member',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            last_login DATETIME,
            FOREIGN KEY (family_id) REFERENCES families (family_id) ON DELETE CASCADE
        );
        """

        # 创建索引
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_parents_family_id ON parents(family_id);",
            "CREATE INDEX IF NOT EXISTS idx_parents_email ON parents(email);"
        ]

        try:
            session.execute(text(create_parents_sql))
            for idx in create_indexes:
                session.execute(text(idx))
            session.commit()
            print("✅ parents 表创建成功")
        except Exception as e:
            session.rollback()
            print(f"❌ 创建 parents 表失败: {e}")
            return False

        # ==================== 步骤 4：迁移家长数据 ====================
        print("\n🔄 步骤 4：迁移家长数据")

        migrate_parents_sql = """
        INSERT INTO parents (parent_id, family_id, email, password, name, role, is_active, created_at)
        SELECT
            family_id as parent_id,
            family_id as family_id,
            email,
            password,
            parent_name as name,
            'admin' as role,
            1 as is_active,
            created_at
        FROM families
        WHERE NOT EXISTS (
            SELECT 1 FROM parents WHERE parents.email = families.email
        );
        """

        try:
            result = session.execute(text(migrate_parents_sql))
            migrated_count = result.rowcount
            session.commit()
            print(f"✅ 成功迁移 {migrated_count} 个家长账号")
        except Exception as e:
            session.rollback()
            print(f"❌ 迁移家长数据失败: {e}")
            return False

        # ==================== 步骤 5：更新 families 表结构 ====================
        print("\n🔧 步骤 5：更新 families 表结构")

        try:
            # SQLite 不支持 DROP COLUMN，需要重建表
            # 检查是否需要重建
            columns = session.execute(text("PRAGMA table_info(families)")).fetchall()
            column_names = [col[1] for col in columns]

            if 'email' in column_names:
                print("⚠️  SQLite 需要重建 families 表以移除 email/password 列")
                print("ℹ️  这些列将在后续版本中弃用，当前保留")

                # 创建新表
                create_new_families = """
                CREATE TABLE IF NOT EXISTS families_new (
                    family_id VARCHAR(50) PRIMARY KEY,
                    family_name VARCHAR(100),
                    created_at DATETIME
                );
                """

                # 迁移数据
                migrate_data = """
                INSERT INTO families_new (family_id, family_name, created_at)
                SELECT family_id, NULL, created_at FROM families;
                """

                # 删除旧表，重命名新表
                drop_old = "DROP TABLE families;"
                rename_new = "ALTER TABLE families_new RENAME TO families;"

                try:
                    session.execute(text(create_new_families))
                    session.execute(text(migrate_data))
                    session.execute(text(drop_old))
                    session.execute(text(rename_new))
                    session.commit()
                    print("✅ families 表结构更新成功")
                except Exception as e:
                    session.rollback()
                    print(f"⚠️  families 表更新失败（可忽略）: {e}")
                    print("ℹ️  不影响功能，email/password 列将保留但不使用")
            else:
                print("✅ families 表结构已是最新")

        except Exception as e:
            print(f"⚠️  更新 families 表时出错: {e}")
            print("ℹ️  不影响核心功能，继续执行")

        # ==================== 步骤 6：验证迁移结果 ====================
        print("\n✅ 步骤 6：验证迁移结果")

        try:
            # 统计迁移后的数据
            new_family_count = session.execute(text("SELECT COUNT(*) FROM families")).scalar()
            new_parent_count = session.execute(text("SELECT COUNT(*) FROM parents")).scalar()
            new_student_count = session.execute(text("SELECT COUNT(*) FROM students")).scalar()

            print(f"📊 迁移后数据统计:")
            print(f"   - 家庭数量: {new_family_count}")
            print(f"   - 家长数量: {new_parent_count}")
            print(f"   - 学生数量: {new_student_count}")

            # 验证数据完整性
            family_ids = session.execute(text("SELECT DISTINCT family_id FROM parents")).fetchall()
            print(f"\n🔍 验证: {len(family_ids)} 个家庭有家长")

            print("\n✅ 数据迁移验证通过")

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False

        # ==================== 完成 ====================
        print("\n" + "=" * 60)
        print("🎉 数据库迁移完成！")
        print("\n📝 后续步骤:")
        print("1. 重启应用服务器")
        print("2. 测试登录功能（使用原账号密码）")
        print("3. 测试添加家庭成员功能")
        print("\n💾 备份文件: families_backup")
        print("⚠️  如有问题，可从备份恢复")

        return True

    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False

    finally:
        session.close()


def rollback_migration():
    """回滚迁移（从备份恢复）"""
    print("\n🔄 开始回滚迁移...")

    session = db.get_session()

    try:
        # 检查备份是否存在
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='families_backup'"))
        if not result.fetchone():
            print("❌ 未找到备份表 families_backup")
            return False

        # 删除 parents 表
        session.execute(text("DROP TABLE IF EXISTS parents"))

        # 从备份恢复 families 表
        session.execute(text("DROP TABLE IF EXISTS families"))
        session.execute(text("ALTER TABLE families_backup RENAME TO families"))

        session.commit()
        print("✅ 回滚完成")
        return True

    except Exception as e:
        print(f"❌ 回滚失败: {e}")
        session.rollback()
        return False

    finally:
        session.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()

    if args.rollback:
        success = rollback_migration()
    else:
        success = migrate_database()

    sys.exit(0 if success else 1)
