"""
数据库诊断脚本
检查表是否真的创建了
"""
from models import db
from sqlalchemy import text
import os

print("=" * 60)
print("🔍 数据库诊断")
print("=" * 60)

# 1. 检查数据库路径
print(f"\n📂 数据库 URL: {db.engine.url}")
print(f"📂 数据库类型: {db.engine.dialect.name}")

# 2. 尝试连接
session = db.get_session()
try:
    # 3. 检查表是否存在
    result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result.fetchall()]
    print(f"\n📊 现有表: {tables}")

    # 4. 检查 families 表
    if 'families' in tables:
        print("✅ families 表存在")
        count = session.execute(text("SELECT COUNT(*) FROM families")).scalar()
        print(f"   记录数: {count}")
    else:
        print("❌ families 表不存在")

    session.close()
except Exception as e:
    print(f"❌ 错误: {e}")
    session.close()

print("=" * 60)
