#!/usr/bin/env python3
"""验证学生管理页面的视觉修复"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 验证学生管理页面修复")
        print("="*70)

        # 访问学生管理页面
        print("\n📍 访问学生管理页面")
        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print(f"  当前URL: {page.url}")

        page.screenshot(path='visual2_01_students_page.png')
        print("  ✅ 截图: visual2_01_students_page.png")

        # 检查是否被重定向到登录页
        if 'login' in page.url:
            print("  ⚠️ 页面重定向到登录页")
            print("  -> 需要先登录才能访问学生管理页面")
        else:
            # 检查页面元素
            print("\n📍 检查页面元素")

            container = page.locator('.container').first
            if container.count() > 0:
                width = container.evaluate('el => el.offsetWidth')
                print(f"  ✓ 容器宽度: {width}px")

            header = page.locator('.header').first
            if header.count() > 0:
                bg_color = header.evaluate('el => window.getComputedStyle(el).backgroundColor')
                text_color = header.evaluate('el => window.getComputedStyle(el).color')
                print(f"  ✓ Header 背景: {bg_color}, 文字: {text_color}")

            add_btn = page.locator('button:has-text("添加学生")').first
            if add_btn.count() > 0:
                bg_color = add_btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
                text_color = add_btn.evaluate('el => window.getComputedStyle(el).color')
                print(f"  ✓ 添加按钮背景: {bg_color}, 文字: {text_color}")

            labels = page.locator('.input-group label').all()
            print(f"  ✓ 找到 {len(labels)} 个标签")
            for i, label in enumerate(labels[:2]):
                color = label.evaluate('el => window.getComputedStyle(el).color')
                text = label.inner_text()[:15]
                print(f"    Label [{i+1}] '{text}': {color}")

        print("\n" + "="*70)
        print("✅ 检查完成")
        print("="*70)

        browser.close()

if __name__ == '__main__':
    main()
