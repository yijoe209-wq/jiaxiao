"""
完整测试：注册 → 登录 → 添加任务 → 跳转任务中心 → 查看任务
"""
import asyncio
from playwright.async_api import async_playwright


async def test_full_user_flow():
    """完整模拟用户操作流程"""
    print("\n" + "="*60)
    print("完整用户流程测试")
    print("="*60)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=1000)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # ========== 步骤1: 访问登录页 ==========
        print("\n📍 步骤1: 访问登录页")
        await page.goto("https://edu-track.zeabur.app/login")
        await asyncio.sleep(2)
        print(f"   当前URL: {page.url}")
        await page.screenshot(path="flow_01_login.png")

        # ========== 步骤2: 切换到注册标签 ==========
        print("\n📍 步骤2: 切换到注册标签")
        register_tab = page.locator('.tab:has-text("注册")')
        await register_tab.click()
        await asyncio.sleep(1)
        print("   ✅ 点击注册标签")

        # ========== 步骤3: 填写注册信息 ==========
        print("\n📍 步骤3: 填写注册信息")
        await page.fill('#registerEmail', "full_test@example.com")
        await page.fill('#registerPassword', "test123456")
        await page.fill('#registerName', "完整流程测试")
        await asyncio.sleep(1)
        await page.screenshot(path="flow_02_filled.png")
        print("   ✅ 表单填写完成")

        # ========== 步骤4: 提交注册 ==========
        print("\n📍 步骤4: 提交注册")
        submit_btn = page.locator('#registerForm button[type="submit"]')
        await submit_btn.click()
        print("   ⏳ 等待跳转...")
        await asyncio.sleep(5)

        current_url = page.url
        print(f"   当前URL: {current_url}")
        await page.screenshot(path="flow_03_after_register.png")

        # ========== 步骤5: 检查是否登录成功 ==========
        print("\n📍 步骤5: 检查登录状态")
        # 检查 localStorage
        local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
        print(f"   localStorage: {local_storage[:200]}...")

        # ========== 步骤6: 访问任务中心 ==========
        print("\n📍 步骤6: 访问任务中心")
        await page.goto("https://edu-track.zeabur.app/")
        await asyncio.sleep(3)
        print(f"   当前URL: {page.url}")
        await page.screenshot(path="flow_04_task_center.png")

        # 检查任务列表
        tasks = page.locator('[class*="task"]')
        task_count = await tasks.count()
        print(f"   当前任务数: {task_count}")

        # ========== 步骤7: 添加学生（如果没有） ==========
        print("\n📍 步骤7: 添加学生")
        await page.goto("https://edu-track.zeabur.app/students")
        await asyncio.sleep(2)

        # 点击添加学生按钮
        add_student_btn = page.locator('button:has-text("添加学生")')
        if await add_student_btn.count() > 0:
            await add_student_btn.click()
            await asyncio.sleep(1)

            # 填写学生信息
            await page.fill('#nameInput', "测试学生小明")
            await page.select_option('#gradeInput', "五年级")
            await page.fill('#classInput', "3班")
            await asyncio.sleep(1)

            # 提交
            submit = page.locator('button:has-text("添加学生")')
            await submit.click()
            await asyncio.sleep(2)
            print("   ✅ 学生添加成功")

        # ========== 步骤8: 添加任务 ==========
        print("\n📍 步骤8: 添加任务")
        await page.goto("https://edu-track.zeabur.app/add")
        await asyncio.sleep(2)
        await page.screenshot(path="flow_05_add_task.png")

        # 输入任务
        textarea = page.locator('textarea')
        await textarea.fill("英语：完成第3单元单词练习，明天前提交")
        await asyncio.sleep(1)

        # 点击 AI 解析
        parse_btn = page.locator('button:has-text("AI 智能解析")')
        await parse_btn.click()
        print("   ⏳ 等待 AI 解析...")
        await asyncio.sleep(15)

        await page.screenshot(path="flow_06_after_parse.png")

        # ========== 步骤9: 确认任务 ==========
        print("\n📍 步骤9: 确认任务")
        # 查找确认按钮
        confirm_btn = page.locator('button:has-text("确认"), button:has-text("保存")')
        btn_count = await confirm_btn.count()
        print(f"   找到确认按钮: {btn_count} 个")

        if btn_count > 0:
            await confirm_btn.first.click()
            print("   ⏳ 等待跳转到任务中心...")
            await asyncio.sleep(5)

            await page.screenshot(path="flow_07_after_confirm.png")

            # ========== 步骤10: 检查任务中心 ==========
            print("\n📍 步骤10: 检查任务中心")
            current_url = page.url
            print(f"   当前URL: {current_url}")

            if "edu-track.zeabur.app" in current_url:
                await asyncio.sleep(2)

                # 检查任务列表
                tasks = page.locator('[class*="task"]')
                task_count = await tasks.count()
                print(f"   ✅ 任务中心任务数: {task_count}")

                if task_count > 0:
                    # 查看前3个任务
                    for i in range(min(task_count, 3)):
                        task = tasks.nth(i)
                        text = await task.text_content()
                        print(f"      任务 {i+1}: {text[:100]}...")
                else:
                    print("   ❌ 任务中心仍然没有任务！")

                    # 打印控制台日志
                    console_logs = await page.evaluate("() => window.consoleLogs || []")
                    print(f"   控制台日志: {console_logs}")

        await page.screenshot(path="flow_08_final.png")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        await page.screenshot(path="flow_error.png")

    finally:
        await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(test_full_user_flow())
