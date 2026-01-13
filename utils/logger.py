"""
日志工具模块
提供结构化日志记录功能
"""
import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from config import Config


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name='app', log_dir=None, log_level=None):
        """
        初始化日志记录器

        Args:
            name: 日志记录器名称
            log_dir: 日志目录路径
            log_level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level or getattr(logging, Config.LOG_LEVEL))

        # 避免重复添加 handler
        if self.logger.handlers:
            return

        # 日志目录
        self.log_dir = Path(log_dir or Config.LOG_DIR)
        self.log_dir.mkdir(exist_ok=True)

        # 控制台输出（带颜色）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 文件输出（结构化 JSON）
        file_handler = logging.FileHandler(
            self.log_dir / f'{name}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def log_message(self, event_type, data=None, success=True, error=None, level='info'):
        """
        记录结构化日志

        Args:
            event_type: 事件类型（如：wechat_receive, llm_call, task_create）
            data: 事件数据（字典）
            success: 是否成功
            error: 错误信息
            level: 日志级别（info, warning, error, debug）
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'success': success,
            'data': data or {},
            'error': str(error) if error else None
        }

        log_message = json.dumps(log_entry, ensure_ascii=False)

        # 根据级别选择日志方法
        log_func = getattr(self.logger, level.lower(), self.logger.info)

        if success:
            log_func(f"[{event_type}] {log_message}")
        else:
            log_func(f"[{event_type}_FAILED] {log_message}")

    def info(self, message):
        """记录 info 级别日志"""
        self.logger.info(message)

    def warning(self, message):
        """记录 warning 级别日志"""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """记录 error 级别日志"""
        self.logger.error(message, exc_info=exc_info)

    def debug(self, message):
        """记录 debug 级别日志"""
        self.logger.debug(message)

    def critical(self, message):
        """记录 critical 级别日志"""
        self.logger.critical(message)


# 全局日志实例
logger = StructuredLogger()


def get_logger(name='app'):
    """获取日志记录器实例"""
    return StructuredLogger(name)
