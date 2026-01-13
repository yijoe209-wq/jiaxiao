"""
Flask 主应用
微信服务器接入、API 接口、健康检查
"""
from flask import Flask, request, jsonify, render_template, redirect
from werkzeug.utils import secure_filename
from lxml import etree
from datetime import datetime
from config import Config
from models import db, init_db, Family, Student, Task, PendingTask
from utils import logger, metrics, MetricMiddleware
from llm_parser import parse_message
import hashlib
import json
import os
import secrets
import uuid


# 创建 Flask 应用
app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大上传 16MB

# 初始化指标中间件
MetricMiddleware(app)

# 初始化数据库
init_db(Config.DATABASE_URL)

# 创建上传目录
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ========== 路由定义 ==========

@app.route('/')
def index():
    """首页 - 快速输入页面"""
    return render_template('simulate.html')


@app.route('/tasks')
def tasks_page():
    """任务确认页面"""
    return render_template('tasks.html')


@app.route('/my-tasks')
def my_tasks_page():
    """我的任务 - 任务查看和管理页面"""
    return render_template('my-tasks.html')


@app.route('/students')
def students_page():
    """学生管理页面"""
    return render_template('students.html')


@app.route('/login')
def login_page():
    """登录/注册页面"""
    return render_template('auth.html')


@app.route('/logout')
def logout_page():
    """退出登录"""
    return redirect('/login')


@app.route('/confirm')
def confirm_page():
    """任务确认页面（微信内打开）"""
    pending_id = request.args.get('pending_id')
    return render_template('confirm.html', pending_id=pending_id)


@app.route('/wechat-auth')
def wechat_auth():
    """
    微信网页授权入口
    引导用户到微信授权页面
    """
    import requests
    from urllib.parse import quote

    pending_id = request.args.get('pending_id', '')
    code = request.args.get('code', '')

    # 如果已经有 code，说明已经授权过，直接跳转到确认页
    if code:
        return redirect(f'/confirm?pending_id={pending_id}')

    # 构建 OAuth2.0 授权 URL
    redirect_uri = quote(f"https://achievement-senior-any-manchester.trycloudflare.com/wechat-auth?pending_id={pending_id}")
    auth_url = (
        f"https://open.weixin.qq.com/connect/oauth2/authorize?"
        f"appid={Config.WECHAT_APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=snsapi_base&"
        f"state=STATE#wechat_redirect"
    )

    logger.info(f"微信网页授权: redirect_uri={redirect_uri}")
    return redirect(auth_url)


@app.route('/wechat-callback')
def wechat_callback():
    """
    微信授权回调
    通过 code 获取用户 openid
    """
    import requests

    code = request.args.get('code')
    pending_id = request.args.get('pending_id', '')

    if not code:
        return "授权失败", 400

    # 通过 code 获取 access_token 和 openid
    token_url = (
        f"https://api.weixin.qq.com/sns/oauth2/access_token?"
        f"appid={Config.WECHAT_APP_ID}&"
        f"secret={Config.WECHAT_APP_SECRET}&"
        f"code={code}&"
        f"grant_type=authorization_code"
    )

    try:
        response = requests.get(token_url, timeout=10)
        data = response.json()

        if 'openid' in data:
            openid = data['openid']
            logger.info(f"微信授权成功: openid={openid[:10]}...")

            # 跳转到确认页面
            return redirect(f'/confirm?pending_id={pending_id}')
        else:
            logger.error(f"微信授权失败: {data}")
            return "授权失败，请重试", 400

    except Exception as e:
        logger.error(f"微信授权异常: {e}", exc_info=True)
        return "授权异常，请重试", 500


@app.route('/simulate')
def simulate_page():
    """模拟微信转发页面（用于测试）"""
    return render_template('simulate.html')


@app.route('/wechat-simulate')
def wechat_simulate_page():
    """微信多选消息模拟器（真实场景测试）"""
    return render_template('wechat-simulate.html')



# ========== 微信消息处理工具 ==========

