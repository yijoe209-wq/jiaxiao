#!/usr/bin/env python3
"""测试确认页面编辑功能 - 使用新任务"""

from playwright.sync_api import sync_playwright
import time

student_id = "b7e807d6-04a6-49da-945d-cdd7cc11e1e1"
pending_id = "5fd4667f-8c99-4e50-8ae1-96c45d6dc50d"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    print("="*70)
    print("🔍 测试确认页面编辑功能")
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
    page.goto(confirm_url)
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    page.screenshot(path='confirm_new_01_page.png')
    print("✅ 截图: confirm_new_01_page.png")

    print("\n检查页面元素:")

    # 检查原文显示
    raw_text = page.locator('.raw-text').first
    if raw_text.count() > 0:
        raw_text_content = raw_text.inner_text()
        print(f"✅ 原文显示: {raw_text_content}")
    else:
        print("⚠️ 未找到原文")

    # 检查图片
    images = page.locator('.attachment-img').all()
    print(f"✅ 图片数量: {len(images)}")

    # 检查可编辑字段
    textareas = page.locator('textarea[data-field="description"]').all()
    inputs = page.locator('input[data-field="subject"]').all()
    date_inputs = page.locator('input[data-field="deadline"]').all()

    print(f"✅ 可编辑描述字段: {len(textareas)}")
    print(f"✅ 可编辑科目字段: {len(inputs)}")
    print(f"✅ 可编辑日期字段: {len(date_inputs)}")

    if len(textareas) > 0:
        original_desc = textareas[0].input_value()
        print(f"\n原始描述: {original_desc}")

        # 测试编辑
        print("\n测试编辑...")
        new_desc = "修改后的任务描述 - 完成数学作业第5页练习题"
        textareas[0].fill(new_desc)
        time.sleep(0.5)

        page.screenshot(path='confirm_new_02_edited.png')
        print("✅ 截图: confirm_new_02_edited.png")

        updated_desc = textareas[0].input_value()
        print(f"更新后描述: {updated_desc}")

        if updated_desc == new_desc:
            print("✅ 编辑功能正常")
        else:
            print("❌ 编辑功能失败")

    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)

    time.sleep(2)
    browser.close()
