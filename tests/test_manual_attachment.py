#!/usr/bin/env python3
"""
手动测试附件预览 - 使用现有任务
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    print("="*70)
    print("🧪 手动测试附件预览功能")
    print("="*70)
    print("\n💡 使用说明：")
    print("1. 脚本会打开浏览器并访问任务中心")
    print("2. 请手动操作创建带附件的任务（如果还没有）")
    print("3. 然后脚本将自动测试附件预览功能")
    print("\n" + "="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 访问任务中心
            await page.goto("http://localhost:5001/my-tasks")
            await page.wait_for_load_state("networkidle")

            print("\n✅ 浏览器已打开，等待 30 秒供您操作...")
            print("   请在浏览器中：")
            print("   - 如果需要登录，请登录")
            print("   - 如果需要创建带附件的任务，请创建")
            print("\n⏱️  倒计时开始...")

            # 等待 30 秒让用户操作
            for i in range(30, 0, -5):
                print(f"   剩余 {i} 秒...")
                await asyncio.sleep(5)

            print("\n🔍 开始检查任务列表...")

            # 检查任务
            await page.wait_for_load_state("networkidle")
            tasks = await page.query_selector_all('.task-card')

            print(f"\n找到 {len(tasks)} 个任务")

            if len(tasks) == 0:
                print("⚠️  没有找到任务")
                return

            # 检查每个任务的附件
            has_attachment = False
            for i, task in enumerate(tasks):
                try:
                    attachment_info = await task.evaluate("""el => {
                        const attachmentSpan = Array.from(el.querySelectorAll('span')).find(s => s.textContent.includes('附件'));
                        return attachmentSpan ? attachmentSpan.textContent.trim() : null;
                    }""")

                    if attachment_info:
                        has_attachment = True
                        print(f"\n任务 {i+1}: {attachment_info}")

                        # 查找缩略图
                        thumbnails = await task.query_selector_all('img[alt^="附件"]')
                        print(f"  - 找到 {len(thumbnails)} 个缩略图")

                        if len(thumbnails) > 0:
                            print(f"\n  🖼️  点击第一个缩略图测试预览...")

                            # 点击缩略图
                            await thumbnails[0].click()
                            await asyncio.sleep(1)

                            # 检查模态框
                            modal = page.locator('#imageModal')
                            is_visible = await modal.is_visible()

                            if is_visible:
                                print(f"  ✅ 模态框已打开！")

                                # 检查图片
                                modal_image = page.locator('#modalImage')
                                img_src = await modal_image.get_attribute('src')
                                print(f"  - 图片已加载: {img_src[:80] if img_src else '未加载'}...")

                                # 检查下载链接
                                download_link = page.locator('#downloadLink')
                                download_href = await download_link.get_attribute('href')
                                print(f"  - 下载链接: {'✅' if download_href else '❌'}")

                                # 检查计数器
                                counter = page.locator('#imageCounter')
                                if await counter.is_visible():
                                    counter_text = await counter.text_content()
                                    print(f"  - 计数器: {counter_text}")

                                # 测试键盘导航
                                print(f"\n  ⌨️  测试键盘导航...")

                                # 测试下一张
                                next_btn = page.locator('#nextBtn')
                                if await next_btn.is_enabled():
                                    await page.keyboard.press('ArrowRight')
                                    await asyncio.sleep(0.5)
                                    print(f"  - 右箭头导航 ✅")

                                    # 返回第一张
                                    await page.keyboard.press('ArrowLeft')
                                    await asyncio.sleep(0.5)
                                    print(f"  - 左箭头导航 ✅")

                                # 测试关闭
                                await page.keyboard.press('Escape')
                                await asyncio.sleep(0.5)

                                is_closed = not await modal.is_visible()
                                if is_closed:
                                    print(f"  - ESC 关闭模态框 ✅")
                                else:
                                    print(f"  - ESC 关闭失败 ❌")

                                print(f"\n  🎉 附件预览功能测试通过！")
                                break
                            else:
                                print(f"  ❌ 模态框未打开")
                    else:
                        # 检查是否有附件但不显示缩略图
                        attachment_check = await task.evaluate("""el => {
                            const html = el.innerHTML;
                            return html.includes('attachment') || html.includes('附件');
                        }""")
                        if attachment_check:
                            print(f"任务 {i+1}: 有附件数据但未显示缩略图")

                except Exception as e:
                    print(f"任务 {i+1}: 检查出错 - {e}")
                    continue

            if not has_attachment:
                print("\n⚠️  没有找到带附件的任务")
                print("💡 提示：需要创建包含图片附件的任务来测试预览功能")
            else:
                print("\n" + "="*70)
                print("✅ 测试完成！")
                print("="*70)

            print("\n保持浏览器打开 10 秒供您查看...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
