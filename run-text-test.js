const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 收集 console 错误和警告
  const errors = [];
  const warnings = [];

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
    }
  });

  page.on('pageerror', error => {
    console.log('❌ Page Error:', error.message);
    errors.push({
      text: error.message,
      stack: error.stack,
      type: 'pageerror'
    });
  });

  page.on('requestfailed', request => {
    const failure = request.failure();
    console.log('❌ Request Failed:', request.url(), failure?.errorText);
    errors.push({
      text: `Request failed: ${request.url()} - ${failure?.errorText}`,
      type: 'requestfailed'
    });
  });

  try {
    // 1. 打开首页
    console.log('\n========== 📍 步骤 1: 打开首页 ==========');
    await page.goto('https://davis-listprice-maria-letters.trycloudflare.com', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    const initialUrl = page.url();
    console.log('✅ 首页加载完成, URL:', initialUrl);

    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/text-01-homepage.png', fullPage: true });

    // 2. 测试纯文本输入（不上传图片）
    console.log('\n========== 📍 步骤 2: 测试文本输入 ==========');

    // 查找文本输入框
    const textInputSelectors = [
      'textarea',
      'input[type="text"]',
      'input[placeholder*="消息"]',
      'input[placeholder*="输入"]',
      '[contenteditable="true"]',
      '.message-input',
      '[class*="input"] textarea',
      '[class*="input"] input'
    ];

    let textInput = null;
    for (const selector of textInputSelectors) {
      try {
        const elements = await page.locator(selector).all();
        if (elements.length > 0) {
          const element = page.locator(selector).first();
          const visible = await element.isVisible();
          if (visible) {
            textInput = element;
            console.log(`✅ 找到可见的文本输入框: ${selector}`);
            break;
          }
        }
      } catch (e) {
        // 继续尝试下一个选择器
      }
    }

    if (!textInput) {
      console.log('⚠️  未找到文本输入框，尝试获取所有输入元素');

      // 列出页面上所有输入元素
      const allInputs = await page.locator('input, textarea, [contenteditable="true"]').all();
      console.log(`📝 页面共有 ${allInputs.length} 个输入元素`);

      for (let i = 0; i < allInputs.length; i++) {
        try {
          const tag = await allInputs[i].evaluate(e => e.tagName);
          const type = await allInputs[i].getAttribute('type');
          const placeholder = await allInputs[i].getAttribute('placeholder');
          const visible = await allInputs[i].isVisible();
          console.log(`  输入 ${i + 1}: <${tag}> type="${type}" placeholder="${placeholder}" visible=${visible}`);

          if (visible && !textInput) {
            textInput = allInputs[i];
          }
        } catch (e) {
          // 继续下一个
        }
      }
    }

    if (textInput) {
      // 输入测试消息
      const testMessage = '今天的数学作业是完成练习册第10页';
      console.log(`✅ 输入测试消息: "${testMessage}"`);

      await textInput.click();
      await textInput.fill(testMessage);

      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'screenshots/text-02-message-entered.png', fullPage: true });
      console.log('📸 已保存截图: text-02-message-entered.png');

      // 点击"智能解析"按钮
      console.log('\n========== 📍 步骤 3: 点击智能解析按钮 ==========');

      const buttonSelectors = [
        'button:has-text("智能解析")',
        'button:has-text("解析")',
        'button[type="submit"]',
        '[role="button"]:has-text("智能解析")',
        '[role="button"]:has-text("解析")',
        '.submit-button',
        '[class*="submit"] button',
        '[class*="analyze"] button'
      ];

      let analyzeButton = null;
      for (const selector of buttonSelectors) {
        try {
          const elements = await page.locator(selector).all();
          if (elements.length > 0) {
            const element = page.locator(selector).first();
            const visible = await element.isVisible();
            if (visible) {
              analyzeButton = element;
              console.log(`✅ 找到可见的按钮: ${selector}`);
              break;
            }
          }
        } catch (e) {
          // 继续尝试下一个选择器
        }
      }

      if (!analyzeButton) {
        console.log('⚠️  未找到按钮，列出所有按钮元素');

        const allButtons = await page.locator('button, [role="button"]').all();
        console.log(`📝 页面共有 ${allButtons.length} 个按钮元素`);

        for (let i = 0; i < Math.min(allButtons.length, 10); i++) {
          try {
            const text = await allButtons[i].textContent();
            const visible = await allButtons[i].isVisible();
            console.log(`  按钮 ${i + 1}: "${text?.trim()}" visible=${visible}`);

            if (visible && (text?.includes('解析') || text?.includes('提交') || text?.includes('发送')) && !analyzeButton) {
              analyzeButton = allButtons[i];
            }
          } catch (e) {
            // 继续下一个
          }
        }
      }

      if (analyzeButton) {
        console.log('✅ 点击智能解析按钮');
        await analyzeButton.click();

        // 等待跳转或响应
        console.log('⏳ 等待页面响应...');
        await page.waitForTimeout(5000);

        await page.screenshot({ path: 'screenshots/text-03-after-click.png', fullPage: true });
        console.log('📸 已保存截图: text-03-after-click.png');

        // 验证是否成功跳转
        const finalUrl = page.url();
        console.log(`📍 最终 URL: ${finalUrl}`);

        const urlChanged = initialUrl !== finalUrl;
        if (urlChanged) {
          console.log('✅ URL 已改变，页面发生了跳转');
        }

        // 检查页面内容
        const finalPageText = await page.textContent('body');
        const keywords = ['确认', 'confirm', '任务', 'task', '创建', '成功', '解析成功'];
        const foundKeywords = keywords.filter(kw => finalPageText.includes(kw));

        if (foundKeywords.length > 0) {
          console.log(`✅ 找到关键词: ${foundKeywords.join(', ')}`);
        }

        // 检查是否有错误消息
        const errorKeywords = ['错误', 'error', '失败', 'fail', '异常'];
        const foundErrors = errorKeywords.filter(kw => finalPageText.toLowerCase().includes(kw));

        if (foundErrors.length > 0) {
          console.log(`⚠️  发现错误关键词: ${foundErrors.join(', ')}`);
        }

      } else {
        console.log('⚠️  未找到智能解析按钮');
      }

    } else {
      console.log('⚠️  未找到文本输入框');
    }

    // 最终截图
    console.log('\n========== 📍 最终状态 ==========');
    await page.screenshot({ path: 'screenshots/text-04-final.png', fullPage: true });
    console.log('📸 已保存最终截图: text-04-final.png');

  } catch (error) {
    console.error('❌ 测试过程中出错:', error.message);
    console.error('堆栈:', error.stack);
    await page.screenshot({ path: 'screenshots/text-error.png', fullPage: true });
  } finally {
    // 报告 console 错误
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

    // 保存报告
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalErrors: errors.length,
        totalWarnings: warnings.length
      },
      errors: errors,
      warnings: warnings
    };

    fs.writeFileSync('screenshots/text-test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 测试报告已保存到 screenshots/text-test-report.json');

    await browser.close();
  }
})();
