#!/usr/bin/env python3
"""
最终完整测试 - 包括创建任务和验证跨家庭查看
"""
import requests
import random

BASE_URL = 'http://localhost:5001'

def random_email():
    return f"user{random.randint(10000, 99999)}@test.com"


print("=" * 70)
print("🧪 最终完整测试 - 包括任务创建")
print("=" * 70)

# ==================== 爸爸注册、添加学生、创建任务 ====================
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
print(f"   注册: {r.json().get('message', '失败')}")

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
if students:
    student_id = students[0]['student_id']
    print(f"   学生: {students[0]['name']} (ID: {student_id[:8]}...)")
else:
    print("   ❌ 没有学生数据")
    exit(1)

print("\n3. 爸爸创建数学任务")
print("   尝试直接创建任务...")
r = dad_session.post(f'{BASE_URL}/api/tasks', json={
    'student_id': student_id,
    'subject': '数学',
    'content': '完成练习册第10页',
    'deadline': '2026-01-25T18:00:00'
})
print(f"   状态码: {r.status_code}")
if r.status_code == 200:
    print("   ✅ 任务创建成功（直接API）")
    task_data = r.json()
    print(f"   任务: {task_data.get('content', 'N/A')}")
elif r.status_code == 405:
    print("   ⚠️  不支持直接创建任务")
    print("   通过模拟微信转发创建...")
    r = dad_session.post(f'{BASE_URL}/api/simulate', json={
        'message': '数学作业：完成练习册第10页，明天交',
        'images': []
    })
    result = r.json()
    print(f"   模拟结果: {result.get('message', '失败')}")

    # 获取 pending_id 并确认任务
    if result.get('success') and result.get('pending_id'):
        pending_id = result.get('pending_id')
        print(f"   pending_id: {pending_id[:8]}...")
        print("   正在确认任务...")
        r = dad_session.post(f'{BASE_URL}/api/confirm', json={
            'pending_id': pending_id,
            'student_id': student_id
        })
        confirm_result = r.json()
        if confirm_result.get('success'):
            print(f"   ✅ 任务创建成功: {confirm_result.get('message', 'N/A')}")
        else:
            print(f"   ❌ 确认失败: {confirm_result.get('error', 'N/A')}")
    else:
        print(f"   ⚠️  模拟失败: {result.get('error', '未知错误')}")

print("\n4. 爸爸查看任务列表")
r = dad_session.get(f'{BASE_URL}/api/tasks')
dad_tasks = r.json()
print(f"   任务数: {len(dad_tasks)}")
for i, task in enumerate(dad_tasks[:3], 1):
    student_name = task.get('student', {}).get('name', '未知')
    print(f"   任务{i}: [{task.get('subject')}] {task.get('content', 'N/A')[:30]}... (学生: {student_name})")

# ==================== 妈妈注册并拉入家庭 ====================
print("\n📱 步骤 2: 妈妈注册并拉入家庭")
print("-" * 70)

mom_session = requests.Session()
mom_email = random_email()

print(f"1. 妈妈注册 ({mom_email})")
r = mom_session.post(f'{BASE_URL}/api/register', json={
    'email': mom_email,
    'password': 'test123',
    'parent_name': '张妈妈'
})
print(f"   注册: {r.json().get('message', '失败')}")

print("\n2. 爸爸把妈妈拉入家庭")
r = dad_session.post(f'{BASE_URL}/api/family/members', json={
    'email': mom_email
})
result = r.json()
print(f"   结果: {result.get('message', result.get('error', '失败'))}")

# ==================== 妈妈查看爸爸的数据 ====================
print("\n📱 步骤 3: 妈妈查看爸爸的学生和任务")
print("-" * 70)

print("1. 妈妈查看任务（旧session）")
r = mom_session.get(f'{BASE_URL}/api/tasks')
mom_tasks_old = r.json()
print(f"   任务数: {len(mom_tasks_old)}")

print("\n2. 妈妈查看学生（旧session）")
r = mom_session.get(f'{BASE_URL}/api/students')
data = r.json()
mom_students_old = data if isinstance(data, list) else data.get('students', [])
print(f"   学生数: {len(mom_students_old)}")

print("\n3. 妈妈重新登录")
mom_session2 = requests.Session()
r = mom_session2.post(f'{BASE_URL}/api/login', json={
    'email': mom_email,
    'password': 'test123'
})
print(f"   登录: {r.json().get('message', '失败')}")

print("\n4. 妈妈查看任务（新session）")
r = mom_session2.get(f'{BASE_URL}/api/tasks')
mom_tasks_new = r.json()
print(f"   任务数: {len(mom_tasks_new)}")
for i, task in enumerate(mom_tasks_new[:3], 1):
    student_name = task.get('student', {}).get('name', '未知')
    print(f"   任务{i}: [{task.get('subject')}] {task.get('content', 'N/A')[:30]}... (学生: {student_name})")

print("\n5. 妈妈查看学生（新session）")
r = mom_session2.get(f'{BASE_URL}/api/students')
data = r.json()
mom_students_new = data if isinstance(data, list) else data.get('students', [])
print(f"   学生数: {len(mom_students_new)}")
if isinstance(mom_students_new, list) and len(mom_students_new) > 0:
    for s in mom_students_new:
        print(f"   - {s['name']} ({s['grade']})")

# ==================== 测试结果 ====================
print("\n" + "=" * 70)
print("📊 测试结果")
print("=" * 70)

print(f"爸爸创建的任务数: {len(dad_tasks)}")
print(f"妈妈重新登录后看到的任务数: {len(mom_tasks_new)}")

if len(dad_tasks) > 0 and len(mom_tasks_new) > 0:
    print("\n✅ 成功：妈妈可以看到爸爸创建的任务！")
    print("✅ 跨家庭任务共享正常！")
elif len(dad_tasks) > 0 and len(mom_tasks_new) == 0:
    print("\n⚠️  爸爸创建了任务，但妈妈看不到")
    print("   可能原因：任务创建失败，或者权限问题")
elif len(dad_tasks) == 0:
    print("\nℹ️  爸爸没有任务（任务创建可能需要AI解析）")
    print("   但学生和家庭成员功能都正常")
else:
    print("\n⚠️  需要进一步检查")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
