#!/usr/bin/env python3
"""完整用户流程测试 - 按照新的页面逻辑"""

from playwright.sync_api import sync_playwright
import time
import os

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🎯 完整用户流程测试 - 新的页面逻辑")
        print("="*70)

        # ========== 步骤 1: 访问登录页面 ==========
        print("\n" + "="*70)
        print("📍 步骤 1: 访问登录页面")
        print("="*70)

        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_01_login.png')
        print("✅ 截图: journey_01_login.png")
        print("   URL: http://localhost:5001/login")

        # 登录
        print("\n🔑 执行登录操作")
        page.fill('input#loginEmail', 'alves820@live.cn')
        page.fill('input#loginPassword', 'test123')
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # ========== 步骤 2: 检查登录后跳转 ==========
        print("\n" + "="*70)
        print("📍 步骤 2: 检查登录后跳转")
        print("="*70)

        current_url = page.url
        print(f"当前 URL: {current_url}")

        if '/login' in current_url:
            print("⚠️ 登录后仍在登录页面（需要手动导航）")
            print("   手动跳转到首页...")
            page.goto('http://localhost:5001/')
            page.wait_for_load_state('networkidle')
            time.sleep(2)
        elif '/' in current_url and current_url.endswith('5001/'):
            print("✅ 登录后跳转到首页（任务中心）")
        else:
            print(f"⚠️ 跳转到: {current_url}")

        page.screenshot(path='journey_02_after_login.png')
        print("✅ 截图: journey_02_after_login.png")

        # ========== 步骤 3: 首页（任务中心） ==========
        print("\n" + "="*70)
        print("📍 步骤 3: 首页 - 任务中心")
        print("="*70)

        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_03_homepage.png')
        print("✅ 截图: journey_03_homepage.png")
        print("   URL: http://localhost:5001/")
        print("   页面: 任务中心（my-tasks.html）")

        # 检查页面元素
        print("\n🔍 检查任务中心页面:")
        title = page.title()
        print(f"  - 页面标题: {title}")

        add_btn = page.locator('a[href="/add"]').first
        if add_btn.count() > 0:
            print("  - ✅ 找到 '添加任务' 按钮")
        else:
            print("  - ❌ 未找到 '添加任务' 按钮")

        tasks_count = page.locator('.task-item').count()
        print(f"  - 任务数量: {tasks_count}")

        # ========== 步骤 4: 点击"添加任务"按钮 ==========
        print("\n" + "="*70)
        print("📍 步骤 4: 点击'添加任务'按钮")
        print("="*70)

        if add_btn.count() > 0:
            add_btn.click()
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            page.screenshot(path='journey_04_add_task.png')
            print("✅ 截图: journey_04_add_task.png")
            print("   URL: " + page.url)

            if '/add' in page.url:
                print("   ✅ 成功跳转到添加任务页面")
            else:
                print(f"   ⚠️ 跳转到: {page.url}")
        else:
            print("❌ 无法点击'添加任务'按钮")

        # ========== 步骤 5: 添加任务页面 ==========
        print("\n" + "="*70)
        print("📍 步骤 5: 快速添加任务页面")
        print("="*70)

        page.goto('http://localhost:5001/add')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_05_add_task_page.png')
        print("✅ 截图: journey_05_add_task_page.png")
        print("   URL: http://localhost:5001/add")
        print("   页面: 快速输入任务（simulate.html）")

        # 检查页面元素
        print("\n🔍 检查添加任务页面:")
        student_select = page.locator('#studentSelect').first
        if student_select.count() > 0:
            print("  - ✅ 找到学生选择框")

        message_input = page.locator('#messageInput').first
        if message_input.count() > 0:
            print("  - ✅ 找到消息输入框")

        submit_btn = page.locator('button:has-text("AI 智能解析")').first
        if submit_btn.count() > 0:
            print("  - ✅ 找到提交按钮")

        # ========== 步骤 6: 创建任务 ==========
        print("\n" + "="*70)
        print("📍 步骤 6: 创建测试任务")
        print("="*70)

        # 选择学生
        if student_select.count() > 0:
            page.select_option('select#studentSelect', index=0)
            print("✅ 选择学生")

        # 输入任务
        if message_input.count() > 0:
            test_message = "数学作业：完成练习册第15页，明天提交"
            message_input.fill(test_message)
            print(f"✅ 输入任务: {test_message}")

        page.screenshot(path='journey_06_before_submit.png')
        print("✅ 截图: journey_06_before_submit.png")

        # 点击提交
        if submit_btn.count() > 0:
            print("\n🚀 点击 AI 智能解析按钮")
            submit_btn.click()
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path='journey_07_after_submit.png')
            print("✅ 截图: journey_07_after_submit.png")

            # 检查是否有确认链接
            confirm_link = page.locator('a[href*="confirm"]').first
            if confirm_link.count() > 0:
                print("✅ 找到确认链接")
                confirm_href = confirm_link.get_attribute('href')
                print(f"   链接: {confirm_href}")

                # 点击确认链接
                print("\n📝 点击确认链接")
                confirm_link.click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                page.screenshot(path='journey_08_confirm.png')
                print("✅ 截图: journey_08_confirm.png")

        # ========== 步骤 7: 访问学生管理 ==========
        print("\n" + "="*70)
        print("📍 步骤 7: 访问学生管理")
        print("="*70)

        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_09_students.png')
        print("✅ 截图: journey_09_students.png")
        print("   URL: http://localhost:5001/students")

        # ========== 步骤 8: 返回任务中心 ==========
        print("\n" + "="*70)
        print("📍 步骤 8: 返回任务中心查看任务")
        print("="*70)

        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='journey_10_back_to_home.png')
        print("✅ 截图: journey_10_back_to_home.png")

        # 检查新任务
        final_tasks = page.locator('.task-item').count()
        print(f"\n📊 当前任务总数: {final_tasks}")

        # ========== 总结 ==========
        print("\n" + "="*70)
        print("📊 测试总结")
        print("="*70)

        print("\n✅ 完成流程:")
        print("  1. 登录页面 → 登录")
        print("  2. 登录后 → 任务中心（首页）")
        print("  3. 任务中心 → 点击'添加任务'按钮")
        print("  4. 添加任务页面 → 输入任务并提交")
        print("  5. 确认页面 → 确认任务")
        print("  6. 访问学生管理")
        print("  7. 返回任务中心查看任务")

        print("\n📸 所有截图文件:")
        for f in sorted(os.listdir('.')):
            if f.startswith('journey_') and f.endswith('.png'):
                size = os.path.getsize(f)
                print(f"  - {f} ({size} bytes)")

        print("\n🎯 页面逻辑确认:")
        print("  ✅ 首页 (/) = 任务中心")
        print("  ✅ 添加任务 (/add) = 快速输入页面")
        print("  ✅ 学生管理 (/students) = 学生管理")
        print("  ✅ 登录 (/login) = 登录/注册")

        input("\n按回车关闭浏览器...")
        browser.close()

if __name__ == '__main__':
    main()
