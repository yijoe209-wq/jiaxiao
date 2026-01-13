"""
增强版 LLM 解析器
支持识别复合任务（多条任务）
"""
from llm_parser import LLMParser
from datetime import datetime
import json


class EnhancedParser(LLMParser):
    """增强版解析器，支持复合任务"""

    # 增强的系统提示词（精简版）
    ENHANCED_SYSTEM_PROMPT = """你是家校任务助手。解析微信群消息中的作业和通知。

【核心能力】识别复合任务和截止时间
当消息中包含多条独立任务时，请将它们拆分为独立的任务列表。
重点识别截止时间关键词：今天、明天、后天、这周五、下周、X月X日、X号前等。

【识别规则】
1. 多条任务判断：包含序号（1.2.3.或第一、第二）、分段明确、多个不同动作
2. 单条任务判断：只有一个明确动作、内容简短
3. 截止时间识别：必须提取所有时间相关信息，包括相对时间（明天、下周）和绝对时间（1月15日）

【输出格式】
单条任务：
{"type":"single","intent":"assignment","subject":"语文","deadline":"明天","description":"背诵古诗","task_type":"背诵","details":"背诵《春晓》等三首古诗","confidence":0.95}

多条任务：
{"type":"multiple","total":3,"tasks":[{"sequence":1,"subject":"数学","deadline":"明天","description":"完成习题","task_type":"练习"},{"sequence":2,"subject":"语文","deadline":"后天","description":"背诵课文","task_type":"背诵"}],"confidence":0.95}

【任务类型】阅读、背诵、书写、练习、听写、其他

规则：
- 只返回JSON，不要其他文字
- deadline尽量保持原文（如"明天"、"本周五"），方便后续处理
- 如果没有明确截止时间，deadline设为null
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = self.ENHANCED_SYSTEM_PROMPT

    def parse(self, text, student_names=None):
        """
        解析消息（支持复合任务）

        Args:
            text: 消息文本
            student_names: 学生名字列表

        Returns:
            dict: 解析结果
        """
        if not text or not text.strip():
            return {
                'type': 'single',
                'intent': 'ignore',
                'confidence': 0.0,
                'need_confirm': False,
                'raw_text': text
            }

        # 使用增强的 Prompt
        try:
            result = self._call_llm_enhanced(text, student_names)
            return result
        except Exception as e:
            # 降级到父类解析器
            return super().parse(text, student_names)

    def _call_llm_enhanced(self, text, student_names=None):
        """使用增强 Prompt 调用 LLM"""
        if not self.client:
            return {
                'type': 'single',
                'intent': 'ignore',
                'confidence': 0.0
            }

        user_message = f"请解析以下消息（注意可能是多条任务）：\n\n{text}"

        if student_names:
            user_message += f"\n\n该家庭的学生：{', '.join(student_names)}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=2000,  # 增加输出长度以支持多条任务
        )

        content = response.choices[0].message.content.strip()

        # 去掉 markdown 标记
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]

        result = json.loads(content)
        result['raw_text'] = text

        return result

    def format_for_display(self, result):
        """格式化结果用于显示"""
        if result.get('type') == 'multiple':
            lines = []
            lines.append(f"📋 识别到 {result['total']} 条任务")
            lines.append("")

            for task in result.get('tasks', []):
                lines.append(f"{task['sequence']}. {task.get('task_type', '任务')}：{task['description']}")
                lines.append(f"   详情：{task['details'][:50]}...")
                lines.append("")

            return '\n'.join(lines)
        else:
            return f"任务：{result.get('description')}"


# 创建增强版解析器实例
enhanced_parser = EnhancedParser()


def parse_message_enhanced(text, student_names=None):
    """使用增强版解析器解析消息"""
    return enhanced_parser.parse(text, student_names)


if __name__ == '__main__':
    # 测试真实消息
    message = '''语文任务：
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


7.周一听写《称赞》这课剩余的词语和《纸船和风筝》这课的词语，提前准备，自行练习。'''

    print("=" * 70)
    print("🚀 增强版解析器测试")
    print("=" * 70)
    print()

    result = parse_message_enhanced(message, ['小明', '小红'])

    print(json.dumps(result, ensure_ascii=False, indent=2))
