"""
增强版任务解析器
使用 LLM (DeepSeek/OpenAI) 智能解析作业消息
"""
import requests
import json
from config import Config
from utils import logger


class EnhancedParser:
    """增强版解析器，使用 LLM 进行智能解析"""

    def __init__(self):
        self.api_key = Config.LLM_API_KEY
        self.api_base = Config.LLM_API_BASE
        self.model = Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

    def parse(self, content):
        """
        解析消息内容，提取任务信息

        Args:
            content: 消息内容

        Returns:
            dict: 解析结果
                {
                    'type': 'multiple' | 'single',
                    'intent': 'create_task' | 'ignore',
                    'tasks': [...],
                    'total': N
                }
        """
        try:
            # 调用 LLM 解析
            tasks = self._call_llm(content)

            if not tasks:
                return {
                    'intent': 'ignore',
                    'message': '未识别到有效任务'
                }

            # 判断任务数量
            if len(tasks) == 1:
                return {
                    'type': 'single',
                    'intent': 'create_task',
                    'task': tasks[0],
                    'total': 1
                }
            else:
                return {
                    'type': 'multiple',
                    'intent': 'create_task',
                    'tasks': tasks,
                    'total': len(tasks)
                }

        except Exception as e:
            logger.error(f"LLM 解析失败: {e}", exc_info=True)
            # 返回降级结果
            return {
                'intent': 'ignore',
                'message': f'解析失败: {str(e)}'
            }

    def _call_llm(self, content):
        """
        调用 LLM API 解析任务

        Args:
            content: 消息内容

        Returns:
            list: 任务列表
        """
        # 构建提示词
        prompt = f"""你是一个智能作业任务提取助手。请从老师的作业消息中提取所有学习任务。

老师发的作业消息：
{content}

请严格按照以下 JSON 格式输出任务列表（不要添加任何其他文字）：

[
  {{
    "subject": "科目",
    "description": "任务描述",
    "task_type": "任务类型（书写/阅读/背诵/练习/听写/其他）",
    "details": "详细要求"
  }}
]

注意：
1. 一行中有多个科目的作业时，要分别提取
2. 科目包括：语文、数学、英语、物理、化学、生物、历史、地理、政治等
3. 任务类型要准确判断
4. 描述要简洁明了
5. "无作业"不要提取为任务
"""

        # 调用 API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析 JSON
                tasks = json.loads(content)
                logger.info(f"LLM 解析成功，识别到 {len(tasks)} 个任务")
                return tasks
            else:
                logger.error(f"LLM API 请求失败: {response.status_code}")
                return []

        except requests.Timeout:
            logger.error("LLM API 请求超时")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"LLM 返回的 JSON 解析失败: {e}")
            logger.error(f"原始内容: {content}")
            return []
        except Exception as e:
            logger.error(f"LLM 调用异常: {e}")
            return []


# 创建全局实例
enhanced_parser = EnhancedParser()
