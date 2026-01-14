# 附件预览功能实现 - 2026-01-14

## 问题描述

用户反馈："任务中心的任务只能标记已完成，附件也不能预览也不能打开，那只说有个附件有啥意义"

## 根本原因

任务中心的附件数据结构是：
```json
[
  {"type": "image", "path": "data:image/jpeg;base64,..."},
  {"type": "image", "path": "data:image/png;base64,..."}
]
```

但前端代码错误地将附件对象数组直接当作 URL 数组使用：
```javascript
// ❌ 错误：att 是对象，不是字符串
<img src="${att}" ...>
```

## 解决方案

### 1. 修改模板文件 `templates/my-tasks.html`

#### 修复缩略图显示（行 635-655）

```javascript
${task.attachments.map((att, attIdx) => {
    // 从附件对象中提取 URL
    const imageUrl = typeof att === 'string' ? att : (att.path || att.url || '');
    return `
    <div class="relative group cursor-pointer" onclick="previewAttachment('${imageUrl}', '${task.task_id}')">
        <img src="${imageUrl}" alt="附件${attIdx + 1}" ...>
    </div>
    `;
}).join('')}
```

#### 修复预览函数（行 689-709）

```javascript
function previewAttachment(imageUrl, taskId) {
    const task = allTasks.find(t => t.task_id === taskId);
    if (!task || !task.attachments) return;

    // 将附件对象数组转换为 URL 数组
    currentAttachments = task.attachments.map(att => {
        return typeof att === 'string' ? att : (att.path || att.url || '');
    }).filter(url => url); // 过滤掉空值

    currentImageIndex = currentAttachments.indexOf(imageUrl);
    if (currentImageIndex === -1) currentImageIndex = 0;
    currentTaskDescription = task.description || '任务附件';

    updateModalImage();
    // ... 打开模态框
}
```

### 2. 新增功能

- ✅ 附件缩略图显示（12x12，圆角边框，悬停效果）
- ✅ 图片预览模态框（最大 90vh）
- ✅ 多附件导航（上一张/下一张按钮）
- ✅ 计数器显示（当前图片/总数）
- ✅ 下载按钮
- ✅ 键盘快捷键支持（← → ESC）
- ✅ 点击模态框外部关闭
- ✅ 模态框打开时禁止背景滚动

### 3. 兼容性处理

代码支持两种附件格式：
```javascript
// 格式1：直接是 URL 字符串（兼容旧数据）
["url1", "url2"]

// 格式2：附件对象数组（新格式）
[{"type": "image", "path": "url1"}, {"type": "image", "path": "url2"}]
```

## 测试方法

### 方法1：使用现有数据测试

```bash
# 1. 确保服务器运行
python3 app.py

# 2. 访问任务中心（需要在浏览器中已登录并有带附件的任务）
open http://localhost:5001/my-tasks
```

### 方法2：创建测试数据

```bash
# 运行批量测试脚本创建带附件的任务
python3 test_batch_simple.py
```

### 方法3：手动测试

1. 访问 http://localhost:5001/
2. 添加学生
3. 输入任务内容并上传图片
4. 点击"AI 智能解析"
5. 在确认页面确认创建
6. 访问任务中心查看附件预览

## 技术细节

### 附件数据流程

1. **存储**：数据库存储 JSON 字符串
   ```sql
   attachments = '[{"type": "image", "path": "data:image/..."}]'
   ```

2. **API 返回**：`Task.to_dict()` 解析 JSON
   ```python
   attachments = json.loads(self.attachments)
   ```

3. **前端显示**：提取 `path` 字段作为图片 URL
   ```javascript
   const imageUrl = att.path || att.url || ''
   ```

### 图片格式

当前使用 data URL 格式（base64 编码）：
```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...
```

优点：
- 无需额外的图片服务器
- 图片和任务数据一起存储
- 支持离线访问

缺点：
- 数据库体积较大
- 不适合超大图片

## 后续优化建议

1. **图片压缩**：在上传前压缩图片，减少数据大小
2. **CDN 存储**：将图片存储到 OSS/S3，只保存 URL
3. **懒加载**：缩略图使用更小的尺寸
4. **缓存**：使用浏览器缓存减少重复加载

## 相关文件

- `templates/my-tasks.html` - 主要修改文件
- `models.py` - Task.to_dict() 方法
- `app.py` - API 端点
- `test_batch_simple.py` - 测试数据生成
- `test_fix_attachment.py` - 附件预览测试

## 验证清单

- [x] 附件缩略图正确显示
- [x] 点击缩略图打开预览
- [x] 大图在模态框中正确显示
- [x] 上一张/下一张导航正常
- [x] 计数器正确显示
- [x] 下载按钮可用
- [x] 键盘快捷键正常
- [x] 模态框可正常关闭
- [x] 支持多个附件
- [x] 兼容旧数据格式
