#!/usr/bin/env python3
"""
测试前端页面的完整加载
验证所有页面能否正常访问和渲染
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5001"

class FrontendPageTest:
    def __init__(self):
        self.session = requests.Session()

    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)

    def print_success(self, message):
        print(f"✅ {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def print_info(self, message):
        print(f"ℹ️  {message}")

    def test_page_load(self, url, expected_elements=None):
        """测试页面是否能加载"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 检查是否有基本HTML结构
                has_html = bool(soup.find('html'))
                has_body = bool(soup.find('body'))
                has_title = bool(soup.find('title'))

                self.print_success(f"页面加载成功: {url}")
                self.print_info(f"  - HTML结构: {'✓' if has_html else '✗'}")
                self.print_info(f"  - Body标签: {'✓' if has_body else '✗'}")
                self.print_info(f"  - Title: {soup.title.string if has_title else '无'}")

                # 检查CSS样式
                styles = soup.find_all('link', rel='stylesheet')
                inline_styles = soup.find_all('style')
                self.print_info(f"  - 外部样式: {len(styles)} 个")
                self.print_info(f"  - 内联样式: {len(inline_styles)} 个")

                # 检查JavaScript
                scripts = soup.find_all('script')
                self.print_info(f"  - 脚本: {len(scripts)} 个")

                # 检查特定元素
                if expected_elements:
                    for element_desc, selector in expected_elements.items():
                        found = bool(soup.select(selector))
                        status = '✓' if found else '✗'
                        self.print_info(f"  - {element_desc}: {status}")

                return True, soup
            else:
                self.print_error(f"页面加载失败: {url} (HTTP {response.status_code})")
                return False, None
        except Exception as e:
            self.print_error(f"加载页面时出错: {e}")
            return False, None

    def test_login_page(self):
        """测试登录页面"""
        self.print_section("测试1: 登录页面")

        expected_elements = {
            "登录卡片": ".card",
            "邮箱输入框": "input[name='email']",
            "密码输入框": "input[name='password']",
            "登录按钮": "button[type='submit']",
            "注册标签": ".tab-button"
        }

        success, soup = self.test_page_load(f"{BASE_URL}/login", expected_elements)
        return success

    def test_index_page(self):
        """测试首页（未登录）"""
        self.print_section("测试2: 首页（未登录状态）")

        expected_elements = {
            "标题": "h1",
            "学生选择器": "#studentSelect",
            "任务输入框": "textarea#messageInput",
            "提交按钮": "button#submitBtn"
        }

        success, soup = self.test_page_load(f"{BASE_URL}/", expected_elements)
        return success

    def test_login(self):
        """执行登录"""
        self.print_section("测试3: 用户登录")

        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }

        response = self.session.post(f"{BASE_URL}/api/login", json=login_data)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.print_success(f"登录成功！")
                self.print_info(f"  - Family ID: {result.get('family_id')}")
                self.print_info(f"  - 家长: {result.get('parent_name')}")
                return True
            else:
                self.print_error(f"登录失败: {result.get('error')}")
                return False
        else:
            self.print_error(f"登录请求失败: HTTP {response.status_code}")
            return False

    def test_index_after_login(self):
        """测试登录后的首页"""
        self.print_section("测试4: 首页（登录后）")

        expected_elements = {
            "标题": "h1",
            "学生选择器": "#studentSelect",
            "任务输入框": "textarea#messageInput",
            "提交按钮": "button#submitBtn"
        }

        success, soup = self.test_page_load(f"{BASE_URL}/", expected_elements)
        return success

    def test_students_page(self):
        """测试学生管理页面"""
        self.print_section("测试5: 学生管理页面")

        expected_elements = {
            "页面标题": "h1",
            "添加学生按钮": "#addStudentBtn",
            "学生列表容器": "#studentsList"
        }

        success, soup = self.test_page_load(f"{BASE_URL}/students", expected_elements)
        return success

    def test_tasks_page(self):
        """测试任务中心页面"""
        self.print_section("测试6: 任务中心页面")

        expected_elements = {
            "页面标题": "h1",
            "筛选器": ".filter-group",
            "任务列表": "#tasksList"
        }

        success, soup = self.test_page_load(f"{BASE_URL}/tasks", expected_elements)
        return success

    def test_unauthorized_redirect(self):
        """测试未登录访问受保护页面"""
        self.print_section("测试7: 未登录重定向测试")

        # 创建一个新的session（未登录）
        temp_session = requests.Session()

        protected_pages = [
            ("/students", "学生管理"),
            ("/tasks", "任务中心")
        ]

        for path, name in protected_pages:
            response = temp_session.get(f"{BASE_URL}{path}", allow_redirects=False)
            if response.status_code in [302, 301]:
                self.print_success(f"{name}: 正确重定向到登录页 (HTTP {response.status_code})")
                self.print_info(f"  - 重定向到: {response.headers.get('Location', '未知')}")
            elif response.status_code == 200:
                # 检查页面内容是否包含登录相关元素
                soup = BeautifulSoup(response.text, 'html.parser')
                has_login = bool(soup.find("input", {"name": "email"}))
                if has_login:
                    self.print_success(f"{name}: 页面加载但显示登录表单")
                else:
                    self.print_error(f"{name}: 安全漏洞 - 未登录可以访问！")
            else:
                self.print_info(f"{name}: HTTP {response.status_code}")

    def test_css_consistency(self):
        """测试CSS样式一致性"""
        self.print_section("测试8: CSS样式检查")

        pages_to_check = [
            ("登录页", "/login"),
            ("首页", "/"),
            ("学生管理", "/students"),
            ("任务中心", "/tasks")
        ]

        print("\n检查日式极简设计应用情况:")
        for name, path in pages_to_check:
            response = self.session.get(f"{BASE_URL}{path}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                styles = soup.find_all('style')

                # 检查是否使用了CSS变量
                has_css_vars = False
                for style in styles:
                    if '--zen-bg' in style.string or '--zen-text' in style.string:
                        has_css_vars = True
                        break

                # 检查是否还有emoji
                body_text = soup.get_text()
                has_emoji = any(char in body_text for char in ['📚', '👤', '➕', '✏️', '📋', '❌', '⚠️'])

                status = "✓" if has_css_vars else "✗"
                emoji_status = "✓" if not has_emoji else "✗"
                print(f"  {name}: CSS变量 {status}, 无emoji {emoji_status}")

    def run_all_tests(self):
        """运行所有前端测试"""
        print("\n" + "🚀" * 30)
        print("  前端页面自动化测试")
        print("🚀" * 30)

        results = []

        # 测试1: 登录页面
        results.append(("登录页面", self.test_login_page()))

        # 测试2: 首页（未登录）
        results.append(("首页（未登录）", self.test_index_page()))

        # 测试3: 登录
        login_success = self.test_login()
        results.append(("用户登录", login_success))

        if not login_success:
            self.print_error("登录失败，跳过需要登录的测试")
            self.print_summary(results, skip_rest=True)
            return

        # 测试4: 首页（登录后）
        results.append(("首页（登录后）", self.test_index_after_login()))

        # 测试5: 学生管理页面
        results.append(("学生管理页面", self.test_students_page()))

        # 测试6: 任务中心页面
        results.append(("任务中心页面", self.test_tasks_page()))

        # 测试7: 未登录重定向
        self.test_unauthorized_redirect()

        # 测试8: CSS一致性
        self.test_css_consistency()

        # 总结
        self.print_summary(results)

    def print_summary(self, results, skip_rest=False):
        """打印测试总结"""
        self.print_section("测试总结")

        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"\n通过: {passed}/{total}")
        for name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {name}")

        if skip_rest:
            print("\n⚠️  部分测试因登录失败而跳过")
        elif passed == total:
            print("\n🎉 所有测试通过！")
        else:
            print(f"\n⚠️  {total - passed} 个测试失败")

        print("\n" + "="*60)


if __name__ == "__main__":
    tester = FrontendPageTest()
    tester.run_all_tests()