def verify_signature(signature, timestamp, nonce, token):
    """
    验证微信签名

    Args:
        signature: 微信签名
        timestamp: 时间戳
        nonce: 随机数
        token: 配置的 Token

    Returns:
        bool: 验证是否通过
    """
    # 排序并拼接
    params = sorted([token, timestamp, nonce])
    tmp_str = ''.join(params)

    # SHA1 加密
    sha1 = hashlib.sha1()
    sha1.update(tmp_str.encode('utf-8'))
    hashcode = sha1.hexdigest()

    # 调试日志
    logger.info(f"🔐 签名验证: token={token}, timestamp={timestamp}, nonce={nonce}")
    logger.info(f"🔐 拼接后: {tmp_str}")
    logger.info(f"🔐 计算签名: {hashcode}")
    logger.info(f"🔐 微信签名: {signature}")
    logger.info(f"🔐 验证结果: {hashcode == signature}")

    return hashcode == signature


def parse_xml(xml_data):
    """
    解析微信 XML 消息

    Args:
        xml_data: XML 字符串

    Returns:
        dict: 解析后的消息数据
    """
    root = etree.fromstring(xml_data)
    data = {}

    # 提取所有字段
    for child in root:
        data[child.tag] = child.text

    return data


def build_xml_response(to_user, from_user, content):
    """
    构建微信 XML 响应

    Args:
        to_user: 接收方 OpenID
        from_user: 发送方 OpenID
        content: 消息内容

    Returns:
        str: XML 字符串
    """
    template = """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(to_user, from_user, int(datetime.now().timestamp()), content)

    response = template.strip()
    logger.info(f"📤 构建XML响应: to_user={to_user[:10]}..., content_preview={content[:50]}...")
    return response


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    """微信消息入口"""

    # GET 请求：服务器验证
    if request.method == 'GET':
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')

        logger.info(f"收到微信验证请求: signature={signature}, timestamp={timestamp}")

        if verify_signature(signature, timestamp, nonce, Config.WECHAT_TOKEN):
            logger.info("✅ 微信签名验证成功")
            return echostr
        else:
            logger.warning("❌ 微信签名验证失败")
            return 'Invalid signature', 403

    # POST 请求：消息处理
    else:
        try:
            # 解析 XML
            xml_data = request.data
            msg_data = parse_xml(xml_data)

            wechat_id = msg_data.get('FromUserName')  # 用户OpenID
            original_id = msg_data.get('ToUserName')    # 公众号原始ID
            msg_type = msg_data.get('MsgType')
            create_time = msg_data.get('CreateTime')

            logger.log_message('wechat_receive', {
                'wechat_id': wechat_id,
                'msg_type': msg_type,
                'create_time': create_time
            })

            logger.info(f"📨 收到消息: from_user={wechat_id[:10]}..., to_user(公众号)={original_id}, type={msg_type}")

            # 文本消息
            if msg_type == 'text':
                content = msg_data.get('Content', '')
                return handle_text_message(wechat_id, original_id, content)

            # 图片消息
            elif msg_type == 'image':
                pic_url = msg_data.get('PicUrl', '')
                return handle_image_message(wechat_id, original_id, pic_url)

            # 其他消息类型
            else:
                logger.info(f"暂不支持的消息类型: {msg_type}")
                return build_xml_response(
                    wechat_id,
                    original_id,
                    "暂不支持此类型消息"
                )

        except Exception as e:
            logger.error(f"消息处理失败: {e}", exc_info=True)
            return 'Error', 500


def process_ai_async(wechat_id, content, pending_images):
    """
    后台异步处理 AI 解析

    Args:
        wechat_id: 用户 OpenID
        content: 消息内容
        pending_images: 暂存的图片列表
    """
    try:
        logger.info(f"🔄 后台AI解析开始: wechat_id={wechat_id}")

        # 使用 task_service 处理（支持图片）
        from task_service import task_service
        result = task_service.process_message(wechat_id, content, pending_images)

        logger.info(f"✅ 后台AI解析完成: wechat_id={wechat_id}, success={result['success']}, pending_id={result.get('pending_id')}")

        # 清空已暂存的图片
        if pending_images and hasattr(handle_image_message, 'pending_images'):
            handle_image_message.pending_images.pop(wechat_id, None)

    except Exception as e:
        logger.error(f"❌ 后台AI解析失败: wechat_id={wechat_id}, error={e}", exc_info=True)


def handle_view_tasks_command(wechat_id, original_id):
    """
    处理"查看任务"命令 - 显示最新待确认任务

    Args:
        wechat_id: 用户 OpenID
        original_id: 公众号原始ID

    Returns:
        str: XML 响应
    """
    try:
        session = db.get_session()

        # 查询最新的待确认任务
        latest_pending = session.query(PendingTask).filter(
            PendingTask.wechat_id == wechat_id,
            PendingTask.expires_at > datetime.now()
        ).order_by(PendingTask.created_at.desc()).first()

        if not latest_pending:
            return build_xml_response(
                wechat_id,
                original_id,
                "📭 暂无待确认任务\n\n💡 提示：请先发送老师作业消息，AI 会自动提取任务"
            )

        # 获取任务数据
        task_data = json.loads(latest_pending.task_data)
        pending_id = latest_pending.pending_id

        # 构建消息
        lines = []
        lines.append("✨ 最新待确认任务")
        lines.append("")

        if task_data.get('type') == 'multiple':
            # 复合任务
            total = task_data.get('total_tasks', 0)
            lines.append(f"📊 共 {total} 条任务")
            lines.append("")

            # 显示所有任务（完整描述）
            tasks = task_data.get('tasks', [])
            for idx, task in enumerate(tasks, 1):
                desc = task.get('description', '任务')
                lines.append(f"{idx}. {desc}")

        else:
            # 单条任务
            desc = task_data.get('description', '任务')
            lines.append(f"📝 {desc}")

        lines.append("")
        lines.append("━━━━━━━━━")
        lines.append("")
        lines.append("👉 点击下方链接直接在微信内确认:")
        # 使用微信网页授权链接
        auth_url = f"https://achievement-senior-any-manchester.trycloudflare.com/wechat-auth?pending_id={pending_id}"
        lines.append(f"<a href='{auth_url}'>📱 点此查看并确认任务</a>")
        lines.append("")
        lines.append("💡 点击链接后可以:")
        lines.append("  • 在微信内直接查看任务")
        lines.append("  • 修改任务内容")
        lines.append("  • 选择学生分配")

        session.close()

        return build_xml_response(wechat_id, original_id, '\n'.join(lines))

    except Exception as e:
        logger.error(f"查看任务失败: {e}", exc_info=True)
        return build_xml_response(
            wechat_id,
            original_id,
            "❌ 查询失败，请稍后重试"
        )


def handle_confirm_latest_command(wechat_id, original_id):
    """
    处理"确认"命令 - 显示任务和学生选择菜单
    """
    try:
        session = db.get_session()

        # 查询最新的待确认任务
        latest_pending = session.query(PendingTask).filter(
            PendingTask.wechat_id == wechat_id,
            PendingTask.expires_at > datetime.now()
        ).order_by(PendingTask.created_at.desc()).first()

        if not latest_pending:
            session.close()
            return build_xml_response(
                wechat_id,
                original_id,
                "📭 暂无待确认任务\n\n💡 提示：请先发送老师作业消息，AI 会自动提取任务"
            )

        # 获取任务数据
        task_data = json.loads(latest_pending.task_data)
        pending_id = latest_pending.pending_id

        # 获取所有学生
        students = session.query(Student).order_by(Student.created_at).all()

        if not students:
            session.close()
            return build_xml_response(
                wechat_id,
                original_id,
                "❌ 未找到学生信息\n\n💡 请先在网页版添加学生：\nhttps://achievement-senior-any-manchester.trycloudflare.com/tasks"
            )

        # 构建确认消息
        lines = []
        lines.append("✨ 最新待确认任务")
        lines.append("")

        if task_data.get('type') == 'multiple':
            total = task_data.get('total_tasks', 0)
            lines.append(f"📊 共 {total} 条任务")
            lines.append("")

            # 显示所有任务
            tasks = task_data.get('tasks', [])
            for idx, task in enumerate(tasks, 1):
                desc = task.get('description', '任务')
                lines.append(f"{idx}. {desc}")
        else:
            desc = task_data.get('description', '任务')
            lines.append(f"📝 {desc}")

        lines.append("")
        lines.append("━━━━━━━━━")
        lines.append("")
        lines.append("👤 请选择学生分配任务：")
        lines.append("")

        # 显示学生列表（带序号）
        for idx, student in enumerate(students, 1):
            lines.append(f"{idx}. {student.name}（{student.grade}）")

        lines.append("")
        lines.append("💡 回复学生序号确认（如：回复 1）")

        session.close()

        # 暂存 pending_id，用于后续确认
        if not hasattr(handle_confirm_latest_command, 'pending_confirm'):
            handle_confirm_latest_command.pending_confirm = {}
        handle_confirm_latest_command.pending_confirm[wechat_id] = pending_id

        # 暂存学生列表
        if not hasattr(handle_confirm_latest_command, 'students_list'):
            handle_confirm_latest_command.students_list = {}
        handle_confirm_latest_command.students_list[wechat_id] = {str(i): s for i, s in enumerate(students, 1)}

        return build_xml_response(wechat_id, original_id, '\n'.join(lines))

    except Exception as e:
        logger.error(f"确认任务失败: {e}", exc_info=True)
        return build_xml_response(
            wechat_id,
            original_id,
            "❌ 确认失败，请稍后重试"
        )


def handle_help_command(wechat_id, original_id):
    """
    处理"帮助"命令 - 显示使用说明
    """
    help_text = """📖 使用帮助

