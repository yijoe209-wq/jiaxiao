# PWA 浏览器兼容性指南

## 📱 各平台支持情况

### Android（支持最好）

**完全支持的浏览器：**
- ✅ Chrome - 最佳体验
- ✅ Edge - 完整支持
- ✅ Firefox - 完整支持
- ✅ Opera - 完整支持
- ✅ Samsung Internet - 完整支持

**部分支持的浏览器：**
- ⚠️ UC 浏览器 - 支持，但体验可能不同
- ⚠️ QQ 浏览器 - 支持，但有限制
- ⚠️ 百度浏览器 - 支持，但有限制

**安装方法：**
1. 访问网站
2. 浏览器会自动提示"安装应用"或"添加到主屏幕"
3. 点击"安装"或"添加"

---

### iOS（限制较多）

**支持的浏览器：**
- ✅ **Safari** - iOS 上唯一完全支持 PWA 的浏览器

**不支持的浏览器：**
- ❌ Chrome for iOS - 不支持 PWA 安装（使用 Safari 内核）
- ❌ Firefox for iOS - 不支持 PWA 安装
- ❌ Edge for iOS - 不支持 PWA 安装
- ❌ 其他第三方浏览器 - 都不支持

**iOS 限制：**
- 只能通过 Safari 安装
- 安装后不能设为默认浏览器
- iOS 16.4+ 支持通知（需要用户授权）

**安装方法：**
1. 使用 Safari 访问网站
2. 点击底部"分享"按钮 📤
3. 向下滚动，找到"添加到主屏幕"
4. 点击"添加"

---

### 桌面端

**支持的浏览器：**
- ✅ Chrome (Windows, macOS, Linux)
- ✅ Edge (Windows, macOS)
- ✅ Opera (Windows, macOS)
- ⚠️ Firefox - 支持，但不提示安装
- ⚠️ Safari (macOS) - 支持，但不提示安装

---

## 🎯 用户建议

### Android 用户
**推荐使用 Chrome，但其他主流浏览器也可以！**
- Chrome、Edge、Firefox、Opera 都完全支持
- 国内浏览器（UC、QQ 等）也基本支持

### iOS 用户
**必须使用 Safari！**
- 只能在 Safari 中安装 PWA
- Chrome、Firefox 等不支持 PWA 安装

---

## 💡 优化建议

### 1. 添加浏览器检测
使用 `browser-check.js` 检测用户浏览器，并给出提示

### 2. 添加安装指引
在不同页面添加安装说明：
```html
<div id="install-prompt" style="display:none;">
    <h3>📱 安装到手机</h3>
    <p><strong>Android:</strong> 点击浏览器菜单 → "安装应用" 或 "添加到主屏幕"</p>
    <p><strong>iOS:</strong> 点击分享按钮 → "添加到主屏幕"</p>
</div>
```

### 3. 优化 iOS 体验
- 使用 Safari 特定的 meta 标签
- 提供清晰的安装指引

---

## 📊 市场覆盖率

### 全球
- **Android Chrome:** ~70% 市场份额 ✅
- **Android 其他浏览器:** ~20% 部分支持 ⚠️
- **iOS Safari:** ~25% 市场份额 ✅

### 中国
- **Android Chrome:** ~40% 市场份额 ✅
- **Android UC/QQ:** ~30% 部分支持 ⚠️
- **iOS Safari:** ~20% 市场份额 ✅
- **微信内置浏览器:** 不支持 PWA ❌

---

## ⚠️ 特殊情况

### 微信内置浏览器
**不支持 PWA 安装**
- 用户需要点击"在浏览器中打开"
- 然后才能安装 PWA

### 解决方案
在页面添加提示：
```html
<div id="wechat-tip" style="display:none;">
    <p>💡 点击右上角"..." → 在浏览器中打开</p>
</div>

<script>
// 检测微信浏览器
const isWechat = /micromessenger/i.test(navigator.userAgent);
if (isWechat) {
    document.getElementById('wechat-tip').style.display = 'block';
}
</script>
```

---

## 🎨 自定义安装提示

可以根据用户浏览器显示不同的安装指引：

```javascript
// 检测浏览器和平台
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
const isAndroid = /Android/.test(navigator.userAgent);
const isChrome = /Chrome/.test(navigator.userAgent);
const isSafari = /^((?!chrome).)*safari/i.test(navigator.userAgent);

// 显示对应的安装提示
if (isIOS && isSafari) {
    // iOS Safari: 显示"添加到主屏幕"指引
} else if (isAndroid && isChrome) {
    // Android Chrome: 显示"安装应用"指引
} else if (isAndroid) {
    // Android 其他浏览器: 显示通用安装指引
}
```

---

## 📖 参考资源

- [PWA Browser Support](https://webkit.org/blog/102407/pwa-support-on-ios-16-4/)
- [Can I Use Service Workers](https://caniuse.com/serviceworkers)
- [Can I Use Web App Manifest](https://caniuse.com/manifest)

---

## ✨ 总结

### Android
- ✅ **Chrome** - 推荐，最佳体验
- ✅ **Edge, Firefox, Opera** - 完全支持
- ⚠️ **UC, QQ** - 部分支持

### iOS
- ✅ **Safari** - 唯一选择
- ❌ **其他浏览器** - 不支持

### 建议
- 不要限制用户只能使用 Chrome
- 添加浏览器检测和友好提示
- 优化 Safari 体验（因为 iOS 必须用 Safari）
