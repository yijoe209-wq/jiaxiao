"""
LLM 解析器模块
使用 DeepSeek/OpenAI API 解析微信群消息
"""
import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from config import Config
from utils import logger, metrics, track_time, FallbackParser


class LLMParser:
    """LLM 消息解析器"""

    # 系统提示词（精简版，提升响应速度）
    SYSTEM_PROMPT = """你是家校任务助手。解析微信群消息中的作业和通知。

返回JSON格式：
{
  "intent": "assignment|notification|ignore",
  "subject": "语文|数学|英语|null",
  "deadline": "YYYY-MM-DD HH:MM:SS|null",
  "description": "任务简短描述（20字以内）",
  "confidence": 0.85,
  "need_confirm": true
}

规则：
- 作业：包含"作业"、"练习"、"背诵"、"抄写"、"完成"等
- 通知：包含"通知"、"提醒"、"家长会"等
- 科目：语文/数学/英语/其他
- confidence低于0.7时need_confirm必须为true
- 只返回JSON，不要其他文字
"""

    def __init__(self, api_key=None, api_base=None, model=None):
        """
        初始化 LLM 解析器

        Args:
            api_key: API Key
            api_base: API Base URL
            model: 模型名称
        """
        self.api_key = api_key or Config.LLM_API_KEY
        self.api_base = api_base or Config.LLM_API_BASE
        self.model = model or Config.LLM_MODEL

        if not self.api_key:
            logger.warning("LLM_API_KEY 未设置，将使用降级解析器")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        ) if self.api_key else None

    @track_time('llm_parse')
    def parse(self, text, student_names=None):
        """
        解析消息文本

        Args:
            text: 消息文本
            student_names: 学生名字列表（用于自动判断归属）

        Returns:
            dict: 解析结果
        """
        if not text or not text.strip():
            return {
                'intent': 'ignore',
                'confidence': 0.0,
                'need_confirm': False,
                'raw_text': text
            }

        # 如果没有配置 API Key，使用降级解析器
        if not self.client:
            logger.log_message('llm_fallback', {'reason': 'no_api_key'})
            return FallbackParser.parse(text)

        try:
            result = self._call_llm(text, student_names)
            logger.log_message('llm_parse_success', {
                'intent': result.get('intent'),
                'confidence': result.get('confidence')
            })
            return result

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}", exc_info=True)
            logger.log_message('llm_error', {
                'error': str(e),
                'text_length': len(text)
            }, success=False)

            # 降级到关键词匹配
            logger.info("使用降级解析器")
            return FallbackParser.parse(text)

    def _call_llm(self, text, student_names=None):
        """
        调用 LLM API

        Args:
            text: 消息文本
            student_names: 学生名字列表

        Returns:
            dict: 解析结果
        """
        # 构建用户消息
        user_message = f"请解析以下消息：\n\n{text}"

        # 如果有学生信息，添加到提示中
        if student_names:
            user_message += f"\n\n该家庭的学生：{', '.join(student_names)}"

        # 调用 API（设置超时时间）
        import httpx

        # 创建自定义 timeout 的 httpx 客户端
        timeout = httpx.Timeout(
            connect=10.0,  # 连接超时 10 秒
            read=30.0,     # 读取超时 30 秒
            write=10.0,    # 写入超时 10 秒
            pool=5.0       # 连接池超时 5 秒
        )

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
            http_client=httpx.Client(timeout=timeout)
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS,
        )

        # 提取结果
        content = response.choices[0].message.content.strip()

        # 解析 JSON
        # 去掉可能的 markdown 代码块标记
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]

        result = json.loads(content)

        # 添加原始文本
        result['raw_text'] = text

        # 验证必填字段
        if 'intent' not in result:
            raise ValueError("LLM 返回缺少 intent 字段")

        # 设置默认值
        result.setdefault('subject', None)
        result.setdefault('deadline', None)
        result.setdefault('description', text[:50])
        result.setdefault('confidence', 0.7)
        result.setdefault('need_confirm', False)

        # 如果置信度低于 0.7，强制要求确认
        if result['confidence'] < 0.7:
            result['need_confirm'] = True

        # 处理截止时间
        if result.get('deadline'):
            try:
                result['deadline'] = self._parse_deadline(result['deadline'])
            except Exception as e:
                logger.warning(f"截止时间解析失败: {e}")
                result['deadline'] = None

        return result

    def _parse_deadline(self, deadline_str):
        """
        解析截止时间字符串

        Args:
            deadline_str: 时间字符串

        Returns:
            datetime: datetime 对象
        """
        if not deadline_str:
            return None

        # 尝试解析常见格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(deadline_str, fmt)
            except ValueError:
                continue

        # 如果无法解析，返回 None
        logger.warning(f"无法解析时间格式: {deadline_str}")
        return None

    def batch_parse(self, messages, student_names=None):
        """
        批量解析消息

        Args:
            messages: 消息列表
            student_names: 学生名字列表

        Returns:
            list: 解析结果列表
        """
        results = []
        for msg in messages:
            result = self.parse(msg, student_names)
            results.append(result)
        return results


# 全局解析器实例
parser = LLMParser()


def parse_message(text, student_names=None):
    """
    解析单条消息（便捷函数）

    Args:
        text: 消息文本
        student_names: 学生名字列表

    Returns:
        dict: 解析结果
    """
    return parser.parse(text, student_names)
