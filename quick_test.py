"""
快速测试关键功能
"""
import asyncio
from playwright.async_api import async_playwright


async def quick_test():
    """快速测试 3 个关键问题"""
    print("\n" + "="*60)
    print("快速测试关键功能")
    print("="*60)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=1000)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # 测试 1: 任务显示
        print("\n测试 1: 任务中心显示")
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(2)

        tasks = await page.locator('[class*="task"]').count()
        print(f"✓ 任务数量: {tasks}")

        # 测试 2: 筛选功能
        print("\n测试 2: 筛选功能")
        filters = await page.locator('.filter, nav a').count()
        print(f"✓ 筛选项: {filters} 个")

        if filters > 0:
            # 记录初始状态
            initial_tasks = tasks

            # 点击筛选
            await page.locator('.filter, nav a').nth(1).click()
            await asyncio.sleep(1)

            # 检查变化
            after_filter = await page.locator('[class*="task"]').count()
            print(f"✓ 筛选后任务: {after_filter} 个")

            if after_filter != initial_tasks:
                print("✓ 筛选功能正常")
            else:
                print("⚠️ 筛选可能无效")

        # 测试 3: 页面回退
        print("\n测试 3: 页面回退")
        await page.goto("https://edu-track.zeabur.app/students")
        await asyncio.sleep(1)
        print(f"✓ 当前: {page.url[:50]}...")

        await page.go_back()
        await asyncio.sleep(1)
        print(f"✓ 回退后: {page.url[:50]}...")

        # 测试 4: 学生管理和任务创建
        print("\n测试 4: 添加任务时能否选择学生")
        await page.goto("https://edu-track.zeabur.app/add")
        await asyncio.sleep(2)

        # 输入任务
        await page.locator('textarea').fill("测试任务")
        await asyncio.sleep(0.5)

        # 检查学生选择器
        select = await page.locator('select').count()
        radio = await page.locator('input[type="radio"]').count()
        cards = await page.locator('[class*="student"]').count()

        print(f"✓ 下拉选择: {select} 个")
        print(f"✓ 单选按钮: {radio} 个")
        print(f"✓ 学生卡片: {cards} 个")

        if select > 0 or radio > 0 or cards > 0:
            print("✓ 有学生选择方式")
        else:
            print("⚠️ 未找到学生选择器")
            await page.screenshot(path="no_student_selector.png")

        await asyncio.sleep(2)

        # 截图保存
        await page.screenshot(path="test_result.png")
        print("\n✓ 截图已保存: test_result.png")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        await page.screenshot(path="test_error.png")

    finally:
        await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(quick_test())
