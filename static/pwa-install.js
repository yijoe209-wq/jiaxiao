// PWA Service Worker 注册脚本
// 在所有页面的 </body> 前添加此脚本

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('Service Worker 注册成功:', registration.scope);

                // 检查更新
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // 有新版本可用
                            console.log('PWA: 发现新版本，请刷新页面');
                            // 可以在这里添加"刷新"按钮
                        }
                    });
                });
            })
            .catch(error => {
                console.log('Service Worker 注册失败:', error);
            });
    });
}

// 检测是否在 PWA 模式下运行
window.addEventListener('appinstalled', () => {
    console.log('PWA: 应用已安装');
    // 可以隐藏"安装"按钮或显示欢迎消息
});
