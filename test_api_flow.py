"""
API 测试完整流程
"""
import requests
import json

base_url = "https://edu-track.zeabur.app"

# 1. 注册新用户
print("\n1. 注册新用户")
register_data = {
    "email": "flow_test@example.com",
    "password": "test123456",
    "parent_name": "流程测试"
}
r = requests.post(f"{base_url}/api/register", json=register_data)
print(f"状态: {r.status_code}")
print(f"响应: {r.text}")

# 2. 添加学生
print("\n2. 添加学生")
add_student_data = {
    "name": "测试学生小明",
    "grade": "五年级",
    "class_name": "3班"
}
r = requests.post(f"{base_url}/api/students", json=add_student_data)
print(f"状态: {r.status_code}")
result = r.json()
student_id = result.get('student_id')
print(f"学生ID: {student_id}")

# 3. 创建待确认任务
print("\n3. 创建任务（模拟 AI 解析）")
import uuid
pending_id = str(uuid.uuid4())
task_data = {
    "type": "single",
    "description": "英语：完成第3单元单词练习",
    "subject": "英语",
    "task_type": "书写",
    "details": "明天前提交"
}
from datetime import datetime, timedelta

# 这里需要直接创建任务到数据库，但我们要测试完整流程
print("跳过 AI 解析，直接在任务中心查询")

# 4. 获取任务列表
print("\n4. 获取任务列表")
r = requests.get(f"{base_url}/api/tasks")
print(f"状态: {r.status_code}")
tasks = r.json()
print(f"任务数量: {len(tasks)}")

# 5. 按学生筛选（如果有任务）
if len(tasks) > 0:
    print("\n5. 任务内容示例")
    for task in tasks[:3]:
        print(f"   - {task.get('description', 'N/A')}")
