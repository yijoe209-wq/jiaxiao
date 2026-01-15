#!/usr/bin/env python3
"""测试注册 API 返回的 cookies"""

import requests
import random
import string

random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
test_email = f"cookie_test_{random_suffix}@example.com"

# 创建 session
session = requests.Session()

# 注册
register_data = {
    'email': test_email,
    'password': 'Test123456',
    'parent_name': 'Cookie测试用户'
}

print("1. 注册...")
response = session.post('http://localhost:5001/api/register', json=register_data)
print(f"   状态码: {response.status_code}")
result = response.json()
print(f"   响应: {result}")

print(f"\n2. Cookies:")
for cookie in session.cookies:
    print(f"   {cookie.name} = {cookie.value[:50]}...")
    print(f"      domain: {cookie.domain}")
    print(f"      path: {cookie.path}")

print(f"\n3. 检查登录状态...")
response = session.get('http://localhost:5001/api/auth/check')
auth_result = response.json()
print(f"   loggedIn: {auth_result.get('loggedIn')}")

if auth_result.get('loggedIn'):
    print(f"   user: {auth_result.get('user')}")
else:
    print("   ❌ 未登录！session 没有生效")
