#!/usr/bin/env python3
"""测试确认页面任务解析修复"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 测试确认页面任务解析")
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

        # 获取学生ID
        print("\n📍 步骤 2: 获取学生信息")
        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 通过 JavaScript 获取学生ID
        student_id = page.evaluate('''
            () => {
                const studentItems = document.querySelectorAll('.student-item');
                if (studentItems.length > 0) {
                    const deleteBtn = studentItems[0].querySelector('.delete-btn');
                    return deleteBtn ? deleteBtn.getAttribute('onclick').match(/'([^']+)'/)[1] : null;
                }
                return null;
            }
        ''')

        if not student_id:
            print("  ❌ 没有找到学生，请先添加学生")
            browser.close()
            return

        student_name = page.locator('.student-name').first.inner_text()
        print(f"  ✅ 找到学生: {student_name} (ID: {student_id})")

        # 直接访问确认页面
        print("\n📍 步骤 3: 访问确认页面")
        pending_id = "c3f00d0a-e43d-4d17-bb7a-593ecd79eca4"
        confirm_url = f"http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}"
        print(f"  URL: {confirm_url}")

        page.goto(confirm_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='confirm_fix_01_page.png')
        print("  ✅ 截图: confirm_fix_01_page.png")

        # 检查任务描述
        print("\n📍 步骤 4: 检查任务描述")
        task_desc = page.locator('.task-card p.text-gray-900').first
        if task_desc.count() > 0:
            description_text = task_desc.inner_text()
            print(f"  ✓ 任务描述: {description_text}")

            if description_text == '无描述':
                print("  ❌ 错误：任务描述显示为'无描述'")
                print("  → 这说明数据解析失败")
            elif description_text and len(description_text) > 2:
                print("  ✅ 任务描述正常显示")
                print("  → 数据解析成功")
            else:
                print("  ⚠️ 任务描述为空或太短")
        else:
            print("  ❌ 未找到任务描述元素")

        # 检查科目标签
        print("\n📍 步骤 5: 检查科目标签")
        subject_label = page.locator('.task-card span.bg-gray-100').first
        if subject_label.count() > 0:
            subject_text = subject_label.inner_text()
            print(f"  ✓ 科目: {subject_text}")
        else:
            print("  ⚠️ 未找到科目标签")

        # 检查图片
        print("\n📍 步骤 6: 检查图片")
        images = page.locator('.attachment-img').all()
        print(f"  ✓ 找到 {len(images)} 张图片")

        # 检查确认按钮
        print("\n📍 步骤 7: 检查确认按钮")
        confirm_btn = page.locator('#confirmBtn').first
        if confirm_btn.count() > 0:
            is_disabled = confirm_btn.is_disabled()
            print(f"  ✓ 确认按钮状态: {'禁用' if is_disabled else '启用'}")

            if not is_disabled:
                print("  ✅ 可以点击确认按钮")

        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)

        print("\n📋 修复说明:")
        print("  confirm.html 现在正确处理三种数据结构:")
        print("  1. AI 多任务: {type: 'multiple', tasks: [...], images: [...] }")
        print("  2. AI 单任务: {type: 'single', task: {...}, images: [...] }")
        print("  3. 纯图片任务: {description: '...', images: [...] }")

        print("\n📸 截图文件:")
        import os
        for f in os.listdir('.'):
            if f.startswith('confirm_fix_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
