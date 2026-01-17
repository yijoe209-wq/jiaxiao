"""
增强版 LLM 解析器
使用 DeepSeek/OpenAI API 智能解析微信群消息
支持单任务和多任务识别
"""
from openai import OpenAI
from config import Config
from utils import logger
from utils.fallback import FallbackParser
import json
import re


class EnhancedParser:
    """增强版解析器，使用 LLM API"""

    def __init__(self):
        """初始化解析器"""
        self.client = None
        self.fallback_parser = FallbackParser()

        # 检查 API Key
        if not Config.LLM_API_KEY:
            logger.warning("⚠️ LLM_API_KEY 未配置，将使用降级解析器")
            return

        try:
            # 初始化 OpenAI 客户端（兼容 DeepSeek）
            self.client = OpenAI(
                api_key=Config.LLM_API_KEY,
                base_url=Config.LLM_API_BASE
            )
            logger.info(f"✅ LLM 客户端初始化成功: {Config.LLM_MODEL}")
        except Exception as e:
            logger.error(f"❌ LLM 客户端初始化失败: {e}")
            self.client = None

    def parse(self, content):
        """
        解析消息内容

        Args:
            content: 消息文本

        Returns:
            dict: 解析结果
        """
        if not content or not content.strip():
            return {
                'intent': 'ignore',
                'type': 'single',
                'description': '',
                'confidence': 0.0
            }

        # 优先使用 LLM 解析
        if self.client:
            try:
                result = self._call_llm(content)
                if result:
                    return result
            except Exception as e:
                logger.error(f"❌ LLM 解析失败，使用降级方案: {e}")

        # 降级到关键词解析
        logger.info("⚠️ 使用降级解析器")
        fallback_result = self.fallback_parser.parse(content)

        # 转换为统一格式
        return {
            'intent': fallback_result.get('intent', 'ignore'),
            'type': 'single',
            'subject': fallback_result.get('subject'),
            'deadline': fallback_result.get('deadline').isoformat() if fallback_result.get('deadline') else None,
            'description': fallback_result.get('description', content),
            'confidence': fallback_result.get('confidence', 0.5),
            'task_type': None,
            'details': content
        }

    def _call_llm(self, content):
        """
        调用 LLM API 解析消息

        Args:
            content: 消息文本

        Returns:
            dict: 解析结果
        """
        # 构建提示词
        system_prompt = """你是一个专业的作业任务提取助手。你的任务是从老师发在微信群的消息中提取作业任务。

**返回格式**（必须是合法的 JSON）：
{
  "intent": "assignment" | "notification" | "ignore",
  "type": "single" | "multiple",
  "tasks": [
    {
      "sequence": 1,
      "subject": "语文/数学/英语/政治/历史/地理/生物/科学/音乐/美术/体育/其他",
      "task_type": "阅读/背诵/书写/练习/听写/其他",
      "description": "简短的任务描述（10-20字）",
      "details": "完整的任务原文",
      "deadline": "截止日期（YYYY-MM-DD格式，或相对时间如'明天'）"
    }
  ],
  "total": 任务总数
}

**识别规则**：
1. **intent（意图）**：
   - assignment: 包含作业、练习、背诵、抄写、完成、复习、预习等关键词
   - notification: 包含通知、提醒、带物品、家长会等关键词
   - ignore: 明确说明"无作业"、"没有作业"等

2. **subject（科目）**：
   - 语文/数学/英语/政治/历史/地理/生物/科学/音乐/美术/体育/其他
   - 根据关键词判断：如"单词"、"听写"→英语，"古诗"、"背诵"→语文

3. **task_type（任务类型）**：
   - 阅读：阅读课文、看书等
   - 背诵：背诵古诗、课文等
   - 书写：抄写、默写、写字等
   - 练习：做练习册、试卷、作业本等
   - 听写：单词听写、生字听写等
   - 其他：无法归类的任务

4. **deadline（截止时间）**：
   - 提取明确的日期（如"明天"、"1月15日"、"周三"、"明天前"、"后天前"、"本周内"等）
   - 如果消息中有时间相关词语但无法确定具体日期，提取相对时间（如"明天前"→明天，"后天前"→后天）
   - 如果完全没有提到时间，返回 null

**示例**：

输入：
"1.英语：1-4单元粗体字单词一英一汉；4单元短语一英一汉；打卡
2.政治：卷子，3题不写；地理：第一单元卷子写完；历史：卷子；生物：无作业
3.语文：文言文卷子四题写完；卷子写完
4.数学：卷子写完；上课写的4题研究一下"

输出：
{
  "intent": "assignment",
  "type": "multiple",
  "tasks": [
    {"sequence": 1, "subject": "英语", "task_type": "书写", "description": "1-4单元粗体字单词一英一汉", "details": "1-4单元粗体字单词一英一汉", "deadline": null},
    {"sequence": 2, "subject": "英语", "task_type": "书写", "description": "4单元短语一英一汉", "details": "4单元短语一英一汉", "deadline": null},
    {"sequence": 3, "subject": "英语", "task_type": "其他", "description": "打卡", "details": "打卡", "deadline": null},
    {"sequence": 4, "subject": "政治", "task_type": "练习", "description": "卷子（3题不写）", "details": "卷子，3题不写", "deadline": null},
    {"sequence": 5, "subject": "地理", "task_type": "练习", "description": "第一单元卷子写完", "details": "第一单元卷子写完", "deadline": null},
    {"sequence": 6, "subject": "历史", "task_type": "练习", "description": "卷子", "details": "卷子", "deadline": null},
    {"sequence": 7, "subject": "语文", "task_type": "练习", "description": "文言文卷子四题写完", "details": "文言文卷子四题写完", "deadline": null},
    {"sequence": 8, "subject": "语文", "task_type": "练习", "description": "卷子写完", "details": "卷子写完", "deadline": null},
    {"sequence": 9, "subject": "数学", "task_type": "练习", "description": "卷子写完", "details": "卷子写完", "deadline": null},
    {"sequence": 10, "subject": "数学", "task_type": "其他", "description": "上课写的4题研究一下", "details": "上课写的4题研究一下", "deadline": null}
  ],
  "total": 10
}

输入：
"语文：完成《春晓》背诵，明天检查"

输出：
{
  "intent": "assignment",
  "type": "single",
  "tasks": [
    {"sequence": 1, "subject": "语文", "task_type": "背诵", "description": "完成《春晓》背诵", "details": "完成《春晓》背诵，明天检查", "deadline": "明天"}
  ],
  "total": 1
}

输入：
"英语作业：完成第3单元单词练习，每个单词写5遍，明天前提交"

输出：
{
  "intent": "assignment",
  "type": "single",
  "tasks": [
    {"sequence": 1, "subject": "英语", "task_type": "书写", "description": "第3单元单词练习，每个单词写5遍", "details": "英语作业：完成第3单元单词练习，每个单词写5遍，明天前提交", "deadline": "明天"}
  ],
  "total": 1
}

输入：
"今天没有作业"

输出：
{
  "intent": "ignore",
  "type": "single",
  "tasks": [],
  "total": 0
}

**重要**：
- 只返回 JSON，不要有其他文字
- tasks 数组中的每个任务必须包含所有必需字段
- 如果是 multiple 类型，tasks 数组至少要有 2 个任务
- description 要简洁，details 保留原文
"""

        try:
            # 调用 LLM API
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS
            )

            # 解析响应
            response_text = response.choices[0].message.content.strip()
            logger.info(f"🤖 LLM 原始响应: {response_text[:200]}...")

            # 提取 JSON（可能包含 markdown 代码块）
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            elif response_text.startswith('```'):
                response_text = response_text.strip('`').replace('json', '').strip()

            # 解析 JSON
            result = json.loads(response_text)
            logger.info(f"✅ LLM 解析成功: intent={result.get('intent')}, type={result.get('type')}, total={result.get('total', 0)}")

            # 验证并标准化结果
            return self._normalize_result(result)

        except json.JSONDecodeError as e:
            logger.error(f"❌ LLM 返回的 JSON 格式错误: {e}")
            logger.error(f"原始响应: {response_text}")
            return None
        except Exception as e:
            logger.error(f"❌ LLM API 调用失败: {e}")
            return None

    def _normalize_result(self, result):
        """
        标准化解析结果

        Args:
            result: LLM 返回的原始结果

        Returns:
            dict: 标准化后的结果
        """
        intent = result.get('intent', 'ignore')

        # 如果是 ignore，直接返回
        if intent == 'ignore' or result.get('total', 0) == 0:
            return {
                'intent': 'ignore',
                'type': 'single',
                'description': '',
                'confidence': 0.9
            }

        task_type = result.get('type', 'single')
        tasks = result.get('tasks', [])

        # 单任务：转换为简单格式
        if task_type == 'single' and len(tasks) == 1:
            task = tasks[0]
            return {
                'intent': 'assignment',
                'type': 'single',
                'subject': task.get('subject'),
                'task_type': task.get('task_type'),
                'description': task.get('description', task.get('details', ''))[:100],
                'details': task.get('details', ''),
                'deadline': task.get('deadline'),
                'confidence': 0.9
            }

        # 多任务：返回任务列表
        return {
            'intent': 'assignment',
            'type': 'multiple',
            'total': len(tasks),
            'tasks': tasks,
            'confidence': 0.9
        }


# 导出单例
enhanced_parser = EnhancedParser()
