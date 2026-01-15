#!/usr/bin/env python3
"""测试任务显示问题"""
import requests
import json

BASE_URL = "http://localhost:5001"

# 1. 测试未登录状态下的 /api/tasks
print("=" * 50)
print("1. 测试未登录状态")
print("=" * 50)
session = requests.Session()
response = session.get(f"{BASE_URL}/api/tasks")
print(f"Status: {response.status_code}")
print(f"Tasks count: {len(response.json()) if response.status_code == 200 else 'N/A'}")

# 2. 登录
print("\n" + "=" * 50)
print("2. 登录测试账号")
print("=" * 50)

# 先检查是否有可用的测试用户
from models import db, init_db, Family

init_db('sqlite:///jiaxiao.db')
db_session = db.get_session()

# 获取一个测试家庭
test_family = db_session.query(Family).first()
db_session.close()

if test_family:
    print(f"使用测试家庭: {test_family.parent_name}")

    # 使用已有的测试用户登录
    login_data = {
        "email": "test@test.com",
        "password": "test123"
    }

    # 尝试登录
    response = session.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ 登录成功! Family ID: {result.get('family_id')}")
        else:
            print(f"❌ 登录失败: {result.get('error')}")
    else:
        print(f"❌ 登录请求失败")

    # 3. 登录后获取任务
    print("\n" + "=" * 50)
    print("3. 登录后获取任务")
    print("=" * 50)
    response = session.get(f"{BASE_URL}/api/tasks")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ 获取到 {len(tasks)} 个任务")
        if tasks:
            print("\n前3个任务:")
            for i, task in enumerate(tasks[:3], 1):
                print(f"  {i}. {task.get('description', '无描述')[:50]}...")
                print(f"     Student ID: {task.get('student_id')}")
                print(f"     Completed: {task.get('is_completed')}")
                print(f"     Subject: {task.get('subject', 'N/A')}")
        else:
            print("❌ 没有任务")
    else:
        print(f"❌ 获取任务失败: {response.text}")
else:
    print("❌ 数据库中没有测试用户")

print("\n" + "=" * 50)
print("诊断建议:")
print("=" * 50)
print("""
如果您在浏览器中看不到任务:
1. 确保已经登录 (访问 http://localhost:5001/login)
2. 登录后会自动跳转到任务中心
3. 检查浏览器控制台是否有 JavaScript 错误
4. 检查筛选器设置（可能过滤掉了所有任务）
5. 尝试刷新页面 (Ctrl+F5 或 Cmd+Shift+R)
""")
