"""
简化的 E2E 测试脚本
只测试核心功能，不依赖复杂的选择器
"""

import asyncio
import sys
from datetime import datetime
from playwright.async_api import async_playwright


async def test_login_and_register():
    """测试登录和注册功能"""
    print("\n" + "="*60)
    print("🧪 测试: 登录和注册")
    print("="*60)

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # 1. 访问登录页面
        print("\n1️⃣ 访问登录页面")
        await page.goto("https://edu-track.zeabur.app/login")
        await asyncio.sleep(2)

        title = await page.title()
        print(f"   页面标题: {title}")

        # 截图
        await page.screenshot(path="test_01_login_page.png")
        print("   📸 截图已保存: test_01_login_page.png")

        # 2. 尝试注册新用户
        print("\n2️⃣ 尝试注册新用户")

        # 点击注册标签
        try:
            register_tab = page.locator(".tab").filter(has_text="注册")
            await register_tab.first.click()
            await asyncio.sleep(1)
            print("   ✅ 已切换到注册标签")
        except Exception as e:
            print(f"   ⚠️ 切换注册标签失败: {e}")

        # 生成测试账号
        test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        test_password = "test123456"
        test_name = "测试家长"

        print(f"   测试邮箱: {test_email}")

        # 填写表单
        try:
            await page.fill("#registerEmail", test_email)
            await page.fill("#registerPassword", test_password)

            # 查找并填写姓名
            name_input = page.locator("input").filter(has_text="姓名").or_(
                page.locator("input[placeholder*='姓名']")
            ).or_(
                page.locator("input[placeholder*='家长']")
            )

            if await name_input.count() > 0:
                await name_input.first.fill(test_name)
                print("   ✅ 表单填写成功")
            else:
                print("   ⚠️ 未找到姓名输入框")

            await asyncio.sleep(1)

            # 截图
            await page.screenshot(path="test_02_register_filled.png")
            print("   📸 截图已保存: test_02_register_filled.png")

            # 提交注册
            print("\n3️⃣ 提交注册")

            # 点击注册按钮
            submit_btn = page.locator("#registerForm button[type='submit']")
            await submit_btn.click()

            # 等待响应
            await asyncio.sleep(5)

            # 检查结果
            current_url = page.url
            print(f"   当前 URL: {current_url}")

            # 截图
            await page.screenshot(path="test_03_after_register.png")
            print("   📸 截图已保存: test_03_after_register.png")

            if "/login" not in current_url:
                print("   ✅ 注册成功，已跳转")
            else:
                print("   ⚠️ 仍在登录页面")

        except Exception as e:
            print(f"   ❌ 注册失败: {e}")
            await page.screenshot(path="test_error_register.png")

        await asyncio.sleep(2)
        await browser.close()


async def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*60)
    print("🧪 测试: 健康检查")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("\n访问 /health 端点")
            response = await page.goto("https://edu-track.zeabur.app/health")

            if response.status == 200:
                text = await response.text()
                print(f"   ✅ 健康检查通过")
                print(f"   响应: {text[:200]}...")
            else:
                print(f"   ❌ 状态码: {response.status}")

        except Exception as e:
            print(f"   ❌ 错误: {e}")

        await browser.close()


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 开始测试")
    print("="*60)
    print(f"测试环境: https://edu-track.zeabur.app")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 测试 1: 健康检查
        await test_health_check()

        # 测试 2: 登录和注册
        await test_login_and_register()

        print("\n" + "="*60)
        print("✅ 测试完成")
        print("="*60)
        print("\n📸 查看截图文件:")
        print("   - test_01_login_page.png")
        print("   - test_02_register_filled.png")
        print("   - test_03_after_register.png")
        print("")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
