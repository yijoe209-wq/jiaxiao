"""
测试 session cookie 在页面跳转时的传递
"""
import asyncio
from playwright.async_api import async_playwright


async def test_cookie_flow():
    """测试 cookie 传递"""
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=1000)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # 1. 登录
        print("\n1. 登录")
        await page.goto("https://edu-track.zeabur.app/login")
        await page.fill('#loginEmail', "flow_test@example.com")
        await page.fill('#loginPassword', "test123456")
        await page.locator('#loginForm button[type="submit"]').click()
        await asyncio.sleep(5)

        # 检查 cookie
        cookies = await context.cookies()
        print(f"   Cookies: {len(cookies)} 个")
        for cookie in cookies:
            print(f"      - {cookie['name']}: {cookie['value'][:20]}...")

        # 2. 直接访问任务中心 API
        print("\n2. 直接访问任务中心 API")
        response = await page.goto("https://edu-track.zeabur.app/api/tasks")
        print(f"   状态码: {response.status}")

        # 获取响应文本
        text = await page.evaluate("() => document.body.innerText")
        print(f"   响应: {text[:200]}...")

        # 3. 访问任务中心页面
        print("\n3. 访问任务中心页面")
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(3)

        # 检查页面标题
        title = await page.title()
        print(f"   页面标题: {title}")

        # 检查控制台日志
        console_logs = await page.evaluate("""
            () => {
                return window.consoleLogs || [];
            }
        """)
        if console_logs:
            print(f"   控制台日志: {console_logs}")

        # 4. 检查 taskList 元素
        task_list = await page.locator('#taskList').count()
        print(f"   taskList 元素: {task_list} 个")

        if task_list > 0:
            inner_html = await page.locator('#taskList').inner_html()
            print(f"   taskList 内容: {inner_html[:200]}...")
        else:
            # 检查是否有空状态提示
            empty = await page.locator('[class*="empty"]').count()
            print(f"   空状态提示: {empty} 个")

        await page.screenshot(path="cookie_flow_test.png")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(test_cookie_flow())
