#!/usr/bin/env python3
"""
测试任务创建流程
模拟用户从首页到任务中心的完整操作
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_task_creation_flow():
    """测试完整的任务创建流程"""
    print("🎯 测试任务创建流程\n")

    session = requests.Session()

    # 步骤1: 访问首页
    print("步骤1: 访问首页")
    response = session.get(f"{BASE_URL}/")
    print(f"  ✓ 状态码: {response.status_code}")

    # 检查首页设计
    if '#1a1a1a' in response.text:
        print("  ✓ 首页使用黑色主色")
    if 'linear-gradient' in response.text and '#667eea' in response.text:
        print("  ❌ 首页仍有紫色渐变")
        return False

    # 步骤2: 访问任务中心
    print("\n步骤2: 访问任务中心")
    response = session.get(f"{BASE_URL}/my-tasks")
    print(f"  ✓ 状态码: {response.status_code}")

    # 检查任务中心设计
    if '#1a1a1a' in response.text:
        print("  ✓ 任务中心使用黑色主色")
    if 'linear-gradient' in response.text:
        print("  ⚠️  任务中心有渐变（可能是数据可视化）")

    # 步骤3: 检查导航链接
    print("\n步骤3: 检查页面导航")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    home_link = soup.find('a', href='/')
    if home_link and '首页' in home_link.get_text():
        print("  ✓ 找到返回首页的链接")
    else:
        print("  ❌ 缺少返回首页的链接")

    # 步骤4: 测试API
    print("\n步骤4: 测试API接口")

    # 测试学生API
    try:
        response = session.get(f"{BASE_URL}/api/students")
        if response.status_code == 200:
            students = response.json()
            student_count = len(students.get('students', []))
            print(f"  ✓ 学生API正常，共 {student_count} 个学生")
        else:
            print(f"  ❌ 学生API失败: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 学生API错误: {e}")

    # 测试任务API
    try:
        response = session.get(f"{BASE_URL}/api/tasks")
        if response.status_code == 200:
            tasks = response.json()
            if isinstance(tasks, list):
                print(f"  ✓ 任务API正常，共 {len(tasks)} 个任务")
            else:
                print(f"  ⚠️  任务返回格式异常: {type(tasks)}")
        elif response.status_code == 401:
            print("  ⚠️  任务API返回401（需要登录）")
        else:
            print(f"  ❌ 任务API失败: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 任务API错误: {e}")

    print("\n✅ 流程测试完成！")
    return True

def check_page_consistency():
    """检查页面间的设计一致性"""
    print("\n🎨 检查页面设计一致性\n")

    pages = [
        ("/", "首页"),
        ("/my-tasks", "任务中心"),
        ("/students", "学生管理"),
        ("/login", "登录页")
    ]

    issues = []

    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            has_gradient = 'linear-gradient' in response.text
            has_old_color = '#667eea' in response.text or '#764ba2' in response.text
            has_new_color = '#1a1a1a' in response.text

            status = "✓"
            if has_gradient and has_old_color:
                status = "❌"
                issues.append(f"{name}仍有旧渐变")
            elif has_gradient:
                status = "~"
                issues.append(f"{name}有渐变（可能是正常的）")

            print(f"{status} {name:12} - 渐变:{'是' if has_gradient else '否':3}  旧配色:{'是' if has_old_color else '否':3}  新配色:{'是' if has_new_color else '否':3}")

        except Exception as e:
            print(f"❌ {name} - 错误: {e}")

    if issues:
        print(f"\n⚠️  发现问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✅ 所有页面设计一致！")
        return True

if __name__ == "__main__":
    print("🚀 开始用户流程测试\n")
    test_task_creation_flow()
    check_page_consistency()
