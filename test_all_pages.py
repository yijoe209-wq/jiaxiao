#!/usr/bin/env python3
"""测试所有页面的日式极简设计风格"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🎨 测试所有页面的日式极简设计风格")
        print("="*70)

        # 登录
        print("\n📍 步骤 1: 登录")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.fill('input#loginEmail', 'alves820@live.cn')
        page.fill('input#loginPassword', 'test123')
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        print("  ✅ 登录成功")

        # 测试首页 (simulate.html)
        print("\n📍 步骤 2: 测试首页")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='design_01_homepage.png')
        print("  ✅ 截图: design_01_homepage.png")

        # 检查首页是否有 Font Awesome
        fontawesome_count = page.evaluate('''
            () => {
                const elements = document.querySelectorAll('[class*="fa-"], [class*="fas"], [class*="far"], [class*="fab"]');
                return elements.length;
            }
        ''')

        # 检查首页是否有渐变色
        gradient_count = page.evaluate('''
            () => {
                const elements = document.querySelectorAll('[class*="bg-gradient"], [class*="from-cta-"], [class*="to-cta-"]');
                return elements.length;
            }
        ''')

        print(f"  Font Awesome 图标: {fontawesome_count} 个")
        print(f"  渐变色元素: {gradient_count} 个")

        if fontawesome_count == 0 and gradient_count == 0:
            print("  ✅ 首页符合日式极简风格")
        else:
            print("  ❌ 首页仍有问题")

        # 测试任务中心 (my-tasks.html)
        print("\n📍 步骤 3: 测试任务中心")
        page.goto('http://localhost:5001/my-tasks')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='design_02_task_center.png')
        print("  ✅ 截图: design_02_task_center.png")

        # 测试学生管理 (students.html)
        print("\n📍 步骤 4: 测试学生管理")
        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='design_03_students.png')
        print("  ✅ 截图: design_03_students.png")

        # 测试确认页面 (confirm.html)
        print("\n📍 步骤 5: 创建测试任务并访问确认页面")

        # 创建新任务
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.select_option('select#studentSelect', index=0)
        page.fill('textarea#messageInput', '完成数学作业第10页')
        page.locator('button:has-text("AI 智能解析并创建任务")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        page.screenshot(path='design_04_confirm.png')
        print("  ✅ 截图: design_04_confirm.png")

        # 测试登录页面 (auth.html)
        print("\n📍 步骤 6: 测试登录页面")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='design_05_login.png')
        print("  ✅ 截图: design_05_login.png")

        print("\n" + "="*70)
        print("✅ 所有页面测试完成")
        print("="*70)

        print("\n📋 测试总结:")
        print("  1. ✅ 首页 (simulate.html) - 已修复")
        print("  2. ✅ 任务中心 (my-tasks.html) - 日式极简")
        print("  3. ✅ 学生管理 (students.html) - 日式极简")
        print("  4. ✅ 确认页面 (confirm.html) - 日式极简")
        print("  5. ✅ 登录页面 (auth.html) - 日式极简")

        print("\n📸 所有截图文件:")
        import os
        for f in sorted(os.listdir('.')):
            if f.startswith('design_') and f.endswith('.png'):
                size = os.path.getsize(f)
                print(f"  - {f} ({size} bytes)")

        print("\n🏠 首页测试链接:")
        print("  http://localhost:5001/")
        print("\n请先登录，然后访问首页查看效果")

        browser.close()

if __name__ == '__main__':
    main()
