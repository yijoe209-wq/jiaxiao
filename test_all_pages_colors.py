#!/usr/bin/env python3
"""简单测试：检查所有页面的按钮和颜色"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("="*70)
        print("🎨 检查所有页面的按钮颜色")
        print("="*70)

        # 测试所有页面
        pages_to_test = [
            ('http://localhost:5001/', '首页'),
            ('http://localhost:5001/my-tasks', '任务中心'),
            ('http://localhost:5001/students', '学生管理'),
            ('http://localhost:5001/login', '登录页'),
        ]

        results = []

        for url, name in pages_to_test:
            print(f"\n📍 测试: {name}")
            print(f"   URL: {url}")

            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # 检查背景色
            bg = page.evaluate('() => window.getComputedStyle(document.body).backgroundColor')
            print(f"   ✓ 页面背景: {bg}")

            # 查找所有按钮
            buttons = page.locator('button').all()
            print(f"   ✓ 找到 {len(buttons)} 个按钮")

            # 检查每个按钮的颜色
            for i, btn in enumerate(buttons[:5]):  # 只检查前5个按钮
                try:
                    text = btn.inner_text()[:20]
                    bg_color = btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
                    text_color = btn.evaluate('el => window.getComputedStyle(el).color')

                    # 检查是否是橙色
                    is_orange = 'orange' in bg_color.lower() or '255, 165' in bg_color or '#f' in bg_color.lower() and '#97' in bg_color.lower()

                    result = {
                        'page': name,
                        'button_text': text,
                        'bg_color': bg_color,
                        'is_orange': is_orange
                    }
                    results.append(result)

                    status = "❌ 橙色!" if is_orange else "✓"
                    print(f"      {status} [{i+1}] '{text}': {bg_color}")
                except Exception as e:
                    print(f"      ⚠️ 按钮检查失败: {e}")

            # 截图
            filename = f'color_check_{name.replace(" ", "_")}.png'
            page.screenshot(path=filename)
            print(f"   ✅ 截图: {filename}")

        # 总结
        print("\n" + "="*70)
        print("📊 测试结果总结")
        print("="*70)

        orange_buttons = [r for r in results if r['is_orange']]

        if orange_buttons:
            print(f"\n❌ 发现 {len(orange_buttons)} 个橙色按钮:")
            for r in orange_buttons:
                print(f"   - 页面: {r['page']}")
                print(f"     按钮: {r['button_text']}")
                print(f"     颜色: {r['bg_color']}")
        else:
            print("\n✅ 所有按钮颜色正常！没有发现橙色按钮")

        print("\n📸 所有截图文件:")
        import os
        for f in sorted(os.listdir('.')):
            if f.startswith('color_check_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
