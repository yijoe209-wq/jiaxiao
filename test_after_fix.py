#!/usr/bin/env python3
"""测试 SECRET_KEY 修复后的任务中心"""

from playwright.sync_api import sync_playwright
import time

print("="*70)
print("🔍 测试 SECRET_KEY 修复")
print("="*70)
print("\n⚠️ 请先重启 Flask 服务器:")
print("   1. 停止当前服务器 (Ctrl+C)")
print("   2. 重新运行: python3 app.py")
print("\n按回车继续测试...")
input()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

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

    print("\n步骤 2: 访问任务中心")
    page.goto('http://localhost:5001/my-tasks')
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    # 检查任务数据
    all_tasks = page.evaluate('() => typeof allTasks !== "undefined" ? allTasks : null')
    all_students = page.evaluate('() => typeof allStudents !== "undefined" ? allStudents : null')

    print(f"\n数据加载状态:")
    print(f"  allTasks: {len(all_tasks) if all_tasks else 0} 个任务")
    print(f"  allStudents: {len(all_students) if all_students else 0} 个学生")

    # 检查页面渲染
    task_items = page.locator('.task-item').all()
    print(f"\n页面渲染:")
    print(f"  渲染任务数: {len(task_items)}")

    if len(task_items) > 0:
        print("  ✅ 任务正常显示")

        first_task_text = task_items[0].inner_text()
        print(f"\n  第一个任务:")
        print(f"  {first_task_text[:200]}...")
    else:
        print("  ❌ 页面没有显示任务")

    # 检查统计
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

    print(f"\n统计:")
    print(f"  紧急: {stats.get('urgent')}")
    print(f"  警告: {stats.get('warning')}")
    print(f"  待办: {stats.get('pending')}")
    print(f"  完成: {stats.get('completed')}")

    page.screenshot(path='task_center_after_fix.png')
    print(f"\n✅ 截图: task_center_after_fix.png")

    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)

    print("\n如果任务正常显示，说明 SECRET_KEY 修复成功！")

    time.sleep(2)
    browser.close()
