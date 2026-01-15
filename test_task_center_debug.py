#!/usr/bin/env python3
"""调试任务中心页面"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # 监听控制台消息
    console_messages = []
    def handle_console(msg):
        console_messages.append({
            'type': msg.type,
            'text': msg.text
        })
        if msg.type == 'error':
            print(f"  [控制台错误] {msg.text}")

    page.on('console', handle_console)

    print("登录并访问任务中心...")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    page.goto('http://localhost:5001/my-tasks')
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    # 获取 allTasks 变量
    all_tasks = page.evaluate('() => typeof allTasks !== "undefined" ? allTasks : null')
    print(f"\nallTasks: {all_tasks}")

    if all_tasks:
        print(f"任务数量: {len(all_tasks)}")
        if len(all_tasks) > 0:
            print(f"第一个任务: {all_tasks[0]}")
    else:
        print("allTasks 未定义")

    # 获取 allStudents 变量
    all_students = page.evaluate('() => typeof allStudents !== "undefined" ? allStudents : null')
    print(f"\nallStudents: {all_students}")

    if all_students:
        print(f"学生数量: {len(all_students)}")
    else:
        print("allStudents 未定义")

    # 检查筛选状态
    filters = page.evaluate('''
        () => {
            return {
                student: document.getElementById('studentFilter')?.value,
                subject: document.getElementById('subjectFilter')?.value,
                status: document.getElementById('statusFilter')?.value,
                quick: typeof currentQuickFilter !== 'undefined' ? currentQuickFilter : 'undefined'
            };
        }
    ''')

    print(f"\n筛选状态: {filters}")

    # 打印所有控制台消息
    print(f"\n控制台消息 ({len(console_messages)} 条):")
    for msg in console_messages[:10]:  # 只显示前10条
        print(f"  [{msg['type']}] {msg['text']}")

    page.screenshot(path='task_center_debug.png')
    print(f"\n截图: task_center_debug.png")

    time.sleep(2)
    browser.close()
