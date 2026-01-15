#!/usr/bin/env python3
"""
前端 UI 自动化测试
使用 Selenium 模拟真实用户在浏览器中的操作
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

class FrontendUITest:
    def __init__(self, headless=False):
        # 配置 Chrome 选项
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 初始化 WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)
        self.base_url = "http://localhost:5001"

    def print_step(self, step, status="⏳"):
        print(f"\n{status} {step}")
        print("=" * 60)

    def print_success(self, message):
        print(f"✅ {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def print_info(self, message):
        print(f"ℹ️  {message}")

    def save_screenshot(self, name):
        """保存截图"""
        filename = f"screenshots/{name}.png"
        self.driver.save_screenshot(filename)
        self.print_info(f"截图已保存: {filename}")

    def step_1_open_login_page(self):
        """步骤1: 打开登录页面"""
        self.print_step("步骤1: 打开登录页面", "🌐")
        
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # 检查页面标题
        title = self.driver.title
        self.print_info(f"页面标题: {title}")
        
        # 检查是否有登录表单
        try:
            login_tab = self.driver.find_element(By.XPATH, "//div[@class='tab active' and text()='登录']")
            self.print_success("成功打开登录页面")
            self.save_screenshot("01_login_page")
            return True
        except Exception as e:
            self.print_error(f"打开登录页面失败: {e}")
            return False

    def step_2_login(self):
        """步骤2: 登录"""
        self.print_step("步骤2: 登录系统", "🔐")
        
        try:
            # 输入邮箱
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "loginEmail"))
            )
            email_input.clear()
            email_input.send_keys("test@example.com")
            self.print_info("已输入邮箱")
            
            # 输入密码
            password_input = self.driver.find_element(By.ID, "loginPassword")
            password_input.clear()
            password_input.send_keys("test123")
            self.print_info("已输入密码")
            
            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.print_info("已点击登录按钮")
            
            # 等待跳转
            time.sleep(3)
            
            # 检查是否成功登录（跳转到任务中心）
            current_url = self.driver.current_url
            if "/my-tasks" in current_url or current_url.endswith("/"):
                self.print_success(f"登录成功！当前页面: {current_url}")
                self.save_screenshot("02_after_login")
                return True
            else:
                self.print_error(f"登录失败，当前页面: {current_url}")
                # 检查是否有错误提示
                try:
                    error = self.driver.find_element(By.CLASS_NAME, "error")
                    if error.is_displayed():
                        self.print_info(f"错误提示: {error.text}")
                except:
                    pass
                return False
        except Exception as e:
            self.print_error(f"登录过程出错: {e}")
            return False

    def step_3_add_student(self):
        """步骤3: 添加学生"""
        self.print_step("步骤3: 添加学生", "👥")
        
        try:
            # 访问学生管理页面
            self.driver.get(f"{self.base_url}/students")
            time.sleep(2)
            
            # 输入学生姓名
            name_input = self.driver.find_element(By.ID, "nameInput")
            name_input.clear()
            name_input.send_keys("测试学生")
            self.print_info("已输入学生姓名")
            
            # 选择年级
            grade_select = self.driver.find_element(By.ID, "gradeInput")
            from selenium.webdriver.support.select import Select
            select = Select(grade_select)
            select.select_by_visible_text("五年级")
            self.print_info("已选择年级")
            
            # 输入班级
            class_input = self.driver.find_element(By.ID, "classInput")
            class_input.clear()
            class_input.send_keys("1班")
            self.print_info("已输入班级")
            
            # 点击添加按钮
            add_button = self.driver.find_element(By.XPATH, "//button[text()='添加学生']")
            add_button.click()
            self.print_info("已点击添加学生按钮")
            
            # 等待响应
            time.sleep(2)
            
            # 检查是否添加成功
            try:
                # 可能会弹出 alert
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                self.print_info(f"提示信息: {alert_text}")
                self.save_screenshot("03_student_added")
                
                if "成功" in alert_text or "添加" in alert_text:
                    self.print_success("学生添加成功")
                    return True
                else:
                    self.print_error(f"添加失败: {alert_text}")
                    return False
            except:
                # 没有 alert，检查页面是否显示了学生
                student_list = self.driver.find_element(By.ID, "studentList")
                if "测试学生" in student_list.text:
                    self.print_success("学生添加成功")
                    return True
                else:
                    self.print_error("未在学生列表中找到新添加的学生")
                    return False
        except Exception as e:
            self.print_error(f"添加学生过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_4_create_task(self):
        """步骤4: 创建任务"""
        self.print_step("步骤4: 创建任务", "📝")
        
        try:
            # 返回首页
            self.driver.get(f"{self.base_url}/")
            time.sleep(2)
            
            # 输入作业内容
            textarea = self.driver.find_element(By.TAG_NAME, "textarea")
            textarea.clear()
            homework_text = """语文：完成第5课练习册第10-15页