🎯 快速开始：
1. 发送老师作业消息（文字+图片）
2. 等 10 秒 AI 智能解析
3. 发送"确认"快速创建任务

📋 常用命令：
• 查看任务 - 查看最新待确认任务
• 确认 - 快速确认最新任务
• 帮助 - 显示此说明

💡 小技巧：
• 可以先发送图片，再发送文字
• AI 会自动识别科目和类型
• 支持：语文、数学、英语等

🔗 网页版：
https://achievement-senior-any-manchester.trycloudflare.com/tasks"""

    return build_xml_response(wechat_id, original_id, help_text)


def handle_student_selection(wechat_id, original_id, student_number):
    """
    处理学生选择，确认任务分配
    """
    try:
        # 获取暂存的数据
        if not hasattr(handle_confirm_latest_command, 'pending_confirm') or wechat_id not in handle_confirm_latest_command.pending_confirm:
            return build_xml_response(
                wechat_id,
                original_id,
                '❌ 会话已过期，请重新发送"确认"命令'
            )

        if not hasattr(handle_confirm_latest_command, 'students_list') or wechat_id not in handle_confirm_latest_command.students_list:
            return build_xml_response(
                wechat_id,
                original_id,
                '❌ 会话已过期，请重新发送"确认"命令'
            )

        pending_id = handle_confirm_latest_command.pending_confirm[wechat_id]
        students_map = handle_confirm_latest_command.students_list[wechat_id]
        student = students_map[student_number]

        # 确认任务
        from task_service import task_service
        result = task_service.confirm_tasks(
            pending_id,
            student.student_id
        )

        # 清除暂存数据
        del handle_confirm_latest_command.pending_confirm[wechat_id]
        del handle_confirm_latest_command.students_list[wechat_id]

        if result['success']:
            return build_xml_response(
                wechat_id,
                original_id,
                f"✅ 任务已成功确认！\n\n👤 学生：{student.name}（{student.grade}）\n📊 已创建 {result.get('created_count', 0)} 条任务\n\n💡 发送'查看任务'查看详情"
            )
        else:
            return build_xml_response(
                wechat_id,
                original_id,
                f"❌ 确认失败：{result.get('error', '未知错误')}"
            )

    except Exception as e:
        logger.error(f"学生选择处理失败: {e}", exc_info=True)
        return build_xml_response(
            wechat_id,
            original_id,
            "❌ 确认失败，请稍后重试"
        )


