#!/usr/bin/env python3
"""调试确认页面"""

from playwright.sync_api import sync_playwright
import time

student_id = "b7e807d6-04a6-49da-945d-cdd7cc11e1e1"
pending_id = "5fd4667f-8c99-4e50-8ae1-96c45d6dc50d"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # 监听控制台
    console_msgs = []
    def handle_console(msg):
        if msg.type in ['error', 'warning']:
            console_msgs.append(f"[{msg.type}] {msg.text}")
            print(f"  {msg.type}: {msg.text}")

    page.on('console', handle_console)

    print("登录...")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("\n访问确认页面...")
    confirm_url = f'http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}'
    page.goto(confirm_url)
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    # 检查 taskData 变量
    task_data = page.evaluate('''
        () => {
            return {
                hasTaskData: typeof taskData !== 'undefined',
                taskData: typeof taskData !== 'undefined' ? taskData : null,
                hasStudentData: typeof studentData !== 'undefined',
                studentData: typeof studentData !== 'undefined' ? studentData : null
            };
        }
    ''')

    print(f"\n数据状态:")
    print(f"  hasTaskData: {task_data['hasTaskData']}")
    print(f"  hasStudentData: {task_data['hasStudentData']}")

    if task_data['taskData']:
        print(f"\ntaskData:")
        print(f"  type: {task_data['taskData'].get('type')}")
        print(f"  has raw_text: {'raw_text' in task_data['taskData']}")
        print(f"  has task: {'task' in task_data['taskData']}")

    print(f"\n控制台错误/警告 ({len(console_msgs)} 条):")
    for msg in console_msgs:
        print(f"  {msg}")

    page.screenshot(path='confirm_debug.png')
    print(f"\n截图: confirm_debug.png")

    time.sleep(2)
    browser.close()
