"""检查浏览器控制台日志"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=500)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()
    
    # 收集控制台日志
    console_messages = []
    page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
    
    try:
        # 登录
        await page.goto("https://edu-track.zeabur.app/login", wait_until='networkidle')
        await page.fill('#loginEmail', "flow_test@example.com")
        await page.fill('#loginPassword', "test123456")
        await page.locator('#loginForm button[type=\"submit\"]').click()
        await asyncio.sleep(5)
        
        # 直接访问任务中心
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(3)
        
        print("\n=== 浏览器控制台日志 ===")
        for msg in console_messages:
            print(msg)
        
        # 检查 taskList 内容
        task_list = await page.locator('#taskList').inner_html()
        print(f"\ntaskList HTML: {task_list[:200]}...")
        
    finally:
        await browser.close()

asyncio.run(main())