def handle_text_message(wechat_id, original_id, content):
    """
    处理文本消息（方案 A：立即返回 + 后台处理）

    Args:
        wechat_id: 用户 OpenID
        original_id: 公众号原始ID
        content: 消息内容

    Returns:
        str: XML 响应
    """
    import threading

    # 检查是否为命令
    content_stripped = content.strip()

    if content_stripped in ['查看任务', '任务', '我的任务']:
        return handle_view_tasks_command(wechat_id, original_id)

    if content_stripped in ['确认', '确认任务', '确认最新']:
        return handle_confirm_latest_command(wechat_id, original_id)

    if content_stripped in ['帮助', 'help', '？', '?']:
        return handle_help_command(wechat_id, original_id)

    # 检查是否为学生选择（数字输入）
    if hasattr(handle_confirm_latest_command, 'students_list') and wechat_id in handle_confirm_latest_command.students_list:
        students_map = handle_confirm_latest_command.students_list.get(wechat_id, {})
        if content_stripped in students_map:
            # 用户选择了学生
            return handle_student_selection(wechat_id, original_id, content_stripped)

    # 获取暂存的图片（如果有）
    pending_images = getattr(handle_image_message, 'pending_images', {}).get(wechat_id, [])
    image_count = len(pending_images)

    logger.info(f"📨 收到文本消息: wechat_id={wechat_id}, content_length={len(content)}, images={image_count}")

    # 立即返回确认消息（< 1秒）
    quick_reply = f"""✅ 已收到！AI 正在智能解析任务...

⏰ 预计需要 5-10 秒
💬 已收到 {len(content)} 字文字{' + ' + str(image_count) + ' 张图片' if image_count > 0 else ''}

⏳ 等 10 秒后：
• 发送"确认" - 直接创建任务
• 发送"查看任务" - 查看详情"""

    # 启动后台线程处理 AI 解析
    thread = threading.Thread(
        target=process_ai_async,
        args=(wechat_id, content, pending_images),
        daemon=True
    )
    thread.start()

    logger.info(f"🚀 立即返回确认消息: wechat_id={wechat_id}")

    # 立即返回（不等待 AI 解析）
    return build_xml_response(wechat_id, original_id, quick_reply)


