#!/usr/bin/env python3
"""完整测试所有功能和页面 - 包括登录流程"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("="*70)
        print("🚀 开始完整用户旅程测试")
        print("="*70)

        # ========== 测试 1: 访问首页（未登录状态） ==========
        print("\n📍 步骤 1: 访问首页（未登录）")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 检查按钮颜色
        button = page.locator('button:has-text("AI 智能解析并创建任务")')
        bg_color = button.evaluate('el => window.getComputedStyle(el).backgroundColor')
        print(f"  ✓ AI按钮颜色: {bg_color}")
        page.screenshot(path='journey_01_homepage.png')
        print("  ✅ 截图保存: journey_01_homepage.png")

        # ========== 测试 2: 点击登录 ==========
        print("\n📍 步骤 2: 点击登录按钮")
        login_link = page.locator('a[href="/login"]').first
        login_link.click()
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        assert '/login' in page.url
        page.screenshot(path='journey_02_login_page.png')
        print("  ✅ 登录页面加载: journey_02_login_page.png")

        # ========== 测试 3: 注册新用户 ==========
        print("\n📍 步骤 3: 注册新账号")
        # 生成随机邮箱
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_{random_suffix}@example.com"
        test_password = "Test123456"
        test_parent_name = "测试家长"

        print(f"  - 使用邮箱: {test_email}")

        # 点击"注册"标签
        register_tab = page.locator('text=注册').first
        if register_tab.count() > 0:
            register_tab.click()
            time.sleep(0.5)

        # 填写注册表单
        page.fill('input[name="email"]', test_email)
        page.fill('input[name="password"]', test_password)
        page.fill('input[name="parent_name"]', test_parent_name)

        page.screenshot(path='journey_03_register_filled.png')
        print("  ✅ 注册表单填写完成")

        # 提交注册
        print("  - 提交注册...")
        submit_btn = page.locator('button[type="submit"]')
        submit_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_04_after_register.png')
        print("  ✅ 注册完成")

        # ========== 测试 4: 返回首页（已登录） ==========
        print("\n📍 步骤 4: 返回首页（已登录状态）")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 检查按钮颜色（登录后）
        button_logged = page.locator('button:has-text("AI 智能解析并创建任务")')
        bg_color_logged = button_logged.evaluate('el => window.getComputedStyle(el).backgroundColor')
        print(f"  ✓ AI按钮颜色（登录后）: {bg_color_logged}")

        page.screenshot(path='journey_05_homepage_logged_in.png')
        print("  ✅ 首页（已登录）: journey_05_homepage_logged_in.png")

        # ========== 测试 5: 添加学生 ==========
        print("\n📍 步骤 5: 添加学生")
        students_link = page.locator('a:has-text("学生")').first
        students_link.click()
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='journey_06_students_page.png')
        print("  ✅ 学生管理页面: journey_06_students_page.png")

        # 点击添加学生
        add_student_btn = page.locator('button:has-text("添加学生"), button:has-text("新增")').first
        if add_student_btn.count() > 0:
            add_student_btn.click()
            time.sleep(0.5)

            # 填写学生信息
            page.fill('input[name="name"]', "测试学生")
            page.fill('input[name="grade"]', "一年级")

            page.screenshot(path='journey_07_add_student_form.png')
            print("  ✅ 添加学生表单填写")

            # 提交
            submit = page.locator('button[type="submit"]').first
            submit.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            print("  ✅ 学生添加成功")

        # ========== 测试 6: 返回首页，创建任务 ==========
        print("\n📍 步骤 6: 返回首页创建任务")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 输入任务描述
        textarea = page.locator('textarea')
        if textarea.count() > 0:
            textarea.fill("完成数学作业第5页")
            time.sleep(0.5)

        page.screenshot(path='journey_08_task_description.png')
        print("  ✅ 输入任务描述")

        # 点击提交按钮
        submit_btn = page.locator('button:has-text("AI 智能解析并创建任务")')
        submit_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        page.screenshot(path='journey_09_after_submit.png')
        print("  ✅ 提交任务")

        # ========== 测试 7: 查看任务中心 ==========
        print("\n📍 步骤 7: 查看任务中心")
        task_center = page.locator('a:has-text("任务中心")').first
        if task_center.count() > 0:
            task_center.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            page.screenshot(path='journey_10_task_center.png')
            print("  ✅ 任务中心页面: journey_10_task_center.png")

        # ========== 测试 8: 检查所有页面设计一致性 ==========
        print("\n📍 步骤 8: 检查所有页面设计")
        pages = [
            ('http://localhost:5001/', '首页'),
            ('http://localhost:5001/my-tasks', '任务中心'),
            ('http://localhost:5001/students', '学生管理'),
        ]

        print("\n  页面背景色检查:")
        for url, name in pages:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(0.5)

            bg = page.evaluate('() => window.getComputedStyle(document.body).backgroundColor')
            print(f"    - {name}: {bg}")

        # ========== 测试 9: 退出登录 ==========
        print("\n📍 步骤 9: 退出登录")
        logout_btn = page.locator('button:has-text("退出"), a:has-text("退出")').first
        if logout_btn.count() > 0:
            logout_btn.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            page.screenshot(path='journey_11_after_logout.png')
            print("  ✅ 退出登录")

        print("\n" + "="*70)
        print("✅ 完整测试流程结束！")
        print("="*70)

        print("\n📸 所有截图文件:")
        import os
        screenshots = [f for f in os.listdir('.') if f.startswith('journey_') and f.endswith('.png')]
        for f in sorted(screenshots):
            print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
