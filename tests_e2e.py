"""
Playwright E2E 测试
家校任务管理助手 - 完整用户流程测试

运行前准备:
1. 安装依赖: pip install playwright pytest pytest-asyncio
2. 安装浏览器: playwright install chromium
3. 运行测试: pytest tests_e2e.py -v --headed

或者直接运行: python tests_e2e.py
"""

import asyncio
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, expect


class EduTrackTest:
    """家校任务管理助手 E2E 测试"""

    def __init__(self, base_url="https://edu-track.zeabur.app"):
        self.base_url = base_url
        self.browser = None
        self.context = None
        self.page = None

        # 测试数据
        self.test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        self.test_password = "test123456"
        self.test_parent_name = "测试家长"

        # 现有账号（用于登录测试）
        self.existing_email = "alves820@live.cn"
        # 注意: 需要手动设置密码

    async def setup(self):
        """初始化浏览器"""
        print("\n" + "="*60)
        print("🚀 启动测试环境")
        print("="*60)

        p = await async_playwright().start()
        self.browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口
            slow_mo=500  # 放慢操作速度，便于观察
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN'
        )
        self.page = await self.context.new_page()

        print(f"✅ 浏览器已启动")
        print(f"🌐 测试环境: {self.base_url}")

    async def teardown(self):
        """清理资源"""
        print("\n" + "="*60)
        print("🧹 清理测试环境")
        print("="*60)

        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

        print("✅ 浏览器已关闭")

    async def take_screenshot(self, name):
        """截图"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_screenshot_{name}_{timestamp}.png"
        await self.page.screenshot(path=filename)
        print(f"📸 截图已保存: {filename}")

    async def wait(self, seconds=1):
        """等待"""
        await asyncio.sleep(seconds)

    # ========== 测试场景 ==========

    async def test_scenario_1_register_and_login(self):
        """场景 1: 新用户注册和首次使用"""
        print("\n" + "="*60)
        print("📝 场景 1: 新用户注册和首次使用")
        print("="*60)

        # 1. 访问登录页面
        print(f"\n1️⃣ 访问登录页面: {self.base_url}/login")
        await self.page.goto(f"{self.base_url}/login")
        await self.wait(2)

        # 检查页面标题
        title = await self.page.title()
        print(f"   页面标题: {title}")
        assert "登录" in title or "注册" in title

        # 2. 切换到注册标签
        print("\n2️⃣ 切换到注册标签")
        register_tab = self.page.locator('.tab:has-text("注册")')
        await register_tab.first.click()
        await self.wait(1)

        # 3. 填写注册信息
        print("\n3️⃣ 填写注册信息")
        print(f"   邮箱: {self.test_email}")
        print(f"   密码: {self.test_password}")
        print(f"   家长姓名: {self.test_parent_name}")

        await self.page.fill('#registerEmail', self.test_email)
        await self.page.fill('#registerPassword', self.test_password)

        # 查找家长姓名输入框
        parent_name_input = self.page.locator('input[placeholder*="家长"], input[placeholder*="姓名"]')
        if await parent_name_input.count() > 0:
            await parent_name_input.fill(self.test_parent_name)
        else:
            print("   ⚠️ 未找到家长姓名输入框")

        await self.wait(1)

        # 4. 提交注册
        print("\n4️⃣ 提交注册")
        async with self.page.expect_response(
            re.compile(r"/api/register"),
            timeout=10000
        ) as response_info:
            await self.page.locator('#registerForm button[type="submit"]').click()

        response = await response_info.value
        status = response.status
        print(f"   响应状态码: {status}")

        if status == 200:
            print("   ✅ 注册成功")
        else:
            text = await response.text()
            print(f"   ❌ 注册失败: {text}")
            await self.take_screenshot("register_failed")

        await self.wait(3)

        # 5. 验证登录状态
        print("\n5️⃣ 验证登录状态")
        current_url = self.page.url
        print(f"   当前 URL: {current_url}")

        # 检查是否跳转到首页
        if current_url == f"{self.base_url}/" or current_url == f"{self.base_url}":
            print("   ✅ 自动跳转到首页")
        else:
            print(f"   ⚠️ 未跳转到首页，当前: {current_url}")

        await self.take_screenshot("after_register")

    async def test_scenario_2_add_student(self):
        """场景 3: 添加学生信息"""
        print("\n" + "="*60)
        print("👨‍🎓 场景 3: 添加学生信息")
        print("="*60)

        # 1. 访问学生管理页面
        print(f"\n1️⃣ 访问学生管理页面")
        await self.page.goto(f"{self.base_url}/students")
        await self.wait(2)

        # 2. 检查页面状态
        print("\n2️⃣ 检查页面状态")
        empty_state = await self.page.locator('text=暂无学生').count()
        if empty_state > 0:
            print("   ✅ 显示暂无学生提示")
        else:
            print("   ℹ️ 已有学生数据")

        # 3. 点击添加学生
        print("\n3️⃣ 点击添加学生按钮")
        add_button = self.page.locator('button:has-text("添加学生"), button:has-text("新增学生")')
        if await add_button.count() > 0:
            await add_button.first.click()
            await self.wait(1)
        else:
            print("   ⚠️ 未找到添加学生按钮")

        # 4. 填写学生信息
        print("\n4️⃣ 填写学生信息")
        student_name = "张三"
        student_grade = "三年级"
        student_class = "2班"

        print(f"   姓名: {student_name}")
        print(f"   年级: {student_grade}")
        print(f"   班级: {student_class}")

        await self.page.fill('input[name="name"]', student_name)
        await self.page.fill('input[name="grade"]', student_grade)
        await self.page.fill('input[name="class_name"]', student_class)
        await self.wait(1)

        # 5. 提交表单
        print("\n5️⃣ 提交表单")
        async with self.page.expect_response(
            re.compile(r"/api/students"),
            timeout=10000
        ) as response_info:
            await self.page.click('button:has-text("确定"), button:has-text("保存"), button:has-text("提交")')

        response = await response_info.value
        status = response.status
        print(f"   响应状态码: {status}")

        if status == 200:
            print("   ✅ 添加学生成功")
        else:
            text = await response.text()
            print(f"   ❌ 添加失败: {text}")
            await self.take_screenshot("add_student_failed")

        await self.wait(2)

        # 6. 验证学生信息
        print("\n6️⃣ 验证学生信息")
        student_card = self.page.locator(f'text={student_name}')
        if await student_card.count() > 0:
            print(f"   ✅ 找到学生: {student_name}")
        else:
            print(f"   ❌ 未找到学生: {student_name}")
            await self.take_screenshot("verify_student_failed")

        await self.take_screenshot("after_add_student")

    async def test_scenario_4_quick_add_task(self):
        """场景 4: 快速添加任务（AI 解析）"""
        print("\n" + "="*60)
        print("📋 场景 4: 快速添加任务（AI 解析）")
        print("="*60)

        # 1. 访问快速添加页面
        print(f"\n1️⃣ 访问快速添加页面")
        await self.page.goto(f"{self.base_url}/add")
        await self.wait(2)

        # 2. 输入作业消息（单任务）
        print("\n2️⃣ 输入作业消息")
        task_message = "英语：1-4单元粗体字单词一英一汉；4单元短语一英一汉；打卡"
        print(f"   消息内容: {task_message}")

        textarea = self.page.locator('textarea[name="message"], textarea')
        await textarea.fill(task_message)
        await self.wait(1)

        # 3. 点击 AI 解析
        print("\n3️⃣ 点击 AI 解析按钮")
        parse_button = self.page.locator('button:has-text("AI 解析"), button:has-text("解析")')
        await parse_button.click()
        print("   ⏳ 等待 AI 解析...")

        # 等待解析完成（10-15秒）
        await self.wait(12)

        # 4. 检查解析结果
        print("\n4️⃣ 检查解析结果")
        await self.take_screenshot("after_parse")

        # 查找任务预览
        task_preview = self.page.locator('.task-preview, .parsed-task, [class*="task"]')
        if await task_preview.count() > 0:
            print("   ✅ 显示任务预览")
        else:
            print("   ⚠️ 未显示任务预览")
            await self.take_screenshot("parse_no_result")

        # 5. 选择学生
        print("\n5️⃣ 选择学生")
        student_select = self.page.locator('select[name="student_id"], .student-select')
        if await student_select.count() > 0:
            await student_select.select_option(index=0)
            print("   ✅ 已选择学生")
        else:
            print("   ⚠️ 未找到学生选择器")

        await self.wait(1)

        # 6. 确认创建
        print("\n6️⃣ 确认创建任务")
        confirm_button = self.page.locator('button:has-text("确认"), button:has-text("创建")')

        try:
            async with self.page.expect_response(
                re.compile(r"/api/confirm"),
                timeout=10000
            ) as response_info:
                await confirm_button.click()

            response = await response_info.value
            status = response.status
            print(f"   响应状态码: {status}")

            if status == 200:
                print("   ✅ 任务创建成功")
            else:
                text = await response.text()
                print(f"   ⚠️ 创建响应: {text}")

        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            await self.take_screenshot("create_task_failed")

        await self.wait(3)

        # 7. 验证跳转到任务中心
        print("\n7️⃣ 验证跳转到任务中心")
        current_url = self.page.url
        print(f"   当前 URL: {current_url}")

        if "/tasks" in current_url or current_url.endswith("/"):
            print("   ✅ 已跳转到任务中心")
        else:
            print(f"   ⚠️ 未跳转到任务中心")

        await self.take_screenshot("task_center")

    async def test_scenario_5_task_center(self):
        """场景 5: 任务中心管理"""
        print("\n" + "="*60)
        print("🎯 场景 5: 任务中心管理")
        print("="*60)

        # 1. 访问任务中心
        print(f"\n1️⃣ 访问任务中心")
        await self.page.goto(f"{self.base_url}/")
        await self.wait(2)

        # 2. 检查任务列表
        print("\n2️⃣ 检查任务列表")
        task_cards = self.page.locator('[class*="task-card"], .task-item, [class*="task"]')
        count = await task_cards.count()
        print(f"   任务数量: {count}")

        if count > 0:
            print("   ✅ 找到任务")

            # 获取第一个任务的文本
            first_task = task_cards.first
            text = await first_task.text_content()
            print(f"   第一个任务: {text[:100]}...")
        else:
            print("   ⚠️ 暂无任务")

        await self.take_screenshot("task_center_list")

        # 3. 检查筛选功能
        print("\n3️⃣ 检查筛选功能")
        filter_all = self.page.locator('text=全部, [data-filter="all"]')
        if await filter_all.count() > 0:
            print("   ✅ 找到筛选器")
        else:
            print("   ⚠️ 未找到筛选器")

    async def test_scenario_6_complete_task(self):
        """场景 6: 完成和编辑任务"""
        print("\n" + "="*60)
        print("✅ 场景 6: 完成和编辑任务")
        print("="*60)

        # 1. 访问任务中心
        print(f"\n1️⃣ 访问任务中心")
        await self.page.goto(f"{self.base_url}/")
        await self.wait(2)

        # 2. 查找未完成任务
        print("\n2️⃣ 查找未完成任务")
        complete_button = self.page.locator('button:has-text("完成"), [class*="complete"]')

        if await complete_button.count() > 0:
            print("   ✅ 找到完成按钮")
            await self.wait(1)

            # 3. 标记任务完成
            print("\n3️⃣ 标记任务完成")

            try:
                async with self.page.expect_response(
                    re.compile(r"/api/tasks/.*/complete"),
                    timeout=10000
                ) as response_info:
                    await complete_button.first.click()

                response = await response_info.value
                status = response.status
                print(f"   响应状态码: {status}")

                if status == 200:
                    print("   ✅ 任务已完成")
                else:
                    print(f"   ⚠️ 状态码: {status}")

            except Exception as e:
                print(f"   ❌ 操作失败: {e}")

            await self.wait(2)
            await self.take_screenshot("after_complete")

        else:
            print("   ⚠️ 未找到完成按钮（可能没有任务或都已完成）")

    async def test_scenario_7_multi_task(self):
        """场景 7: 多任务批量确认"""
        print("\n" + "="*60)
        print("📊 场景 7: 多任务批量确认")
        print("="*60)

        # 1. 访问快速添加页面
        print(f"\n1️⃣ 访问快速添加页面")
        await self.page.goto(f"{self.base_url}/add")
        await self.wait(2)

        # 2. 输入多科目作业消息
        print("\n2️⃣ 输入多科目作业消息")
        task_message = """
