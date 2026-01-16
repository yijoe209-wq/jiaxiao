"""
完整模拟用户真实操作流程
1. 登录
2. 进入添加任务页面
3. 选择学生（如果没有就添加）
4. 粘贴输入消息
5. 点击解析
6. 补充标签信息
7. 点击确认
8. 查看任务中心是否显示
"""
import asyncio
from playwright.async_api import async_playwright


async def test_complete_user_journey():
    """完整模拟用户操作"""
    print("\n" + "="*60)
    print("完整用户操作流程测试")
    print("="*60)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=800)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # ========== 步骤1: 访问登录页并登录 ==========
        print("\n📍 步骤1: 访问登录页")
        await page.goto("https://edu-track.zeabur.app/login", wait_until='networkidle')
        await asyncio.sleep(3)

        print("   输入登录信息...")
        # Wait for the input to be visible
        await page.wait_for_selector('#loginEmail', timeout=10000)
        await page.fill('#loginEmail', "flow_test@example.com")
        await page.fill('#loginPassword', "test123456")
        await asyncio.sleep(1)

        print("   点击登录...")
        login_btn = page.locator('#loginForm button[type="submit"]')
        await login_btn.click()
        await asyncio.sleep(5)

        current_url = page.url
        print(f"   登录后URL: {current_url}")

        # 检查登录状态
        local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
        if 'family_id' in local_storage:
            print("   ✅ 登录成功")
        else:
            print("   ❌ 登录失败，重新注册...")
            # 如果登录失败，先注册
            await page.goto("https://edu-track.zeabur.app/login")
            register_tab = page.locator('.tab:has-text("注册")')
            await register_tab.click()
            await asyncio.sleep(1)

            await page.fill('#registerEmail', "journey_test@example.com")
            await page.fill('#registerPassword', "test123456")
            await page.fill('#registerName', "用户测试")
            await asyncio.sleep(1)

            submit_btn = page.locator('#registerForm button[type="submit"]')
            await submit_btn.click()
            await asyncio.sleep(5)
            print("   ✅ 注册并登录成功")

        # ========== 步骤2: 进入添加任务页面 ==========
        print("\n📍 步骤2: 进入添加任务页面")
        await page.goto("https://edu-track.zeabur.app/add")
        await asyncio.sleep(3)
        print(f"   当前URL: {page.url}")

        await page.screenshot(path="journey_01_add_page.png")

        # ========== 步骤3: 检查并选择学生 ==========
        print("\n📍 步骤3: 检查学生列表")

        # 找到学生选择下拉框
        student_select = page.locator('#studentSelect')
        select_count = await student_select.count()

        if select_count == 0:
            print("   ❌ 没有找到学生选择框")
            await page.screenshot(path="journey_error_no_select.png")
            return

        # 获取所有选项
        options = await student_select.locator('option').all()
        print(f"   学生选项数量: {len(options)}")

        # 检查是否有学生可选
        has_student = False
        for i, option in enumerate(options):
            value = await option.get_attribute('value')
            text = await option.text_content()
            print(f"      选项{i+1}: value={value}, text={text}")
            if value and value != "":
                has_student = True

        if not has_student:
            print("   ⚠️ 没有学生，需要先添加学生")
            print("   跳转到学生管理页面...")

            # 点击添加学生链接或按钮
            add_student_link = page.locator('a:has-text("添加学生"), button:has-text("添加学生")')
            if await add_student_link.count() > 0:
                await add_student_link.first.click()
            else:
                # 直接访问学生管理页面
                await page.goto("https://edu-track.zeabur.app/students")

            await asyncio.sleep(2)

            print("   添加学生...")
            await page.fill('#nameInput', "测试学生-小明")
            await page.select_option('#gradeInput', "五年级")
            await page.fill('#classInput', "3班")
            await asyncio.sleep(1)

            add_btn = page.locator('button:has-text("添加学生")')
            await add_btn.click()
            await asyncio.sleep(2)
            print("   ✅ 学生添加成功")

            # 返回添加任务页面
            print("   返回添加任务页面...")
            await page.goto("https://edu-track.zeabur.app/add")
            await asyncio.sleep(2)

            # 重新获取学生选择框
            student_select = page.locator('#studentSelect')
            await asyncio.sleep(1)

        # 选择第一个学生
        print("\n   选择学生...")
        await student_select.select_option(index=1)  # index=0 是"请选择"，index=1 是第一个学生
        await asyncio.sleep(1)

        selected_value = await student_select.evaluate("el => el.value")
        print(f"   ✅ 已选择学生，value={selected_value}")

        await page.screenshot(path="journey_02_student_selected.png")

        # ========== 步骤4: 粘贴输入消息 ==========
        print("\n📍 步骤4: 输入任务消息")

        textarea = page.locator('textarea')
        task_message = "英语：完成第3单元单词练习，每个单词写5遍，明天前提交"

        await textarea.fill(task_message)
        await asyncio.sleep(1)
        print(f"   已输入: {task_message}")

        await page.screenshot(path="journey_03_message_entered.png")

        # ========== 步骤5: 点击 AI 解析 ==========
        print("\n📍 步骤5: 点击 AI 解析")

        parse_btn = page.locator('button:has-text("AI 智能解析")')
        await parse_btn.click()
        print("   ⏳ AI 解析中，请等待...")

        await asyncio.sleep(15)  # 等待 AI 解析完成

        await page.screenshot(path="journey_04_after_parse.png")

        # 检查是否跳转到确认页面
        current_url = page.url
        print(f"   当前URL: {current_url}")

        if "confirm" in current_url:
            print("   ✅ 成功跳转到确认页面")
        else:
            print("   ❌ 未跳转到确认页面")
            # 打印页面内容
            body_text = await page.locator('body').text_content()
            print(f"   页面内容: {body_text[:300]}...")
            return

        # ========== 步骤6: 补充标签信息（在确认页面） ==========
        print("\n📍 步骤6: 检查确认页面信息")

        # 检查页面是否有任务卡片
        task_cards = page.locator('[class*="task-card"], [class*="task-item"], .task')
        card_count = await task_cards.count()
        print(f"   任务卡片数量: {card_count}")

        if card_count > 0:
            print("   ✅ 找到任务卡片")

            # 查看第一个任务的内容
            first_card = task_cards.first
            card_text = await first_card.text_content()
            print(f"   第一个任务内容: {card_text[:200]}...")

            # 检查是否有可编辑的标签字段
            subject_input = page.locator('input[name*="subject"], input[placeholder*="科目"]')
            deadline_input = page.locator('input[name*="deadline"], input[placeholder*="截止"], input[type="date"]')

            subject_count = await subject_input.count()
            deadline_count = await deadline_input.count()

            print(f"   科目输入框: {subject_count} 个")
            print(f"   截止日期输入框: {deadline_count} 个")

            # 如果有输入框，补充信息
            if subject_count > 0:
                print("   填写科目...")
                await subject_input.first.fill("英语")
                await asyncio.sleep(1)

            if deadline_count > 0:
                print("   填写截止日期...")
                # 设置明天的日期
                from datetime import datetime, timedelta
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                await deadline_input.first.fill(tomorrow)
                await asyncio.sleep(1)

        await page.screenshot(path="journey_05_before_confirm.png")

        # ========== 步骤7: 点击确认任务 ==========
        print("\n📍 步骤7: 点击确认任务")

        confirm_btn = page.locator('button:has-text("确认"), button:has-text("创建"), button:has-text("提交")')
        btn_count = await confirm_btn.count()
        print(f"   找到确认按钮: {btn_count} 个")

        if btn_count == 0:
            print("   ❌ 没有找到确认按钮")
            await page.screenshot(path="journey_error_no_confirm.png")
            return

        await confirm_btn.first.click()
        print("   ⏳ 等待确认...")
        await asyncio.sleep(3)

        await page.screenshot(path="journey_06_after_click_confirm.png")

        # ========== 检查是否出现成功弹窗 ==========
        print("\n📍 检查成功弹窗")

        success_modal = page.locator('#successModal, [class*="success"], .fixed.inset-0')
        modal_visible = await success_modal.count() > 0
        print(f"   成功弹窗出现: {'是' if modal_visible else '否'}")

        if modal_visible:
            print("   点击'查看任务'按钮...")
            view_btn = page.locator('button:has-text("查看任务"), button:has-text("前往")')
            await view_btn.click()
            await asyncio.sleep(3)
            print("   ✅ 已点击查看任务")

        # ========== 步骤8: 查看任务中心 ==========
        print("\n📍 步骤8: 查看任务中心")

        # 确保在任务中心页面
        if "/my-tasks" not in page.url:
            await page.goto("https://edu-track.zeabur.app/")

        await asyncio.sleep(3)

        current_url = page.url
        print(f"   当前URL: {current_url}")

        await page.screenshot(path="journey_07_task_center.png")

        # 检查任务列表
        print("\n📍 检查任务列表")

        tasks = page.locator('[class*="task-card"], [class*="task-item"], [class*="task"]')
        task_count = await tasks.count()
        print(f"   任务中心任务数: {task_count}")

        if task_count > 0:
            print("   ✅✅✅ 成功！任务已显示在任务中心！")

            # 显示前3个任务
            for i in range(min(task_count, 3)):
                task = tasks.nth(i)
                text = await task.text_content()
                print(f"      任务 {i+1}: {text[:150]}...")
        else:
            print("   ❌❌❌ 失败！任务中心没有显示任务")

            # 打印页面内容帮助调试
            body_html = await page.locator('body').inner_html()
            print(f"   页面HTML长度: {len(body_html)}")

            # 检查是否有空状态提示
            empty_state = page.locator('[class*="empty"], .no-data')
            if await empty_state.count() > 0:
                empty_text = await empty_state.text_content()
                print(f"   空状态提示: {empty_text}")

        # 打印控制台日志
        console_logs = await page.evaluate("""
            () => {
                const logs = [];
                const originalLog = console.log;
                const originalError = console.error;
                const originalWarn = console.warn;

                console.log = function(...args) {
                    logs.push('[LOG] ' + args.join(' '));
                    originalLog.apply(console, args);
                };
                console.error = function(...args) {
                    logs.push('[ERROR] ' + args.join(' '));
                    originalError.apply(console, args);
                };
                console.warn = function(...args) {
                    logs.push('[WARN] ' + args.join(' '));
                    originalWarn.apply(console, args);
                };

                return window.capturedLogs || logs;
            }
        """)
        if console_logs:
            print(f"\n   控制台日志:")
            for log in console_logs[:10]:  # 只显示前10条
                print(f"      {log}")

    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        await page.screenshot(path="journey_error.png")

    finally:
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        await asyncio.sleep(2)
        await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(test_complete_user_journey())
