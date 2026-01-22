"""
添加测试数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Family, Student, Task
from datetime import datetime, timedelta
import uuid

def seed_test_data():
    """添加测试数据"""

    session = db.get_session()

    try:
        # 1. 确保测试用户存在
        test_user = session.query(Family).filter_by(email='testuser@example.com').first()
        if not test_user:
            print("创建测试用户...")
            test_user = Family(
                family_id=str(uuid.uuid4()),
                email='testuser@example.com',
                parent_name='测试用户',
                password='7d608a2e2d9a0b72f3c7e0d6e8f1a2b3'  # test123456的hash
            )
            session.add(test_user)
            session.commit()
        else:
            print(f"测试用户已存在: {test_user.parent_name}")

        family_id = test_user.family_id

        # 2. 添加测试学生
        students_to_add = [
            {'name': '张小明', 'grade': '三年级', 'class_name': '1班'},
            {'name': '张小红', 'grade': '五年级', 'class_name': '2班'},
        ]

        for student_data in students_to_add:
            existing = session.query(Student).filter_by(
                family_id=family_id,
                name=student_data['name']
            ).first()

            if not existing:
                print(f"创建学生: {student_data['name']}")
                student = Student(
                    student_id=str(uuid.uuid4()),
                    family_id=family_id,
                    name=student_data['name'],
                    grade=student_data['grade'],
                    class_name=student_data['class_name']
                )
                session.add(student)
            else:
                print(f"学生已存在: {student_data['name']}")

        session.commit()

        # 获取学生ID
        students = session.query(Student).filter_by(family_id=family_id).all()

        if not students:
            print("没有学生，跳过任务创建")
            return

        # 3. 添加测试任务（使用WeChat ID）
        wechat_id = f"web_{family_id}"  # Web用户使用family_id作为wechat_id

        tasks_to_add = [
            {
                'subject': '数学',
                'title': '完成数学练习册第5页',
                'description': '完成课本P25-P26的习题，注意计算准确',
                'due_date': datetime.now() + timedelta(days=1),
                'completed': False
            },
            {
                'subject': '语文',
                'title': '背诵古诗三首',
                'description': '背诵《静夜思》、《春晓》、《登鹳雀楼》，家长签字',
                'due_date': datetime.now() + timedelta(days=2),
                'completed': True
            },
            {
                'subject': '英语',
                'title': '听写Unit 3单词',
                'description': '英语课本Unit 3所有单词，要求拼写正确',
                'due_date': datetime.now() + timedelta(days=3),
                'completed': False
            },
            {
                'subject': '数学',
                'title': '口算练习',
                'description': '完成口算练习册第8页，限时10分钟',
                'due_date': datetime.now() + timedelta(days=-1),  # 已过期
                'completed': False
            },
        ]

        for task_data in tasks_to_add:
            # 检查是否已存在相似任务
            existing = session.query(Task).filter_by(
                wechat_id=wechat_id,
                description=task_data['description']
            ).first()

            if not existing:
                # 随机分配给一个学生
                import random
                student = random.choice(students)

                task = Task(
                    task_id=str(uuid.uuid4()),
                    student_id=student.student_id,
                    wechat_id=wechat_id,
                    subject=task_data['subject'],
                    description=task_data['description'],
                    deadline=task_data['due_date'],
                    status='confirmed',
                    is_completed=task_data['completed'],
                    intent='assignment'
                )
                session.add(task)
                print(f"创建任务: {task_data['title']}")
            else:
                print(f"任务已存在: {task_data['title']}")

        session.commit()

        # 统计数据
        task_count = session.query(Task).filter_by(wechat_id=wechat_id).count()
        student_count = session.query(Student).filter_by(family_id=family_id).count()

        print(f"\n✅ 测试数据添加完成:")
        print(f"   学生数: {student_count}")
        print(f"   任务数: {task_count}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_test_data()
