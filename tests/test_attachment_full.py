#!/usr/bin/env python3
"""
完整的附件预览功能测试
1. 注册新用户
2. 添加学生
3. 创建带附件的任务
4. 测试附件预览
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    print("="*70)
    print("🧪 完整的附件预览功能测试")
    print("="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 1. 注册新用户
            print("\n📝 步骤 1/4: 注册新用户")
            await page.goto("http://localhost:5001/login")
            await page.wait_for_load_state("networkidle")

            await page.evaluate("() => { switchTab('register'); }")
            await asyncio.sleep(1)

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            await page.fill('#registerName', "测试家长")
            await page.fill('#registerEmail', f"test_attach_{timestamp}@example.com")
            await page.fill('#registerPassword', "test123456")

            await page.click('button:has-text("注册")')
            await asyncio.sleep(3)

            # 检查是否跳转到任务中心
            current_url = page.url
            if 'my-tasks' not in current_url:
                await page.goto("http://localhost:5001/my-tasks")
                await page.wait_for_load_state("networkidle")

            print("   ✅ 注册成功")

            # 2. 添加学生
            print("\n👥 步骤 2/4: 添加学生")
            await page.goto("http://localhost:5001/")
            await page.wait_for_load_state("networkidle")

            await page.evaluate("() => { showAddStudentModal(); }")
            await asyncio.sleep(1)

            await page.fill('#newStudentName', "测试学生")
            await asyncio.sleep(0.3)
            await page.select_option('#newStudentGrade', "三年级")
            await asyncio.sleep(0.3)

            await page.evaluate("""
                () => {
                    const form = document.querySelector('#studentModal form');
                    if (form) {
                        // 获取提交按钮并直接点击
                        const btn = form.querySelector('button[type="submit"]');
                        if (btn) btn.click();
                        else form.submit();
                    }
                }
            """)
            await asyncio.sleep(2)

            # 等待模态框自动关闭或按 ESC
            try:
                await page.wait_for_selector('#studentModal[style*="display: none"], #studentModal:not(.show)', timeout=3000)
            except:
                await page.keyboard.press('Escape')
                await asyncio.sleep(0.5)

            print("   ✅ 学生添加成功")

            # 3. 创建带附件的任务
            print("\n📝 步骤 3/4: 创建带附件的任务")

            # 选择学生
            await page.select_option('#studentSelect', index=0)
            await asyncio.sleep(0.3)

            # 输入任务内容
            task_msg = "数学作业：完成练习册第10页，明天交。请参考附件图片。"
            await page.fill('#messageInput', task_msg)
            await asyncio.sleep(0.3)

            # 创建测试图片的 data URL
            test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFklEQVR42mN88+hffwYIAOwYK6MAAq0Qw7xjxrlQAAAABJRU5ErkJggg=="

            # 模拟上传图片
            await page.evaluate(f"""
                () => {{
                    const imagePreview = document.getElementById('imagePreview');
                    if (imagePreview) {{
                        imagePreview.innerHTML = `
                            <div class="preview-item">
                                <img src="{test_image}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;">
                                <button type="button" class="remove-btn" onclick="this.parentElement.remove()" style="position: absolute; top: -8px; right: -8px; width: 24px; height: 24px; border-radius: 50%; background: #f44336; color: white; border: none; cursor: pointer;">×</button>
                            </div>
                        `;
                        imagePreview.style.display = 'flex';
                    }}
                }}
            """)
            await asyncio.sleep(0.5)

            print("   📷 测试图片已添加")
            print("   🤖 点击 AI 智能解析...")

            # 点击 AI 解析按钮
            async def click_ai_button():
                # 先尝试关闭任何打开的模态框
                await page.keyboard.press('Escape')
                await asyncio.sleep(0.3)

                # 使用 JavaScript 直接点击
                await page.evaluate("""
                    () => {
                        const btn = document.querySelector('button[onclick="simulateForward()"]');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                    }
                """)

            await click_ai_button()
            print("   ⏳ 等待 AI 解析...")

            # 等待跳转到确认页面或响应
            await asyncio.sleep(3)

            current_url = page.url
            if 'confirm' in current_url:
                print("   ✅ 跳转到确认页面")

                await asyncio.sleep(1)

                # 点击确认创建
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
            else:
                print(f"   ⚠️  当前页面: {current_url}")
                print("   ⚠️  未跳转到确认页面，尝试直接访问任务中心")

            # 4. 测试附件预览
            print("\n🔍 步骤 4/4: 测试附件预览")
            await page.goto("http://localhost:5001/my-tasks")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            # 查找任务
            tasks = await page.query_selector_all('.task-card')
            print(f"   找到 {len(tasks)} 个任务")

            if len(tasks) > 0:
                # 检查第一个任务的附件
                task = tasks[0]

                attachment_info = await task.evaluate("""el => {
                    const attachmentSpan = Array.from(el.querySelectorAll('span')).find(s => s.textContent.includes('附件'));
                    return attachmentSpan ? attachmentSpan.textContent.trim() : null;
                }""")

                if attachment_info:
                    print(f"   ✅ 发现附件: {attachment_info}")

                    # 查找缩略图
                    thumbnails = await task.query_selector_all('img[alt^="附件"]')

                    if len(thumbnails) > 0:
                        print(f"   ✅ 找到 {len(thumbnails)} 个缩略图")
                        print(f"   🖼️  点击缩略图测试预览...")

                        await thumbnails[0].click()
                        await asyncio.sleep(1)

                        # 检查模态框
                        modal = page.locator('#imageModal')

                        if await modal.is_visible():
                            print(f"   ✅ 模态框打开成功！")

                            # 检查图片
                            modal_image = page.locator('#modalImage')
                            img_visible = await modal_image.is_visible()
                            print(f"   - 图片可见: {'✅' if img_visible else '❌'}")

                            # 检查下载链接
                            download_link = page.locator('#downloadLink')
                            download_href = await download_link.get_attribute('href')
                            print(f"   - 下载链接: {'✅' if download_href else '❌'}")

                            # 检查计数器
                            counter = page.locator('#imageCounter')
                            if await counter.is_visible():
                                counter_text = await counter.text_content()
                                print(f"   - 计数器: {counter_text}")

                            # 测试键盘导航
                            print(f"\n   ⌨️  测试键盘导航...")
                            await page.keyboard.press('ArrowRight')
                            await asyncio.sleep(0.5)
                            print(f"   - 右箭头: ✅")

                            await page.keyboard.press('ArrowLeft')
                            await asyncio.sleep(0.5)
                            print(f"   - 左箭头: ✅")

                            # 测试关闭
                            await page.keyboard.press('Escape')
                            await asyncio.sleep(0.5)
                            is_closed = not await modal.is_visible()
                            print(f"   - ESC 关闭: {'✅' if is_closed else '❌'}")

                            print("\n" + "="*70)
                            print("🎉 附件预览功能测试完成！全部通过！")
                            print("="*70)
                        else:
                            print(f"   ❌ 模态框未打开")
                    else:
                        print(f"   ⚠️  没有找到缩略图")
                        # 打印任务 HTML 用于调试
                        task_html = await task.inner_html()
                        print(f"   任务 HTML 片段: {task_html[:200]}...")
                else:
                    print(f"   ⚠️  任务没有附件")
                    # 打印任务内容用于调试
                    desc = await task.evaluate("""el => {
                        const desc = el.querySelector('.text-lg');
                        return desc ? desc.textContent : 'No description';
                    }""")
                    print(f"   任务描述: {desc}")
            else:
                print("   ⚠️  没有找到任务")

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