def handle_image_message(wechat_id, original_id, pic_url):
    """
    处理图片消息

    Args:
        wechat_id: 用户 OpenID
        original_id: 公众号原始ID
        pic_url: 图片 URL

    Returns:
        str: XML 响应
    """
    try:
        import requests
        from urllib.parse import urlparse

        # 下载图片
        response = requests.get(pic_url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"下载图片失败: {response.status_code}")

        # 生成文件名
        ext = '.jpg'  # 微信图片默认为 jpg
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(response.content)

        # 图片访问 URL
        file_url = f"/uploads/{filename}"

        # 暂存图片到会话（使用内存缓存）
        # TODO: 生产环境建议使用 Redis
        if not hasattr(handle_image_message, 'pending_images'):
            handle_image_message.pending_images = {}

        if wechat_id not in handle_image_message.pending_images:
            handle_image_message.pending_images[wechat_id] = []

        handle_image_message.pending_images[wechat_id].append(file_url)

        image_count = len(handle_image_message.pending_images[wechat_id])

        logger.info(f"收到图片，已暂存: {filename}, 用户 {wechat_id} 当前累计 {image_count} 张")

        return build_xml_response(
            wechat_id,
            original_id,
            f"📷 图片已收到（{image_count}/{image_count}）\n\n继续发送文字或其他图片，完成后请发送文字消息触发解析"
        )

    except Exception as e:
        logger.error(f"处理图片消息失败: {e}", exc_info=True)
        return build_xml_response(
            wechat_id,
            original_id,
            f"❌ 图片处理失败: {str(e)}"
        )


def build_confirm_message(result, pending_id):
    """
    构建确认消息（包含微信内打开链接）

    Args:
        result: 解析结果
        pending_id: 待确认任务 ID

    Returns:
        str: 确认消息文本
    """
    # 使用 Cloudflare Tunnel 外网地址（微信可访问）
    host_url = "https://achievement-senior-any-manchester.trycloudflare.com"

    # 生成确认链接
    confirm_url = f"{host_url}/confirm?pending_id={pending_id}"

    lines = []

    if result.get('type') == 'multiple':
        # 复合任务
        lines.append("✅ 已识别任务")
        lines.append("")
        lines.append(f"📊 共 {result['total_tasks']} 条任务")

        # 显示前3条任务预览
        tasks = result.get('tasks', [])[:3]
        for task in tasks:
            lines.append(f"{task['sequence']}. {task['description']}")

        if result['total_tasks'] > 3:
            lines.append(f"... 还有 {result['total_tasks'] - 3} 条")

    else:
        # 单条任务
        lines.append("✅ 已识别任务")
        lines.append("")
        lines.append(f"📝 {result.get('description', '任务')}")

    lines.append("")
    lines.append("━━━━━━━━━")
    lines.append("")
    lines.append("<a href='" + confirm_url + "'>👉 点此确认任务</a>")
    lines.append("")
    lines.append("在微信中打开，可直接分配给学生")

    return '\n'.join(lines)


