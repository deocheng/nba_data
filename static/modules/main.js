/**
 * NBA Data Module - 主入口文件
 * 按正确顺序加载所有模块
 */

// 加载顺序很重要：1. 常量 → 2. 工具函数 → 3. API → 4. 组件 → 5. 图表

// 动态加载模块
const ModuleLoader = {
    basePath: '/static/modules/',
    
    loadScript: (src) => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    },
    
    loadCSS: (href) => {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = reject;
            document.head.appendChild(link);
        });
    },
    
    async loadAll: async () => {
        try {
            // 加载样式
            await ModuleLoader.loadCSS('/static/styles/common.css');
            
            // 按顺序加载JS模块
            await ModuleLoader.loadScript('/static/modules/constants.js');
            await ModuleLoader.loadScript('/static/modules/utils.js');
            await ModuleLoader.loadScript('/static/modules/api.js');
            await ModuleLoader.loadScript('/static/modules/components.js');
            await ModuleLoader.loadScript('/static/modules/charts.js');
            await ModuleLoader.loadScript('/static/modules/lazy-load.js');
            
            console.log('NBA Data Module loaded successfully');
            
            // 触发加载完成事件
            window.dispatchEvent(new Event('NBADataModuleLoaded'));
            
        } catch (error) {
            console.error('Failed to load NBA Data Module:', error);
        }
    }
};

// 自动加载
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ModuleLoader.loadAll());
} else {
    ModuleLoader.loadAll();
}

// 导出加载器供手动调用
window.NBADataModule = {
    load: () => ModuleLoader.loadAll(),
    Components,
    Charts,
    Utils,
    Constants
};
