#!/usr/bin/env python3
"""测试确认页面的任务解析"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 测试确认页面任务解析")
        print("="*70)

        # 步骤 1: 登录
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

        # 步骤 2: 访问首页并创建任务
        print("\n📍 步骤 2: 创建测试任务")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 输入任务描述
        textarea = page.locator('textarea').first
        textarea.fill("完成数学作业第5页")
        time.sleep(0.5)

        page.screenshot(path='confirm_test_01_input.png')
        print("  ✅ 截图: confirm_test_01_input.png")

        # 点击 AI 解析按钮
        print("\n📍 步骤 3: 点击 AI 解析按钮")
        ai_btn = page.locator('button:has-text("AI 智能解析并创建任务")').first
        ai_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # 检查是否有确认链接
        print("\n📍 步骤 4: 检查响应")
        page.screenshot(path='confirm_test_02_after_click.png')
        print("  ✅ 截图: confirm_test_02_after_click.png")

        # 查找确认链接
        confirm_link = page.locator('a[href*="confirm"]').first
        if confirm_link.count() > 0:
            print("  ✅ 找到确认链接")

            # 获取链接
            href = confirm_link.get_attribute('href')
            print(f"  链接: {href}")

            # 点击链接
            print("\n📍 步骤 5: 访问确认页面")
            confirm_link.click()
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            page.screenshot(path='confirm_test_03_confirm_page.png')
            print("  ✅ 截图: confirm_test_03_confirm_page.png")

            # 检查页面内容
            print("\n📍 步骤 6: 检查任务描述")
            task_desc = page.locator('.task-card p.text-gray-900').first
            if task_desc.count() > 0:
                description_text = task_desc.inner_text()
                print(f"  ✓ 任务描述: {description_text}")

                if description_text == '无描述':
                    print("  ❌ 错误：任务描述显示为'无描述'")
                elif description_text:
                    print("  ✅ 任务描述正常显示")
                else:
                    print("  ⚠️ 任务描述为空")
            else:
                print("  ⚠️ 未找到任务描述元素")

        else:
            print("  ⚠️ 未找到确认链接")
            print("  提示：需要先添加学生才能创建任务")

            # 添加学生
            print("\n📍 步骤 5: 添加学生")
            page.goto('http://localhost:5001/students')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            page.fill('input#nameInput', '测试学生')
            page.select_option('select#gradeInput', '一年级')
            page.locator('button:has-text("添加学生")').click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            print("  ✅ 学生添加成功，请重新测试")

        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)

        browser.close()

if __name__ == '__main__':
    main()
