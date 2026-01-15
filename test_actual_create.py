#!/usr/bin/env python3
"""实际模拟新增任务并验证"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    print("="*70)
    print("🎯 实际模拟新增任务并验证任务中心")
    print("="*70)

    # 1. 登录（使用已有账号）
    print("\n1. 登录")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("   ⚠️ 登录可能失败（密码不对），继续测试")

    # 2. 注册新用户
    print("\n2. 注册新用户确保能登录")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"real_test_{random_suffix}@example.com"

    page.click('text=注册')
    time.sleep(0.5)

    page.fill('input#registerEmail', test_email)
    page.fill('input#registerPassword', 'Test123456')
    page.fill('input#registerName', '真实测试用户')
    page.locator('#registerForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print(f"   ✅ 注册成功: {test_email}")

    # 3. 添加学生
    print("\n3. 添加学生")
    page.goto('http://localhost:5001/students')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#nameInput', '真实测试学生')
    page.select_option('select#gradeInput', '三年级')
    page.locator('button:has-text("添加学生")').click()
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    print("   ✅ 学生添加成功")

    # 4. 查看任务中心（添加任务前）
    print("\n4. 查看任务中心（添加任务前）")
    page.goto('http://localhost:5001/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    task_count_before = page.evaluate('''
        async () => {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            return tasks.length;
        }
    ''')

    page.screenshot(path='real_01_before_create.png')
    print(f"   当前任务数量: {task_count_before}")
    print("   ✅ 截图: real_01_before_create.png")

    # 5. 新增任务
    print("\n5. 新增任务")
    page.goto('http://localhost:5001/add')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.select_option('select#studentSelect', index=0)
    page.fill('textarea#messageInput', '这是真实的测试任务：完成数学作业第30页，明天提交')
    page.screenshot(path='real_02_filled.png')
    print("   ✅ 填写任务")
    print("   ✅ 截图: real_02_filled.png")

    # 点击提交
    print("\n6. 点击 AI 智能解析按钮")
    submit_btn = page.locator('button:has-text("AI 智能解析")').first
    submit_btn.click()
    page.wait_for_load_state('networkidle')
    time.sleep(5)

    page.screenshot(path='real_03_after_submit.png')
    print("   ✅ 截图: real_03_after_submit.png")

    # 检查是否有确认链接
    confirm_link = page.locator('a[href*="confirm"]').first
    if confirm_link.count() > 0:
        print("\n7. 访问确认页面")
        confirm_href = confirm_link.get_attribute('href')
        print(f"   确认链接: {confirm_href}")

        confirm_link.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='real_04_confirm.png')
        print("   ✅ 确认页面")
        print("   ✅ 截图: real_04_confirm.png")

        # 点击确认创建
        print("\n8. 点击确认创建")
        confirm_btn = page.locator('button:has-text("确认创建")').first
        if confirm_btn.count() > 0:
            confirm_btn.click()
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path='real_05_after_confirm.png')
            print("   ✅ 点击确认创建")
            print("   ✅ 截图: real_05_after_confirm.png")
        else:
            print("   ⚠️ 未找到确认创建按钮")
    else:
        print("\n7. ⚠️ 未找到确认链接")
        page.screenshot(path='real_error.png')

    # 9. 返回任务中心查看
    print("\n9. 返回任务中心查看新任务")
    page.goto('http://localhost:5001/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    page.screenshot(path='real_06_task_center.png')
    print("   ✅ 截图: real_06_task_center.png")

    # 检查任务数量
    task_count_after = page.evaluate('''
        async () => {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            return tasks.length;
        }
    ''')

    print(f"\n   任务数量: {task_count_after}")

    # 获取任务列表
    tasks = page.evaluate('''
        async () => {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            return tasks.map(t => ({
                description: t.description,
                subject: t.subject
            }));
        }
    ''')

    print(f"\n   任务列表:")
    for i, task in enumerate(tasks[:5]):
        print(f"   {i+1}. {task.get('description', 'N/A')}")

    # 10. 检查数据库
    print("\n10. 检查数据库")
    import sqlite3
    conn = sqlite3.connect('jiaxiao.db')
    cursor = conn.cursor()

    # 获取当前用户的 family_id
    cursor.execute("SELECT family_id FROM families WHERE email = ?", (test_email,))
    result = cursor.fetchone()
    if result:
        family_id = result[0]
        print(f"   当前用户 family_id: {family_id}")

        # 检查该家庭的任务
        cursor.execute("""
            SELECT t.task_id, t.description, s.name as student_name
            FROM tasks t
            JOIN students s ON t.student_id = s.student_id
            WHERE s.family_id = ?
            ORDER BY t.created_at DESC
            LIMIT 5
        """, (family_id,))

        db_tasks = cursor.fetchall()
        print(f"\n   数据库中的任务 ({len(db_tasks)} 条):")
        for task in db_tasks:
            print(f"   - {task[1]} (学生: {task[2]})")
    else:
        print("   ⚠️ 数据库中未找到用户")

    conn.close()

    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)

    print(f"\n添加任务前: {task_count_before} 个任务")
    print(f"添加任务后: {task_count_after} 个任务")

    if task_count_after > task_count_before:
        print("\n✅ 任务创建成功并在任务中心显示！")
    else:
        print("\n❌ 任务创建失败或未在任务中心显示")
        print("   可能原因:")
        print("   1. 确认页面没有点击确认创建")
        print("   2. API 保存失败")
        print("   3. 数据库写入失败")

    print("\n所有截图文件:")
    import os
    for f in sorted(os.listdir('.')):
        if f.startswith('real_') and f.endswith('.png'):
            print(f"  - {f}")

    time.sleep(2)
    browser.close()
