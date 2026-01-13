const { test, expect } = require('@playwright/test');

test.describe('家小应用流程测试', () => {
  test('完整流程测试：图片上传和任务创建', async ({ page }) => {
    // 收集 console 错误
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          text: msg.text(),
          location: msg.location()
        });
        console.log('❌ Console Error:', msg.text());
      }
    });

    // 1. 打开首页
    console.log('📍 步骤 1: 打开首页');
    await page.goto('https://davis-listprice-maria-letters.trycloudflare.com');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/01-homepage.png' });
    console.log('✅ 首页加载完成');

    // 等待页面加载
    await page.waitForTimeout(2000);

    // 2. 测试图片上传功能
    console.log('📍 步骤 2: 测试图片上传');

    // 查找文件输入框
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached({ timeout: 5000 });
    console.log('✅ 找到文件输入框');

    // 上传测试图片
    const testImagePath = '/Volumes/data/vibe-coding-projects/jiaxiao/uploads/d8b96800062e43cfa54ba66057e2bea2.png';
    await fileInput.setInputFiles(testImagePath);
    console.log('✅ 文件已选择');

    // 等待预览显示
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/02-image-uploaded.png' });

    // 验证图片预览是否显示
    const imagePreview = page.locator('img[src*="blob:"], img[class*="preview"], img[alt*="preview"], .image-preview img, [class*="image"] img').first();
    const imageVisible = await imagePreview.isVisible().catch(() => false);

    if (imageVisible) {
      console.log('✅ 图片预览已显示');
    } else {
      console.log('⚠️  未找到图片预览元素');
    }

    // 验证"已选择 X 张"计数
    const counterText = await page.locator('text=/已选择.*张/, text=/Selected.*images?/i').first().textContent().catch(() => '');
    if (counterText) {
      console.log(`✅ 计数器显示: ${counterText.trim()}`);
    } else {
      console.log('⚠️  未找到计数器文本');
    }

    // 3. 测试任务创建
    console.log('📍 步骤 3: 测试任务创建');

    // 查找文本输入框
    const textInput = page.locator('textarea, input[type="text"]').first();
    await expect(textInput).toBeAttached({ timeout: 5000 });

    // 输入测试消息
    const testMessage = '今天的数学作业是完成练习册第10页';
    await textInput.fill(testMessage);
    console.log(`✅ 已输入测试消息: "${testMessage}"`);

    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/03-message-entered.png' });

    // 点击"智能解析"按钮
    console.log('📍 步骤 4: 点击智能解析按钮');

    const analyzeButton = page.locator('button:has-text("智能解析"), button:has-text("解析"), button[type="submit"]').first();
    await expect(analyzeButton).toBeAttached({ timeout: 5000 });
    await analyzeButton.click();
    console.log('✅ 已点击智能解析按钮');

    // 等待跳转或响应
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'screenshots/04-after-click.png' });

    // 验证是否成功跳转到确认页面
    const currentUrl = page.url();
    console.log(`📍 当前 URL: ${currentUrl}`);

    // 检查是否有确认页面的特征
    const hasConfirmationPage = await page.locator('text=/确认|confirm|任务|task/i').count() > 0;

    if (currentUrl.includes('confirm') || hasConfirmationPage) {
      console.log('✅ 成功跳转到确认页面');
    } else {
      console.log('⚠️  可能未跳转到确认页面，请检查截图');
    }

    // 最终截图
    await page.screenshot({ path: 'screenshots/05-final.png', fullPage: true });

    // 4. 报告 console 错误
    console.log('\n📍 步骤 5: Console 错误汇总');
    if (errors.length > 0) {
      console.log(`\n❌ 发现 ${errors.length} 个 console 错误:\n`);
      errors.forEach((error, index) => {
        console.log(`错误 ${index + 1}:`);
        console.log(`  消息: ${error.text}`);
        if (error.location) {
          console.log(`  位置: ${error.location.url}:${error.location.lineNumber}`);
        }
        console.log('');
      });
    } else {
      console.log('✅ 未发现 console 错误');
    }

    // 保存错误报告
    if (errors.length > 0) {
      const fs = require('fs');
      const errorReport = {
        timestamp: new Date().toISOString(),
        totalErrors: errors.length,
        errors: errors
      };
      fs.writeFileSync(
        'screenshots/error-report.json',
        JSON.stringify(errorReport, null, 2)
      );
      console.log('📄 错误报告已保存到 screenshots/error-report.json');
    }
  });
});
