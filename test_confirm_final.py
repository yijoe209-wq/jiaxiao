#!/usr/bin/env python3
"""测试确认页面任务解析 - 最终版本"""

from playwright.sync_api import sync_playwright
import time

student_id = "b7e807d6-04a6-49da-945d-cdd7cc11e1e1"
pending_id = "c3f00d0a-e43d-4d17-bb7a-593ecd79eca4"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    print("="*70)
    print("🔍 测试确认页面任务解析修复")
    print("="*70)

    print("\n登录...")
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    print("✅ 登录成功")

    print("\n访问确认页面...")
    confirm_url = f'http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}'
    print(f"URL: {confirm_url}")

    page.goto(confirm_url)
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    page.screenshot(path='confirm_final.png')
    print("✅ 截图: confirm_final.png")

    print("\n检查页面内容:")

    # 检查任务描述
    task_desc = page.locator('.task-card p.text-gray-900').first
    if task_desc.count() > 0:
        description_text = task_desc.inner_text()
        print(f"\n任务描述: {description_text}")

        if description_text == '无描述':
            print("❌ 失败：显示'无描述'")
            print("   原因：数据解析失败，无法从 task.task.description 获取数据")
        elif description_text and len(description_text) > 2:
            print("✅ 成功：任务描述正常显示")
            print(f"   描述内容: {description_text}")
        else:
            print("⚠️ 警告：任务描述为空或太短")
    else:
        print("❌ 错误：未找到任务描述元素")

    # 检查科目标签
    subject_label = page.locator('.task-card span.bg-gray-100').first
    if subject_label.count() > 0:
        subject_text = subject_label.inner_text()
        print(f"\n科目标签: {subject_text}")
    else:
        print("\n⚠️ 未找到科目标签")

    # 检查图片
    images = page.locator('.attachment-img').all()
    print(f"\n图片数量: {len(images)}")

    # 检查确认按钮
    confirm_btn = page.locator('#confirmBtn').first
    if confirm_btn.count() > 0:
        is_disabled = confirm_btn.is_disabled()
        print(f"\n确认按钮: {'启用' if not is_disabled else '禁用'}")

    print("\n" + "="*70)
    print("测试完成")
    print("="*70)

    print("\n修复内容:")
    print("  confirm.html 的 renderTasks() 函数现在正确处理:")
    print("  1. AI 多任务: taskData.tasks → 提取 tasks 数组")
    print("  2. AI 单任务: taskData.task → 包装为 [taskData.task]")
    print("  3. 纯图片任务: taskData 本身 → 包装为 [taskData]")

    print("\n任务描述字段优先级:")
    print("  task.description → task.details → task.raw_text → '无描述'")

    browser.close()

    # 等待用户查看
    input("\n按回车键关闭浏览器...")
    browser.close()
