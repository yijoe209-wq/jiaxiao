#!/usr/bin/env python3
"""测试任务中心 API"""

import requests
import json

# 登录获取 session
session = requests.Session()

print("1. 登录...")
login_data = {
    'email': 'alves820@live.cn',
    'password': 'test123'
}
response = session.post('http://localhost:5001/api/login', json=login_data)
print(f"   登录响应: {response.status_code}")
print(f"   Cookies: {session.cookies.get_dict()}")

print("\n2. 获取任务列表...")
response = session.get('http://localhost:5001/api/tasks')
print(f"   状态码: {response.status_code}")

if response.status_code == 200:
    tasks = response.json()
    print(f"   任务数量: {len(tasks)}")

    if len(tasks) > 0:
        print("\n   前3个任务:")
        for i, task in enumerate(tasks[:3]):
            print(f"   {i+1}. {task.get('description', '无描述')}")
            print(f"      学生ID: {task.get('student_id')}")
            print(f"      完成: {task.get('is_completed')}")
    else:
        print("   ⚠️ 任务列表为空")
else:
    print(f"   错误: {response.text}")

print("\n3. 检查 session 信息...")
response = session.get('http://localhost:5001/api/auth/check')
print(f"   认证状态: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   已认证: {data.get('authenticated')}")
    print(f"   用户ID: {data.get('user_id')}")
