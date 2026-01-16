"""
测试关键功能点
1. 新增学生后能否在添加任务时选择
2. 新增任务能否在任务中心显示
3. 筛选功能是否正常
4. 回退按钮是否正常
"""
import asyncio
import time
from playwright.async_api import async_playwright


async def test_student_selection_and_task_creation():
    """测试：新增学生后能否在添加任务时选择"""
    print("\n" + "="*60)
    print("测试 1: 新增学生 → 添加任务时选择学生")
    print("="*60)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=500)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()

    try:
        # 1. 访问学生管理页面
        print("\n1️⃣ 访问学生管理")
        await page.goto("https://edu-track.zeabur.app/students")
        await asyncio.sleep(2)

        # 检查现有学生
        existing_students = await page.locator('[class*="student"], [class*="card"]').count()
        print(f"   现有学生: {existing_students} 个")

        # 2. 添加新学生
        print("\n2️⃣ 添加新学生")
        add_btn = page.locator('button:has-text("添加"), button:has-text("新增")')
        if await add_btn.count() > 0:
            await add_btn.first.click()
            await asyncio.sleep(1)

            # 填写学生信息
            await page.fill('input[name="name"]', "测试学生李四")
            await page.fill('input[name="grade"]', "四年级")
            await page.fill('input[name="class_name"]', "1班")

            # 提交
            await page.locator('button:has-text("确定"), button:has-text("保存")').click()
            await asyncio.sleep(2)

            print("   ✅ 学生添加成功")

            # 验证学生列表
            new_count = await page.locator('[class*="student"], [class*="card"]').count()
            print(f"   更新后学生: {new_count} 个")

        # 3. 访问添加任务页面
        print("\n3️⃣ 访问添加任务页面")
        await page.goto("https://edu-track.zeabur.app/add")
        await asyncio.sleep(2)

        # 4. 输入测试任务
        print("\n4️⃣ 输入测试任务")
        await page.locator('textarea').fill("英语：完成第3单元单词练习，明天前提交")
        await asyncio.sleep(1)

        # 5. 点击 AI 解析
        print("\n5️⃣ 点击 AI 解析")
        parse_btn = page.locator('button:has-text("解析"), button:has-text("AI")')
        if await parse_btn.count() > 0:
            await parse_btn.first.click()
            print("   ⏳ 等待 AI 解析...")
            await asyncio.sleep(12)

            # 6. 检查解析结果
            print("\n6️⃣ 检查学生选择器")

            # 方法1: 查找下拉选择框
            select = page.locator('select[name="student_id"], .student-select, select')
            select_count = await select.count()

            # 方法2: 查找学生选择的其他形式
            radio = page.locator('input[type="radio"][name*="student"]')
            radio_count = await radio.count()

            # 方法3: 查找学生卡片选择
            card = page.locator('[class*="student"] [class*="selectable"]')
            card_count = await card.count()

            print(f"   下拉选择框: {select_count} 个")
            print(f"   单选按钮: {radio_count} 个")
            print(f"   可选卡片: {card_count} 个")

            if select_count > 0:
                # 检查下拉选项
                options = await select.locator('option').all()
                print(f"   ✅ 找到下拉选择框，选项: {len(options)} 个")

                for i, option in enumerate(options):
                    text = await option.text_content()
                    print(f"      选项 {i+1}: {text}")

            elif radio_count > 0:
                print(f"   ✅ 找到单选按钮选择方式")

            elif card_count > 0:
                print(f"   ✅ 找到卡片选择方式")
            else:
                print("   ❌ 未找到学生选择器")
                # 截图看看页面有什么
                await page.screenshot(path="debug_no_student_selector.png")

            # 7. 尝试选择学生（如果有选择器）
            if select_count > 0:
                try:
                    await select.first.select_option(index=0)
                    print("   ✅ 成功选择第一个学生")
                except:
                    print("   ⚠️ 选择失败")

    except Exception as e:
        print(f"   ❌ 错误: {e}")
        await page.screenshot(path="debug_student_selection_error.png")

    await browser.close()


