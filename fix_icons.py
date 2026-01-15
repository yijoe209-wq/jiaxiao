#!/usr/bin/env python3
"""批量替换 Font Awesome 图标为 Heroicons"""

import re

file_path = '/Volumes/data/vibe-coding-projects/jiaxiao/templates/simulate.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 图标替换映射
replacements = [
    # Line 341: 灯泡图标
    (r'<i class="fas fa-lightbulb text-primary-500 mr-2 text-lg animate-pulse-slow"></i>',
     '<svg class="w-5 h-5 text-[#1a1a1a] mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>'),

    # Line 384: 锁图标
    (r'<i class="fas fa-lock text-primary-500 text-3xl"></i>',
     '<svg class="w-12 h-12 text-[#1a1a1a]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>'),

    # Line 390: 登录图标
    (r'<i class="fas fa-sign-in-alt mr-2"></i>立即登录',
     '<svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>立即登录'),

    # Line 448: 新增学生图标
    (r'<i class="fas fa-user-plus text-primary-500 mr-2"></i>新增学生',
     '<svg class="w-4 h-4 inline-block mr-2 text-[#1a1a1a]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>新增学生'),

    # Line 451: 关闭图标
    (r'<i class="fas fa-times text-xl"></i>',
     '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>'),

    # Line 486: 加号图标
    (r'<i class="fas fa-plus mr-2"></i>添加',
     '<svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>添加'),

    # Line 547: 成功图标
    (r'<i class="fas fa-check-circle mr-2"></i>',
     '<svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'),

    # Line 670: AI 图标
    (r'<i class="fas fa-magic mr-2 text-lg"></i>',
     '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>'),
]

# 执行替换
for old, new in replacements:
    content = content.replace(old, new)

# 保存文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Font Awesome 图标已全部替换为 Heroicons")

# 验证是否还有 Font Awesome
remaining = re.findall(r'<i class="fa[srl] fa-[\w-]+[\s\S]*?</i>', content)
if remaining:
    print(f"⚠️ 仍有 {len(remaining)} 个 Font Awesome 图标未替换:")
    for icon in remaining:
        print(f"  - {icon[:50]}")
else:
    print("✅ 所有 Font Awesome 图标已成功替换")
