#!/usr/bin/env python3
"""完整用户流程测试 - 逐个页面截图并分析"""

from playwright.sync_api import sync_playwright
import time
import os

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 完整用户流程测试 - 逐页面分析")
        print("="*70)

        # 步骤 1: 访问登录页面
        print("\n" + "="*70)
        print("📍 页面 1: 登录页面 (http://localhost:5001/login)")
        print("="*70)

        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='flow_01_login.png')
        print("✅ 截图: flow_01_login.png")

        # 检查登录页面
        print("\n🔍 检查登录页面:")
        print("  - 是否有 Font Awesome: ", page.locator('[class*="fa-"]').count())
        print("  - 是否有渐变色: ", page.locator('[class*="gradient"]').count())

        # 登录
        page.fill('input#loginEmail', 'alves820@live.cn')
        page.fill('input#loginPassword', 'test123')
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # 步骤 2: 检查登录后跳转到哪里
        print("\n" + "="*70)
        print("📍 登录后检查")
        print("="*70)

        current_url = page.url
        print(f"当前 URL: {current_url}")

        if '/my-tasks' in current_url:
            print("⚠️ 登录后跳转到任务中心，不是首页")
            print("   首页应该是: http://localhost:5001/")

        # 步骤 3: 访问首页
        print("\n" + "="*70)
        print("📍 页面 2: 首页 (http://localhost:5001/)")
        print("="*70)

        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='flow_02_homepage.png')
        print("✅ 截图: flow_02_homepage.png")

        # 检查首页
        print("\n🔍 检查首页:")
        fontawesome = page.locator('[class*="fa-"]').count()
        gradients = page.locator('[class*="gradient"]').count()
        print(f"  - Font Awesome 图标: {fontawesome} 个")
        print(f"  - 渐变色元素: {gradients} 个")

        # 检查页面标题
        title = page.title()
        print(f"  - 页面标题: {title}")

        # 步骤 4: 访问任务中心
        print("\n" + "="*70)
        print("📍 页面 3: 任务中心 (http://localhost:5001/my-tasks)")
        print("="*70)

        page.goto('http://localhost:5001/my-tasks')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='flow_03_task_center.png')
        print("✅ 截图: flow_03_task_center.png")

        print("\n🔍 检查任务中心:")
        print(f"  - Font Awesome: {page.locator('[class*=\"fa-\"]').count()} 个")
        print(f"  - 渐变色: {page.locator('[class*=\"gradient\"]').count()} 个")

        # 步骤 5: 访问学生管理
        print("\n" + "="*70)
        print("📍 页面 4: 学生管理 (http://localhost:5001/students)")
        print("="*70)

        page.goto('http://localhost:5001/students')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='flow_04_students.png')
        print("✅ 截图: flow_04_students.png")

        print("\n🔍 检查学生管理:")
        print(f"  - Font Awesome: {page.locator('[class*=\"fa-\"]').count()} 个")
        print(f"  - 渐变色: {page.locator('[class*=\"gradient\"]').count()} 个")

        # 总结
        print("\n" + "="*70)
        print("📊 测试总结")
        print("="*70)

        print("\n所有截图:")
        for f in sorted(os.listdir('.')):
            if f.startswith('flow_') and f.endswith('.png'):
                print(f"  - {f}")

        print("\n请查看这些截图，分析每个页面的问题")
        print("我会根据你的反馈逐一修复")

        input("\n按回车关闭浏览器...")
        browser.close()

if __name__ == '__main__':
    main()
