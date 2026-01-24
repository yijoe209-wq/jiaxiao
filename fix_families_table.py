#!/usr/bin/env python3
"""
修复 families 表结构 - 删除旧字段
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def fix_families_table():
    """修复 families 表，删除旧字段"""
    print("🔧 修复 families 表结构...")
    print("=" * 60)

    try:
        db_url = os.getenv('DATABASE_URL', '').replace('postgresql+psycopg://', 'postgresql://')
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # 检查当前结构
            print("\n📊 当前 families 表结构:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'families'
                ORDER BY ordinal_position
            """))
            columns = list(result.fetchall())
            for col in columns:
                print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")

            # 删除旧字段
            print("\n🗑️  删除旧字段...")
            old_columns = ['email', 'password', 'parent_name']

            for col_name in old_columns:
                # 检查字段是否存在
                exists = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'families' AND column_name = :col_name
                    )
                """), {'col_name': col_name}).scalar()

                if exists:
                    try:
                        conn.execute(text(f"ALTER TABLE families DROP COLUMN IF EXISTS {col_name}"))
                        conn.commit()
                        print(f"  ✅ 已删除字段: {col_name}")
                    except Exception as e:
                        print(f"  ⚠️  删除字段 {col_name} 失败: {e}")
                else:
                    print(f"  ℹ️  字段不存在: {col_name}")

            # 验证修复后的结构
            print("\n✅ 修复后的 families 表结构:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'families'
                ORDER BY ordinal_position
            """))
            columns = list(result.fetchall())
            for col in columns:
                print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")

            print("\n" + "=" * 60)
            print("🎉 families 表结构修复完成！")
            return True

    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_families_table()
    sys.exit(0 if success else 1)
