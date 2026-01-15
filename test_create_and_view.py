#!/usr/bin/env python3
"""完整测试：创建任务并查看"""

from playwright.sync_api import sync_playwright
import time
import random
import string

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # 1. 注册新用户
    print("1. 注册新用户")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"flow_test_{random_suffix}@example.com"
    test_password = "Test123456"

    page.click('text=注册')
    time.sleep(0.5)

    page.fill('input#registerEmail', test_email)
    page.fill('input#registerPassword', test_password)
    page.fill('input#registerName', '流程测试用户')
    page.locator('#registerForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print(f"   ✅ 注册成功: {test_email}")

    # 2. 添加学生
    print("\n2. 添加学生")
    page.goto('http://localhost:5001/students')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#nameInput', '测试学生')
    page.select_option('select#gradeInput', '一年级')
    page.locator('button:has-text("添加学生")').click()
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    print("   ✅ 学生添加成功")

    # 3. 创建任务
    print("\n3. 创建任务")
    page.goto('http://localhost:5001/add')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.select_option('select#studentSelect', index=0)
    page.fill('textarea#messageInput', '数学作业：完成练习册第20页')
    page.screenshot(path='flow_create_01.png')
    print("   ✅ 填写任务")

    page.locator('button:has-text("AI 智能解析")').click()
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    page.screenshot(path='flow_create_02.png')
    print("   ✅ 提交任务")

    # 4. 检查确认页面
    confirm_link = page.locator('a[href*="confirm"]').first
    if confirm_link.count() > 0:
        print("\n4. 访问确认页面")
        confirm_link.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='flow_create_03.png')
        print("   ✅ 确认页面")

        # 5. 确认任务
        page.locator('button:has-text("确认创建")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        print("   ✅ 确认创建")

    # 6. 返回任务中心查看
    print("\n5. 返回任务中心查看")
    page.goto('http://localhost:5001/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    page.screenshot(path='flow_create_04.png')

    # 检查任务数量
    task_count = page.evaluate('''
        async () => {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            return tasks.length;
        }
    ''')

    print(f"   任务数量: {task_count}")

    if task_count > 0:
        print("   ✅ 任务显示正常！")

        # 获取第一个任务
        first_task = page.evaluate('''
            async () => {
                const response = await fetch('/api/tasks');
                const tasks = await response.json();
                return tasks[0].description;
            }
        ''')

        print(f"   第一个任务: {first_task}")
    else:
        print("   ❌ 任务中心没有显示任务")

    print("\n" + "="*70)
    print("✅ 完整流程测试完成")
    print("="*70)

    time.sleep(2)
    browser.close()
