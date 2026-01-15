#!/usr/bin/env python3
"""
模拟真实用户完整使用流程
测试：登录 -> 添加学生 -> 创建任务 -> 查看任务中心
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

class UserFlowTest:
    def __init__(self):
        self.session = requests.Session()
        self.family_id = None
        self.parent_name = None
        self.student_id = None

    def print_step(self, step, status="⏳"):
        print(f"\n{status} {step}")
        print("=" * 60)

    def print_success(self, message):
        print(f"✅ {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def print_info(self, message):
        print(f"ℹ️  {message}")

    def step_1_login(self):
        """步骤1: 登录系统"""
        self.print_step("步骤1: 登录系统", "🔐")

        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }

        response = self.session.post(f"{BASE_URL}/api/login", json=login_data)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.family_id = result.get('family_id')
                self.parent_name = result.get('parent_name')
                self.print_success(f"登录成功！")
                self.print_info(f"家长: {self.parent_name}")
                self.print_info(f"Family ID: {self.family_id}")
                return True
            else:
                self.print_error(f"登录失败: {result.get('error')}")
                return False
        else:
            self.print_error(f"登录请求失败: HTTP {response.status_code}")
            return False

    def step_2_check_students(self):
        """步骤2: 查看学生列表"""
        self.print_step("步骤2: 查看学生列表", "👥")

        response = self.session.get(f"{BASE_URL}/api/students")

        if response.status_code == 200:
            result = response.json()
            students = result.get('students', [])
            self.print_success(f"获取到 {len(students)} 个学生")

            if students:
                for i, student in enumerate(students, 1):
                    self.print_info(f"  {i}. {student['name']} - {student.get('grade', '未设置年级')}")
                self.student_id = students[0]['student_id']
                return True
            else:
                self.print_info("还没有学生，需要添加")
                return False
        else:
            self.print_error(f"获取学生列表失败: HTTP {response.status_code}")
            return False

    def step_3_add_student(self):
        """步骤3: 添加学生"""
        self.print_step("步骤3: 添加学生", "➕")

        student_data = {
            "name": "小明",
            "grade": "五年级",
            "class_name": "3班"
        }

        response = self.session.post(
            f"{BASE_URL}/api/students",
            json=student_data
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.student_id = result.get('student_id')
                self.print_success(f"学生添加成功！")
                self.print_info(f"学生 ID: {self.student_id}")
                return True
            else:
                self.print_error(f"添加失败: {result.get('error')}")
                return False
        else:
            self.print_error(f"添加学生失败: HTTP {response.status_code}")
            self.print_info(response.text)
            return False

    def step_4_create_task(self):
        """步骤4: 创建任务"""
        self.print_step("步骤4: 创建任务", "📝")

        task_data = {
            "message": "语文：完成第5课练习册\n数学：做口算题卡第3页\n英语：背诵单词 lesson 1-3",
            "images": []
        }

        response = self.session.post(
            f"{BASE_URL}/api/simulate",
            json=task_data
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.pending_id = result.get('pending_id')
                tasks = result.get('tasks', [])
                self.print_success(f"AI 解析成功！识别到 {len(tasks)} 个任务")
                for i, task in enumerate(tasks, 1):
                    self.print_info(f"  {i}. {task.get('subject', '其他')}: {task.get('description', '')[:50]}...")
                return True, tasks
            else:
                self.print_error(f"AI 解析失败: {result.get('error')}")
                return False, []
        else:
            self.print_error(f"创建任务失败: HTTP {response.status_code}")
            self.print_info(response.text)
            return False, []

    def step_5_confirm_task(self, tasks):
        """步骤5: 确认任务"""
        self.print_step("步骤5: 确认任务", "✅")

        confirm_data = {
            "pending_id": self.pending_id,
            "student_id": self.student_id,
            "updated_tasks": tasks
        }

        response = self.session.post(
            f"{BASE_URL}/api/confirm",
            json=confirm_data
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.print_success(f"任务确认成功！")
                return True
            else:
                self.print_error(f"确认失败: {result.get('error')}")
                return False
        else:
            self.print_error(f"确认任务失败: HTTP {response.status_code}")
            self.print_info(response.text)
            return False

    def step_6_view_tasks(self):
        """步骤6: 查看任务中心"""
        self.print_step("步骤6: 查看任务中心", "📊")

        response = self.session.get(f"{BASE_URL}/api/tasks")

        if response.status_code == 200:
            tasks = response.json()
            self.print_success(f"获取到 {len(tasks)} 个任务")

            if tasks:
                self.print_info("任务列表:")
                for i, task in enumerate(tasks[:5], 1):  # 只显示前5个
                    status = "✓ 已完成" if task.get('is_completed') else "⏳ 待完成"
                    subject = task.get('subject', '其他')
                    desc = task.get('description', '')[:40]
                    self.print_info(f"  {i}. [{subject}] {desc}... {status}")

                if len(tasks) > 5:
                    self.print_info(f"  ... 还有 {len(tasks) - 5} 个任务")
                return True
            else:
                self.print_info("还没有任务")
                return True
        else:
            self.print_error(f"获取任务失败: HTTP {response.status_code}")
            return False

    def run(self):
        """运行完整流程"""
        print("\n" + "=" * 60)
        print("🚀 开始用户流程测试")
        print("=" * 60)

        # 步骤1: 登录
        if not self.step_1_login():
            return False

        # 步骤2: 查看学生
        has_students = self.step_2_check_students()

        # 步骤3: 如果没有学生，添加一个
        if not has_students:
            if not self.step_3_add_student():
                return False

        # 步骤4: 创建任务
        success, tasks = self.step_4_create_task()
        if not success:
            return False

        # 步骤5: 确认任务
        if not self.step_5_confirm_task(tasks):
            return False

        # 等待一下，确保数据保存
        time.sleep(1)

        # 步骤6: 查看任务中心
        if not self.step_6_view_tasks():
            return False

        # 测试完成
        print("\n" + "=" * 60)
        print("✅ 用户流程测试全部通过！")
        print("=" * 60)
        return True


def test_unauthorized_access():
    """测试未登录访问"""
    print("\n" + "=" * 60)
    print("🔒 测试未登录访问控制")
    print("=" * 60)

    session = requests.Session()

    # 测试1: 未登录访问任务
    print("\n测试1: 未登录访问任务列表")
    response = session.get(f"{BASE_URL}/api/tasks")
    if response.status_code == 401:
        print("✅ 正确拦截：未登录无法访问任务")
    else:
        print(f"❌ 安全漏洞：未登录可以访问任务 (HTTP {response.status_code})")

    # 测试2: 未登录访问学生
    print("\n测试2: 未登录访问学生列表")
    response = session.get(f"{BASE_URL}/api/students")
    if response.status_code == 401:
        print("✅ 正确拦截：未登录无法访问学生")
    else:
        print(f"❌ 安全漏洞：未登录可以访问学生 (HTTP {response.status_code})")

    # 测试3: 未登录创建任务
    print("\n测试3: 未登录创建任务")
    response = session.post(f"{BASE_URL}/api/simulate", json={"message": "test"})
    if response.status_code == 401:
        print("✅ 正确拦截：未登录无法创建任务")
    else:
        print(f"❌ 安全漏洞：未登录可以创建任务 (HTTP {response.status_code})")


if __name__ == "__main__":
    # 测试未登录访问控制
    test_unauthorized_access()

    print("\n" * 2)

    # 测试完整的用户流程
    tester = UserFlowTest()
    success = tester.run()

    if success:
        print("\n" + "🎉 " * 20)
        print("所有测试通过！系统运行正常！")
        print("🎉 " * 20)
    else:
        print("\n" + "⚠️ " * 20)
        print("测试失败，请检查问题")
        print("⚠️ " * 20)