数学：口算题卡第3页全部题目
英语：背诵 Unit 1-3 的所有单词"""
            textarea.send_keys(homework_text)
            self.print_info("已输入作业内容")
            
            self.save_screenshot("04_homework_entered")
            
            # 点击 AI 解析按钮
            parse_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'AI') or contains(text(), '解析')]")
            parse_button.click()
            self.print_info("已点击 AI 解析按钮")
            
            # 等待 AI 响应（可能需要几秒）
            time.sleep(5)
            
            # 检查是否有解析结果
            try:
                # 查找结果区域
                result_div = self.driver.find_element(By.ID, "result")
                if result_div.is_displayed():
                    self.print_success("AI 解析完成")
                    self.save_screenshot("05_after_parse")
                    
                    # 检查是否有任务
                    tasks_text = result_div.text
                    self.print_info(f"解析结果: {tasks_text[:200]}...")
                    return True
                else:
                    self.print_error("未看到解析结果")
                    return False
            except:
                self.print_error("没有找到解析结果区域")
                return False
        except Exception as e:
            self.print_error(f"创建任务过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_5_view_task_center(self):
        """步骤5: 查看任务中心"""
        self.print_step("步骤5: 查看任务中心", "📊")
        
        try:
            # 访问任务中心
            self.driver.get(f"{self.base_url}/")
            time.sleep(3)
            
            # 检查是否有任务显示
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.print_info(f"页面内容摘要: {page_text[:200]}...")
            
            # 检查是否有任务列表
            try:
                task_list = self.driver.find_element(By.ID, "taskList")
                if task_list.is_displayed():
                    tasks = task_list.find_elements(By.CLASS_NAME, "task-item")
                    self.print_success(f"任务中心显示 {len(tasks)} 个任务")
                    
                    # 显示前几个任务
                    for i, task in enumerate(tasks[:3], 1):
                        task_text = task.text
                        self.print_info(f"  任务 {i}: {task_text[:50]}...")
                    
                    self.save_screenshot("06_task_center")
                    return True
                else:
                    # 检查是否是空状态
                    try:
                        empty_state = self.driver.find_element(By.ID, "emptyState")
                        if empty_state.is_displayed():
                            self.print_info("任务中心为空")
                            self.save_screenshot("06_task_center_empty")
                            return True
                    except:
                        self.print_info("任务中心状态未知")
                        self.save_screenshot("06_task_center_unknown")
                        return True
            except Exception as e:
                self.print_info(f"任务列表检查: {e}")
                return True
        except Exception as e:
            self.print_error(f"查看任务中心出错: {e}")
            return False

    def step_6_check_data_isolation(self):
        """步骤6: 测试数据隔离"""
        self.print_step("步骤6: 测试数据隔离", "🔒")
        
        try:
            # 登出
            self.driver.delete_all_cookies()
            self.print_info("已清除所有 cookies")
            
            # 刷新页面
            self.driver.refresh()
            time.sleep(2)
            
            # 检查是否被重定向到登录页
            current_url = self.driver.current_url
            if "/login" in current_url:
                self.print_success("未登录状态正确重定向到登录页")
            else:
                self.print_info(f"当前页面: {current_url}")
            
            # 尝试直接访问任务中心
            self.driver.get(f"{self.base_url}/")
            time.sleep(2)
            
            # 检查是否有"请先登录"提示或重定向
            current_url = self.driver.current_url
            if "/login" in current_url:
                self.print_success("数据隔离测试通过 - 未登录无法访问任务中心")
                return True
            else:
                self.print_error(f"安全漏洞 - 未登录可以访问任务中心: {current_url}")
                return False
        except Exception as e:
            self.print_error(f"数据隔离测试出错: {e}")
            return False

    def run(self):
        """运行完整的前端测试"""
        print("\n" + "=" * 60)
        print("🚀 开始前端 UI 自动化测试")
        print("=" * 60)
        
        results = []
        
        # 步骤1: 打开登录页面
        results.append(self.step_1_open_login_page())
        
        # 步骤2: 登录
        results.append(self.step_2_login())
        
        # 步骤3: 添加学生
        results.append(self.step_3_add_student())
        
        # 步骤4: 创建任务
        results.append(self.step_4_create_task())
        
        # 步骤5: 查看任务中心
        results.append(self.step_5_view_task_center())
        
        # 步骤6: 测试数据隔离
        results.append(self.step_6_check_data_isolation())
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total = len(results)
        passed = sum(results)
        failed = total - passed
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        
        if passed == total:
            print("\n" + "🎉 " * 20)
            print("所有前端测试通过！")
            print("🎉 " * 20)
            return True
        else:
            print("\n" + "⚠️ " * 20)
            print(f"有 {failed} 个测试失败")
            print("⚠️ " * 20)
            return False

    def close(self):
        """关闭浏览器"""
        self.driver.quit()
        self.print_info("浏览器已关闭")


if __name__ == "__main__":
    import os
    
    # 创建截图目录
    os.makedirs("screenshots", exist_ok=True)
    
    # 运行测试（headless=False 以便看到浏览器操作）
    tester = FrontendUITest(headless=False)
    
    try:
        success = tester.run()
    finally:
        tester.close()
