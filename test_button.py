#!/usr/bin/env python3
"""使用 Playwright 实际测试页面按钮颜色"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 访问首页
        print("📸 正在访问首页...")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')

        # 等待页面完全加载
        time.sleep(2)

        # 截图首页
        page.screenshot(path='homepage_actual.png', full_page=True)
        print('✅ 已保存首页截图: homepage_actual.png')

        # 检查按钮的颜色
        button = page.locator('button:has-text("AI 智能解析并创建任务")')

        # 获取按钮的计算样式
        bg_color = button.evaluate('el => window.getComputedStyle(el).backgroundColor')
        print(f'\n🎨 按钮背景色: {bg_color}')

        # 检查是否有渐变
        bg_image = button.evaluate('el => window.getComputedStyle(el).backgroundImage')
        print(f'🎨 按钮 background-image: {bg_image}')

        # 获取按钮的 class 属性
        button_class = button.get_attribute('class')
        print(f'\n📦 按钮 class: {button_class}')

        # 获取按钮的完整 HTML
        button_html = button.inner_html()
        print(f'\n📄 按钮 HTML 内容: {button_html[:200]}...')

        # 测试点击其他页面
        print('\n🔍 测试导航到任务中心...')
        task_center = page.locator('a:has-text("任务中心")')
        if task_center.count() > 0:
            task_center.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            page.screenshot(path='task_center_actual.png', full_page=True)
            print('✅ 已保存任务中心截图: task_center_actual.png')

        browser.close()
        print('\n✅ 测试完成！')

if __name__ == '__main__':
    main()
