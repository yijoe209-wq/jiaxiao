"""
完整测试：登录 → 添加任务 → 确认 → 查看任务中心
"""
import asyncio
from playwright.async_api import async_playwright


async def test_real_user_flow():
    """完整模拟真实用户操作"""
    print("\n" + "="*60)
    print("真实用户流程测试")
    print("="*60)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=500)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # ========== 步骤1: 访问登录页 ==========
        print("\n📍 步骤1: 访问登录页")
        await page.goto("https://edu-track.zeabur.app/login")
        await asyncio.sleep(2)

        # ========== 步骤2: 登录（使用已注册账号） ==========
        print("\n📍 步骤2: 登录")
        await page.fill('#loginEmail', "flow_test@example.com")
        await page.fill('#loginPassword', "test123456")
        await asyncio.sleep(1)

        login_btn = page.locator('#loginForm button[type="submit"]')
        await login_btn.click()
        print("   ⏳ 登录中...")
        await asyncio.sleep(5)

        current_url = page.url
        print(f"   当前URL: {current_url}")

        # 检查登录状态
        local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
        print(f"   localStorage: {local_storage[:200]}...")

        # ========== 步骤3: 访问任务中心 ==========
        print("\n📍 步骤3: 访问任务中心")
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(3)

        # 检查任务数量
        tasks = page.locator('[class*="task"]')
        task_count = await tasks.count()
        print(f"   当前任务数: {task_count}")
        await page.screenshot(path="real_01_task_center.png")

        # ========== 步骤4: 添加学生（如果需要） ==========
        print("\n📍 步骤4: 检查学生")
        await page.goto("https://edu-track.zeabur.app/students")
        await asyncio.sleep(2)

        students = await page.locator('.student-item').count()
        print(f"   现有学生: {students} 个")

        if students == 0:
            print("   添加学生...")
            await page.fill('#nameInput', "测试学生")
            await page.select_option('#gradeInput', "五年级")
            await page.fill('#classInput', "1班")

            add_btn = page.locator('button:has-text("添加学生")')
            await add_btn.click()
            await asyncio.sleep(2)
            print("   ✅ 学生添加成功")

        # ========== 步骤5: 添加任务 ==========
        print("\n📍 步骤5: 添加任务")
        await page.goto("https://edu-track.zeabur.app/add")
        await asyncio.sleep(2)

        # 先选择学生
        print("   选择学生...")
        student_select = page.locator('#studentSelect')
        await student_select.select_option(index=0)
        await asyncio.sleep(1)
        print("   ✅ 学生已选择")

        # 输入任务
        print("   输入任务...")
        textarea = page.locator('textarea')
        await textarea.fill("数学：完成第20页练习题，明天提交")
        await asyncio.sleep(1)

        await page.screenshot(path="real_02_before_parse.png")

        # 点击 AI 解析
        print("   点击 AI 解析...")
        parse_btn = page.locator('button:has-text("AI 智能解析")')
        await parse_btn.click()
        print("   ⏳ AI 解析中...")
        await asyncio.sleep(15)

        await page.screenshot(path="real_03_after_parse.png")

        # ========== 步骤6: 确认任务 ==========
        print("\n📍 步骤6: 确认任务")

        # 检查是否跳转到确认页面
        current_url = page.url
        print(f"   当前URL: {current_url}")

        if "confirm" in current_url or "tasks" in current_url:
            # 选择学生
            student_select = page.locator('select[name="student_id"]')
            select_count = await student_select.count()

            if select_count > 0:
                print("   选择学生...")
                await student_select.select_option(index=0)
                await asyncio.sleep(1)

            # 点击确认
            confirm_btn = page.locator('button:has-text("确认"), button:has-text("保存"), button:has-text("提交"), button:has-text("创建")')
            btn_count = await confirm_btn.count()
            print(f"   找到确认按钮: {btn_count} 个")

            if btn_count > 0:
                await confirm_btn.first.click()
                print("   ⏳ 等待确认...")
                await asyncio.sleep(3)

                # 检查是否出现成功弹窗
                success_modal = page.locator('#successModal, [class*="success"]')
                modal_visible = await success_modal.count() > 0
                print(f"   成功弹窗: {'是' if modal_visible else '否'}")

                if modal_visible:
                    print("   点击'查看任务'按钮...")
                    view_btn = page.locator('button:has-text("查看任务"), button:has-text("前往")')
                    await view_btn.click()
                    await asyncio.sleep(3)

        # ========== 步骤7: 检查任务中心 ==========
        print("\n📍 步骤7: 检查任务中心")
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(3)

        await page.screenshot(path="real_04_final_task_center.png")

        # 检查任务列表
        tasks = page.locator('[class*="task"]')
        task_count = await tasks.count()
        print(f"   任务中心任务数: {task_count}")

        if task_count > 0:
            print("   ✅ 成功！任务已显示")
            for i in range(min(task_count, 3)):
                task = tasks.nth(i)
                text = await task.text_content()
                print(f"      任务 {i+1}: {text[:100]}...")
        else:
            print("   ❌ 任务中心仍然没有任务")

            # 打印页面内容
            body_text = await page.locator('body').text_content()
            print(f"   页面内容: {body_text[:200]}...")

        # 检查控制台日志
        console_logs = await page.evaluate("""
            () => {
                const logs = [];
                const originalLog = console.log;
                console.log = function(...args) {
                    logs.push(args.join(' '));
                    originalLog.apply(console, args);
                };
                return window.consoleLogs || [];
            }
        """)
        print(f"   控制台日志: {console_logs}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        await page.screenshot(path="real_error.png")

    finally:
        await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(test_real_user_flow())
