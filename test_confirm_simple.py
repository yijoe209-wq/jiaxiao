#!/usr/bin/env python3
"""简单测试确认页面"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    print("登录...")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("添加学生...")
    page.goto('http://localhost:5001/students')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#nameInput', '测试学生A')
    page.select_option('select#gradeInput', '一年级')
    page.locator('button:has-text("添加学生")').click()
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # 获取学生ID
    student_id = page.evaluate('''
        () => {
            const deleteBtn = document.querySelector('.delete-btn');
            return deleteBtn ? deleteBtn.getAttribute('onclick').match(/'([^']+)'/)[1] : null;
        }
    ''')

    print(f"学生ID: {student_id}")

    # 访问确认页面
    print("访问确认页面...")
    pending_id = "c3f00d0a-e43d-4d17-bb7a-593ecd79eca4"
    page.goto(f'http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    page.screenshot(path='confirm_simple.png')
    print("截图: confirm_simple.png")

    # 检查任务描述
    task_desc = page.locator('.task-card p.text-gray-900').first
    if task_desc.count() > 0:
        description_text = task_desc.inner_text()
        print(f"任务描述: {description_text}")

        if description_text == '无描述':
            print("❌ 错误：显示'无描述'")
        else:
            print("✅ 正常显示任务描述")
    else:
        print("❌ 未找到任务描述")

    browser.close()
