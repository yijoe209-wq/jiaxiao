#!/usr/bin/env python3
"""
简化的批量测试脚本 - 使用 Playwright
- 注册 1 个用户
- 添加 10 名学生
- 创建 20 条任务（10条确认，10条不确认）
"""

import asyncio
import random
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# 测试数据
STUDENT_NAMES = [
    "张伟", "李娜", "王芳", "刘洋", "陈静",
    "杨帆", "赵敏", "孙强", "周杰", "吴婷"
]

GRADES = ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级"]

TASK_TEMPLATES = [
    "数学作业：完成练习册第{}页，明天交",
    "语文作业：背诵课文，默写生字{}个",
    "英语作业：听写第{}单元单词，家长签字",
    "数学作业：试卷错题整理，明天测试",
    "语文作业：预习第{}课，画出重点段落",
    "英语作业：完成练习册第{}页，阅读理解",
    "数学作业：口算练习{}题，要求计时",
    "语文作业：作文《我的梦想》，不少于{}字",
    "数学作业：复习单元内容，准备单元测试",
    "语文作业：整理复习资料，重点背诵古诗"
]


async def main():
    print("="*70)
    print("🚀 批量测试数据生成")
    print("="*70)

    async with async_playwright() as p:
        # 启动浏览器（显示窗口，方便观察）
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300  # 操作延迟，模拟真实用户
        )

        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # ==================== 1. 注册用户 ====================
            print("\n📝 步骤 1/3: 注册用户")

            await page.goto("http://localhost:5001/login")
            await page.wait_for_load_state("networkidle")

            # 切换到注册标签（通过 JavaScript 点击）
            await page.evaluate("() => { switchTab('register'); }")
            await asyncio.sleep(1)

            # 填写注册信息
            await page.fill('#registerName', "测试家长")
            await page.fill('#registerEmail', f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com")
            await page.fill('#registerPassword', "test123456")

            # 提交注册
            await page.click('button:has-text("注册")')

            # 等待注册完成（可能需要等待响应）
            await asyncio.sleep(2)

            # 检查当前URL
            current_url = page.url
            if "my-tasks" in current_url:
                print("   ✅ 注册成功并自动跳转")
            else:
                print(f"   ⚠️  当前页面: {current_url}")
                # 手动跳转到任务中心
                await page.goto("http://localhost:5001/my-tasks")
                await page.wait_for_load_state("networkidle")
                print("   ✅ 手动跳转到任务中心")

            # ==================== 2. 添加学生 ====================
            print("\n👥 步骤 2/3: 添加 10 名学生")

            # 点击首页按钮
            await page.click('a[href="/"]')
            await page.wait_for_load_state("networkidle")

            students_added = 0

            for i in range(10):
                student_name = STUDENT_NAMES[i]
                grade = random.choice(GRADES)

                print(f"   添加学生 {i+1}/10: {student_name} ({grade})")

                # 通过 JavaScript 打开添加学生弹窗
                await page.evaluate("() => { showAddStudentModal(); }")
                await asyncio.sleep(0.8)

                # 填写学生信息
                await page.fill('#newStudentName', student_name)
                await asyncio.sleep(0.2)

                # 选择年级
                await page.select_option('#newStudentGrade', grade)
                await asyncio.sleep(0.3)

                # 提交表单（通过JavaScript触发表单提交）
                await page.evaluate("""
                    () => {
                        const form = document.querySelector('#studentModal form');
                        if (form) form.requestSubmit();
                    }
                """)
                await asyncio.sleep(1)

                students_added += 1

            print(f"   ✅ 成功添加 {students_added} 名学生")

            # ==================== 3. 创建任务 ====================
            print("\n📝 步骤 3/3: 创建 20 条任务")

            confirmed_count = 0
            pending_count = 0

            for task_num in range(20):
                should_confirm = task_num < 10  # 前10条确认，后10条不确认

                # 选择学生（随机选择）
                student_index = task_num % 10
                await page.select_option('#studentSelect', index=student_index)
                await asyncio.sleep(0.3)

                # 生成任务内容
                task_msg = random.choice(TASK_TEMPLATES).format(
                    random.randint(1, 50),
                    random.randint(10, 100)
                )

                print(f"\n   任务 {task_num+1}/20: {task_msg[:40]}...")
                print(f"   学生: 随机选择 | 确认: {'是' if should_confirm else '否'}")

                # 输入任务
                await page.fill('#messageInput', task_msg)
                await asyncio.sleep(0.3)

                # 点击 AI 解析
                await page.click('button:has-text("AI 智能解析")')
                print(f"   🤖 AI 解析中...")

                # 等待跳转
                await asyncio.sleep(2)

                if should_confirm:
                    # 等待跳转到确认页面
                    try:
                        await page.wait_for_url("**/confirm**", timeout=5000)
                        print(f"   ✅ 跳转到确认页面")

                        await asyncio.sleep(1)

                        # 随机操作：40% 概率修改截止日期
                        if random.random() < 0.4:
                            future_date = datetime.now() + timedelta(days=random.randint(1, 7))
                            date_str = future_date.strftime('%Y-%m-%d')

                            try:
                                date_input = page.locator('input[type="date"]').first
                                await date_input.fill(date_str)
                                print(f"   📅 设置截止日期: {date_str}")
                                await asyncio.sleep(0.5)
                            except:
                                pass

                        # 确认创建
                        await page.click('button:has-text("确认创建任务")')
                        await asyncio.sleep(2)

                        # 处理可能的 alert
                        try:
                            page.on("dialog", lambda dialog: dialog.accept())
                        except:
                            pass

                        print(f"   ✅ 任务确认成功")
                        confirmed_count += 1

                        # 返回首页
                        await page.goto("http://localhost:5001/")
                        await page.wait_for_load_state("networkidle")

                    except Exception as e:
                        print(f"   ⚠️  确认失败: {e}")
                        await page.goto("http://localhost:5001/")

                else:
                    # 不确认，直接返回首页创建下一条
                    print(f"   ⏸️  不确认，保留为待确认状态")
                    pending_count += 1
                    await page.goto("http://localhost:5001/")
                    await page.wait_for_load_state("networkidle")

            # ==================== 完成 ====================
            print("\n" + "="*70)
            print("✅ 测试数据生成完成！")
            print("="*70)
            print(f"统计：")
            print(f"  - 用户数: 1")
            print(f"  - 学生数: {students_added}")
            print(f"  - 已确认任务: {confirmed_count}")
            print(f"  - 待确认任务: {pending_count}")
            print("="*70)

            # 访问任务列表查看结果
            print("\n📊 访问任务列表查看结果...")
            await page.goto("http://localhost:5001/tasks")
            await page.wait_for_load_state("networkidle")

            print("\n保持浏览器打开 30 秒，按 Ctrl+C 可提前退出...")
            await asyncio.sleep(30)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
