#!/usr/bin/env python3
"""完整功能测试 - 正确处理登录流程"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("="*70)
        print("🚀 完整功能测试")
        print("="*70)

        # ========== 测试 1: 首页（未登录状态） ==========
        print("\n✅ 步骤 1: 访问首页（未登录）")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='test_01_home_unlogged.png')
        print("  - 首页加载完成（有登录遮罩层）")

        # ========== 测试 2: 注册新账号 ==========
        print("\n✅ 步骤 2: 注册账号")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='test_02_login_page.png')

        # 点击注册 tab
        register_tab = page.locator('div.tab:has-text("注册")')
        register_tab.click()
        time.sleep(0.5)
        page.screenshot(path='test_03_register_tab.png')

        # 填写注册表单
        import random
        import string
        random_email = f"test{''.join(random.choices(string.digits, k=6))}@test.com"

        page.fill('input#registerEmail', random_email)
        page.fill('input#registerPassword', 'Test123456')
        page.fill('input#registerName', '测试家长')
        page.screenshot(path='test_04_register_filled.png')
        print(f"  - 填写注册表单: {random_email}")

        # 点击注册按钮（精确选择）
        register_btn = page.locator('#registerForm button[type="submit"]')
        register_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path='test_05_after_register.png')
        print("  - 注册提交完成")

        # ========== 测试 3: 首页（已登录状态） ==========
        print("\n✅ 步骤 3: 首页（已登录）")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='test_06_home_logged.png')
        print("  - 首页加载完成（已登录）")

        # ========== 测试 4: 输入任务描述 ==========
        print("\n✅ 步骤 4: 测试任务输入")
        textarea = page.locator('textarea')
        if textarea.count() > 0:
            textarea.fill("完成数学作业第5页")
            time.sleep(0.5)
            page.screenshot(path='test_07_text_input.png')
            print("  - 任务描述输入完成")

        # ========== 测试 5: 点击AI按钮 ==========
        print("\n✅ 步骤 5: 测试AI解析按钮")
        ai_btn = page.locator('button:has-text("AI 智能解析并创建任务")')
        if ai_btn.count() > 0:
            ai_btn.click()
            time.sleep(3)
            page.screenshot(path='test_08_after_ai.png')
            print("  - AI按钮点击完成")

        # ========== 测试 6: 任务中心 ==========
        print("\n✅ 步骤 6: 任务中心")
        task_link = page.locator('a:has-text("任务中心")').first
        if task_link.count() > 0:
            task_link.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            page.screenshot(path='test_09_task_center.png')
            print("  - 任务中心页面加载")

        # ========== 测试 7: 学生管理 ==========
        print("\n✅ 步骤 7: 学生管理")
        student_link = page.locator('a:has-text("学生")').first
        if student_link.count() > 0:
            student_link.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            page.screenshot(path='test_10_students.png')
            print("  - 学生管理页面加载")

            # 尝试添加学生
            add_btn = page.locator('button:has-text("添加"), button:has-text("新增")').first
            if add_btn.count() > 0:
                add_btn.click()
                time.sleep(0.5)
                page.screenshot(path='test_11_add_student.png')
                print("  - 打开添加学生表单")

        # ========== 测试 8: 返回首页 ==========
        print("\n✅ 步骤 8: 返回首页")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='test_12_back_home.png')
        print("  - 返回首页完成")

        # ========== 测试 9: 退出登录 ==========
        print("\n✅ 步骤 9: 退出登录")
        logout_btn = page.locator('button:has-text("退出"), a:has-text("退出")').first
        if logout_btn.count() > 0:
            logout_btn.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            page.screenshot(path='test_13_logout.png')
            print("  - 退出登录完成")

        print("\n" + "="*70)
        print("✅ 所有功能测试完成")
        print("="*70)

        print("\n📸 所有截图:")
        import os
        for f in sorted(os.listdir('.')):
            if f.startswith('test_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
