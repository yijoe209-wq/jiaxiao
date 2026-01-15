#!/usr/bin/env python3
"""测试任务中心页面显示"""

from playwright.sync_api import sync_playwright
import time
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        print("="*70)
        print("🔍 测试任务中心页面")
        print("="*70)

        # 登录
        print("\n步骤 1: 登录")
        page.goto('http://localhost:5001/login')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.fill('input#loginEmail', 'alves820@live.cn')
        page.fill('input#loginPassword', 'test123')
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        print("  ✅ 登录成功")

        # 访问任务中心
        print("\n步骤 2: 访问任务中心")
        page.goto('http://localhost:5001/my-tasks')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        page.screenshot(path='task_center_01_page.png')
        print("  ✅ 截图: task_center_01_page.png")

        # 检查任务数量
        print("\n步骤 3: 检查任务数据")

        # 通过 JavaScript 获取任务数据
        tasks_data = page.evaluate('''
            async () => {
                try {
                    const response = await fetch('/api/tasks');
                    const tasks = await response.json();
                    return {
                        count: tasks.length,
                        first_task: tasks[0],
                        has_data: tasks.length > 0
                    };
                } catch (error) {
                    return { error: error.message };
                }
            }
        ''')

        print(f"  API 返回任务数量: {tasks_data.get('count', 0)}")

        if tasks_data.get('has_data'):
            first_task = tasks_data.get('first_task')
            print(f"  第一个任务: {first_task.get('description', '无描述')}")
            print(f"  学生ID: {first_task.get('student_id')}")

        # 检查页面渲染
        print("\n步骤 4: 检查页面渲染")

        task_items = page.locator('.task-item').all()
        print(f"  页面渲染任务数: {len(task_items)}")

        if len(task_items) > 0:
            print("  ✅ 任务正常显示")

            # 获取第一个任务的文本
            first_item_text = task_items[0].inner_text()
            print(f"  第一个任务内容: {first_item_text[:100]}...")
        else:
            print("  ❌ 页面没有显示任务")

            # 检查是否有错误
            console_errors = page.evaluate('''
                () => {
                    return window.__errors || [];
                }
            ''')

            if console_errors:
                print(f"  控制台错误: {console_errors}")

        # 检查统计数据
        print("\n步骤 5: 检查统计数据")

        stats = page.evaluate('''
            () => {
                return {
                    urgent: document.getElementById('urgentCount')?.textContent,
                    warning: document.getElementById('warningCount')?.textContent,
                    pending: document.getElementById('pendingCount')?.textContent,
                    completed: document.getElementById('completedCount')?.textContent
                };
            }
        ''')

        print(f"  紧急: {stats.get('urgent')}")
        print(f"  警告: {stats.get('warning')}")
        print(f"  待办: {stats.get('pending')}")
        print(f"  完成: {stats.get('completed')}")

        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)

        # 保持浏览器打开让用户查看
        print("\n浏览器将保持打开，按回车键关闭...")
        input()

        browser.close()

if __name__ == '__main__':
    main()
