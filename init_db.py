"""
初始化数据库脚本
创建数据库表，并插入测试数据（可选）
"""
from config import Config
from models import db, Family, Student, Task
from utils import logger


def init_database(drop_tables=False):
    """
    初始化数据库

    Args:
        drop_tables: 是否先删除现有表（慎用）
    """
    if drop_tables:
        logger.warning("⚠️ 即将删除所有数据库表...")
        confirm = input("确认删除？(yes/no): ")
        if confirm.lower() == 'yes':
            db.drop_tables()
        else:
            logger.info("已取消")
            return

    # 创建表
    db.create_tables()
    logger.info("✅ 数据库表创建成功")


def create_test_data():
    """创建测试数据"""
    session = db.get_session()

    # 创建测试家庭
    family = Family(
        parent_wechat_id='test_wechat_id_123',
        parent_name='测试家长'
    )
    session.add(family)
    session.commit()

    # 创建测试学生
    student1 = Student(
        family_id=family.family_id,
        name='小明',
        grade='三年级',
        class_name='3班2班'
    )
    student2 = Student(
        family_id=family.family_id,
        name='小红',
        grade='一年级',
        class_name='1班1班'
    )
    session.add(student1)
    session.add(student2)
    session.commit()

    logger.info(f"✅ 测试数据创建成功")
    logger.info(f"  - 家庭 ID: {family.family_id}")
    logger.info(f"  - 学生 1: {student1.name} ({student1.student_id})")
    logger.info(f"  - 学生 2: {student2.name} ({student2.student_id})")

    session.close()


def main():
    """主函数"""
    print("=" * 50)
    print("家校任务管理助手 - 数据库初始化")
    print("=" * 50)
    print()

    print("请选择操作：")
    print("1. 创建数据库表")
    print("2. 删除并重新创建表（危险）")
    print("3. 创建测试数据")
    print("4. 全部执行（创建表 + 测试数据）")
    print("0. 退出")
    print()

    choice = input("请输入选项 (0-4): ").strip()

    if choice == '1':
        init_database()
    elif choice == '2':
        init_database(drop_tables=True)
    elif choice == '3':
        create_test_data()
    elif choice == '4':
        init_database()
        create_test_data()
    elif choice == '0':
        print("退出")
    else:
        print("无效选项")


if __name__ == '__main__':
    main()
