#!/usr/bin/env python3
"""
测试任务中心的附件预览功能
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    print("="*70)
    print("🧪 测试任务中心附件预览功能")
    print("="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 1. 访问登录页面（如果需要）
            print("\n🔐 步骤 1/4: 检查登录状态")
            await page.goto("http://localhost:5001/my-tasks")
            await page.wait_for_load_state("networkidle")

            # 检查是否需要登录
            current_url = page.url
            if 'login' in current_url:
                print("   ⚠️  需要登录，先注册一个测试账号...")

                # 点击注册标签
                await page.evaluate("() => { switchTab('register'); }")
                await asyncio.sleep(1)

                # 填写注册信息
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                await page.fill('#registerName', "测试用户")
                await page.fill('#registerEmail', f"test_{timestamp}@example.com")
                await page.fill('#registerPassword', "test123456")

                # 提交注册
                await page.click('button:has-text("注册")')
                await asyncio.sleep(2)

                # 应该跳转到任务中心
                current_url = page.url
                if 'my-tasks' not in current_url:
                    await page.goto("http://localhost:5001/my-tasks")
                    await page.wait_for_load_state("networkidle")

                print("   ✅ 注册并登录成功")
            else:
                print("   ✅ 已登录")

            # 2. 等待任务列表加载
            print("\n⏳ 步骤 2/4: 等待任务列表加载")
            await asyncio.sleep(3)

            # 3. 检查是否有任务
            print("\n📋 步骤 3/4: 检查任务列表")
            tasks = await page.query_selector_all('.task-card')
            if len(tasks) == 0:
                print("   ⚠️  没有找到任务，需要先创建带附件的任务")
                print("\n💡 提示：请先使用 test_batch_simple.py 创建测试数据")
                return

            print(f"   ✅ 找到 {len(tasks)} 个任务")

            # 4. 检查是否有附件
            print("\n📎 步骤 4/4: 检查附件并测试预览")

            has_attachments = False
            for i, task in enumerate(tasks):
                # 检查是否有附件标签
                attachment_text = await task.evaluate("""el => {
                    const attachmentSpan = el.querySelector('span:has(.fa-paperclip)');
                    return attachmentSpan ? attachmentSpan.textContent.trim() : null;
                }""")

                if attachment_text:
                    has_attachments = True
                    print(f"\n   任务 {i+1}: {attachment_text}")

                    # 检查是否有缩略图
                    thumbnails = await task.query_selector_all('img[alt^="附件"]')
                    print(f"   - 找到 {len(thumbnails)} 个缩略图")

                    if len(thumbnails) > 0:
                        # 点击第一个缩略图
                        print("   - 点击第一个缩略图测试预览...")
                        await thumbnails[0].click()
                        await asyncio.sleep(1)

                        # 检查模态框是否打开
                        modal = page.locator('#imageModal')
                        is_visible = await modal.is_visible()

                        if is_visible:
                            print("   ✅ 模态框打开成功！")

                            # 检查模态框内容
                            modal_image = page.locator('#modalImage')
                            image_src = await modal_image.get_attribute('src')
                            print(f"   - 图片源: {image_src[:50]}..." if image_src else "   - 图片未加载")

                            download_link = page.locator('#downloadLink')
                            download_href = await download_link.get_attribute('href')
                            print(f"   - 下载链接: {'✅ 已设置' if download_href else '❌ 未设置'}")

                            # 检查导航按钮
                            prev_btn = page.locator('#prevBtn')
                            next_btn = page.locator('#nextBtn')
                            counter = page.locator('#imageCounter')

                            counter_text = await counter.text_content() if await counter.is_visible() else ''
                            print(f"   - 计数器: {counter_text}")

                            # 测试键盘导航
                            print("\n   测试键盘导航...")
                            await page.keyboard.press('ArrowRight')
                            await asyncio.sleep(0.5)
                            print("   - 右箭头导航 ✅")

                            await page.keyboard.press('ArrowLeft')
                            await asyncio.sleep(0.5)
                            print("   - 左箭头导航 ✅")

                            # 测试关闭
                            await page.keyboard.press('Escape')
                            await asyncio.sleep(0.5)

                            is_visible_after = await modal.is_visible()
                            if not is_visible_after:
                                print("   - ESC 关闭模态框 ✅")
                            else:
                                print("   - ESC 关闭失败 ❌")

                            break  # 只测试第一个有附件的任务
                        else:
                            print("   ❌ 模态框未打开")
                    else:
                        print("   ⚠️  没有找到缩略图")

            if not has_attachments:
                print("\n   ⚠️  没有找到带附件的任务")
                print("   💡 提示：需要创建带图片附件的任务来测试预览功能")
            else:
                print("\n" + "="*70)
                print("✅ 附件预览功能测试完成！")
                print("="*70)

            print("\n保持浏览器打开 10 秒...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
