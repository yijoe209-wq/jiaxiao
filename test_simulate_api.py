#!/usr/bin/env python3
"""直接测试 /api/simulate API"""

import requests
import json

# 先注册获取 session
session = requests.Session()

random_suffix = 'test123'
test_email = f"direct_test_{random_suffix}@example.com"

print("1. 注册...")
register_data = {
    'email': test_email,
    'password': 'Test123456',
    'parent_name': '直接测试'
}
response = session.post('http://localhost:5001/api/register', json=register_data)
print(f"   状态: {response.status_code}")
result = response.json()
print(f"   结果: {result}")

# 添加学生
print("\n2. 添加学生...")
add_student_data = {
    'name': '测试学生',
    'grade': '一年级'
}
response = session.post('http://localhost:5001/api/students', json=add_student_data)
print(f"   状态: {response.status_code}")
result = response.json()
print(f"   结果: {result}")

student_id = result.get('student_id')
print(f"   学生ID: {student_id}")

# 创建任务
print("\n3. 调用 /api/simulate...")
simulate_data = {
    'message': '测试任务：完成数学作业第10页',
    'images': []
}

response = session.post('http://localhost:5001/api/simulate', json=simulate_data)
print(f"   状态: {response.status_code}")
result = response.json()
print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if result.get('success'):
    print(f"\n   ✅ 任务创建成功!")
    print(f"   pending_id: {result.get('pending_id')}")
else:
    print(f"\n   ❌ 任务创建失败")
    print(f"   错误: {result.get('error')}")
