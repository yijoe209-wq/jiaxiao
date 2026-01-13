const { test, expect } = require('@playwright/test');

test.describe('家小应用流程测试', () => {
  test('完整流程测试：图片上传和任务创建', async ({ page }) => {
    // 收集 console 错误和警告
    const errors = [];
    const warnings = [];
    const logs = [];

    page.on('console', msg => {
      const msgObj = {
        text: msg.text(),
        type: msg.type(),
        location: msg.location()
      };

      if (msg.type() === 'error') {
        errors.push(msgObj);
        console.log('❌ Console Error:', msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msgObj);
        console.log('⚠️  Console Warning:', msg.text());
      } else {
        logs.push(msgObj);
        console.log('📝 Console Log:', msg.text());
      }
    });

    // 监听页面错误
    page.on('pageerror', error => {
      console.log('❌ Page Error:', error.message);
      errors.push({
        text: error.message,
        stack: error.stack,
        type: 'pageerror'
      });
    });

    // 监听请求失败
    page.on('requestfailed', request => {
      const failure = request.failure();
      console.log('❌ Request Failed:', request.url(), failure?.errorText);
      errors.push({
        text: `Request failed: ${request.url()} - ${failure?.errorText}`,
        type: 'requestfailed'
      });
    });

    // 1. 打开首页
    console.log('\n========== 📍 步骤 1: 打开首页 ==========');
    await page.goto('https://davis-listprice-maria-letters.trycloudflare.com', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    const initialUrl = page.url();
    console.log('✅ 首页加载完成, URL:', initialUrl);

    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/01-homepage.png', fullPage: true });
    console.log('📸 已保存截图: screenshots/01-homepage.png');

    // 记录页面标题
    const title = await page.title();
    console.log('📄 页面标题:', title);

    // 2. 测试图片上传功能
    console.log('\n========== 📍 步骤 2: 测试图片上传 ==========');

    // 查找文件输入框
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached({ timeout: 10000 });
    console.log('✅ 找到文件输入框');

    // 上传测试图片
    const testImagePath = '/Volumes/data/vibe-coding-projects/jiaxiao/uploads/d8b96800062e43cfa54ba66057e2bea2.png';
    console.log('📤 开始上传图片:', testImagePath);

    await fileInput.setInputFiles(testImagePath);
    console.log('✅ 文件已选择');

    // 等待一段时间，观察页面变化
    console.log('⏳ 等待页面响应...');
    await page.waitForTimeout(3000);

    // 检查页面是否发生了变化
    const afterUploadUrl = page.url();
    console.log('📍 上传后的 URL:', afterUploadUrl);

    await page.screenshot({ path: 'screenshots/02-image-uploaded.png', fullPage: true });
    console.log('📸 已保存截图: screenshots/02-image-uploaded.png');

    // 获取页面文本内容
    const pageText = await page.textContent('body');
    console.log('📝 页面包含的关键文本:');

    // 检查关键文本
    const keywords = ['图片解析成功', '已选择', '张', '智能解析', '确认', '任务'];
    for (const keyword of keywords) {
      if (pageText.includes(keyword)) {
        console.log(`  ✅ 找到: "${keyword}"`);
      }
    }

    // 验证图片预览是否显示
    const images = await page.locator('img').all();
    console.log(`\n🖼️  页面共有 ${images.length} 个图片元素`);

    for (let i = 0; i < Math.min(images.length, 5); i++) {
      try {
        const src = await images[i].getAttribute('src');
        const alt = await images[i].getAttribute('alt');
        const visible = await images[i].isVisible();
        console.log(`  图片 ${i + 1}: src="${src?.substring(0, 50)}...", alt="${alt}", visible=${visible}`);
      } catch (e) {
        console.log(`  图片 ${i + 1}: 无法读取信息`);
      }
    }

    // 3. 判断当前页面状态
    console.log('\n========== 📍 步骤 3: 判断页面状态 ==========');

    // 如果 URL 改变或页面显示"图片解析成功"，可能已经跳转
    const urlChanged = initialUrl !== afterUploadUrl;
    const hasSuccessMessage = pageText.includes('图片解析成功') || pageText.includes('解析成功');

    if (urlChanged) {
      console.log('✅ URL 已改变，可能发生了页面跳转');
    }

    if (hasSuccessMessage) {
      console.log('✅ 发现"解析成功"相关文本');
    }

    // 如果页面还在原始状态，尝试继续测试任务创建
    if (!urlChanged && !hasSuccessMessage) {
      console.log('\n========== 📍 步骤 4: 测试任务创建 ==========');

      try {
        // 检查页面是否仍然可用
        await page.waitForTimeout(1000);

        // 查找文本输入框
        const textInputSelectors = [
          'textarea',
          'input[type="text"]',
          'input[placeholder*="消息"]',
          'input[placeholder*="输入"]',
          '[contenteditable="true"]'
        ];

        let textInput = null;
        for (const selector of textInputSelectors) {
          try {
            const element = page.locator(selector).first();
            if (await element.count() > 0) {
              textInput = element;
              console.log(`✅ 找到文本输入框: ${selector}`);
              break;
            }
          } catch (e) {
            // 继续尝试下一个选择器
          }
        }

        if (textInput) {
          // 输入测试消息
          const testMessage = '今天的数学作业是完成练习册第10页';
          await textInput.fill(testMessage);
          console.log(`✅ 已输入测试消息: "${testMessage}"`);

          await page.waitForTimeout(1000);
          await page.screenshot({ path: 'screenshots/03-message-entered.png', fullPage: true });
          console.log('📸 已保存截图: screenshots/03-message-entered.png');

          // 点击"智能解析"按钮
          console.log('\n========== 📍 步骤 5: 点击智能解析按钮 ==========');

          const buttonSelectors = [
            'button:has-text("智能解析")',
            'button:has-text("解析")',
            'button[type="submit"]',
            '[role="button"]:has-text("智能解析")',
            '[role="button"]:has-text("解析")'
          ];

          let analyzeButton = null;
          for (const selector of buttonSelectors) {
            try {
              const element = page.locator(selector).first();
              if (await element.count() > 0) {
                analyzeButton = element;
                console.log(`✅ 找到按钮: ${selector}`);
                break;
              }
            } catch (e) {
              // 继续尝试下一个选择器
            }
          }

          if (analyzeButton) {
            await analyzeButton.click();
            console.log('✅ 已点击智能解析按钮');

            // 等待跳转或响应
            console.log('⏳ 等待页面响应...');
            await page.waitForTimeout(3000);

            await page.screenshot({ path: 'screenshots/04-after-click.png', fullPage: true });
            console.log('📸 已保存截图: screenshots/04-after-click.png');

            // 验证是否成功跳转到确认页面
            const finalUrl = page.url();
            console.log(`📍 最终 URL: ${finalUrl}`);

            // 检查是否有确认页面的特征
            const finalPageText = await page.textContent('body');
            const confirmationKeywords = ['确认', 'confirm', '任务', 'task', '创建'];
            const foundKeywords = confirmationKeywords.filter(kw => finalPageText.includes(kw));

            if (finalUrl.includes('confirm') || foundKeywords.length > 0) {
              console.log('✅ 可能已跳转到确认页面');
              console.log(`  找到的关键词: ${foundKeywords.join(', ')}`);
            } else {
              console.log('⚠️  未检测到确认页面特征');
            }
          } else {
            console.log('⚠️  未找到智能解析按钮');
          }
        } else {
          console.log('⚠️  未找到文本输入框');
        }
      } catch (error) {
        console.log('❌ 任务创建测试出错:', error.message);
      }
    }

    // 最终截图
    console.log('\n========== 📍 最终状态 ==========');
    await page.screenshot({ path: 'screenshots/05-final.png', fullPage: true });
    console.log('📸 已保存最终截图: screenshots/05-final.png');

    // 6. 报告 console 错误
    console.log('\n========== 📍 Console 错误汇总 ==========');

    if (errors.length > 0) {
      console.log(`\n❌ 发现 ${errors.length} 个错误:\n`);
      errors.forEach((error, index) => {
        console.log(`错误 ${index + 1}:`);
        console.log(`  类型: ${error.type}`);
        console.log(`  消息: ${error.text}`);
        if (error.location) {
          console.log(`  位置: ${error.location.url}:${error.location.lineNumber}`);
        }
        if (error.stack) {
          console.log(`  堆栈: ${error.stack?.substring(0, 200)}...`);
        }
        console.log('');
      });
    } else {
      console.log('✅ 未发现 console 错误');
    }

    if (warnings.length > 0) {
      console.log(`\n⚠️  发现 ${warnings.length} 个警告:\n`);
      warnings.forEach((warning, index) => {
        console.log(`警告 ${index + 1}: ${warning.text}`);
      });
    }

    // 保存错误报告
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalErrors: errors.length,
        totalWarnings: warnings.length,
        totalLogs: logs.length
      },
      errors: errors,
      warnings: warnings
    };

    const fs = require('fs');
    fs.writeFileSync('screenshots/test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 测试报告已保存到 screenshots/test-report.json');

    // 如果有严重错误，抛出异常
    if (errors.length > 0) {
      throw new Error(`测试过程中发现 ${errors.length} 个错误`);
    }
  });
});
