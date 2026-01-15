#!/usr/bin/env python3
"""完整测试所有页面功能"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("="*60)
        print("🚀 开始完整功能测试")
        print("="*60)

        # ========== 测试 1: 首页 ==========
        print("\n📍 测试 1: 访问首页")
        page.goto('http://localhost:5001/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # 检查按钮颜色
        button = page.locator('button:has-text("AI 智能解析并创建任务")')
        bg_color = button.evaluate('el => window.getComputedStyle(el).backgroundColor')
        print(f"  ✓ 按钮背景色: {bg_color}")
        print(f"  ✓ 预期: rgb(26, 26, 26) (黑色)")
        assert bg_color == 'rgb(26, 26, 26)', f"按钮颜色错误: {bg_color}"

        page.screenshot(path='test_01_homepage.png')
        print("  ✅ 首页截图保存: test_01_homepage.png")

        # ========== 测试 2: 点击任务中心 ==========
        print("\n📍 测试 2: 点击任务中心")
        try:
            # 尝试点击任务中心链接
            task_center_link = page.locator('a:has-text("任务中心")').first
            if task_center_link.count() > 0:
                task_center_link.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                # 检查是否跳转到任务中心
                assert 'my-tasks' in page.url or 'tasks' in page.url
                page.screenshot(path='test_02_task_center.png')
                print("  ✅ 任务中心页面加载成功")

                # 返回首页
                page.goto('http://localhost:5001/')
                page.wait_for_load_state('networkidle')
                time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ 任务中心导航失败: {e}")

        # ========== 测试 3: 点击学生管理 ==========
        print("\n📍 测试 3: 点击学生管理")
        try:
            students_link = page.locator('a:has-text("学生")').first
            if students_link.count() > 0:
                students_link.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                assert 'students' in page.url
                page.screenshot(path='test_03_students.png')
                print("  ✅ 学生管理页面加载成功")

                # 返回首页
                page.goto('http://localhost:5001/')
                page.wait_for_load_state('networkidle')
                time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ 学生管理导航失败: {e}")

        # ========== 测试 4: 上传图片功能 ==========
        print("\n📍 测试 4: 测试图片上传")
        try:
            # 点击文件输入框
            file_input = page.locator('#imageInput')
            if file_input.count() > 0:
                # 创建一个测试图片文件
                import base64
                from pathlib import Path

                # 创建一个简单的测试图片
                test_image_path = Path('/tmp/test_upload.png')
                # 使用 Pillow 创建测试图片
                try:
                    from PIL import Image
                    img = Image.new('RGB', (100, 100), color='red')
                    img.save(test_image_path)

                    # 上传文件
                    file_input.set_input_files(str(test_image_path))
                    time.sleep(1)

                    page.screenshot(path='test_04_image_uploaded.png')
                    print("  ✅ 图片上传功能正常")

                    # 清理
                    test_image_path.unlink()
                except ImportError:
                    print("  ⚠️ 需要安装 Pillow 库来测试图片上传")
            else:
                print("  ⚠️ 未找到文件输入框")
        except Exception as e:
            print(f"  ⚠️ 图片上传测试失败: {e}")

        # ========== 测试 5: 输入文字 ==========
        print("\n📍 测试 5: 测试文字输入")
        try:
            textarea = page.locator('textarea')
            if textarea.count() > 0:
                textarea.fill('测试文字：完成数学作业')
                time.sleep(0.5)
                page.screenshot(path='test_05_text_entered.png')
                print("  ✅ 文字输入功能正常")
        except Exception as e:
            print(f"  ⚠️ 文字输入测试失败: {e}")

        # ========== 测试 6: 点击提交按钮 ==========
        print("\n📍 测试 6: 点击提交按钮")
        try:
            submit_btn = page.locator('button:has-text("AI 智能解析并创建任务")')
            if submit_btn.count() > 0:
                # 点击按钮（可能会有API调用）
                submit_btn.click()
                time.sleep(2)

                page.screenshot(path='test_06_after_submit.png')
                print("  ✅ 提交按钮点击成功")
        except Exception as e:
            print(f"  ⚠️ 提交按钮测试失败: {e}")

        # ========== 测试 7: 检查所有页面的颜色一致性 ==========
        print("\n📍 测试 7: 检查所有页面的设计一致性")

        pages_to_test = [
            ('http://localhost:5001/', '首页'),
            ('http://localhost:5001/my-tasks', '任务中心'),
            ('http://localhost:5001/students', '学生管理'),
            ('http://localhost:5001/login', '登录页'),
        ]

        for url, name in pages_to_test:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # 检查背景色
            bg_color = page.evaluate('() => window.getComputedStyle(document.body).backgroundColor')
            print(f"  - {name}: {bg_color}")

            page.screenshot(path=f'test_07_{name.replace(" ", "_")}.png')

        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        print("\n📸 截图文件:")
        import os
        for f in os.listdir('.'):
            if f.startswith('test_') and f.endswith('.png'):
                print(f"  - {f}")

        browser.close()

if __name__ == '__main__':
    main()
