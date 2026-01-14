#!/usr/bin/env python3
"""
使用 Playwright 批量生成测试数据
- 10 名学生
- 20 条任务消息
- 10 条解析并确认
- 10 条不确认
"""

import asyncio
import random
from playwright.async_api import async_playwright

# 测试数据
STUDENT_NAMES = [
    "张伟", "李娜", "王芳", "刘洋", "陈静",
    "杨帆", "赵敏", "孙强", "周杰", "吴婷"
]

GRADES = ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级"]

# 任务消息模板（包含不同科目和复杂度）
TASK_TEMPLATES = [
    "数学作业：完成练习册第{page}页，明天交",
    "语文作业：背诵课文《{title}》，默写生字{count}个",
    "英语作业：听写第{unit}单元单词，家长签字",
    "数学作业：{title}试卷错题整理，明天测试",
    "语文作业：预习第{chapter}课，画出重点段落",
    "英语作业：完成练习册第{page}页，阅读理解",
    "数学作业：口算练习{count}题，要求计时",
    "语文作业：作文《{title}》，不少于{count}字",
    "英语作业：背诵对话，录制视频发送到群",
    "数学作业：复习{title}单元，准备单元测试",
    "语文作业：整理复习资料，重点背诵古诗{count}首",
    "英语作业：制作单词卡片，每个单词配图",
    "数学作业：完成应用题{count}道，写出解题过程",
    "语文作业：阅读课外书《{title}》，写读书笔记",
    "科学作业：观察{title}，记录观察日记",
    "美术作业：画一幅{title}的画，使用水彩",
    "音乐作业：练习歌曲《{title}》，下节课检查",
    "体育作业：跳绳{count}个，拍视频",
    "数学作业：整理错题本，家长检查签字",
    "语文作业：练字{count}行，注意笔画顺序"
]

SUBJECTS = ["数学", "语文", "英语", "科学", "美术", "音乐", "体育"]

DEADLINES = ["明天", "周五", "下周", "后天"]

# 图片URL示例（使用占位符，实际测试时可以替换为真实图片）
IMAGE_URLS = [
    "https://via.placeholder.com/300x400/FF6B6B/FFFFFF?text=作业图片1",
    "https://via.placeholder.com/300x400/4ECDC4/FFFFFF?text=作业图片2",
    "https://via.placeholder.com/300x400/45B7D1/FFFFFF?text=作业图片3",
    "https://via.placeholder.com/300x400/96CEB4/FFFFFF?text=作业图片4",
    "https://via.placeholder.com/300x400/FFEAA7/333333?text=作业图片5"
]


async def fill_placeholder(input_element, value):
    """填充输入框并触发input事件"""
    await input_element.fill(value)
    await input_element.dispatch_event('input', {'bubbles': True})


async def register_and_login(page, user_num):
    """注册并登录新用户"""
    print(f"\n{'='*60}")
    print(f"📝 注册用户 {user_num}/1")
    print(f"{'='*60}")

    # 访问登录页
    await page.goto("http://localhost:5001/login")
    await page.wait_for_load_state("networkidle")

    # 点击注册标签
    await page.click('text=注册')
    await page.wait_for_timeout(500)

    # 填写注册信息
    email = f"test_user_{user_num}@example.com"
    parent_name = f"测试家长{user_num}"

    await fill_placeholder(page.locator('input[placeholder="家长姓名"]'), parent_name)
    await fill_placeholder(page.locator('input[placeholder="邮箱"]'), email)
    await fill_placeholder(page.locator('input[placeholder="设置密码"]'), "test123456")

    # 提交注册
    await page.click('button:has-text("注册")')

    # 等待跳转
    await page.wait_for_url("**/my-tasks")
    print(f"✅ 注册成功: {email}")

    return email


async def add_students(page, count=10):
    """批量添加学生"""
    students = []

    print(f"\n👥 添加 {count} 名学生...")

    for i in range(count):
        student_name = STUDENT_NAMES[i % len(STUDENT_NAMES)]
        grade = random.choice(GRADES)

        print(f"  添加学生 {i+1}: {student_name} ({grade})")

        # 点击添加学生按钮
        await page.click('button:has-text("添加学生")')
        await page.wait_for_timeout(300)

        # 填写学生信息
        await page.click('button:has-text("新增学生")')

        await page.wait_for_selector('input[placeholder="学生姓名"]')
        await fill_placeholder(page.locator('input[placeholder="学生姓名"]'), student_name)

        # 选择年级
        await page.click('select')
        await page.click(f'option:has-text("{grade}")')

        # 提交
        await page.click('button:has-text("添加")')

        # 等待添加成功
        await page.wait_for_timeout(500)

        # 获取学生ID（从下拉框中获取）
        await page.wait_for_timeout(500)
        select_element = page.locator('select#studentSelect')
        options = await select_element.locator('option').all()

        student_id = None
        for option in options:
            text = await option.text_content()
            if student_name in text:
                student_id = await option.get_attribute('value')
                break

        if student_id:
            students.append({
                'name': student_name,
                'grade': grade,
                'id': student_id
            })
            print(f"    ✅ 添加成功，ID: {student_id}")

        # 关闭弹窗
        await page.wait_for_timeout(300)

    print(f"\n✅ 成功添加 {len(students)} 名学生")
    return students


