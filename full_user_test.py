"""
完整的用户体验测试
分析产品性能、设计、流程逻辑
"""
import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright


class UserJourneyTest:
    """完整用户旅程测试"""

    def __init__(self):
        self.base_url = "https://edu-track.zeabur.app"
        self.results = {
            'performance': {},
            'design': {},
            'flow': {},
            'issues': []
        }

    async def setup(self):
        """初始化浏览器"""
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=False, slow_mo=500)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN'
        )
        self.page = await self.context.new_page()
        self.playwright = p

    async def teardown(self):
        """清理"""
        await self.page.close()
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def measure_page_load(self, url, name):
        """测量页面加载性能"""
        print(f"\n📊 测试: {name}")
        print(f"   URL: {url}")

        start_time = time.time()

        try:
            response = await self.page.goto(url, wait_until='domcontentloaded')
            load_time = time.time() - start_time

            # 等待页面完全加载
            await self.page.wait_for_load_state('networkidle', timeout=5000)
            full_load_time = time.time() - start_time

            # 获取页面信息
            title = await self.page.title()

            self.results['performance'][name] = {
                'dom_loaded': f"{load_time:.2f}s",
                'fully_loaded': f"{full_load_time:.2f}s",
                'status': response.status,
                'title': title
            }

            print(f"   DOM 加载: {load_time:.2f}s")
            print(f"   完全加载: {full_load_time:.2f}s")
            print(f"   状态码: {response.status}")
            print(f"   标题: {title}")

            # 截图
            screenshot_name = f"test_{name.replace(' ', '_').lower()}.png"
            await self.page.screenshot(path=screenshot_name)
            print(f"   📸 截图: {screenshot_name}")

            return True

        except Exception as e:
            self.results['issues'].append({
                'test': name,
                'error': str(e),
                'type': 'performance'
            })
            print(f"   ❌ 错误: {e}")
            return False

    async def test_1_landing_page(self):
        """测试 1: 首页/登录页"""
        print("\n" + "="*60)
        print("场景 1: 访问登录页面")
        print("="*60)

        success = await self.measure_page_load(f"{self.base_url}/login", "登录页")

        if success:
            # 分析设计
            print("\n🎨 设计分析:")

            # 检查主要元素
            logo = await self.page.locator('.logo, h1, .brand').count()
            tabs = await self.page.locator('.tab').count()
            forms = await self.page.locator('form').count()

            print(f"   Logo/标题: {'✅' if logo > 0 else '❌'}")
            print(f"   标签切换: {'✅' if tabs >= 2 else '❌'}")
            print(f"   表单: {forms} 个")

            # 检查样式
            bg_color = await self.page.locator('body').get_attribute('style') or '默认'
            print(f"   背景: {bg_color}")

            self.results['design']['登录页'] = {
                'has_logo': logo > 0,
                'has_tabs': tabs >= 2,
                'form_count': forms,
                'user_friendly': tabs >= 2 and forms >= 2
            }

    async def test_2_register_flow(self):
        """测试 2: 注册流程"""
        print("\n" + "="*60)
        print("场景 2: 新用户注册")
        print("="*60)

        start_time = time.time()

        try:
            # 切换到注册标签
            register_tab = self.page.locator('.tab').filter(has_text='注册')
            await register_tab.first.click()
            await asyncio.sleep(1)

            # 填写表单
            test_email = f"ux_test_{int(time.time())}@example.com"
            await self.page.fill('#registerEmail', test_email)
            await self.page.fill('#registerPassword', 'test123456')

            # 查找姓名输入框
            name_inputs = self.page.locator('input[placeholder*="姓名"], input[placeholder*="家长"]')
            if await name_inputs.count() > 0:
                await name_inputs.first.fill('UX测试用户')

            await asyncio.sleep(0.5)

            # 提交
            submit_btn = self.page.locator('#registerForm button[type="submit"]')
            await submit_btn.click()

            # 等待响应
            await asyncio.sleep(5)

            # 检查结果
            current_url = self.page.url
            flow_time = time.time() - start_time

            if '/login' not in current_url:
                print(f"✅ 注册成功，耗时: {flow_time:.2f}s")
                print(f"   跳转到: {current_url}")

                self.results['flow']['注册'] = {
                    'success': True,
                    'time': f"{flow_time:.2f}s",
                    'redirected': True
                }
            else:
                print(f"❌ 注册失败或未跳转")
                print(f"   当前: {current_url}")

                self.results['flow']['注册'] = {
                    'success': False,
                    'time': f"{flow_time:.2f}s",
                    'redirected': False
                }

        except Exception as e:
            self.results['issues'].append({
                'test': '注册流程',
                'error': str(e)
            })
            print(f"❌ 错误: {e}")

    async def test_3_task_center(self):
        """测试 3: 任务中心"""
        print("\n" + "="*60)
        print("场景 3: 任务中心")
        print("="*60)

        success = await self.measure_page_load(f"{self.base_url}/", "任务中心")

        if success:
            # 分析页面结构
            print("\n🎨 设计分析:")

            # 检查布局
            sidebar = await self.page.locator('.sidebar, nav, [class*="filter"]').count()
            task_list = await self.page.locator('[class*="task"], [class*="card"]').count()
            add_button = await self.page.locator('button:has-text("添加"), button:has-text("新建")').count()

            print(f"   侧边栏/筛选: {'✅' if sidebar > 0 else '❌'}")
            print(f"   任务列表: {task_list} 项")
            print(f"   添加按钮: {'✅' if add_button > 0 else '❌'}")

            # 检查空状态
            empty_state = await self.page.locator('text=暂无, text=没有任务').count()
            if empty_state > 0:
                print(f"   空状态提示: ✅")
            else:
                print(f"   空状态提示: ❌")

            self.results['design']['任务中心'] = {
                'has_sidebar': sidebar > 0,
                'task_count': task_list,
                'has_add_button': add_button > 0,
                'has_empty_state': empty_state > 0
            }

    async def test_4_add_task(self):
        """测试 4: 添加任务"""
        print("\n" + "="*60)
        print("场景 4: 快速添加任务")
        print("="*60)

        success = await self.measure_page_load(f"{self.base_url}/add", "添加任务页")

        if success:
            # 检查页面元素
            textarea = await self.page.locator('textarea').count()
            parse_button = await self.page.locator('button:has-text("解析"), button:has-text("AI")').count()

            print(f"\n🎨 功能检查:")
            print(f"   输入框: {'✅' if textarea > 0 else '❌'}")
            print(f"   AI 解析按钮: {'✅' if parse_button > 0 else '❌'}")

            # 测试输入
            if textarea > 0:
                test_task = "英语：完成第3单元单词练习"
                await self.page.locator('textarea').fill(test_task)
                print(f"   ✅ 输入测试任务: {test_task}")

                # 检查AI解析
                if parse_button > 0:
                    print(f"   ⏳ 点击 AI 解析...")
                    await self.page.locator('button:has-text("解析"), button:has-text("AI")').first.click()

                    # 等待解析
                    await asyncio.sleep(12)

                    # 检查结果
                    result_area = await self.page.locator('[class*="result"], [class*="preview"], [class*="task"]').count()
                    print(f"   解析结果: {'✅ 显示' if result_area > 0 else '❌ 未显示'}")

    async def test_5_students_page(self):
        """测试 5: 学生管理"""
        print("\n" + "="*60)
        print("场景 5: 学生管理")
        print("="*60)

        success = await self.measure_page_load(f"{self.base_url}/students", "学生管理")

        if success:
            # 检查页面
            student_cards = await self.page.locator('[class*="student"], [class*="card"]').count()
            add_button = await self.page.locator('button:has-text("添加"), button:has-text("新增")').count()

            print(f"\n🎨 功能检查:")
            print(f"   学生卡片: {student_cards} 个")
            print(f"   添加按钮: {'✅' if add_button > 0 else '❌'}")

            self.results['design']['学生管理'] = {
                'student_count': student_cards,
                'has_add_button': add_button > 0
            }

    async def test_6_navigation(self):
        """测试 6: 导航测试"""
        print("\n" + "="*60)
        print("场景 6: 导航流程")
        print("="*60)

        try:
            # 测试各个页面的跳转
            pages = [
                ('首页', '/'),
                ('添加任务', '/add'),
                ('任务中心', '/tasks'),
                ('学生管理', '/students'),
            ]

            navigation_results = {}

            for name, path in pages:
                start = time.time()
                await self.page.goto(f"{self.base_url}{path}")
                await self.page.wait_for_load_state('domcontentloaded')
                load_time = time.time() - start

                title = await self.page.title()
                navigation_results[name] = {
                    'time': f"{load_time:.2f}s",
                    'title': title
                }

                print(f"   {name}: {load_time:.2f}s - {title}")

            self.results['performance']['导航'] = navigation_results

        except Exception as e:
            print(f"❌ 导航测试错误: {e}")

    async def test_7_responsive_design(self):
        """测试 7: 响应式设计"""
        print("\n" + "="*60)
        print("场景 7: 响应式设计")
        print("="*60)

        # 测试不同屏幕尺寸
        sizes = [
            ('桌面', 1920, 1080),
            ('笔记本', 1366, 768),
            ('平板', 768, 1024),
            ('手机', 375, 667),
        ]

        responsive_results = {}

        for name, width, height in sizes:
            await self.page.set_viewport_size({'width': width, 'height': height})
            await self.page.goto(f"{self.base_url}/")
            await asyncio.sleep(1)

            # 检查是否有横向滚动条
            has_scroll = await self.page.evaluate(
                '() => document.documentElement.scrollWidth > document.documentElement.clientWidth'
            )

            responsive_results[name] = {
                'width': width,
                'height': height,
                'has_horizontal_scroll': has_scroll
            }

            print(f"   {name} ({width}x{height}): {'✅' if not has_scroll else '❌ 有横向滚动'}")

        self.results['design']['响应式'] = responsive_results

    async def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📋 测试报告")
        print("="*60)

        # 性能报告
        print("\n📊 性能分析:")
        for test, data in self.results['performance'].items():
            if 'fully_loaded' in data:
                status = "✅" if float(data['fully_loaded'].replace('s', '')) < 3 else "⚠️"
                print(f"   {status} {test}: {data['fully_loaded']}")

        # 设计分析
        print("\n🎨 设计分析:")
        for page, data in self.results['design'].items():
            print(f"   {page}:")
            for key, value in data.items():
                print(f"     - {key}: {value}")

        # 流程分析
        print("\n🔄 流程分析:")
        for flow, data in self.results['flow'].items():
            print(f"   {flow}: {data}")

        # 问题列表
        if self.results['issues']:
            print("\n⚠️ 发现的问题:")
            for i, issue in enumerate(self.results['issues'], 1):
                print(f"   {i}. {issue['test']}: {issue.get('error', 'N/A')}")
        else:
            print("\n✅ 未发现明显问题")

        # 总结
        print("\n" + "="*60)
        print("📝 总结")
        print("="*60)

        # 评分
        performance_score = len([t for t in self.results['performance'].values()
                                 if 'fully_loaded' in t and float(t['fully_loaded'].replace('s', '')) < 3])
        total_performance = len(self.results['performance'])

        print(f"\n性能评分: {performance_score}/{total_performance} 页面加载 < 3秒")
        print(f"设计质量: {'良好' if not self.results['issues'] else '需要改进'}")
        print(f"用户体验: {'流畅' if all(f.get('success', True) for f in self.results['flow'].values()) else '有卡顿'}")


async def main():
    """主测试流程"""
    test = UserJourneyTest()

    try:
        await test.setup()

        # 运行所有测试
        await test.test_1_landing_page()
        await test.test_2_register_flow()
        await test.test_3_task_center()
        await test.test_4_add_task()
        await test.test_5_students_page()
        await test.test_6_navigation()
        await test.test_7_responsive_design()

        # 生成报告
        await test.generate_report()

    finally:
        await test.teardown()


if __name__ == "__main__":
    asyncio.run(main())
