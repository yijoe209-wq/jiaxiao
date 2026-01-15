#!/usr/bin/env python3
"""测试登录和 session"""

import requests
import json

session = requests.Session()

# 登录
login_data = {
    'email': 'alves820@live.cn',
    'password': 'test123'
}

print("1. 登录...")
response = session.post('http://localhost:5001/api/login', json=login_data)
print(f"   状态码: {response.status_code}")
result = response.json()
print(f"   响应: {result}")

# 检查 cookies
print(f"\n2. Cookies:")
print(f"   {session.cookies.get_dict()}")

# 获取任务
print("\n3. 获取任务...")
response = session.get('http://localhost:5001/api/tasks')
print(f"   状态码: {response.status_code}")
tasks = response.json()
print(f"   任务数量: {len(tasks)}")

if len(tasks) < 50:
    print(f"\n   前3个任务:")
    for i, task in enumerate(tasks[:3]):
        print(f"   {i+1}. {task.get('description', 'N/A')}")
else:
    print(f"   ⚠️ 返回了太多任务（{len(tasks)}个），可能没有按家庭过滤")
