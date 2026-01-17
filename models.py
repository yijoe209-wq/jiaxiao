"""
数据库模型定义
包含家庭、学生、任务、待确认任务四张表
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index, Numeric, Integer, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import QueuePool
from datetime import datetime
import uuid
import json
import os

Base = declarative_base()


def generate_id():
    """生成唯一ID"""
    return str(uuid.uuid4())


class Family(Base):
    """家庭表"""
    __tablename__ = 'families'

    family_id = Column(String(50), primary_key=True, default=generate_id)
    email = Column(String(100), unique=True, nullable=False, index=True)  # 家长邮箱
    password = Column(String(100), nullable=False)  # 密码（加密存储）
    parent_name = Column(String(50))  # 家长姓名
    created_at = Column(DateTime, default=datetime.now)

    # 关系：一个家庭有多个学生
    students = relationship("Student", back_populates="family", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Family(family_id={self.family_id}, parent_name={self.parent_name})>"


class Student(Base):
    """学生表"""
    __tablename__ = 'students'

    student_id = Column(String(50), primary_key=True, default=generate_id)
    family_id = Column(String(50), ForeignKey('families.family_id'), nullable=False)  # 必须属于某个家庭
    name = Column(String(50), nullable=False)
    grade = Column(String(20))  # 年级，如：三年级
    class_name = Column(String(50))  # 班级，如：3班2班
    created_at = Column(DateTime, default=datetime.now)

    # 关系：一个学生属于一个家庭，有多个任务
    family = relationship("Family", back_populates="students")
    tasks = relationship("Task", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name={self.name}, grade={self.grade})>"


class TaskGroup(Base):
    """任务组表（用于管理复合任务）"""
    __tablename__ = 'task_groups'

    group_id = Column(String(50), primary_key=True, default=generate_id)
    parent_wechat_id = Column(String(100), nullable=False, index=True)  # 家长的 OpenID
    raw_text = Column(Text, nullable=False)  # 原始消息
    total_tasks = Column(Integer, nullable=False)  # 任务总数
    status = Column(String(20), default='pending')  # pending/partially_confirmed/confirmed
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    tasks = relationship("Task", backref="task_group", foreign_keys="Task.group_id")

    def __repr__(self):
        return f"<TaskGroup(group_id={self.group_id}, total_tasks={self.total_tasks})>"


class Task(Base):
    """任务表"""
    __tablename__ = 'tasks'

    task_id = Column(String(50), primary_key=True, default=generate_id)
    student_id = Column(String(50), ForeignKey('students.student_id'), nullable=False, index=True)
    wechat_id = Column(String(100), nullable=False, index=True)  # 消息发送者的 OpenID
    intent = Column(String(20), nullable=False)  # assignment/notification/ignore
    subject = Column(String(50))  # 科目：语文/数学/英语
    deadline = Column(DateTime)  # 截止时间
    description = Column(Text, nullable=False)  # 任务描述
    raw_text = Column(Text)  # 原始消息

    # 新增字段：支持复合任务
    group_id = Column(String(50), ForeignKey('task_groups.group_id'), nullable=True)  # 任务组ID
    sequence = Column(Integer, nullable=True)  # 任务序号（1, 2, 3...）
    task_type = Column(String(20), nullable=True)  # 任务类型：阅读/背诵/书写/练习/听写/其他
    details = Column(Text, nullable=True)  # 任务详细内容（保留原文）

    confidence = Column(Numeric(3, 2))  # AI 置信度：0.00 - 1.00
    status = Column(String(20), default='pending')  # pending/confirmed/completed
    is_completed = Column(Boolean, default=False, index=True)
    attachments = Column(Text)  # JSON array: [{"type": "image", "path": "/uploads/xxx.jpg"}]
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系：一个任务属于一个学生
    student = relationship("Student", back_populates="tasks")

    # 索引
    __table_args__ = (
        Index('idx_student_status', 'student_id', 'status'),
        Index('idx_deadline', 'deadline'),
        Index('idx_wechat_status', 'wechat_id', 'is_completed'),
        Index('idx_group', 'group_id'),  # 新增：任务组索引
    )

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, subject={self.subject}, description={self.description[:20]}...)>"

    def to_dict(self):
        """转换为字典"""
        # 安全解析 attachments JSON
        attachments = []
        if self.attachments and self.attachments.strip():
            try:
                attachments = json.loads(self.attachments)
            except (json.JSONDecodeError, TypeError):
                attachments = []

        # 确保日期格式包含时区信息（使用 +00:00 表示本地时区）
        deadline_str = None
        if self.deadline:
            # 使用 isoformat 并添加时区信息（虽然不转换时区，但让格式明确）
            deadline_str = self.deadline.isoformat()

        return {
            'task_id': self.task_id,
            'student_id': self.student_id,
            'intent': self.intent,
            'subject': self.subject,
            'deadline': deadline_str,
            'description': self.description,
            'raw_text': self.raw_text,
            'group_id': self.group_id,
            'sequence': self.sequence,
            'task_type': self.task_type,
            'details': self.details,
            'confidence': float(self.confidence) if self.confidence else None,
            'status': self.status,
            'is_completed': self.is_completed,
            'attachments': attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class PendingTask(Base):
    """待确认任务临时表"""
    __tablename__ = 'pending_tasks'

    pending_id = Column(String(50), primary_key=True, default=generate_id)
    wechat_id = Column(String(100), nullable=False, index=True)
    task_data = Column(Text, nullable=False)  # JSON string
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PendingTask(pending_id={self.pending_id}, wechat_id={self.wechat_id})>"

    def is_expired(self):
        """检查是否过期"""
        return datetime.now() > self.expires_at

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'pending_id': self.pending_id,
            'wechat_id': self.wechat_id,
            'task_data': json.loads(self.task_data),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 数据库连接和会话管理
class Database:
    """数据库管理类"""

    def __init__(self, database_url='sqlite:///jiaxiao.db'):
        # SQLite 需要特殊配置
        if database_url.startswith('sqlite:///'):
            # 提取数据库文件路径
            db_path = database_url.replace('sqlite:///', '')

            # SQLite 连接配置
            engine_kwargs = {
                'echo': False,
                'pool_pre_ping': True,
                'poolclass': QueuePool,
                'pool_size': 5,
                'max_overflow': 10,
                'connect_args': {
                    'check_same_thread': False,  # 允许多线程访问
                    'timeout': 30,  # 超时时间（秒）
                    'isolation_level': None,  # 自动提交模式
                }
            }
        else:
            # PostgreSQL 等其他数据库
            # 确保 URL 使用正确的驱动 (postgresql+psycopg:// 而不是 postgresql://)
            if database_url.startswith('postgresql://'):
                database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

            engine_kwargs = {
                'echo': False,
                'pool_pre_ping': True,
            }

        self.engine = create_engine(database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

        # 启用 WAL 模式以提高并发性能
        if self.engine.dialect.name == 'sqlite':
            with self.engine.connect() as conn:
                conn.execute(text('PRAGMA journal_mode=WAL'))
                conn.execute(text('PRAGMA synchronous=NORMAL'))
                conn.commit()

        print("✅ 数据库表创建成功")

    def drop_tables(self):
        """删除所有表（慎用）"""
        Base.metadata.drop_all(bind=self.engine)
        print("⚠️ 数据库表已删除")

    def get_session(self):
        """获取数据库会话"""
        # 确保表存在（防止多 worker 进程问题）
        try:
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()

            if not existing_tables or 'families' not in existing_tables:
                print(f"⚠️ 表不存在，重新创建... 当前表: {existing_tables}")
                Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            print(f"⚠️ 检查表时出错: {e}")

        return self.SessionLocal()


# 全局数据库实例
# 优先使用环境变量中的 DATABASE_URL (PostgreSQL)
import os

database_url = os.getenv('DATABASE_URL')

if database_url:
    # 使用 PostgreSQL (Zeabur 提供)
    # 确保使用 psycopg 驱动
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    print(f"📊 使用 PostgreSQL: {database_url}")
else:
    # 降级到 SQLite (本地开发)
    if os.getenv('ENV') == 'development' or os.getenv('ENVIRONMENT') == 'development':
        db_path = os.path.abspath('jiaxiao.db')
    else:
        # Zeabur: 使用 /app/data 目录持久化存储
        data_dir = '/app/data'
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, 'jiaxiao.db')

    database_url = f'sqlite:///{db_path}'
    print(f"📊 使用 SQLite: {db_path}")

db = Database(database_url)


def init_db(database_url=None):
    """初始化数据库"""
    global db
    if database_url:
        db = Database(database_url)

    # 总是创建表（如果不存在）
    db.create_tables()
    return db