async def create_task_with_parsing(page, students, task_num, should_confirm=True):
    """创建任务并解析"""

    student = random.choice(students)
    template = random.choice(TASK_TEMPLATES)

    # 填充模板
    task_message = template.format(
        page=random.randint(1, 50),
        title=random.choice(["加减法", "乘法口诀", "分数的认识", "应用题",
                            "春天", "我的家乡", "难忘的一刻", "我的梦想",
                            "日常对话", "购物", "问路", "天气"]),
        count=random.randint(10, 100),
        unit=random.randint(1, 8),
        chapter=random.randint(1, 20),
        subject=random.choice(SUBJECTS)
    )

    print(f"\n📝 任务 {task_num}: {task_message[:50]}...")
    print(f"   学生: {student['name']} | 确认: {'是' if should_confirm else '否'}")

    # 选择学生
    await page.select_option('select#studentSelect', student['id'])
    await page.wait_for_timeout(300)

    # 输入任务内容
    await page.fill('textarea[placeholder="输入作业内容..."]', task_message)
    await page.wait_for_timeout(300)

    # 50% 概率添加图片
    has_image = random.choice([True, False])
    if has_image:
        print(f"   📷 添加图片附件")

        # 上传图片文件（创建临时图片文件）
        # 注意：Playwright 需要真实文件，这里我们模拟文件选择
        # 实际测试时需要准备真实图片文件

    # 点击AI解析
    print(f"   🤖 点击 AI 智能解析...")
    await page.click('button:has-text("AI 智能解析并创建任务")')

    # 等待解析完成
    await page.wait_for_timeout(2000)

    # 如果需要确认
    if should_confirm:
        print(f"   ✅ 确认创建任务...")

        # 等待跳转到确认页面
        await page.wait_for_url("**/confirm**", timeout=5000)

        # 等待任务加载
        await page.wait_for_timeout(1000)

        # 随机调整科目标签（30%概率）
        if random.random() < 0.3:
            print(f"   🏷️  调整科目标签...")

            # 尝试点击第一个科目标签的下拉框
            subject_select = page.locator('select').first
            try:
                await subject_select.select_option(random.choice(SUBJECTS))
                await page.wait_for_timeout(300)
            except:
                pass

        # 随机添加截止日期（40%概率）
        if random.random() < 0.4:
            print(f"   📅 设置截止日期...")

            date_input = page.locator('input[type="date"]').first
            try:
                # 设置明天到7天后的随机日期
                from datetime import datetime, timedelta
                future_date = datetime.now() + timedelta(days=random.randint(1, 7))
                date_str = future_date.strftime('%Y-%m-%d')
                await date_input.fill(date_str)
                await page.wait_for_timeout(300)
            except:
                pass

        # 点击确认按钮
        await page.click('button:has-text("确认创建任务")')

        # 等待成功提示
        await page.wait_for_timeout(2000)

        # 关闭可能的alert弹窗
        try:
            page.on("dialog", lambda dialog: dialog.accept())
            await page.wait_for_timeout(500)
        except:
            pass

        print(f"   ✅ 任务创建成功")

        # 返回首页
        await page.goto("http://localhost:5001/")
        await page.wait_for_load_state("networkidle")

    else:
        print(f"   ⏸️  不确认任务，保留在pending状态")
        # 返回首页
        await page.goto("http://localhost:5001/")
        await page.wait_for_load_state("networkidle")


async def main():
    """主函数"""
    print("="*60)
    print("🚀 批量测试数据生成脚本")
    print("="*60)
    print("目标：")
    print("  - 注册 1 个用户")
    print("  - 添加 10 名学生")
    print("  - 创建 20 条任务（10条确认，10条不确认）")
    print("="*60)

    async with async_playwright() as p:
        # 启动浏览器（使用 chromium）
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口，方便观察
            slow_mo=500      # 每个操作延迟500ms，模拟真实用户
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )

        page = await context.new_page()

        try:
            # 1. 注册并登录
            await register_and_login(page, 1)

            # 2. 添加学生
            students = await add_students(page, 10)

            # 3. 创建任务（10条确认 + 10条不确认）
            print(f"\n{'='*60}")
            print("📝 开始批量创建任务...")
            print(f"{'='*60}")

            # 前10条任务：解析并确认
            for i in range(10):
                await create_task_with_parsing(page, students, i+1, should_confirm=True)

            # 后10条任务：只解析不确认
            for i in range(10, 20):
                await create_task_with_parsing(page, students, i+1, should_confirm=False)

            print(f"\n{'='*60}")
            print("✅ 测试数据生成完成！")
            print(f"{'='*60}")
            print(f"统计：")
            print(f"  - 用户数: 1")
            print(f"  - 学生数: {len(students)}")
            print(f"  - 已确认任务: 10")
            print(f"  - 待确认任务: 10")
            print(f"{'='*60}")

            # 保持浏览器打开，方便查看结果
            print("\n浏览器将保持打开，按 Ctrl+C 退出...")
            await page.wait_for_timeout(10000)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
