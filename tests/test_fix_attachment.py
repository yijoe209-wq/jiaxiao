#!/usr/bin/env python3
"""
快速测试附件预览修复
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    print("="*70)
    print("🧪 测试附件预览修复")
    print("="*70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 访问任务中心
            print("\n📋 访问任务中心...")
            await page.goto("http://localhost:5001/my-tasks")
            await page.wait_for_load_state("networkidle")

            # 等待任务加载
            await asyncio.sleep(3)

            # 检查任务
            tasks = await page.query_selector_all('.task-card')
            print(f"找到 {len(tasks)} 个任务")

            if len(tasks) > 0:
                # 查找有附件的任务
                for i, task in enumerate(tasks):
                    try:
                        # 检查是否有附件
                        has_attachment = await task.evaluate("""el => {
                            const html = el.innerHTML;
                            return html.includes('fa-paperclip') && html.includes('个附件');
                        }""")

                        if has_attachment:
                            print(f"\n✅ 任务 {i+1} 有附件")

                            # 查找缩略图
                            thumbnails = await task.query_selector_all('img[alt^="附件"]')
                            print(f"  - 找到 {len(thumbnails)} 个缩略图")

                            if len(thumbnails) > 0:
                                # 检查第一个缩略图的 src
                                first_src = await thumbnails[0].get_attribute('src')
                                if first_src:
                                    if first_src.startswith('data:image'):
                                        print(f"  - 缩略图是 data URL ✅")
                                        print(f"  - 数据长度: {len(first_src)} 字符")
                                    else:
                                        print(f"  - 缩略图 URL: {first_src[:80]}...")

                                    # 点击测试预览
                                    print(f"\n  🖼️  点击缩略图测试预览...")
                                    await thumbnails[0].click()
                                    await asyncio.sleep(1)

                                    # 检查模态框
                                    modal = page.locator('#imageModal')
                                    if await modal.is_visible():
                                        print(f"  ✅ 模态框已打开！")

                                        # 检查大图
                                        modal_image = page.locator('#modalImage')
                                        img_src = await modal_image.get_attribute('src')
                                        if img_src:
                                            print(f"  - 大图已加载 ✅")
                                            print(f"  - 数据长度: {len(img_src)} 字符")

                                            # 检查下载链接
                                            download_link = page.locator('#downloadLink')
                                            download_href = await download_link.get_attribute('href')
                                            if download_href:
                                                print(f"  - 下载链接已设置 ✅")
                                            else:
                                                print(f"  - ⚠️  下载链接未设置")

                                            # 检查计数器
                                            counter = page.locator('#imageCounter')
                                            if await counter.is_visible():
                                                counter_text = await counter.text_content()
                                                print(f"  - 计数器: {counter_text}")

                                            print(f"\n  🎉 附件预览功能正常！")

                                            # 关闭模态框
                                            await page.keyboard.press('Escape')
                                            await asyncio.sleep(0.5)
                                        else:
                                            print(f"  - ❌ 大图未加载")
                                    else:
                                        print(f"  - ❌ 模态框未打开")

                                    break  # 只测试第一个有附件的任务
                                else:
                                    print(f"  - ⚠️  缩略图没有 src")
                            else:
                                print(f"  - ⚠️  没有找到缩略图元素")
                                # 打印部分 HTML 用于调试
                                html = await task.inner_html()
                                if 'attachment' in html.lower():
                                    print(f"  - 任务 HTML 包含 'attachment' 但没有缩略图")
                                    print(f"  - HTML 片段: {html[:300]}...")
                    except Exception as e:
                        print(f"任务 {i+1}: 检查出错 - {e}")
                        continue

                print("\n" + "="*70)
                print("✅ 测试完成")
                print("="*70)
            else:
                print("⚠️  没有找到任务")

            print("\n保持浏览器打开 5 秒...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
