"""
完整流程演示
展示从接收到确认的完整流程
"""
from task_service import task_service
from models import db, Student
import json


def demo_real_message():
    """演示真实消息的完整处理流程"""
    print("=" * 80)
    print("🎓 家校任务管理助手 - 完整流程演示")
    print("=" * 80)
    print()

    # 真实的老师消息
    message = """语文任务：
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

    # 测试家长的微信 ID
    test_wechat_id = 'test_wechat_id_123'

    print("📱 第 1 步：家长转发消息到 AI 家校管家")
    print("-" * 80)
    print("消息内容：")
    print(message[:200] + "...")
    print()

    print("🤖 第 2 步：AI 智能解析中...")
    print("-" * 80)

    # 处理消息
    result = task_service.process_message(test_wechat_id, message)

    print(f"✅ 处理完成！")
    print(f"动作：{result.get('action')}")
    print(f"消息：{result.get('message')}")
    print()

    if result['action'] == 'multiple_tasks_created':
        group_id = result['group_id']
        pending_id = result['pending_id']
        total_tasks = result['total_tasks']

        print(f"📊 第 3 步：识别结果")
        print("-" * 80)
        print(f"✨ 识别到 {total_tasks} 条独立任务")
        print(f"📋 任务组 ID：{group_id}")
        print(f"🔔 待确认 ID：{pending_id}")
        print()

        # 查询待确认任务详情
        session = db.get_session()
        from models import PendingTask
        pending = session.query(PendingTask).filter_by(pending_id=pending_id).first()

        if pending:
            task_data = json.loads(pending.task_data)
            print("📝 任务列表：")
            print("-" * 80)

            for task in task_data['tasks']:
                print(f"{task['sequence']}. [{task['task_type']}] {task['description']}")
            print()

        print("👨‍👩‍👧 第 4 步：家长在小程序中确认并分配学生")
        print("-" * 80)
        print("假设家长将所有任务都分配给：小明")
        print()

        # 获取小明的学生 ID
        session = db.get_session()
        xiao_ming = session.query(Student).filter_by(name='小明').first()

        if xiao_ming:
            student_id = xiao_ming.student_id
            print(f"学生 ID：{student_id}")
            print()

            print("💾 第 5 步：确认任务，创建正式记录...")
            print("-" * 80)

            # 确认任务
            confirm_result = task_service.confirm_tasks(
                pending_id=pending_id,
                student_id=student_id
            )

            if confirm_result['success']:
                print(f"✅ 成功创建 {confirm_result['task_count']} 条任务！")
                print()

                print("📋 第 6 步：查看已创建的任务")
                print("-" * 80)

                # 查询创建的任务
                from models import Task
                tasks = session.query(Task).filter_by(
                    student_id=student_id,
                    group_id=group_id
                ).order_by(Task.sequence).all()

                for task in tasks:
                    print(f"✓ 任务 {task.sequence}: [{task.task_type}] {task.description}")
                    print(f"  详情：{task.details[:80]}...")
                    print(f"  状态：{'✅ 已完成' if task.is_completed else '⏳ 待完成'}")
                    print()

                print("🎯 第 7 步：学生查看并完成任务")
                print("-" * 80)
                print("小明登录小程序，看到上述 7 条任务")
                print("可以逐项勾选完成")
                print()

                print("⏰ 第 8 步：定时提醒（每天 17:00）")
                print("-" * 80)
                print("系统会在每天下午 5 点推送未完成任务")
                print(f"当前待完成：{len([t for t in tasks if not t.is_completed])} 项")
                print()

            session.close()

    print("=" * 80)
    print("✨ 流程演示完成！")
    print("=" * 80)


if __name__ == '__main__':
    demo_real_message()
