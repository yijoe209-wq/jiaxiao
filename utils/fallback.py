"""
降级策略模块
LLM 失败时使用基于关键词的简单解析
"""
import re
from datetime import datetime, timedelta


class FallbackParser:
    """降级解析器（LLM 失败时使用）"""

    # 科目关键词映射
    SUBJECT_KEYWORDS = {
        '语文': ['语文', '背诵', '古诗', '课文', '抄写', '阅读'],
        '数学': ['数学', '练习册', '口算', '计算', '应用题', '奥数'],
        '英语': ['英语', '单词', '听写', '读音', '口语', '英语'],
        '科学': ['科学', '实验', '观察'],
        '美术': ['画画', '美术', '手工', '绘画'],
        '音乐': ['音乐', '唱歌', '乐器'],
        '体育': ['体育', '跑步', '跳绳', '运动'],
    }

    # 作业关键词
    ASSIGNMENT_KEYWORDS = ['作业', '练习', '背诵', '抄写', '完成', '复习', '预习']

    # 通知关键词
    NOTIFICATION_KEYWORDS = ['通知', '提醒', '带', '明天', '家长会', '开会']

    # 时间关键词映射
    TIME_KEYWORDS = {
        '明天': 1,
        '后天': 2,
        '下周': 7,
        '本周': 0,
    }

    @staticmethod
    def parse(text):
        """
        基于关键词解析消息

        Args:
            text: 消息文本

        Returns:
            dict: 解析结果
        """
        result = {
            'intent': 'ignore',
            'subject': None,
            'deadline': None,
            'description': text.strip(),
            'confidence': 0.5,
            'need_confirm': True,
            'raw_text': text
        }

        # 判断意图
        if any(word in text for word in FallbackParser.ASSIGNMENT_KEYWORDS):
            result['intent'] = 'assignment'
            result['confidence'] = 0.6

            # 识别科目
            result['subject'] = FallbackParser._detect_subject(text)

            # 识别截止时间
            result['deadline'] = FallbackParser._detect_deadline(text)

        elif any(word in text for word in FallbackParser.NOTIFICATION_KEYWORDS):
            result['intent'] = 'notification'
            result['confidence'] = 0.6

            # 识别时间
            result['deadline'] = FallbackParser._detect_deadline(text)

        return result

    @staticmethod
    def _detect_subject(text):
        """
        识别科目

        Args:
            text: 消息文本

        Returns:
            str: 科目名称，识别不到返回 None
        """
        for subject, keywords in FallbackParser.SUBJECT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return subject
        return None

    @staticmethod
    def _detect_deadline(text):
        """
        识别截止时间

        Args:
            text: 消息文本

        Returns:
            datetime: 截止时间，识别不到返回 None
        """
        # 查找时间关键词
        for keyword, days in FallbackParser.TIME_KEYWORDS.items():
            if keyword in text:
                if days == 0:
                    # 本周：默认周五
                    deadline = datetime.now()
                else:
                    deadline = datetime.now() + timedelta(days=days)

                # 设置为当天 23:59:59
                deadline = deadline.replace(hour=23, minute=59, second=59, microsecond=0)
                return deadline

        # 尝试匹配日期格式（如：1月15日、明天周三等）
        date_patterns = [
            r'(\d+)月(\d+)日',
            r'(\d+)\/(\d+)',
            r'周[一二三四五六日]',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                # 简单处理：返回明天的日期（生产环境需要更复杂的日期解析）
                deadline = datetime.now() + timedelta(days=1)
                deadline = deadline.replace(hour=23, minute=59, second=59, microsecond=0)
                return deadline

        return None

    @staticmethod
    def extract_student_name(text, student_names):
        """
        尝试从文本中提取学生名字

        Args:
            text: 消息文本
            student_names: 该家庭的学生名字列表

        Returns:
            str: 匹配的学生名字，否则返回 None
        """
        for name in student_names:
            if name in text:
                return name
        return None


# 便捷函数
def parse_with_fallback(text):
    """使用降级解析器解析文本"""
    return FallbackParser.parse(text)
