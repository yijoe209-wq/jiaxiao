# 🚀 Zeabur 部署修复指南

**问题**: 数据库表未创建，注册/登录功能无法使用
**原因**: Zeabur 还在使用旧代码
**解决**: 手动触发重新部署

---

## 📝 快速步骤（2 分钟）

### 1. 登录 Zeabur
访问: https://dash.zeabur.com/

### 2. 找到项目
项目名: `jiaxiao` 或 `edu-track`

### 3. 点击服务
通常叫 `web`、`app` 或主服务

### 4. 重新部署
点击 **"Redeploy"** 或 **"重新部署"** 按钮

### 5. 等待完成
等待 2-3 分钟，观察部署进度

### 6. 查看日志
确认看到:
```
✅ 数据库表创建成功
```

---

## ✅ 验证修复

部署完成后，运行:

```bash
python3 simple_test.py
```

或测试 API:

```bash
curl -X POST https://edu-track.zeabur.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","parent_name":"测试"}'
```

**预期结果**:
```json
{
  "success": true,
  "family_id": "...",
  "message": "注册成功"
}
```

---

## 🔍 如果问题仍然存在

### 检查 1: 使用的 Commit
在 Zeabur 日志中搜索 `commit` 或 `sha`，应该是 `a9b5d1f`

### 检查 2: 环境变量
确认 `DATABASE_URL` 已设置（如果使用 Zeabur PostgreSQL）

### 检查 3: 清除缓存
在 Zeabur 设置中禁用构建缓存，然后重新部署

---

## 📞 需要帮助？

查看详细文档:
- `DEPLOYMENT_ISSUES.md` - 完整问题诊断
- `FINAL_SUMMARY.md` - 工作总结

---

**最后更新**: 2026-01-16 12:52
