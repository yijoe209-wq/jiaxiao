#!/usr/bin/env python3
"""获取浏览器控制台错误"""

from playwright.sync_api import sync_playwright
import time

student_id = "b7e807d6-04a6-49da-945d-cdd7cc11e1e1"
pending_id = "5fd4667f-8c99-4e50-8ae1-96c45d6dc50d"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # 监听所有控制台消息
    all_messages = []
    def handle_console(msg):
        all_messages.append({
            'type': msg.type,
            'text': msg.text,
            'location': msg.location
        })

    page.on('console', handle_console)

    # 登录
    page.goto('http://localhost:5001/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.fill('input#loginEmail', 'alves820@live.cn')
    page.fill('input#loginPassword', 'test123')
    page.locator('#loginForm button[type="submit"]').click()
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    # 访问确认页面
    confirm_url = f'http://localhost:5001/confirm?pending_id={pending_id}&student_id={student_id}'
    page.goto(confirm_url)
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    print("="*70)
    print("控制台消息 (全部)")
    print("="*70)

    for i, msg in enumerate(all_messages):
        print(f"\n[{i+1}] {msg['type']}")
        print(f"    文本: {msg['text']}")
        if msg['location']:
            print(f"    位置: {msg['location']}")

    # 获取 taskData
    task_data = page.evaluate('''
        () => {
            if (typeof taskData !== 'undefined') {
                return {
                    type: taskData.type,
                    keys: Object.keys(taskData),
                    has_raw_text: 'raw_text' in taskData,
                    raw_text: taskData.raw_text || '',
                    has_task: 'task' in taskData
                };
            }
            return { error: 'taskData is undefined' };
        }
    ''')

    print("\n" + "="*70)
    print("taskData 信息")
    print("="*70)
    print(f"taskData: {task_data}")

    # 手动触发 renderTasks
    print("\n手动调用 renderTasks()...")
    result = page.evaluate('''
        () => {
            try {
                if (typeof renderTasks === 'function') {
                    renderTasks();
                    return { success: true };
                }
                return { error: 'renderTasks is not defined' };
            } catch (e) {
                return { error: e.message, stack: e.stack };
            }
        }
    ''')

    print(f"renderTasks 调用结果: {result}")

    time.sleep(2)
    page.screenshot(path='confirm_with_errors.png')
    print("\n截图: confirm_with_errors.png")

    input("\n按回车关闭浏览器...")
    browser.close()
