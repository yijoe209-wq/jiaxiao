# 当前状态和问题总结

## 问题描述

Zeabur 部署后，访问 https://edu-track.zeabur.app/login 报错：
```
sqlite3.OperationalError: no such table: families
```

## 根本原因

**数据库表在应用启动时没有被创建**

之前的 `init_db()` 函数逻辑：
```python
def init_db(database_url=None):
    global db
    if database_url:
        db = Database(database_url)
        db.create_tables()  # 只在有新 database_url 时创建表
    elif not db.engine:
        db.create_tables()
    return db
```

问题：当使用默认的 `sqlite:///jiaxiao.db` 时，`db.engine` 已经存在，所以 `create_tables()` 永远不会被调用。

## 已修复的代码

**Commit**: `da734cc`

**修复后的 `init_db()`**：
```python
def init_db(database_url=None):
    """初始化数据库"""
    global db
    if database_url:
        db = Database(database_url)

    # 总是创建表（如果不存在）
    db.create_tables()  # 👈 关键修复：每次启动都调用
    return db
```

## 为什么这样做是安全的

SQLAlchemy 的 `Base.metadata.create_all()` 是**幂等的**：
- 如果表不存在，创建表
- 如果表已存在，跳过（不会报错，不会重复创建）

所以可以安全地在每次应用启动时调用。

## 当前状态

1. ✅ 代码已修复并推送到 GitHub (commit `da734cc` 和 `a9b5d1f`)
2. ⏳ Zeabur 正在重新构建（从你提供的日志可以看到）
3. ⏳ 等待部署完成，查看启动日志

## 验证方法

部署完成后，在 Zeabur 控制台的"日志"页面，应该能看到：
```
✅ 数据库表创建成功
```

如果看到这行，说明修复已应用。

然后测试注册 API：
```bash
curl -X POST https://edu-track.zeabur.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","parent_name":"测试"}'
```

应该返回：
```json
{"success": true, "family_id": "...", "message": "注册成功"}
```

而不是 `no such table: families` 错误。

## 如果问题仍然存在

如果启动日志中有 "✅ 数据库表创建成功"，但仍然报错 `no such table`，那可能是因为：
1. SQLite 数据库文件存储在容器临时目录，重启后丢失
2. 多个 worker 进程同时访问 SQLite 导致锁问题

这时需要改用 Zeabur 提供的 PostgreSQL 服务。

---

**等待中**: Zeabur 部署完成...
