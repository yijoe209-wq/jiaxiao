"""
MVP 完整流程测试脚本
模拟家长转发 → AI 解析 → Web 查看 → 确认 → 完成
"""
import requests
import time
import json

API_BASE = 'http://localhost:5001'

# 真实的老师消息
TEST_MESSAGE = """语文任务：
1.阅读打卡：
朗读《语文园地八》这课，会认字和会写字口头拼读并组词。

朗读课外读物，写阅读笔记。

2.背诵课本1--8单元要求背诵的所有内容。
背诵课本105页的成语和日积月累，录音上传小管家。

3.认真修改作业本里面的错误。

4.书写《快乐的小河》和《语文园地八》的会写字，三字两词加拼音。

词语表《快乐的小河》这课，每个词语写两遍，加拼音。

5.课本105页的成语，每个写2遍，加拼音。日积月累抄写一遍，默写一遍，加拼音，默写后订正并改错。

6.完成青橙派习题中《快乐的小河》和《语文园地八》这课。

7.周一听写《称赞》这课剩余的词语和《纸船和风筝》这课的词语，提前准备，自行练习。"""


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health():
    """测试健康检查"""
    print_section("1️⃣ 健康检查")

    response = requests.get(f"{API_BASE}/health")
    data = response.json()

    print("✅ 服务状态:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data['status'] == 'ok'


def test_process_message():
    """测试消息处理"""
    print_section("2️⃣ 模拟家长转发消息并处理")

    from task_service import task_service

    test_wechat_id = 'test_wechat_id_123'

    print("📱 消息内容:")
    print(TEST_MESSAGE[:200] + "...\n")

    result = task_service.process_message(test_wechat_id, TEST_MESSAGE)

    print(f"✅ 处理结果: {result.get('action')}")
    print(f"📊 识别到: {result.get('total_tasks', 1)} 条任务")
    print(f"🔔 待确认 ID: {result.get('pending_id')}")

    return result.get('pending_id') if result.get('success') else None


def test_view_pending():
    """测试查看待确认任务"""
    print_section("3️⃣ 查看 Web 界面（待确认任务）")

    response = requests.get(f"{API_BASE}/api/pending")
    data = response.json()

    print(f"📋 待确认任务数: {len(data['tasks'])}")

    for idx, pending in enumerate(data['tasks'], 1):
        task_data = pending['task_data']
        print(f"\n{idx}. 任务组 ID: {pending['pending_id'][:20]}...")
        if task_data.get('type') == 'multiple':
            print(f"   包含 {task_data['total_tasks']} 条任务:")
            for task in task_data['tasks'][:3]:  # 只显示前3条
                print(f"   - [{task['task_type']}] {task['description']}")
            if task_data['total_tasks'] > 3:
                print(f"   - ... 还有 {task_data['total_tasks'] - 3} 条")

    return data['tasks'][0]['pending_id'] if data['tasks'] else None


def test_confirm_task(pending_id):
    """测试确认任务"""
    print_section("4️⃣ 确认任务并分配学生")

    # 小明的学生 ID
    student_id = 'bde646c6-6bef-4f8b-88b0-705925f201f8'

    payload = {
        'pending_id': pending_id,
        'student_id': student_id
    }

    print(f"📝 分配给学生: 小明")
    print(f"🔑 Pending ID: {pending_id}")

    response = requests.post(
        f"{API_BASE}/api/confirm",
        json=payload
    )

    result = response.json()

    if result.get('success'):
        print(f"\n✅ 成功创建 {result.get('task_count', 1)} 条任务!")
        print(f"📋 任务组 ID: {result.get('group_id')}")
    else:
        print(f"\n❌ 确认失败: {result.get('error')}")

    return result.get('success')


def test_view_tasks():
    """测试查看已确认任务"""
    print_section("5️⃣ 查看已确认的任务列表")

    student_id = 'bde646c6-6bef-4f8b-88b0-705925f201f8'

    response = requests.get(f"{API_BASE}/api/tasks/{student_id}")
    data = response.json()

    tasks = data.get('tasks', [])

    print(f"📚 小明的任务数: {len(tasks)}")
    print()

    for task in tasks[:10]:  # 只显示前10条
        status = "✅" if task['is_completed'] else "⏳"
        task_type = f"[{task['task_type']}]" if task.get('task_type') else ""
        sequence = f"{task['sequence']}." if task.get('sequence') else ""

        print(f"{status} {sequence} {task_type} {task['description']}")

        if task.get('details'):
            print(f"   详情: {task['details'][:60]}...")
        print()

    if len(tasks) > 10:
        print(f"... 还有 {len(tasks) - 10} 条任务")

    return tasks


def test_complete_task(tasks):
    """测试标记任务完成"""
    print_section("6️⃣ 标记任务完成")

    if not tasks:
        print("❌ 没有可标记的任务")
        return False

    # 找第一个未完成的任务
    task_to_complete = None
    for task in tasks:
        if not task['is_completed']:
            task_to_complete = task
            break

    if not task_to_complete:
        print("✅ 所有任务都已完成")
        return True

    task_id = task_to_complete['task_id']
    print(f"📝 标记完成: {task_to_complete['description']}")

    response = requests.post(f"{API_BASE}/api/tasks/{task_id}/complete")
    result = response.json()

    if result.get('success'):
        print("✅ 已标记为完成")

        # 重新查询验证
        response = requests.get(f"{API_BASE}/api/tasks/{task_to_complete['student_id']}")
        data = response.json()
        task = [t for t in data['tasks'] if t['task_id'] == task_id][0]

        print(f"✅ 验证: 任务状态 = {'已完成' if task['is_completed'] else '未完成'}")
        return True
    else:
        print(f"❌ 操作失败: {result.get('error')}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  🎓 家校任务管理助手 - MVP 完整流程测试")
    print("=" * 80)

    try:
        # 1. 健康检查
        if not test_health():
            print("❌ 服务未就绪，请先启动: python app.py")
            return

        # 2. 处理消息
        pending_id = test_process_message()

        # 3. 查看待确认任务
        if not pending_id:
            # 尝试从 API 获取
            pending_tasks = requests.get(f"{API_BASE}/api/pending").json()['tasks']
            if pending_tasks:
                pending_id = pending_tasks[0]['pending_id']

        if pending_id:
            test_view_pending()

            # 4. 确认任务
            if test_confirm_task(pending_id):
                # 5. 查看任务列表
                tasks = test_view_tasks()

                # 6. 标记完成
                test_complete_task(tasks)

        print_section("✅ MVP 测试完成")
        print("🎉 所有核心功能正常运行！")
        print("\n📱 访问 Web 界面: http://localhost:5001/tasks")
        print("📊 查看系统状态: http://localhost:5001/health")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
