#!/bin/bash

# 家校任务管理应用 - 全面测试脚本
# 测试地址: https://phase-friends-theater-pork.trycloudflare.com

BASE_URL="https://phase-friends-theater-pork.trycloudflare.com"
LOCAL_URL="http://127.0.0.1:5001"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="test123456"

echo "================================================"
echo "家校任务管理应用 - 全面测试"
echo "测试地址: $BASE_URL"
echo "本地地址: $LOCAL_URL"
echo "================================================"
echo ""

# 使用本地URL进行测试（更快更稳定）
API_URL=$LOCAL_URL

# 计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试结果数组
declare -a TEST_RESULTS

# 测试函数
run_test() {
    local test_name=$1
    local test_command=$2
    local expected_result=$3

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "测试 $TOTAL_TESTS: $test_name"

    eval "$test_command"
    local result=$?

    if [ $result -eq 0 ]; then
        echo "✓ 通过"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("✓ $test_name")
    else
        echo "✗ 失败"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS+=("✗ $test_name")
    fi
    echo ""
}

# 1. 健康检查
echo "========== 1. 系统健康检查 =========="
run_test "健康检查API" "curl -sf $API_URL/health | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"status\") == \"ok\" else 1)'"

# 2. 用户认证
echo "========== 2. 用户认证测试 =========="
run_test "用户登录" "curl -sf -X POST $API_URL/api/login -H 'Content-Type: application/json' -d '{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"

# 获取family_id用于后续测试
FAMILY_ID=$(curl -s -X POST $API_URL/api/login -H 'Content-Type: application/json' -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('family_id', ''))")

if [ -z "$FAMILY_ID" ]; then
    echo "错误: 无法获取 family_id，测试终止"
    exit 1
fi

echo "使用 family_id: $FAMILY_ID"
echo ""

# 3. 学生管理
echo "========== 3. 学生管理测试 =========="

run_test "获取学生列表" "curl -sf -X GET $API_URL/api/students -H 'X-Family-ID: $FAMILY_ID' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if \"students\" in data else 1)'"

# 添加学生
TIMESTAMP=$(date +%s)
NEW_STUDENT_NAME="测试学生$TIMESTAMP"
run_test "添加学生" "curl -sf -X POST $API_URL/api/students -H 'Content-Type: application/json' -H 'X-Family-ID: $FAMILY_ID' -d '{\"name\":\"$NEW_STUDENT_NAME\",\"grade\":\"四年级\",\"class_name\":\"5班\"}' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"

# 获取学生ID
STUDENT_ID=$(curl -s -X POST $API_URL/api/students -H 'Content-Type: application/json' -H "X-Family-ID: $FAMILY_ID" -d "{\"name\":\"$NEW_STUDENT_NAME\",\"grade\":\"四年级\",\"class_name\":\"5班\"}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('student_id', ''))")

if [ -n "$STUDENT_ID" ]; then
    # 编辑学生
    run_test "编辑学生信息" "curl -sf -X PUT $API_URL/api/students/$STUDENT_ID -H 'Content-Type: application/json' -H 'X-Family-ID: $FAMILY_ID' -d '{\"name\":\"编辑后的学生\",\"grade\":\"五年级\",\"class_name\":\"6班\"}' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"

    # 删除学生
    run_test "删除学生" "curl -sf -X DELETE $API_URL/api/students/$STUDENT_ID -H 'X-Family-ID: $FAMILY_ID' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"
fi

echo ""

# 4. 任务管理
echo "========== 4. 任务管理测试 =========="

# 获取第一个学生的ID
FIRST_STUDENT_ID=$(curl -s -X GET $API_URL/api/students -H "X-Family-ID: $FAMILY_ID" | python3 -c "import sys, json; data=json.load(sys.stdin); students=data.get('students', []); print(students[0].get('id', '') if students else '')")