1.英语：1-4单元粗体字单词一英一汉；4单元短语一英一汉；打卡
2.政治：卷子，3题不写；地理：第一单元卷子写完；历史：卷子；生物：无作业
3.语文：文言文卷子四题写完；卷子写完
4.数学：卷子写完；上课写的4题研究一下
        """.strip()
        print(f"   消息长度: {len(task_message)} 字")

        textarea = self.page.locator('textarea[name="message"], textarea')
        await textarea.fill(task_message)
        await self.wait(1)

        # 3. 点击 AI 解析
        print("\n3️⃣ 点击 AI 解析按钮")
        parse_button = self.page.locator('button:has-text("AI 解析"), button:has-text("解析")')
        await parse_button.click()
        print("   ⏳ 等待 AI 解析...")

        # 等待解析完成（10-15秒）
        await self.wait(15)

        # 4. 检查解析结果
        print("\n4️⃣ 检查解析结果")
        await self.take_screenshot("after_multi_parse")

        # 查找任务数量提示
        task_count = self.page.locator('text=/共.*条任务/')
        if await task_count.count() > 0:
            count_text = await task_count.text_content()
            print(f"   ✅ {count_text}")
        else:
            print("   ⚠️ 未找到任务数量提示")

        # 5. 确认创建
        print("\n5️⃣ 确认创建所有任务")
        confirm_button = self.page.locator('button:has-text("确认"), button:has-text("创建")')

        try:
            await confirm_button.click()
            await self.wait(3)
            print("   ✅ 已提交创建")
        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            await self.take_screenshot("multi_create_failed")

        await self.take_screenshot("after_multi_create")

    async def test_scenario_9_logout(self):
        """场景 9: 退出登录"""
        print("\n" + "="*60)
        print("🚪 场景 9: 退出登录")
        print("="*60)

        # 1. 访问退出页面
        print(f"\n1️⃣ 访问退出登录")
        await self.page.goto(f"{self.base_url}/logout")
        await self.wait(2)

        # 2. 验证跳转到登录页
        print("\n2️⃣ 验证跳转到登录页")
        current_url = self.page.url
        print(f"   当前 URL: {current_url}")

        if "/login" in current_url:
            print("   ✅ 已跳转到登录页")
        else:
            print(f"   ⚠️ 当前 URL: {current_url}")

        await self.take_screenshot("after_logout")

        # 3. 尝试访问受保护页面
        print("\n3️⃣ 尝试访问受保护页面")
        await self.page.goto(f"{self.base_url}/")
        await self.wait(2)

        current_url = self.page.url
        if "/login" in current_url:
            print("   ✅ 正确重定向到登录页")
        else:
            print(f"   ⚠️ 未重定向，当前: {current_url}")

    # ========== 完整测试流程 ==========

    async def run_all_tests(self):
        """运行所有测试场景"""
        try:
            await self.setup()

            # 场景 1: 注册（使用新账号）
            await self.test_scenario_1_register_and_login()

            # 场景 3: 添加学生
            await self.test_scenario_2_add_student()

            # 场景 4: 快速添加单任务
            await self.test_scenario_4_quick_add_task()

            # 场景 5: 任务中心
            await self.test_scenario_5_task_center()

            # 场景 6: 完成任务
            await self.test_scenario_6_complete_task()

            # 场景 7: 多任务批量确认
            await self.test_scenario_7_multi_task()

            # 场景 9: 退出登录
            await self.test_scenario_9_logout()

            print("\n" + "="*60)
            print("✅ 所有测试场景已完成")
            print("="*60)

        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            await self.take_screenshot("error")

        finally:
            await self.teardown()


async def main():
    """主函数"""
    test = EduTrackTest(base_url="https://edu-track.zeabur.app")
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
