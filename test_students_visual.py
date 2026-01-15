#!/usr/bin/env python3
"""验证学生管理页面的视觉修复"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("="*70)
        print("🔍 验证学生管理页面修复")
        print("="*70)

        # 访问学生管理页面
        print("\n📍 访问学生管理页面")
        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='visual_01_students_page.png')
        print("  ✅ 截图: visual_01_students_page.png")

        # 检查页面宽度
        print("\n📍 检查页面宽度")
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
        print("\n📍 检查 header 背景")
        header = page.locator('.header').first
        if header.count() > 0:
            bg_color = header.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = header.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ Header 背景: {bg_color}")
            print(f"  ✓ Header 文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ Header 颜色正确（黑色背景，白色文字）")
            else:
                print(f"  ⚠️ Header 颜色: 背景={bg_color}, 文字={text_color}")

        # 检查添加学生按钮
        print("\n📍 检查添加学生按钮")
        add_btn = page.locator('button:has-text("添加学生")').first
        if add_btn.count() > 0:
            bg_color = add_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
            text_color = add_btn.evaluate('el => window.getComputedStyle(el).color')
            print(f"  ✓ 按钮背景: {bg_color}")
            print(f"  ✓ 按钮文字: {text_color}")

            if bg_color == 'rgb(26, 26, 26)' and text_color == 'rgb(255, 255, 255)':
                print("  ✅ 按钮颜色正确（黑色背景，白色文字）")
            else:
                print(f"  ⚠️ 按钮颜色: 背景={bg_color}, 文字={text_color}")

        # 检查 label 文字颜色
        print("\n📍 检查表单标签颜色")
        labels = page.locator('.input-group label').all()
        for i, label in enumerate(labels[:3]):
            color = label.evaluate('el => window.getComputedStyle(el).color')
            text = label.inner_text()[:15]
            print(f"  ✓ Label [{i+1}] '{text}': {color}")
            if color == 'rgb(26, 26, 26)':
                print(f"    ✅ 颜色正确")
            else:
                print(f"    ⚠️ 应该是 rgb(26, 26, 26)")

        print("\n" + "="*70)
        print("✅ 视觉检查完成")
        print("="*70)

        print("\n📸 截图文件:")
        print("  - visual_01_students_page.png")

        browser.close()

if __name__ == '__main__':
    main()
