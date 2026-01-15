#!/usr/bin/env python3
"""测试浏览器登录和 session"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    print("1. 访问登录页面")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # 注册新用户来测试
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"test_{random_suffix}@example.com"
    test_password = "Test123456"

    print(f"2. 注册新用户: {test_email}")
    page.click('text=注册')
    time.sleep(0.5)

    page.fill('input#registerEmail', test_email)
    page.fill('input#registerPassword', test_password)
    page.fill('input#registerName', '测试用户')
    page.locator('#registerForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("3. 检查登录后的 cookies")
    cookies = page.context.cookies()
    print(f"   Cookies: {cookies}")

    print("4. 访问任务中心")
    page.goto('http://localhost:5001/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    # 检查任务数量
    task_count = page.evaluate('''
        async () => {
            try {
                const response = await fetch('/api/tasks');
                const tasks = await response.json();
                return tasks.length;
            } catch (e) {
                return -1;
            }
        }
    ''')

    print(f"   任务数量: {task_count}")

    if task_count > 10:
        print("   ⚠️ 返回了太多任务，session 没有正确工作")
    else:
        print("   ✅ 任务数量正常，session 工作正常")

    page.screenshot(path='test_login_result.png')
    print("   截图: test_login_result.png")

    input("\n按回车关闭...")
    browser.close()
