"""
配置管理模块
从环境变量读取配置，提供默认值
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """基础配置类"""

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # 数据库配置
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'sqlite:///jiaxiao.db'
    )

    # 微信配置
    WECHAT_TOKEN = os.getenv('WECHAT_TOKEN', 'your-wechat-token')
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '')
    WECHAT_ENCODING_AES_KEY = os.getenv('WECHAT_ENCODING_AES_KEY', '')

    # LLM 配置 (DeepSeek / OpenAI)
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_API_BASE = os.getenv('LLM_API_BASE', 'https://api.deepseek.com/v1')  # DeepSeek API
    LLM_MODEL = os.getenv('LLM_MODEL', 'deepseek-chat')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '500'))

    # OCR 配置 (腾讯云)
    OCR_SECRET_ID = os.getenv('OCR_SECRET_ID', '')
    OCR_SECRET_KEY = os.getenv('OCR_SECRET_KEY', '')
    OCR_REGION = os.getenv('OCR_REGION', 'ap-beijing')

    # 异步任务配置 (生产环境使用)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')

    # 告警配置 (企业微信/钉钉 Webhook)
    ALERT_WEBHOOK_URL = os.getenv('ALERT_WEBHOOK_URL', '')
    ALERT_ERROR_THRESHOLD = int(os.getenv('ALERT_ERROR_THRESHOLD', '10'))

    # 业务配置
    TASK_CONFIRM_TIMEOUT = int(os.getenv('TASK_CONFIRM_TIMEOUT', '86400'))  # 24小时
    DEFAULT_REMINDER_TIME = os.getenv('DEFAULT_REMINDER_TIME', '17:00')  # 每日提醒时间


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///jiaxiao_dev.db'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

    # 从环境变量读取配置，支持 Zeabur 部署
    # Zeabur 会自动注入 DATABASE_URL 环境变量
    DATABASE_URL = os.getenv('DATABASE_URL')

    # 如果没有提供 DATABASE_URL，使用默认 SQLite
    if not DATABASE_URL:
        DATABASE_URL = 'sqlite:///jiaxiao.db'

    # 服务 URL（用于生成确认链接）
    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5001')

    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        # 生产环境必须设置 SECRET_KEY
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print(f"⚠️  警告：使用随机生成的 SECRET_KEY: {SECRET_KEY[:8]}...")
        print("请在环境变量中设置 SECRET_KEY 以保持会话持久化")


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_URL = 'sqlite:///jiaxiao_test.db'


# 配置字典
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name='default'):
    """根据环境名称获取配置"""
    return config_by_name.get(env_name, DevelopmentConfig)
