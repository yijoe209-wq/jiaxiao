# PostgreSQL 驱动修复报告

**日期**: 2026-01-16
**错误**: `ModuleNotFoundError: No module named 'psycopg2'`

---

## 问题原因

### 错误信息
```
File "/usr/local/lib/python3.13/site-packages/sqlalchemy/dialects/postgresql/psycopg2.py", line 690, in import_dbapi
    import psycopg2
ModuleNotFoundError: No module named 'psycopg2'
```

### 根本原因

1. **requirements.txt** 中指定的是 `psycopg[binary]>=3.2.0`（版本 3，纯 Python）
2. **SQLAlchemy** 默认使用 `psycopg2`（版本 2，需要编译）作为 PostgreSQL 驱动
3. **版本不匹配**: SQLAlchemy 尝试导入不存在的 `psycopg2` 而不是 `psycopg`

### psycopg 版本说明

- **psycopg2** (v2): 旧版本，需要 C 编译，已不再维护
- **psycopg** (v3): 新版本，纯 Python 实现，`psycopg[binary]` 提供
- **requirements.txt**: 已正确使用 `psycopg[binary]`

---

## 解决方案

### 修复代码

**文件**: `models.py`

**修改位置**: `Database.__init__()` 方法

**修改内容**:

```python
# 修改前
else:
    # PostgreSQL 等其他数据库
    engine_kwargs = {
        'echo': False,
        'pool_pre_ping': True,
    }

self.engine = create_engine(database_url, **engine_kwargs)
```

```python
# 修改后
else:
    # PostgreSQL 等其他数据库
    # 确保 URL 使用正确的驱动 (postgresql+psycopg:// 而不是 postgresql://)
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

    engine_kwargs = {
        'echo': False,
        'pool_pre_ping': True,
    }

self.engine = create_engine(database_url, **engine_kwargs)
```

### 工作原理

当 SQLAlchemy 看到 `postgresql+psycopg://` 这样的 URL 时：
- ✅ 它知道要使用 `psycopg` 方言
- ✅ 导入 `psycopg` 包（来自 `psycopg[binary]`）
- ✅ 不会再尝试导入 `psycopg2`

---

## SQLAlchemy URL 格式说明

### PostgreSQL URL 格式

```
# 通用格式
postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

# 指定驱动（推荐）
postgresql+psycopg://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

# SQLAlchemy 支持的驱动
- postgresql+psycopg2://  (使用 psycopg2 - 旧版)
- postgresql+psycopg://   (使用 psycopg - 新版，推荐)
- postgresql+pg8000://    (使用 pg8000 - 纯 Python)
```

### 示例

```
# Zeabur 提供的 DATABASE_URL（可能格式）
postgresql://user:pass@host:5432/dbname

# 修复后自动转换为
postgresql+psycopg://user:pass@host:5432/dbname
```

---

## 测试验证

### 本地测试（SQLite）

```bash
# 本地使用 SQLite，不需要 psycopg
python3 -c "from models import Database; db = Database(); print('✅ SQLite 连接成功')"
```

### Zeabur 部署（PostgreSQL）

修复后，Zeabur 部署应该能正常工作：
1. ✅ 不再报 `ModuleNotFoundError: No module named 'psycopg2'`
2. ✅ 成功导入 `psycopg` 包（来自 `psycopg[binary]`）
3. ✅ 数据库连接正常建立

---

## requirements.txt 确认

当前配置（正确）：

```txt
# PostgreSQL Driver (psycopg v3 - pure Python, no compilation needed)
psycopg[binary]>=3.2.0
```

**说明**:
- ✅ `psycopg[binary]` - 包含完整的 `psycopg` 包（版本 3）
- ✅ 纯 Python 实现，无需编译
- ✅ 与 Python 3.13 兼容

---

## 相关提交

**Commit**: `<pending>`
**消息**: `fix: 修复 PostgreSQL 驱动兼容性问题`

---

## 参考资料

- [SQLAlchemy PostgreSQL 文档](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [psycopg 文档](https://www.psycopg.org/psycopg3/docs/)
- [Zeabur 环境变量](https://zeabur.com/docs/environment-variables)

---

**修复状态**: ✅ 代码已修复
**部署状态**: ⏳ 等待推送到 GitHub 并部署
**最后更新**: 2026-01-16
