#!/usr/bin/env python3
"""直接测试确认页面"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 测试确认页面任务解析（直接访问）")
        print("="*70)

        # 先登录
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

        # 获取一个学生ID
        print("\n📍 步骤 2: 获取学生ID")
        page.goto('http://localhost:5001/api/students')
        time.sleep(0.5)

        students_response = await page.evaluate('() => fetch("/api/students").then(r => r.json())')
        import json
        students_data = students_response

        if students_data.get('students') and len(students_data['students']) > 0:
            student_id = students_data['students'][0]['student_id']
            student_name = students_data['students'][0]['name']
            print(f"  ✅ 找到学生: {student_name} (ID: {student_id})")
        else:
            print("  ❌ 没有学生，请先添加学生")
            browser.close()
            return

        # 直接访问确认页面
        print("\n📍 步骤 3: 访问确认页面")
        pending_id = "c3f00d0a-e43d-4d17-bb7a-593ecd79eca4"
        confirm_url = f"http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}"
        print(f"  URL: {confirm_url}")

        page.goto(confirm_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='confirm_direct_01_page.png')
        print("  ✅ 截图: confirm_direct_01_page.png")

        # 检查任务描述
        print("\n📍 步骤 4: 检查任务描述")
        task_desc = page.locator('.task-card p.text-gray-900').first
        if task_desc.count() > 0:
            description_text = task_desc.inner_text()
            print(f"  ✓ 任务描述: {description_text}")

            if description_text == '无描述':
                print("  ❌ 错误：任务描述显示为'无描述'")
            elif description_text and len(description_text) > 0:
                print("  ✅ 任务描述正常显示")
            else:
                print("  ⚠️ 任务描述为空")
        else:
            print("  ❌ 未找到任务描述元素")

        # 检查科目标签
        print("\n📍 步骤 5: 检查科目标签")
        subject_label = page.locator('.bg-gray-100').first
        if subject_label.count() > 0:
            subject_text = subject_label.inner_text()
            print(f"  ✓ 科目: {subject_text}")
        else:
            print("  ⚠️ 未找到科目标签")

        # 检查图片
        print("\n📍 步骤 6: 检查图片")
        images = page.locator('.attachment-img').all()
        print(f"  ✓ 找到 {len(images)} 张图片")

        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)

        browser.close()

if __name__ == '__main__':
    main()
