"""
任务处理服务
处理接收到的消息，创建任务组和任务
"""
from datetime import datetime, timedelta
from models import db, TaskGroup, Task, PendingTask
from enhanced_parser import enhanced_parser
from utils import logger
import json
import re


def parse_deadline(deadline_str):
    """
    解析截止时间字符串，支持ISO格式和相对时间（如"明天"）

    Args:
        deadline_str: 截止时间字符串

    Returns:
        datetime or None: 解析后的datetime对象
    """
    if not deadline_str:
        return None

    # 尝试ISO格式解析
    try:
        return datetime.fromisoformat(deadline_str)
    except:
        pass

    # 处理相对时间
    deadline_str = deadline_str.strip().lower()

    # 今天
    if deadline_str == '今天' or deadline_str == '今晚':
        now = datetime.now()
        return datetime(now.year, now.month, now.day, 23, 59, 59)

    # 明天
    if deadline_str == '明天' or deadline_str == '明日':
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59)

    # 后天
    if deadline_str == '后天':
        now = datetime.now()
        day_after = now + timedelta(days=2)
        return datetime(day_after.year, day_after.month, day_after.day, 23, 59, 59)

    # 尝试解析"周X"、"星期X"
    weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6, '7': 6}
    match = re.match(r'([周星])([一二三四五六七天日7])', deadline_str)
    if match:
        target_weekday = weekday_map.get(match.group(2))
        if target_weekday is not None:
            now = datetime.now()
            current_weekday = now.weekday()
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # 目标日已过，计算下周
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)
            return datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

    # 无法解析，返回None
    logger.warning(f"无法解析截止时间: {deadline_str}")
    return None


