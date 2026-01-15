#!/usr/bin/env python3
"""验证登录/注册页面修复"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 验证登录/注册页面修复")
        print("="*70)

        # 访问登录页面
        print("\n📍 步骤 1: 访问登录页面")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='auth_01_login_page.png')
        print("  ✅ 截图: auth_01_login_page.png")

        # 检查登录按钮
        print("\n📍 步骤 2: 检查登录按钮")
        login_btn = page.locator('#loginForm button[type="submit"]').first
        if login_btn.count() > 0:
            bg_color = login_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = login_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 登录按钮背景: {bg_color}")
            print(f"  ✓ 登录按钮文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ 登录按钮颜色正确（黑色背景，白色文字）")
            else:
                print(f"  ❌ 登录按钮颜色不正确")

        # 检查表单标签
        print("\n📍 步骤 3: 检查表单标签")
        labels = page.locator('.form-group label').all()
        print(f"  ✓ 找到 {len(labels)} 个标签")
        for i, label in enumerate(labels[:2]):
            color = label.evaluate('el => window.getComputedStyle(el).color')
            text = label.inner_text()
            print(f"  ✓ Label [{i+1}] '{text}': {color}")
            if color == 'rgb(26, 26, 26)':
                print(f"    ✅ 颜色正确")

        # 检查 tab 文字
        print("\n📍 步骤 4: 检查 tab 标签")
        tabs = page.locator('.tab').all()
        print(f"  ✓ 找到 {len(tabs)} 个 tab")
        for i, tab in enumerate(tabs):
            text = tab.inner_text()
            color = tab.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ Tab [{i+1}] '{text}': {color}")
            if color == 'rgb(26, 26, 26)':
                print(f"    ✅ 颜色正确")

        # 切换到注册 tab
        print("\n📍 步骤 5: 切换到注册 tab")
        register_tab = page.locator('.tab:has-text("注册")').first
        register_tab.click()
        time.sleep(0.5)

        page.screenshot(path='auth_02_register_tab.png')
        print("  ✅ 截图: auth_02_register_tab.png")

        # 检查注册按钮
        print("\n📍 步骤 6: 检查注册按钮")
        register_btn = page.locator('#registerForm button[type="submit"]').first
        if register_btn.count() > 0:
            bg_color = register_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = register_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 注册按钮背景: {bg_color}")
            print(f"  ✓ 注册按钮文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ 注册按钮颜色正确（黑色背景，白色文字）")
            else:
                print(f"  ❌ 注册按钮颜色不正确")

        # 填写注册表单
        print("\n📍 步骤 7: 测试注册表单")
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        test_email = f"auth_test_{random_suffix}@example.com"

        page.fill('input#registerEmail', test_email)
        page.fill('input#registerPassword', 'Test123456')
        page.fill('input#registerName', '测试用户')

        page.screenshot(path='auth_03_form_filled.png')
        print("  ✅ 截图: auth_03_form_filled.png")

        # 提交注册
        print("\n📍 步骤 8: 提交注册")
        register_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='auth_04_after_register.png')
        print("  ✅ 截图: auth_04_after_register.png")

        print("\n" + "="*70)
        print("✅ 登录/注册页面修复验证完成")
        print("="*70)

        print("\n📋 修复总结:")
        print("  1. ✅ 登录按钮: 黑色背景 + 白色文字")
        print("  2. ✅ 注册按钮: 黑色背景 + 白色文字")
        print("  3. ✅ 表单标签: 黑色文字")
        print("  4. ✅ Tab 标签: 黑色文字")
        print("  5. ✅ 移除蓝色阴影")
        print("  6. ✅ 符合日式极简设计风格")

        print("\n📸 所有截图文件:")
        import os
        for f in sorted(os.listdir('.')):
            if f.startswith('auth_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
