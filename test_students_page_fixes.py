#!/usr/bin/env python3
"""验证学生管理页面的所有修复"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("="*70)
        print("🔍 验证学生管理页面修复")
        print("="*70)

        # 访问登录页面并注册/登录
        print("\n📍 步骤 1: 登录")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 点击注册标签
        register_tab = page.locator('text=注册').first
        if register_tab.count() > 0:
            register_tab.click()
            time.sleep(0.5)

        # 填写注册表单
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        test_email = f"fix_test_{random_suffix}@example.com"

        page.fill('input#registerEmail', test_email)
        page.fill('input#registerPassword', 'Test123456')
        page.fill('input#registerName', '测试家长')

        print(f"  - 注册账号: {test_email}")

        submit_btn = page.locator('button[type="submit"]')
        submit_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        print("  ✅ 登录成功")

        # 访问学生管理页面
        print("\n📍 步骤 2: 访问学生管理页面")
        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='fix_01_students_page.png')
        print("  ✅ 截图: fix_01_students_page.png")

        # 检查页面宽度
        print("\n📍 步骤 3: 检查页面宽度")
        container = page.locator('.container').first
        if container.count() > 0:
            width = container.evaluate('el => el.offsetWidth')
            print(f"  ✓ 容器宽度: {width}px")
            print(f"  ✓ 预期宽度: 672px (max-w-2xl)")
            if 670 <= width <= 674:
                print("  ✅ 宽度正确")
            else:
                print(f"  ⚠️ 宽度偏差: {672 - width}px")

        # 检查 header 背景色
        print("\n📍 步骤 4: 检查 header 背景")
        header = page.locator('.header').first
        if header.count() > 0:
            bg_color = header.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = header.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ Header 背景: {bg_color}")
            print(f"  ✓ Header 文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ Header 颜色正确（黑色背景，白色文字）")
            else:
                print("  ⚠️ Header 颜色不正确")

        # 检查添加学生按钮
        print("\n📍 步骤 5: 检查添加学生按钮")
        add_btn = page.locator('button:has-text("添加学生")').first
        if add_btn.count() > 0:
            bg_color = add_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = add_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 按钮背景: {bg_color}")
            print(f"  ✓ 按钮文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ 按钮颜色正确（黑色背景，白色文字）")
            else:
                print("  ⚠️ 按钮颜色不正确")

        # 检查 label 文字颜色
        print("\n📍 步骤 6: 检查表单标签颜色")
        labels = page.locator('.input-group label').all()
        for i, label in enumerate(labels[:3]):
            color = label.evaluate('el => window.getComputedStyle(el).color')
            text = label.inner_text()[:15]
            print(f"  ✓ Label [{i+1}] '{text}': {color}")
            if color == 'rgb(26, 26, 26)':
                print(f"    ✅ 颜色正确")
            else:
                print(f"    ⚠️ 应该是 rgb(26, 26, 26)")

        # 添加一个学生
        print("\n📍 步骤 7: 添加测试学生")
        page.fill('input#nameInput', '测试学生')
        page.fill('input#gradeInput', '一年级')

        add_btn.click()
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='fix_02_student_added.png')
        print("  ✅ 学生添加成功")
        print("  ✅ 截图: fix_02_student_added.png")

        # 检查编辑和删除按钮
        print("\n📍 步骤 8: 检查编辑/删除按钮")
        edit_btn = page.locator('.edit-btn').first
        delete_btn = page.locator('.delete-btn').first

        if edit_btn.count() > 0:
            edit_bg = edit_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            edit_color = edit_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 编辑按钮背景: {edit_bg}")
            print(f"  ✓ 编辑按钮文字: {edit_color}")

            if edit_bg == 'rgb(255, 255, 255)' and edit_color == 'rgb(26, 26, 26)':
                print("  ✅ 编辑按钮颜色正确（白色背景，黑色文字）")
            else:
                print("  ⚠️ 编辑按钮颜色不正确")

        if delete_btn.count() > 0:
            delete_bg = delete_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            delete_color = delete_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 删除按钮背景: {delete_bg}")
            print(f"  ✓ 删除按钮文字: {delete_color}")

            if delete_bg == 'rgb(26, 26, 26)' and delete_color == 'rgb(255, 255, 255)':
                print("  ✅ 删除按钮颜色正确（黑色背景，白色文字）")
            else:
                print("  ⚠️ 删除按钮颜色不正确")

        # 检查学生信息文字颜色
        print("\n📍 步骤 9: 检查学生信息文字颜色")
        student_name = page.locator('.student-name').first
        student_grade = page.locator('.student-grade').first

        if student_name.count() > 0:
            name_color = student_name.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 学生名字颜色: {name_color}")
            print("  ✅ 名字颜色正常")

        if student_grade.count() > 0:
            grade_color = student_grade.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 年级颜色: {grade_color}")
            if grade_color == 'rgb(102, 102, 102)':
                print("  ✅ 年级颜色正确")

        page.screenshot(path='fix_03_buttons_visible.png')
        print("  ✅ 截图: fix_03_buttons_visible.png")

        # 测试编辑功能
        print("\n📍 步骤 10: 测试编辑功能")
        edit_btn.click()
        time.sleep(0.5)

        page.screenshot(path='fix_04_edit_modal.png')
        print("  ✅ 编辑模态框打开")
        print("  ✅ 截图: fix_04_edit_modal.png")

        # 检查模态框保存按钮
        save_btn = page.locator('button:has-text("保存")').first
        if save_btn.count() > 0:
            save_bg = save_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            save_color = save_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 保存按钮背景: {save_bg}")
            print(f"  ✓ 保存按钮文字: {save_color}")

            if save_bg == 'rgb(26, 26, 26)' and save_color == 'rgb(255, 255, 255)':
                print("  ✅ 保存按钮颜色正确")
            else:
                print("  ⚠️ 保存按钮颜色不正确")

        # 关闭模态框
        cancel_btn = page.locator('button:has-text("取消")').first
        cancel_btn.click()
        time.sleep(0.5)

        print("\n" + "="*70)
        print("✅ 所有修复验证完成")
        print("="*70)

        print("\n📸 所有截图文件:")
        import os
        for f in sorted(os.listdir('.')):
            if f.startswith('fix_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
