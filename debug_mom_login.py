#!/usr/bin/env python3
"""
Debug mom login to see what family_id she gets in session
"""
import requests
import random

BASE_URL = 'http://localhost:5001'

def random_email():
    return f"user{random.randint(10000, 99999)}@test.com"

print("=" * 70)
print("🔍 调试妈妈登录 - 查看 family_id")
print("=" * 70)

# ==================== 爸爸注册并添加学生 ====================
print("\n📱 步骤 1: 爸爸注册并添加学生")
print("-" * 70)

dad_session = requests.Session()
dad_email = random_email()

print(f"1. 爸爸注册 ({dad_email})")
r = dad_session.post(f'{BASE_URL}/api/register', json={
    'email': dad_email,
    'password': 'test123',
    'parent_name': '李爸爸'
})
result = r.json()
print(f"   结果: {result.get('message', '失败')}")
dad_family_id = result.get('family_id')
print(f"   Dad's family_id: {dad_family_id}")

print("\n2. 爸爸添加学生")
r = dad_session.post(f'{BASE_URL}/api/students', json={
    'name': '小明',
    'grade': '三年级',
    'class_name': '2班'
})
print(f"   状态码: {r.status_code}")

r = dad_session.get(f'{BASE_URL}/api/students')
data = r.json()
students = data if isinstance(data, list) else data.get('students', [])
print(f"   爸爸的学生数: {len(students)}")
if students:
    print(f"   学生: {students[0]['name']}")

# ==================== 妈妈注册 ====================
print("\n📱 步骤 2: 妈妈注册")
print("-" * 70)

mom_session = requests.Session()
mom_email = random_email()

print(f"1. 妈妈注册 ({mom_email})")
r = mom_session.post(f'{BASE_URL}/api/register', json={
    'email': mom_email,
    'password': 'test123',
    'parent_name': '张妈妈'
})
result = r.json()
print(f"   结果: {result.get('message', '失败')}")
mom_family_id = result.get('family_id')
print(f"   Mom's initial family_id: {mom_family_id}")

print("\n2. 妈妈查看学生（拉入家庭前）")
r = mom_session.get(f'{BASE_URL}/api/students')
data = r.json()
students = data if isinstance(data, list) else data.get('students', [])
print(f"   妈妈的学生数: {len(students)}")

# ==================== 爸爸拉妈妈入家庭 ====================
print("\n📱 步骤 3: 爸爸把妈妈拉入家庭")
print("-" * 70)

print(f"1. 爸爸拉妈妈 ({mom_email})")
r = dad_session.post(f'{BASE_URL}/api/family/members', json={
    'email': mom_email
})
result = r.json()
print(f"   结果: {result.get('message', result.get('error', '失败'))}")

# ==================== 检查数据库中的家庭ID ====================
print("\n📱 步骤 4: 检查数据库状态")
print("-" * 70)

import sys
sys.path.insert(0, '/Volumes/data/vibe-coding-projects/jiaxiao')
from app import db
from models import Parent

session = db.get_session()

# 查看妈妈的数据库记录
mom_db = session.query(Parent).filter_by(email=mom_email).first()
if mom_db:
    print(f"   妈妈的数据库 family_id: {mom_db.family_id}")
    print(f"   妈妈的数据库 role: {mom_db.role}")
else:
    print("   ❌ 找不到妈妈的数据库记录")

# 查看爸爸的数据库记录
dad_db = session.query(Parent).filter_by(email=dad_email).first()
if dad_db:
    print(f"   爸爸的数据库 family_id: {dad_db.family_id}")

session.close()

# ==================== 妈妈用旧session查看 ====================
print("\n📱 步骤 5: 妈妈用旧session查看学生")
print("-" * 70)

print("1. 妈妈查看学生（旧session）")
r = mom_session.get(f'{BASE_URL}/api/students')
data = r.json()
students = data if isinstance(data, list) else data.get('students', [])
print(f"   学生数: {len(students)}")

# ==================== 妈妈重新登录 ====================
print("\n📱 步骤 6: 妈妈重新登录")
print("-" * 70)

print("1. 妈妈登录")
mom_session2 = requests.Session()
r = mom_session2.post(f'{BASE_URL}/api/login', json={
    'email': mom_email,
    'password': 'test123'
})
result = r.json()
print(f"   结果: {result.get('message', '失败')}")
new_family_id = result.get('family_id')
print(f"   Mom's NEW family_id from login: {new_family_id}")

print("\n2. 妈妈查看学生（新session）")
r = mom_session2.get(f'{BASE_URL}/api/students')
data = r.json()
students = data if isinstance(data, list) else data.get('students', [])
print(f"   学生数: {len(students)}")
if students:
    for s in students:
        print(f"   - {s['name']} ({s['grade']})")
else:
    print("   ❌ 妈妈看不到学生！")

# ==================== 分析 ====================
print("\n" + "=" * 70)
print("📊 分析结果")
print("=" * 70)
print(f"爸爸的 family_id: {dad_family_id}")
print(f"妈妈的初始 family_id: {mom_family_id}")
print(f"妈妈的数据库 family_id (被拉入后): {mom_db.family_id if mom_db else 'N/A'}")
print(f"妈妈登录后返回的 family_id: {new_family_id}")

if new_family_id == dad_family_id:
    print("\n✅ family_id 一致！问题可能在其他地方")
else:
    print(f"\n❌ family_id 不一致！")
    print(f"   期望: {dad_family_id}")
    print(f"   实际: {new_family_id}")

if len(students) > 0:
    print("\n✅ 妈妈可以看到学生！")
else:
    print("\n❌ 妈妈看不到学生！")