# ========== API 接口 ==========

@app.route('/api/pending')
def get_pending_tasks():
    """获取待确认任务列表"""
    try:
        session = db.get_session()
        pending_tasks = session.query(PendingTask).filter(
            PendingTask.expires_at > datetime.now()
        ).order_by(PendingTask.created_at.desc()).all()

        result = []
        for pending in pending_tasks:
            result.append({
                'pending_id': pending.pending_id,
                'wechat_id': pending.wechat_id,
                'task_data': json.loads(pending.task_data),
                'created_at': pending.created_at.isoformat() if pending.created_at else None,
                'expires_at': pending.expires_at.isoformat() if pending.expires_at else None
            })

        session.close()

        return jsonify({
            'success': True,
            'tasks': result
        })

    except Exception as e:
        logger.error(f"获取待确认任务失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate', methods=['POST'])
def simulate_wechat_forward():
    """模拟微信转发消息（用于测试）"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        images = data.get('images', [])  # 获取图片列表

        if not message and not images:
            return jsonify({'error': '消息内容和图片不能同时为空'}), 400

        # 如果只有图片没有文字，直接创建任务，不调用 AI
        if not message and images:
            import json
            from datetime import timedelta
            session = db.get_session()
            try:
                # 创建单个任务
                task_data = {
                    'type': 'single',
                    'description': '（请查看图片附件）',
                    'subject': None,
                    'deadline': None,
                    'images': images
                }

                # 创建待确认任务
                pending_id = str(uuid.uuid4())
                pending_task = PendingTask(
                    pending_id=pending_id,
                    wechat_id='test_wechat_id_123',
                    task_data=json.dumps(task_data, ensure_ascii=False),
                    expires_at=datetime.now() + timedelta(seconds=86400)
                )
                session.add(pending_task)
                session.commit()

                logger.info(f"创建纯图片任务: pending_id={pending_id}, images={len(images)}")

                return jsonify({
                    'success': True,
                    'total_tasks': 1,
                    'pending_id': pending_id,
                    'message': '任务创建成功，请确认'
                })
            finally:
                session.close()

        # 有文字内容时，使用测试微信号调用 AI 解析
        test_wechat_id = 'test_wechat_id_123'

        # 调用任务服务处理消息
        from task_service import task_service
        result = task_service.process_message(test_wechat_id, message, images)

        if result['success']:
            return jsonify({
                'success': True,
                'total_tasks': result.get('total_tasks', 1),
                'pending_id': result.get('pending_id'),
                'message': '消息解析成功，请点击链接确认'
            })
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"模拟转发失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========== 认证相关 API ==========

def hash_password(password):
    """加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/api/register', methods=['POST'])
def register():
    """家长注册"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        parent_name = data.get('parent_name', '').strip()

        # 验证
        if not email or '@' not in email:
            return jsonify({'error': '请输入有效的邮箱地址'}), 400

        if len(password) < 6:
            return jsonify({'error': '密码至少6位'}), 400

        if not parent_name:
            return jsonify({'error': '请输入家长姓名'}), 400

        session = db.get_session()

        # 检查邮箱是否已注册
        existing = session.query(Family).filter_by(email=email).first()
        if existing:
            session.close()
            return jsonify({'error': '该邮箱已注册'}), 400

        # 创建家庭
        family = Family(
            email=email,
            password=hash_password(password),
            parent_name=parent_name
        )
        session.add(family)
        session.commit()

        family_id = family.family_id
        session.close()

        logger.info(f"新家庭注册: email={email}, name={parent_name}")
        return jsonify({
            'success': True,
            'family_id': family_id,
            'message': '注册成功'
        })

    except Exception as e:
        logger.error(f"注册失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """家长登录"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': '请输入邮箱和密码'}), 400

        session = db.get_session()
        family = session.query(Family).filter_by(email=email).first()

        if not family or family.password != hash_password(password):
            session.close()
            return jsonify({'error': '邮箱或密码错误'}), 401

        session.close()

        # 设置会话（简单实现，使用 session_id）
        session_id = secrets.token_hex(16)

        # 实际项目应该使用 Flask-Login 或 JWT
        # 这里简化为直接返回 family_id
        return jsonify({
            'success': True,
            'family_id': family.family_id,
            'parent_name': family.parent_name,
            'message': '登录成功'
        })

    except Exception as e:
        logger.error(f"登录失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/me', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    try:
        family_id = request.headers.get('X-Family-ID')

        if not family_id:
            return jsonify({'error': '未登录'}), 401

        session = db.get_session()
        family = session.query(Family).filter_by(family_id=family_id).first()

        if not family:
            session.close()
            return jsonify({'error': '用户不存在'}), 404

        result = {
            'family_id': family.family_id,
            'email': family.email,
            'parent_name': family.parent_name
        }

        session.close()
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取用户信息失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========== 学生管理 API ==========

@app.route('/api/students', methods=['GET'])
def get_students():
    """获取当前家庭的学生列表"""
    try:
        family_id = request.headers.get('X-Family-ID')

        session = db.get_session()

        # 如果提供了 family_id，按家庭过滤；否则返回所有学生（演示模式）
        if family_id:
            students = session.query(Student).filter_by(family_id=family_id).order_by(Student.created_at).all()
        else:
            # 演示模式：返回所有学生
            students = session.query(Student).order_by(Student.created_at).all()

        result = [{
            'student_id': s.student_id,
            'name': s.name,
            'grade': s.grade,
            'class_name': s.class_name,
            'created_at': s.created_at.isoformat() if s.created_at else None
        } for s in students]

        session.close()
        return jsonify({'success': True, 'students': result})

    except Exception as e:
        logger.error(f"获取学生列表失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/students', methods=['POST'])
def add_student():
    """添加学生（需要登录）"""
    try:
        family_id = request.headers.get('X-Family-ID')

        if not family_id:
            return jsonify({'error': '未登录'}), 401

        data = request.json
        name = data.get('name', '').strip()
        grade = data.get('grade', '').strip()
        class_name = data.get('class_name', '').strip()

        if not name:
            return jsonify({'error': '学生姓名不能为空'}), 400

        session = db.get_session()
        student = Student(
            family_id=family_id,
            name=name,
            grade=grade if grade else None,
            class_name=class_name if class_name else None
        )
        session.add(student)
        session.commit()

        student_id = student.student_id
        session.close()

        logger.info(f"新增学生: family_id={family_id}, name={name}, grade={grade}, class_name={class_name}, id={student_id}")
        return jsonify({'success': True, 'student_id': student_id})

    except Exception as e:
        logger.error(f"添加学生失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """更新学生信息"""
    try:
        family_id = request.headers.get('X-Family-ID')

        if not family_id:
            return jsonify({'error': '未登录'}), 401

        data = request.json
        name = data.get('name', '').strip()
        grade = data.get('grade', '').strip()
        class_name = data.get('class_name', '').strip()

        if not name:
            return jsonify({'error': '学生姓名不能为空'}), 400

        session = db.get_session()
        student = session.query(Student).filter_by(student_id=student_id).first()

        if not student:
            session.close()
            return jsonify({'error': '学生不存在'}), 404

        # 验证学生是否属于当前家庭
        if student.family_id != family_id:
            session.close()
            return jsonify({'error': '无权操作此学生'}), 403

        # 更新信息
        student.name = name
        student.grade = grade if grade else None
        student.class_name = class_name if class_name else None

        session.commit()
        session.close()

        logger.info(f"更新学生: id={student_id}, name={name}, grade={grade}, class_name={class_name}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"更新学生失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """删除学生"""
    try:
        family_id = request.headers.get('X-Family-ID')

        if not family_id:
            return jsonify({'error': '未登录'}), 401

        session = db.get_session()
        student = session.query(Student).filter_by(student_id=student_id).first()

        if not student:
            session.close()
            return jsonify({'error': '学生不存在'}), 404

        # 验证学生是否属于当前家庭
        if student.family_id != family_id:
            session.close()
            return jsonify({'error': '无权操作此学生'}), 403

        session.delete(student)
        session.commit()
        session.close()

        logger.info(f"删除学生: id={student_id}, family_id={family_id}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"删除学生失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/confirm', methods=['POST'])
def confirm_task():
    """确认任务（支持用户编辑后的数据）"""
    try:
        data = request.json
        pending_id = data.get('pending_id')
        student_id = data.get('student_id')
        updated_tasks = data.get('updated_tasks')  # 用户编辑后的任务数据
        family_id = request.headers.get('X-Family-ID')

        if not pending_id or not student_id:
            return jsonify({'error': '缺少必要参数'}), 400

        session = db.get_session()
        try:
            # 验证学生是否存在
            student = session.query(Student).filter_by(
                student_id=student_id
            ).first()

            if not student:
                session.close()
                return jsonify({'error': '学生不存在'}), 404

            # 如果提供了 family_id，验证学生是否属于当前家庭
            if family_id and student.family_id != family_id:
                session.close()
                return jsonify({'error': '无权操作此学生'}), 403

            # 获取待确认任务（不需要按 wechat_id 过滤）
            pending_task = session.query(PendingTask).filter_by(
                pending_id=pending_id
            ).first()

            if not pending_task:
                session.close()
                return jsonify({'error': '任务不存在或已过期'}), 404

            # 如果用户提供了编辑后的任务数据，先更新
            if updated_tasks:
                import json
                task_data = json.loads(pending_task.task_data)
                if 'tasks' in task_data:
                    task_data['tasks'] = updated_tasks
                pending_task.task_data = json.dumps(task_data, ensure_ascii=False)
                session.commit()
                logger.info(f"更新待确认任务数据: pending_id={pending_id}")
        finally:
            session.close()

        # 使用 task_service 处理
        from task_service import task_service
        result = task_service.confirm_tasks(pending_id, student_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"确认任务失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<student_id>')
def get_student_tasks(student_id):
    """获取学生的任务列表"""
    session = db.get_session()
    try:
        # 返回所有任务（包括已完成），由前端过滤
        tasks = session.query(Task).filter_by(
            student_id=student_id
        ).order_by(Task.created_at.desc()).all()

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """标记任务完成"""
    session = db.get_session()
    try:
        task = session.query(Task).filter_by(task_id=task_id).first()

        if not task:
            return jsonify({'error': '任务不存在'}), 404

        task.is_completed = True
        task.status = 'completed'
        session.commit()

        logger.log_message('task_completed', {'task_id': task_id})

        return jsonify({'success': True, 'message': '任务已完成'})

    except Exception as e:
        logger.error(f"标记任务完成失败: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片文件"""
    try:
        if 'file' not in request.files:
            logger.warning('上传请求中没有文件字段')
            return jsonify({'success': False, 'error': '没有文件'}), 400

        file = request.files['file']

        if file.filename == '':
            logger.warning('文件名为空')
            return jsonify({'success': False, 'error': '未选择文件'}), 400

        if not allowed_file(file.filename):
            logger.warning(f'不支持的文件类型: {file.filename}')
            return jsonify({'success': False, 'error': '不支持的文件类型，仅支持图片（png, jpg, jpeg, gif, webp）'}), 400

        # 生成安全的文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        logger.info(f'准备保存文件: {filename}, 大小: {file.content_length}')

        file.save(filepath)

        # 返回可访问的 URL
        file_url = f"/uploads/{filename}"

        logger.info(f"文件上传成功: {filename}, URL: {file_url}")

        return jsonify({
            'success': True,
            'url': file_url,
            'filename': filename
        })

    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/health')
def health_check():
    """健康检查接口"""
    checks = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # 数据库检查
    try:
        from sqlalchemy import text
        session = db.get_session()
        session.execute(text('SELECT 1'))
        checks['checks']['database'] = 'ok'
    except Exception as e:
        checks['checks']['database'] = f'error: {e}'
        checks['status'] = 'error'

    # LLM API 检查（可选）
    if Config.LLM_API_KEY:
        checks['checks']['llm_api'] = 'configured'
    else:
        checks['checks']['llm_api'] = 'not configured'

    status_code = 200 if checks['status'] == 'ok' else 503
    return jsonify(checks), status_code


@app.route('/metrics')
def get_metrics():
    """查看系统指标"""
    return jsonify(metrics.get_stats())


# ========== 错误处理 ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ========== 启动入口 ==========

if __name__ == '__main__':
    import os

    logger.info("🚀 启动家校任务管理助手")
    logger.info(f"📊 数据库: {Config.DATABASE_URL}")
    logger.info(f"🤖 LLM 模型: {Config.LLM_MODEL}")

    # 从环境变量读取端口，默认 5000
    port = int(os.getenv('PORT', 5001))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
