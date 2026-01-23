// 浏览器兼容性检测和提示
// 可以在主要页面的 </body> 前添加

(function() {
    const userAgent = navigator.userAgent;
    const isIOS = /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
    const isAndroid = /Android/.test(userAgent);
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

    // iOS 用户检测
    if (isIOS && !isSafari) {
        // iOS 用户不在使用 Safari
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #fff3cd;
            color: #856404;
            padding: 12px;
            text-align: center;
            font-size: 14px;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-bottom: 2px solid #ffc107;
        `;
        message.innerHTML = `
            💡 提示：为了最佳体验，请使用
            <strong style="color:#000">Safari</strong>
            浏览器打开此页面
            <button onclick="this.parentElement.remove()"
                    style="margin-left:10px;padding:4px 12px;background:#856404;color:white;border:none;border-radius:4px;cursor:pointer;">
                知道了
            </button>
        `;
        document.body.appendChild(message);
    }

    // Android 用户：检测是否支持 PWA
    if (isAndroid && !('serviceWorker' in navigator)) {
        // 浏览器不支持 Service Worker
        console.log('当前浏览器不支持 PWA，建议使用 Chrome');
    }

    // 检测是否已安装
    window.addEventListener('appinstalled', () => {
        console.log('✅ PWA 已安装');
        // 可以隐藏"安装"按钮或显示欢迎消息
    });

    // 检测是否支持安装
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('✅ 支持 PWA 安装');
        // 可以显示"安装"按钮
    });
})();