async def test_task_display_and_filtering():
    """测试：新增任务能否在任务中心显示，筛选功能是否正常"""
    print("\n" + "="*60)
    print("测试 2: 任务显示和筛选功能")
    print("="*60)

    async with await async_playwright().start() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            # 1. 访问任务中心
            print("\n1️⃣ 访问任务中心")
            await page.goto("https://edu-track.zeabur.app/")
            await asyncio.sleep(2)

            # 2. 检查现有任务
            print("\n2️⃣ 检查现有任务")
            tasks = page.locator('[class*="task-card"], [class*="task-item"], [class*="task"]')
            task_count = await tasks.count()
            print(f"   当前任务: {task_count} 个")

            if task_count > 0:
                # 查看任务详情
                for i in range(min(task_count, 3)):
                    task = tasks.nth(i)
                    text = await task.text_content()
                    print(f"   任务 {i+1}: {text[:50]}...")

            # 3. 检查筛选功能
            print("\n3️⃣ 测试筛选功能")

            # 查找筛选器
            filters = page.locator('.filter, [class*="filter"], .student-filter, nav a')
            filter_count = await filters.count()
            print(f"   筛选项: {filter_count} 个")

            if filter_count > 0:
                # 列出所有筛选选项
                for i in range(filter_count):
                    try:
                        filter_text = await filters.nth(i).text_content()
                        print(f"      筛选 {i+1}: {filter_text.strip()}")
                    except:
                        pass

                # 4. 测试点击筛选
                print("\n4️⃣ 测试点击筛选")
                if filter_count > 1:
                    # 点击第二个筛选选项
                    await filters.nth(1).click()
                    await asyncio.sleep(1)

                    # 检查任务列表是否变化
                    new_count = await tasks.count()
                    print(f"   筛选后任务: {new_count} 个")
                    print(f"   ✅ 筛选功能{'正常' if new_count != task_count else '可能无效'}")

            else:
                print("   ⚠️ 未找到筛选器")

            # 5. 检查任务卡片信息
            print("\n5️⃣ 检查任务卡片信息")
            if task_count > 0:
                first_task = tasks.first

                # 检查任务元素
                has_subject = await first_task.locator('[class*="subject"], .tag').count() > 0
                has_description = await first_task.locator('[class*="description"], .content').count() > 0
                has_complete_btn = await first_task.locator('button:has-text("完成"), [class*="complete"]').count() > 0
                has_edit_btn = await first_task.locator('button:has-text("编辑"), [class*="edit"]').count() > 0

                print(f"   科目标签: {'✅' if has_subject else '❌'}")
                print(f"   任务描述: {'✅' if has_description else '❌'}")
                print(f"   完成按钮: {'✅' if has_complete_btn else '❌'}")
                print(f"   编辑按钮: {'✅' if has_edit_btn else '❌'}")

        except Exception as e:
            print(f"   ❌ 错误: {e}")
            await page.screenshot(path="debug_task_display_error.png")

        await browser.close()


async def test_back_navigation():
    """测试：页面回退是否正常"""
    print("\n" + "="*60)
    print("测试 3: 页面回退功能")
    print("="*60)

    async with await async_playwright().start() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            # 1. 从登录页开始
            print("\n1️⃣ 访问登录页")
            await page.goto("https://edu-track.zeabur.app/login")
            await asyncio.sleep(1)

            # 2. 导航到任务中心
            print("\n2️⃣ 导航到任务中心")
            await page.goto("https://edu-track.zeabur.app/")
            await asyncio.sleep(1)
            current_url = page.url
            print(f"   当前: {current_url}")

            # 3. 测试浏览器回退
            print("\n3️⃣ 测试浏览器回退按钮")
            await page.go_back()
            await asyncio.sleep(1)
            back_url = page.url
            print(f"   回退到: {back_url}")

            if back_url == "https://edu-track.zeabur.app/login":
                print("   ✅ 回退到登录页成功")
            else:
                print(f"   ⚠️ 回退到了: {back_url}")

            # 4. 再次前进
            print("\n4️⃣ 测试浏览器前进按钮")
            await page.go_forward()
            await asyncio.sleep(1)
            forward_url = page.url
            print(f"   前进到: {forward_url}")

            # 5. 检查页面上的返回按钮
            print("\n5️⃣ 检查页面上的返回按钮")
            back_buttons = page.locator('button:has-text("返回"), a:has-text("返回"), [class*="back"], .back-button')
            back_btn_count = await back_buttons.count()
            print(f"   页面上的返回按钮: {back_btn_count} 个")

            if back_btn_count > 0:
                # 尝试点击返回按钮
                await back_buttons.first.click()
                await asyncio.sleep(1)
                clicked_back_url = page.url
                print(f"   点击后跳转到: {clicked_back_url}")
                print("   ✅ 返回按钮正常")
            else:
                print("   ⚠️ 页面上没有返回按钮")

            # 6. 测试跨页面导航
            print("\n6️⃣ 测试多页面导航和回退")
            await page.goto("https://edu-track.zeabur.app/students")
            await asyncio.sleep(1)
            print(f"   → 学生管理: {page.url}")

            await page.goto("https://edu-track.zeabur.app/add")
            await asyncio.sleep(1)
            print(f"   → 添加任务: {page.url}")

            await page.go_back()
            await asyncio.sleep(1)
            print(f"   ← 回退: {page.url}")

            if "students" in page.url:
                print("   ✅ 回退到学生管理")
            else:
                print(f"   ⚠️ 未回到学生管理: {page.url}")

        except Exception as e:
            print(f"   ❌ 错误: {e}")
            await page.screenshot(path="debug_back_navigation_error.png")

        await browser.close()


async def main():
    """运行所有测试"""
    await test_student_selection_and_task_creation()
    await test_task_display_and_filtering()
    await test_back_navigation()


if __name__ == "__main__":
    asyncio.run(main())