if [ -n "$FIRST_STUDENT_ID" ]; then
    echo "使用学生ID: $FIRST_STUDENT_ID"

    run_test "获取学生任务列表" "curl -sf -X GET $API_URL/api/tasks/$FIRST_STUDENT_ID | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if \"success\" in data else 1)'"

    # 创建一个待确认任务用于测试
    # 注意: 这需要模拟微信消息处理
fi

echo ""

# 5. 页面访问
echo "========== 5. 页面访问测试 =========="
run_test "首页可访问" "curl -sf $API_URL/ > /dev/null"
run_test "登录页可访问" "curl -sf $API_URL/login > /dev/null"
run_test "学生管理页可访问" "curl -sf $API_URL/students > /dev/null"
run_test "任务页可访问" "curl -sf $API_URL/tasks > /dev/null"

echo ""

# 6. 边界测试
echo "========== 6. 边界测试 =========="

run_test "未登录访问学生列表应失败" "! curl -sf -X GET $API_URL/api/students | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if \"students\" in data else 1)'"

run_test "无效邮箱注册应失败" "! curl -sf -X POST $API_URL/api/register -H 'Content-Type: application/json' -d '{\"email\":\"invalid\",\"password\":\"123456\",\"parent_name\":\"测试\"}' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"

run_test "短密码注册应失败" "! curl -sf -X POST $API_URL/api/register -H 'Content-Type: application/json' -d '{\"email\":\"test2@example.com\",\"password\":\"12345\",\"parent_name\":\"测试\"}' | python3 -c 'import sys, json; data=json.load(sys.stdin); exit(0 if data.get(\"success\") else 1)'"

echo ""

# 7. 性能测试
echo "========== 7. 性能测试 =========="

# 测试登录响应时间
START_TIME=$(date +%s%N)
curl -s -X POST $API_URL/api/login -H 'Content-Type: application/json' -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" > /dev/null
END_TIME=$(date +%s%N)
LOGIN_TIME=$(( ($END_TIME - $START_TIME) / 1000000 ))
echo "登录响应时间: ${LOGIN_TIME}ms"
if [ $LOGIN_TIME -lt 1000 ]; then
    echo "✓ 登录响应时间 < 1秒"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✓ 登录性能测试")
else
    echo "✗ 登录响应时间 > 1秒"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TEST_RESULTS+=("✗ 登录性能测试")
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# 测试学生列表响应时间
START_TIME=$(date +%s%N)
curl -s -X GET $API_URL/api/students -H "X-Family-ID: $FAMILY_ID" > /dev/null
END_TIME=$(date +%s%N)
STUDENTS_TIME=$(( ($END_TIME - $START_TIME) / 1000000 ))
echo "获取学生列表响应时间: ${STUDENTS_TIME}ms"
if [ $STUDENTS_TIME -lt 500 ]; then
    echo "✓ 学生列表响应时间 < 500ms"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✓ 学生列表性能测试")
else
    echo "✗ 学生列表响应时间 > 500ms"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TEST_RESULTS+=("✗ 学生列表性能测试")
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# 汇总结果
echo "================================================"
echo "测试结果汇总"
echo "================================================"
echo ""
echo "总测试数: $TOTAL_TESTS"
echo "通过: $PASSED_TESTS"
echo "失败: $FAILED_TESTS"
echo "成功率: $(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过！"
else
    echo "⚠️  有 $FAILED_TESTS 个测试失败"
    echo ""
    echo "失败的测试："
    for result in "${TEST_RESULTS[@]}"; do
        if [[ $result == ✗* ]]; then
            echo "  $result"
        fi
    done
fi

echo ""
echo "================================================"
echo "详细测试结果："
echo "================================================"
for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo "================================================"
echo "测试账号信息"
echo "================================================"
echo "邮箱: $TEST_EMAIL"
echo "密码: $TEST_PASSWORD"
echo "Family ID: $FAMILY_ID"
echo ""

# 退出码
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi
