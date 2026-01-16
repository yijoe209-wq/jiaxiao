# 数据库初始化修复

**日期**: 2026-01-16
**错误**: `sqlite3.OperationalError: no such table: families`

---

## 问题原因

### 错误信息
```
sqlite3.OperationalError: no such table: families
[SQL: SELECT families.family_id AS families_family_id...]
```

### 根本原因

在 Zeabur 生产环境中，应用启动时没有自动创建数据库表。

**原代码问题** ([models.py:247-256](models.py#L247-L256)):
```python
def init_db(database_url=None):
    """初始化数据库"""
    global db
    if database_url:
        db = Database(database_url)
        # 重新创建表
        db.create_tables()
    elif not db.engine:
        db.create_tables()
    return db
```

**问题分析**:
1. 当 `database_url=None` 时（使用默认的 SQLite）
2. 条件 `elif not db.engine` 永远为 `False`（因为 db.engine 已经存在）
3. 导致 `create_tables()` 永远不会被调用
4. 数据库表从未创建

---

## 解决方案

### 修复代码

**文件**: [models.py](models.py)

**修改位置**: `init_db()` 函数（第 247-255 行）

**修改后**:
```python
def init_db(database_url=None):
    """初始化数据库"""
    global db
    if database_url:
        db = Database(database_url)

    # 总是创建表（如果不存在）
    db.create_tables()
    return db
```

### 工作原理

1. **无论是否有新的 database_url**，都调用 `create_tables()`
2. `create_tables()` 使用 SQLAlchemy 的 `Base.metadata.create_all()`
3. 这个方法是**幂等的**（idempotent）：
   - ✅ 如果表不存在，创建表
   - ✅ 如果表已存在，跳过（不报错，不重复创建）
4. 可以安全地在每次应用启动时调用

---

## 测试验证

### 本地测试（SQLite）

```bash
# 删除现有数据库（模拟首次部署）
rm jiaxiao.db

# 启动应用
python3 app.py
```

**预期结果**:
- ✅ 应用启动成功
- ✅ 自动创建 `jiaxiao.db` 文件
- ✅ 控制台输出: `✅ 数据库表创建成功`
- ✅ 可以正常注册和登录

### Zeabur 部署（PostgreSQL）

修复后，Zeabur 部署应该能正常工作：

1. ✅ 应用启动时自动创建数据库表
2. ✅ 不再报 `no such table: families` 错误
3. ✅ 用户可以正常登录

---

## 相关代码

### 应用启动入口

**文件**: [app.py:34](app.py#L34)

```python
# 初始化数据库
init_db(Config.DATABASE_URL)
```

这行代码在应用启动时执行，确保数据库表被创建。

### create_tables() 方法

**文件**: [models.py:217-228](models.py#L217-L228)

```python
def create_tables(self):
    """创建所有表"""
    Base.metadata.create_all(bind=self.engine)

    # 启用 WAL 模式以提高并发性能
    if self.engine.dialect.name == 'sqlite':
        with self.engine.connect() as conn:
            conn.execute(text('PRAGMA journal_mode=WAL'))
            conn.execute(text('PRAGMA synchronous=NORMAL'))
            conn.commit()

    print("✅ 数据库表创建成功")
```

**关键点**:
- `Base.metadata.create_all()` 只创建不存在的表
- 对于 SQLite，启用 WAL 模式提高性能
- 对于 PostgreSQL，跳过 WAL 配置

---

## Commit 信息

**Commit**: `da734cc`
**消息**: `fix: 确保数据库表在应用启动时自动创建`

**状态**: ✅ 代码已修复，待推送到 GitHub

---

## 部署后检查

推送到 GitHub 后，Zeabur 会自动部署。部署完成后，请验证：

1. 访问 https://edu-track.zeabur.app/login
2. 尝试注册新用户或使用现有账号登录
3. 检查是否还有 `no such table` 错误
4. 查看应用日志，确认看到 `✅ 数据库表创建成功`

---

**修复状态**: ✅ 代码已修复
**部署状态**: ⏳ 等待推送到 GitHub 并部署
**最后更新**: 2026-01-16
