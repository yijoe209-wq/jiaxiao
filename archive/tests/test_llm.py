"""
测试 LLM 解析功能
"""
from llm_parser import parse_message
from utils import logger


def test_parser():
    """测试解析器"""
    print("=" * 60)
    print("家校任务助手 - LLM 解析测试")
    print("=" * 60)
    print()

    # 测试用例
    test_cases = [
        {
            'name': '语文作业',
            'text': '明天请背诵《山行》，并抄写三遍',
            'student_names': ['小明', '小红']
        },
        {
            'name': '数学作业',
            'text': '数学作业：完成练习册P23-25页',
            'student_names': ['小明', '小红']
        },
        {
            'name': '通知',
            'text': '明天记得带画笔和画纸，有美术课',
            'student_names': ['小明', '小红']
        },
        {
            'name': '英语作业',
            'text': '@所有人 英语单词听写，请家长签字',
            'student_names': ['小明', '小红']
        },
        {
            'name': '忽略消息',
            'text': '收到',
            'student_names': ['小明', '小红']
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试用例 {i}: {case['name']}")
        print(f"{'=' * 60}")
        print(f"原文: {case['text']}")
        print(f"学生: {', '.join(case['student_names'])}")
        print()

        try:
            result = parse_message(case['text'], case['student_names'])

            print("📋 解析结果：")
            print(f"  类型: {result.get('intent')}")
            print(f"  科目: {result.get('subject')}")
            print(f"  截止时间: {result.get('deadline')}")
            print(f"  描述: {result.get('description')}")
            print(f"  置信度: {result.get('confidence', 0):.0%}")
            print(f"  需确认: {result.get('need_confirm')}")

        except Exception as e:
            print(f"❌ 解析失败: {e}")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


def interactive_test():
    """交互式测试"""
    print("=" * 60)
    print("交互式测试模式")
    print("=" * 60)
    print("输入 'quit' 退出")
    print()

    student_names = ['小明', '小红']

    while True:
        text = input("\n请输入消息: ").strip()

        if text.lower() == 'quit':
            print("退出测试")
            break

        if not text:
            continue

        try:
            result = parse_message(text, student_names)

            print("\n📋 解析结果：")
            for key, value in result.items():
                if key != 'raw_text':
                    print(f"  {key}: {value}")

        except Exception as e:
            print(f"❌ 解析失败: {e}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_test()
    else:
        test_parser()
