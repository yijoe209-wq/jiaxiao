#!/usr/bin/env python3
"""创建测试任务"""

import requests
import json

# 登录
session = requests.Session()
login_data = {
    'email': 'alves820@live.cn',
    'password': 'test123'
}
session.post('http://localhost:5001/api/login', json=login_data)

# 创建任务
task_data = {
    'message': '完成数学作业第5页，明天截止',
    'images': []
}

response = session.post('http://localhost:5001/api/simulate', json=task_data)
result = response.json()

print("创建任务结果:")
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success'):
    pending_id = result.get('pending_id')
    print(f"\n✅ 任务创建成功")
    print(f"pending_id: {pending_id}")
    print(f"\n访问确认页面:")
    print(f"http://localhost:5001/confirm?pending_id={pending_id}&student_id=b7e807d6-04a6-49da-945d-cdd7cc11e1e1")
