#!/usr/bin/env python3
"""调试任务创建"""

from playwright.sync_api import sync_playwright
import time
import random
import string

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # 监听控制台
    console_msgs = []
    def handle_console(msg):
        console_msgs.append({
            'type': msg.type,
            'text': msg.text
        })
        if msg.type == 'error':
            print(f"  [错误] {msg.text}")

    page.on('console', handle_console)

    # 注册
    print("1. 注册并登录")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"debug_{random_suffix}@example.com"

    page.click('text=注册')
    time.sleep(0.5)

    page.fill('input#registerEmail', test_email)
    page.fill('input#registerPassword', 'Test123456')
    page.fill('input#registerName', '调试用户')
    page.locator('#registerForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print(f"   ✅ 注册: {test_email}")

    # 检查登录状态
    print("\n2. 检查登录状态")
    auth_check = page.evaluate('''
        async () => {
            try {
                const response = await fetch('/api/auth/check');
                const result = await response.json();
                return result;
            } catch (e) {
                return { error: e.message };
            }
        }
    ''')

    print(f"   登录状态: {auth_check}")

    # 添加学生
    print("\n3. 添加学生")
    page.goto('http://localhost:5001/students')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#nameInput', '调试学生')
    page.select_option('select#gradeInput', '二年级')
    page.locator('button:has-text("添加学生")').click()
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    print("   ✅ 学生添加成功")

    # 创建任务
    print("\n4. 创建任务")
    page.goto('http://localhost:5001/add')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.select_option('select#studentSelect', index=0)
    page.fill('textarea#messageInput', '测试任务：完成数学作业')
    page.screenshot(path='debug_01_before_click.png')
    print("   ✅ 填写任务")

    # 点击按钮
    print("\n5. 点击 AI 智能解析按钮")
    submit_btn = page.locator('button:has-text("AI 智能解析")').first

    # 检查按钮是否可点击
    is_disabled = submit_btn.is_disabled()
    print(f"   按钮禁用状态: {is_disabled}")

    # 检查登录遮罩
    has_overlay = page.evaluate('''
        () => {
            const overlay = document.getElementById('loginOverlay');
            return overlay && overlay.classList.contains('show');
        }
    ''')
    print(f"   登录遮罩显示: {has_overlay}")

    # 点击
    submit_btn.click()
    print("   ✅ 已点击按钮")
    time.sleep(5)

    page.screenshot(path='debug_02_after_click.png')

    # 检查页面状态
    print("\n6. 检查页面状态")

    # 检查是否有结果
    result_div = page.locator('#result').first
    if result_div.count() > 0:
        is_hidden = result_div.is_hidden()
        print(f"   结果区域隐藏: {is_hidden}")
    else:
        print("   未找到结果区域")

    # 检查确认链接
    confirm_links = page.locator('a[href*="confirm"]').all()
    print(f"   确认链接数量: {len(confirm_links)}")

    # 检查控制台错误
    print(f"\n7. 控制台消息 ({len(console_msgs)} 条):")
    for msg in console_msgs[:10]:
        if msg['type'] in ['error', 'warning']:
            print(f"   [{msg['type']}] {msg['text']}")

    page.screenshot(path='debug_03_final.png')

    print("\n所有截图:")
    import os
    for f in os.listdir('.'):
        if f.startswith('debug_') and f.endswith('.png'):
            print(f"  - {f}")

    time.sleep(2)
    browser.close()
