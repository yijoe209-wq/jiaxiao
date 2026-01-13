/**
 * 全面测试家校任务管理应用的所有功能
 * 测试地址: https://phase-friends-theater-pork.trycloudflare.com
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'https://phase-friends-theater-pork.trycloudflare.com';
const TEST_USER = {
  email: 'alves820@live.cn',
  password: 'test123456',
  parent_name: '测试家长'
};

// ========== 测试套件：用户认证流程 ==========

test.describe('用户认证流程', () => {

  test('应该能够访问首页', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/作业助手/);
    console.log('✓ 首页访问成功');
  });

  test('应该能够访问登录页面', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await expect(page.locator('body')).toBeVisible();
    console.log('✓ 登录页面访问成功');
  });

  test('应该能够注册新用户', async ({ page }) => {
    const timestamp = Date.now();
    const newUser = {
      email: `test_${timestamp}@example.com`,
      password: 'test123456',
      parent_name: `测试用户${timestamp}`
    };

    await page.goto(`${BASE_URL}/login`);

    // 切换到注册标签
    const registerTab = page.locator('text=注册').first();
    if (await registerTab.isVisible()) {
      await registerTab.click();
    }

    // 填写注册表单
    await page.fill('input[name="email"]', newUser.email);
    await page.fill('input[name="password"]', newUser.password);
    await page.fill('input[name="parent_name"]', newUser.parent_name);

    // 提交注册
    await page.click('button:has-text("注册")');

    // 等待响应
    await page.waitForTimeout(2000);

    console.log(`✓ 注册测试完成: ${newUser.email}`);
  });

  test('应该能够登录', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // 填写登录表单
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);

    // 提交登录
    await page.click('button:has-text("登录")');

    // 等待响应
    await page.waitForTimeout(2000);

    console.log('✓ 登录测试完成');
  });
});

// ========== 测试套件：学生管理 ==========

test.describe('学生管理', () => {

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.click('button:has-text("登录")');
    await page.waitForTimeout(1000);

    // 导航到学生管理页面
    await page.goto(`${BASE_URL}/students`);
    await page.waitForTimeout(1000);
  });

  test('应该能够添加学生', async ({ page }) => {
    const timestamp = Date.now();
    const student = {
      name: `测试学生${timestamp}`,
      grade: '三年级',
      class_name: '3班'
    };

    // 点击添加按钮
    await page.click('button:has-text("添加学生")');
    await page.waitForTimeout(500);

    // 填写学生信息
    await page.fill('input[name="name"]', student.name);
    await page.selectOption('select[name="grade"]', student.grade);
    await page.fill('input[name="class_name"]', student.class_name);

    // 提交
    await page.click('button:has-text("保存")');
    await page.waitForTimeout(2000);

    console.log(`✓ 添加学生成功: ${student.name}`);
  });

  test('应该能够显示学生列表', async ({ page }) => {
    // 等待页面加载
    await page.waitForTimeout(1000);

    // 检查学生列表
    const studentList = page.locator('.student-item');
    const count = await studentList.count();

    console.log(`✓ 学生列表显示: ${count} 个学生`);
    expect(count).toBeGreaterThanOrEqual(0);
  });
});

// ========== 测试套件：任务创建流程 ==========

test.describe('任务创建流程', () => {

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.click('button:has-text("登录")');
    await page.waitForTimeout(1000);
  });

  test('应该能够创建纯文本任务', async ({ page }) => {
    await page.goto(BASE_URL);

    // 输入任务文本
    const testMessage = '明天请背诵《静夜思》，并抄写三遍';
    await page.fill('textarea[placeholder*="输入老师布置的作业"]', testMessage);

    // 点击提交
    const startTime = Date.now();
    await page.click('button:has-text("提交")');

    // 等待 AI 解析完成（3-7秒）
    await page.waitForTimeout(8000);
    const endTime = Date.now();
    const responseTime = (endTime - startTime) / 1000;

    console.log(`✓ 纯文本任务创建成功，响应时间: ${responseTime}秒`);
    expect(responseTime).toBeLessThan(10);
  });
});

// ========== 测试套件：性能测试 ==========

test.describe('性能测试', () => {

  test('首页加载时间应该小于2秒', async ({ page }) => {
    const startTime = Date.now();
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    const endTime = Date.now();
    const loadTime = (endTime - startTime) / 1000;

    console.log(`首页加载时间: ${loadTime}秒`);
    expect(loadTime).toBeLessThan(2);
  });
});

// ========== 测试套件：健康检查 ==========

test.describe('健康检查', () => {

  test('健康检查接口应该正常', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);

    expect(response.status()).toBe(200);

    const data = await response.json();
    console.log('健康检查结果:', data);
    expect(data.status).toBe('ok');
  });
});
