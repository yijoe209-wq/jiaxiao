#!/usr/bin/env python3
"""
Debug script to check family_id consistency
"""
import sys
sys.path.insert(0, '/Volumes/data/vibe-coding-projects/jiaxiao')

from app import db
from models import Parent, Student, Family
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL
DATABASE_URL = db.engine.url

# Create session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 70)
print("🔍 数据库状态检查")
print("=" * 70)

# 查看所有家长
print("\n👨‍👩‍👧‍👦 所有家长:")
parents = session.query(Parent).all()
for p in parents:
    print(f"  - {p.name} ({p.email})")
    print(f"    family_id: {p.family_id}")
    print(f"    role: {p.role}")
    print()

# 查看所有家庭
print("\n🏠 所有家庭:")
families = session.query(Family).all()
for f in families:
    print(f"  - family_id: {f.family_id}")
    parents_in_family = session.query(Parent).filter_by(family_id=f.family_id).all()
    students_in_family = session.query(Student).filter_by(family_id=f.family_id).all()
    print(f"    家长: {[p.name for p in parents_in_family]}")
    print(f"    学生: {[s.name for s in students_in_family]}")
    print()

# 查看所有学生
print("\n👶 所有学生:")
students = session.query(Student).all()
for s in students:
    print(f"  - {s.name} ({s.grade})")
    print(f"    family_id: {s.family_id}")
    print()

session.close()
