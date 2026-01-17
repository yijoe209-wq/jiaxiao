# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a family-school task management system (家校信息智能管家) that uses AI to parse WeChat group messages from teachers and extract homework/notifications for parents and students. The system allows parents to forward WeChat messages, which are parsed by LLM (DeepSeek), and then confirmed before being added as tasks for students.

**Tech Stack:**
- Backend: Python 3.10+ with Flask
- Database: SQLite (development) / PostgreSQL (production via Zeabur)
- LLM: DeepSeek API (cost-effective alternative to GPT)
- ORM: SQLAlchemy 2.0

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from models import init_db; init_db()"

# Run development server
python app.py

# View logs
tail -f logs/app.log
```

Environment setup:
1. Copy `.env.example` to `.env`
2. Configure required variables: `LLM_API_KEY`, `WECHAT_TOKEN`
3. For production, set `DATABASE_URL` (PostgreSQL)

## Architecture Overview

### Core Data Flow

1. **Message Reception**: WeChat → `/wechat` endpoint → XML parsing
2. **AI Processing**: Text/images → background thread → `enhanced_parser.parse()` → `PendingTask`
3. **User Confirmation**: Web UI → `/api/confirm` → `task_service.confirm_tasks()` → `Task` records
4. **Task Management**: Web UI → CRUD operations via `/api/tasks/*`

### Key Components

**[app.py](app.py)** - Flask application with:
- WeChat message webhook (`/wechat`) handling XML messages
- Session-based authentication (Flask sessions with `family_id`)
- REST API endpoints for tasks, students, confirmation
- Template rendering for web UI
- File upload handling for images

**[models.py](models.py)** - Database models:
- `Family` - Parent account (email/password login)
- `Student` - Child accounts belonging to a family
- `TaskGroup` - Groups multiple related tasks
- `Task` - Individual homework/notification with AI metadata
- `PendingTask` - Temporary storage (24h TTL) for unconfirmed tasks
- `Database` class - Connection pooling with SQLite WAL mode or PostgreSQL

**[task_service.py](task_service.py)** - Business logic:
- `process_message()` - Orchestrates AI parsing and pending task creation
- `confirm_tasks()` - Converts pending tasks to confirmed tasks with student assignment
- `parse_deadline()` - Parses Chinese relative dates (明天, 周一, etc.)

**[config.py](config.py)** - Configuration management:
- Environment-based configs (development/production/testing)
- Database URL selection logic
- WeChat and LLM API credentials

### Database Relationships

```
Family (1) ──< (N) Student (1) ──< (N) Task
                 │
                 └── TaskGroup (1) ──< (N) Task
```

Tasks support:
- Grouping via `TaskGroup` for multi-task messages
- Attachments (images) stored as JSON
- AI confidence scores and parsing metadata
- Chinese deadline parsing (明天, 周X, etc.)

### Authentication & Authorization

- **Family accounts**: Email + SHA256 password hash
- **Session management**: Flask server-side sessions with `family_id`
- **Authorization**: All API endpoints verify `family_id` matches resource ownership
- Helper: `get_current_family_id()` retrieves logged-in user from Flask session

### WeChat Integration

The `/wechat` endpoint handles:
1. **GET**: Server signature verification (SHA1 hash)
2. **POST**: Message processing with immediate response + async AI parsing

Message types supported:
- `text` - Triggers AI parsing via background thread
- `image` - Downloaded and stored, added to pending image buffer
- Commands: "查看任务", "确认", "帮助" for quick actions

**Critical pattern**: Images are buffered in-memory (`handle_image_message.pending_images[wechat_id]`) until a text message triggers parsing. This is a TODO for Redis in production.

### AI Parsing

The `enhanced_parser` module (currently missing - see Known Issues) should provide:
- `parse(content)` - Returns structured task data with intent, subject, deadline, description
- Support for single vs multiple tasks
- Confidence scoring

Expected return format:
```python
{
    'intent': 'assignment',  # or 'notification', 'ignore'
    'type': 'single',  # or 'multiple'
    'tasks': [...],  # for multiple
    'subject': '数学',
    'deadline': '2025-01-18',
    'description': '完成练习册第10页',
    'confidence': 0.9
}
```

### Pending Task Confirmation Flow

1. AI parsing creates `PendingTask` with JSON `task_data` (24h expiry)
2. User receives WeChat message with confirmation link
3. Web UI (`/confirm?pending_id=...`) displays parsed tasks for editing
4. User selects student and confirms via `/api/confirm`
5. `task_service.confirm_tasks()` converts to `Task` records, deletes `PendingTask`

## Important Patterns & Conventions

### Database Sessions

```python
session = db.get_session()
try:
    # Database operations
    session.commit()
finally:
    session.close()
```

Always close sessions explicitly. The `Database` class handles connection pooling.

### Error Handling

Use the logger from `utils.logger`:
```python
from utils import logger
logger.info("Message")
logger.error("Error", exc_info=True)  # Includes stack trace
```

### API Response Format

Success:
```python
return jsonify({'success': True, 'data': ...})
```

Error:
```python
return jsonify({'error': 'message'}), status_code
```

### File Uploads

- Uploaded to `UPLOAD_FOLDER` (./data/uploads local, /app/data/uploads on Zeabur)
- Served via `/uploads/<filename>`
- Max size: 16MB
- Allowed: png, jpg, jpeg, gif, webp

## Known Issues

1. **Missing `enhanced_parser.py`**: The [task_service.py](task_service.py:7) imports `enhanced_parser` which doesn't exist. This needs to be created or the import needs to be fixed.

2. **In-memory image buffer**: `handle_image_message.pending_images` uses function attributes for caching. Should use Redis for production.

3. **Hardcoded URLs**: Some URLs like `https://achievement-senior-any-manchester.trycloudflare.com` are hardcoded for Cloudflare Tunnel. Should use `Config.SERVER_URL`.

## Deployment Notes

### Local Development
- Uses `sqlite:///jiaxiao.db`
- Run `python app.py` (default port 5001)

### Production (Zeabur)
- PostgreSQL via `DATABASE_URL` environment variable
- Persistent storage at `/app/data/`
- Set `ENV=production` environment variable
- Use gunicorn instead of Flask dev server