class TaskService:
    """任务处理服务"""

    @staticmethod
    def process_message(wechat_id, content, images=None):
        """
        处理接收到的消息

        Args:
            wechat_id: 家长的 OpenID
            content: 消息内容
            images: 图片URL列表

        Returns:
            dict: 处理结果
        """
        try:
            images = images or []

            # 1. 调用增强版解析器
            logger.log_message('message_received', {
                'wechat_id': wechat_id,
                'content_length': len(content) if content else 0,
                'images_count': len(images)
            })

            result = enhanced_parser.parse(content if content else '')

            if result.get('intent') == 'ignore':
                return {
                    'success': True,
                    'action': 'ignored',
                    'message': '消息已忽略'
                }

            # 2. 判断是否为复合任务
            if result.get('type') == 'multiple':
                return TaskService._process_multiple_tasks(wechat_id, content, result, images)
            else:
                return TaskService._process_single_task(wechat_id, content, result, images)

        except Exception as e:
            logger.error(f"处理消息失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def _process_multiple_tasks(wechat_id, content, result, images):
        """处理复合任务"""
        session = db.get_session()

        try:
            # 1. 创建任务组
            task_group = TaskGroup(
                parent_wechat_id=wechat_id,
                raw_text=content,
                total_tasks=result.get('total', 0),
                status='pending'
            )
            session.add(task_group)
            session.flush()  # 获取 group_id

            logger.info(f"创建任务组: {task_group.group_id}, 包含 {task_group.total_tasks} 条任务")

            # 2. 创建待确认任务记录（包含图片信息）
            task_data = {
                'type': 'multiple',
                'group_id': task_group.group_id,
                'total_tasks': task_group.total_tasks,
                'tasks': result.get('tasks', []),
                'raw_text': content
            }

            # 如果有图片，添加到 task_data
            if images:
                task_data['images'] = images

            pending_task = PendingTask(
                wechat_id=wechat_id,
                task_data=json.dumps(task_data, ensure_ascii=False),
                expires_at=datetime.now() + timedelta(seconds=86400)  # 24小时
            )
            session.add(pending_task)
            session.commit()

            logger.log_message('multiple_tasks_created', {
                'group_id': task_group.group_id,
                'total_tasks': task_group.total_tasks,
                'pending_id': pending_task.pending_id,
                'images_count': len(images)
            })

            return {
                'success': True,
                'action': 'multiple_tasks_created',
                'group_id': task_group.group_id,
                'total_tasks': task_group.total_tasks,
                'pending_id': pending_task.pending_id,
                'message': f'识别到 {task_group.total_tasks} 条任务，请确认'
            }

        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def _process_single_task(wechat_id, content, result, images):
        """处理单条任务"""
        session = db.get_session()

        try:
            # 创建待确认任务记录（包含图片信息）
            task_data = {
                'type': 'single',
                'task': result,
                'raw_text': content
            }

            # 如果有图片，添加到 task_data
            if images:
                task_data['images'] = images

            pending_task = PendingTask(
                wechat_id=wechat_id,
                task_data=json.dumps(task_data, ensure_ascii=False),
                expires_at=datetime.now() + timedelta(seconds=86400)
            )
            session.add(pending_task)
            session.commit()

            logger.log_message('single_task_created', {
                'pending_id': pending_task.pending_id,
                'intent': result.get('intent'),
                'images_count': len(images)
            })

            return {
                'success': True,
                'action': 'single_task_created',
                'pending_id': pending_task.pending_id,
                'message': '识别到 1 条任务，请确认'
            }

        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def confirm_tasks(pending_id, student_id, assignments=None):
        """
        确认任务并创建正式任务记录

        Args:
            pending_id: 待确认任务 ID
            student_id: 学生 ID
            assignments: 任务分配（复合任务时使用）
                格式: {sequence: student_id}

        Returns:
            dict: 确认结果
        """
        session = db.get_session()

        try:
            # 1. 获取待确认任务
            pending = session.query(PendingTask).filter_by(pending_id=pending_id).first()

            if not pending:
                return {'success': False, 'error': '任务不存在或已过期'}

            if pending.is_expired():
                session.delete(pending)
                session.commit()
                return {'success': False, 'error': '任务已过期'}

            # 2. 解析任务数据
            task_data = json.loads(pending.task_data)

            # 3. 根据类型创建任务
            if task_data['type'] == 'multiple':
                return TaskService._confirm_multiple_tasks(session, pending, task_data, student_id, assignments)
            else:
                return TaskService._confirm_single_task(session, pending, task_data, student_id)

        except Exception as e:
            session.rollback()
            logger.error(f"确认任务失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _confirm_multiple_tasks(session, pending, task_data, default_student_id, assignments):
        """确认复合任务"""
        group_id = task_data['group_id']
        tasks_data = task_data['tasks']
        images = task_data.get('images', [])  # 获取图片列表

        created_tasks = []

        for task_info in tasks_data:
            # 确定学生 ID
            sequence = task_info.get('sequence', 0)
            student_id = default_student_id

            if assignments and sequence in assignments:
                student_id = assignments[sequence]

            # 创建任务
            task = Task(
                group_id=group_id,
                student_id=student_id,
                wechat_id=pending.wechat_id,
                intent=task_info.get('intent', 'assignment'),  # 默认为assignment
                subject=task_info.get('subject'),
                description=task_info.get('description', '任务'),  # 提供默认值
                details=task_info.get('details'),
                raw_text=task_info.get('details', task_info.get('description')),
                sequence=sequence,
                task_type=task_info.get('task_type'),
                confidence=task_info.get('confidence', 0.8),
                status='confirmed'
            )

            # 处理截止时间
            if task_info.get('deadline'):
                task.deadline = parse_deadline(task_info['deadline'])

            # 保存图片附件
            if images:
                attachments = [{'type': 'image', 'path': url} for url in images]
                task.attachments = json.dumps(attachments, ensure_ascii=False)

            session.add(task)
            created_tasks.append(task)

        # 删除待确认任务
        session.delete(pending)
        session.commit()

        logger.log_message('multiple_tasks_confirmed', {
            'group_id': group_id,
            'count': len(created_tasks)
        })

        return {
            'success': True,
            'group_id': group_id,
            'task_count': len(created_tasks),
            'tasks': [t.task_id for t in created_tasks],
            'message': f'成功创建 {len(created_tasks)} 条任务'
        }

    @staticmethod
    def _confirm_single_task(session, pending, task_data, student_id):
        """确认单条任务"""
        # 兼容多种数据结构
        if 'task' in task_data:
            # 旧格式：{task: {...}, images: [...]}
            task_info = task_data['task']
            images = task_data.get('images', [])
        else:
            # 新格式：{description: ..., subject: ..., images: [...]}
            task_info = task_data
            images = task_data.get('images', [])

        # 创建任务
        task = Task(
            student_id=student_id,
            wechat_id=pending.wechat_id,
            intent=task_info.get('intent', 'assignment'),  # 默认为assignment
            subject=task_info.get('subject'),
            description=task_info.get('description', '任务'),  # 提供默认值
            raw_text=task_info.get('raw_text'),
            confidence=task_info.get('confidence', 0.8),
            status='confirmed'
        )

        # 处理截止时间
        if task_info.get('deadline'):
            task.deadline = parse_deadline(task_info['deadline'])

        # 保存图片附件
        if images:
            attachments = [{'type': 'image', 'path': url} for url in images]
            task.attachments = json.dumps(attachments, ensure_ascii=False)

        session.add(task)

        # 删除待确认任务
        session.delete(pending)
        session.commit()

        logger.log_message('single_task_confirmed', {
            'task_id': task.task_id,
            'images_count': len(images)
        })

        return {
            'success': True,
            'task_id': task.task_id,
            'message': '任务已确认'
        }


# 导出服务
task_service = TaskService()
