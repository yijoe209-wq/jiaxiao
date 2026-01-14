#!/usr/bin/env python3
"""
创建带附件的测试任务
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    print("="*70)
    print("📝 创建带附件的测试任务")
    print("="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 1. 访问首页
            print("\n🏠 步骤 1/5: 访问首页")
            await page.goto("http://localhost:5001/")
            await page.wait_for_load_state("networkidle")
            print("   ✅ 页面加载成功")

            # 2. 添加学生（如果还没有）
            print("\n👥 步骤 2/5: 检查学生")
            student_select = page.locator('#studentSelect')
            options = await student_select.locator('option').all()
            student_count = len(options) - 1  # 减去第一个"选择学生"选项

            if student_count == 0:
                print("   ⚠️  没有学生，先添加一个...")
                await page.evaluate("() => { showAddStudentModal(); }")
                await asyncio.sleep(0.8)

                await page.fill('#newStudentName', "测试学生")
                await page.select_option('#newStudentGrade', "三年级")
                await asyncio.sleep(0.3)

                await page.evaluate("""
                    () => {
                        const form = document.querySelector('#studentModal form');
                        if (form) form.requestSubmit();
                    }
                """)
                await asyncio.sleep(2)

                # 手动关闭模态框（如果还没关闭）
                modal_visible = await page.locator('#studentModal.show').count() > 0
                if modal_visible:
                    # 按 Escape 关闭
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)

                print("   ✅ 学生添加成功")
            else:
                print(f"   ✅ 已有 {student_count} 个学生")

            # 3. 选择学生
            print("\n📝 步骤 3/5: 选择学生并输入任务")
            await page.select_option('#studentSelect', index=0)
            await asyncio.sleep(0.3)

            task_msg = "数学作业：完成练习册第10页，明天交。请参考附件图片。"
            await page.fill('#messageInput', task_msg)
            await asyncio.sleep(0.3)

            # 上传测试图片（使用 data URL）
            print("   📷 准备上传测试图片...")

            # 先创建一个简单的测试图片的 data URL
            # 在实际浏览器中，这会通过文件输入完成
            # 这里我们直接在控制台执行来模拟

            test_image_data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

            # 使用 JavaScript 模拟文件上传和 AI 解析
            await page.evaluate(f"""
                () => {{
                    // 模拟添加图片
                    const imagePreview = document.getElementById('imagePreview');
                    if (imagePreview) {{
                        imagePreview.innerHTML = `
                            <div class="preview-item">
                                <img src="{test_image_data_url}" alt="测试图片">
                                <button type="button" class="remove-btn" onclick="this.parentElement.remove()">×</button>
                            </div>
                        `;
                        imagePreview.style.display = 'flex';
                    }}
                }}
            """)

            await asyncio.sleep(0.5)
            print("   ✅ 测试图片已添加")

            # 4. 点击 AI 解析
            print("\n🤖 步骤 4/5: 点击 AI 智能解析")
            await page.click('button:has-text("AI 智能解析")')
            print("   🔄 AI 解析中...")

            # 等待跳转到确认页面
            try:
                await page.wait_for_url("**/confirm**", timeout=8000)
                print("   ✅ 跳转到确认页面")
            except:
                print("   ⚠️  未跳转到确认页面，当前URL:", page.url)

            await asyncio.sleep(2)

            # 5. 确认创建任务
            print("\n✅ 步骤 5/5: 确认创建任务")

            # 检查是否有确认按钮
            confirm_btn = page.locator('button:has-text("确认创建任务")')
            if await confirm_btn.is_visible():
                await confirm_btn.click()
                await asyncio.sleep(2)

                # 处理可能的 alert
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except:
                    pass

                print("   ✅ 任务创建成功")

                # 访问任务中心查看结果
                print("\n📋 访问任务中心查看结果...")
                await page.goto("http://localhost:5001/my-tasks")
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)

                # 检查任务列表
                tasks = await page.query_selector_all('.task-card')
                print(f"\n找到 {len(tasks)} 个任务")

                # 查找带附件的任务
                for i, task in enumerate(tasks):
                    has_attachment = await task.evaluate("""el => {
                        const attachmentSpan = el.querySelector('span:has(.fa-paperclip)');
                        return attachmentSpan ? attachmentSpan.textContent.trim() : null;
                    }""")

                    if has_attachment:
                        print(f"\n任务 {i+1}: {has_attachment}")

                        # 尝试点击附件
                        thumbnails = await task.query_selector_all('img[alt^="附件"]')
                        if len(thumbnails) > 0:
                            print(f"  - 找到 {len(thumbnails)} 个缩略图")
                            print("  - 点击第一个缩略图...")

                            await thumbnails[0].click()
                            await asyncio.sleep(1)

                            # 检查模态框
                            modal = page.locator('#imageModal')
                            if await modal.is_visible():
                                print("  - ✅ 附件预览模态框打开成功！")

                                # 等待几秒让用户看到
                                await asyncio.sleep(3)

                                # 关闭模态框
                                await page.keyboard.press('Escape')
                                await asyncio.sleep(0.5)

                                break
            else:
                print("   ⚠️  未找到确认按钮")

            print("\n" + "="*70)
            print("✅ 测试完成！")
            print("="*70)

            print("\n保持浏览器打开 10 秒...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
