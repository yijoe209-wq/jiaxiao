#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('jiaxiao.db')
cursor = conn.cursor()

cursor.execute("SELECT task_data FROM pending_tasks WHERE pending_id = 'c3f00d0a-e43d-4d17-bb7a-593ecd79eca4'")
row = cursor.fetchone()

if row:
    task_data = json.loads(row[0])
    print("数据结构:")
    print(f"  type: {task_data.get('type')}")
    print(f"  has raw_text: {'raw_text' in task_data}")
    print(f"  raw_text: {task_data.get('raw_text', 'N/A')[:50]}")
    print(f"  has task: {'task' in task_data}")

    if 'task' in task_data:
        task = task_data['task']
        print(f"\ntask 字段:")
        print(f"  description: {task.get('description', 'N/A')[:50]}")
        print(f"  subject: {task.get('subject', 'N/A')}")
        print(f"  keys: {list(task.keys())}")

conn.close()
