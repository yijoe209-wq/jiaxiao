#!/bin/bash
# 从 SVG 生成 PWA 图标

echo "🎨 生成 PWA 图标..."

# 检查是否安装了 ImageMagick
if ! command -v convert &> /dev/null; then
    echo "❌ 需要安装 ImageMagick"
    echo "   macOS: brew install imagemagick"
    exit 1
fi

# 从 SVG 生成 PNG 图标
convert -background none -resize 192x192 capacitor-assets/icon.svg static/icon-192.png
convert -background none -resize 512x512 capacitor-assets/icon.svg static/icon-512.png

# 生成 favicon
convert -background none -resize 32x32 capacitor-assets/icon.svg static/favicon.ico
convert -background none -resize 180x180 capacitor-assets/icon.svg static/apple-touch-icon.png

echo "✅ 图标生成完成！"
echo "   - static/icon-192.png"
echo "   - static/icon-512.png"
echo "   - static/favicon.ico"
echo "   - static/apple-touch-icon.png"
