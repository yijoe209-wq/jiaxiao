#!/usr/bin/env python3
"""移除所有渐变色，改为日式极简风格"""

file_path = '/Volumes/data/vibe-coding-projects/jiaxiao/templates/simulate.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有渐变色按钮为黑色按钮
replacements = [
    # 登录按钮
    ('bg-gradient-to-r from-primary-500 to-primary-600 text-white py-4 rounded-xl font-bold text-base shadow-lg hover:shadow-xl hover:from-primary-600 hover:to-primary-700 transition-all text-center focus:ring-4 focus:ring-primary-500/50 focus:ring-offset-2',
     'bg-[#1a1a1a] hover:bg-[#333333] text-white py-4 rounded-xl font-bold text-base shadow-md hover:shadow-lg transition-all text-center focus:ring-4 focus:ring-gray-500/50 focus:ring-offset-2'),

    # 添加学生按钮
    ('bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold hover:from-primary-600 hover:to-primary-700 transition-all shadow-md',
     'bg-[#1a1a1a] hover:bg-[#333333] text-white rounded-xl font-semibold transition-all shadow-md'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已移除所有渐变色，改为日式极简风格")

# 验证
import re
gradients = re.findall(r'bg-gradient-to-r|from-primary-|to-primary-|from-cta-|to-cta-', content)
if gradients:
    print(f"⚠️ 仍有 {len(gradients)} 个渐变色引用")
else:
    print("✅ 所有渐变色已移除")
