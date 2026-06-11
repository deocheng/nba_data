/**
 * NBA Data Module - 懒加载模块
 * 提供图片懒加载和通用懒加载功能
 */

const LazyLoad = {
    /**
     * 初始化图片懒加载
     */
    init: (options = {}) => {
        const {
            selector = '.lazy-image',
            rootMargin = '100px',
            threshold = 0.1
        } = options;

        // 检查浏览器是否支持Intersection Observer
        if (!('IntersectionObserver' in window)) {
            LazyLoad.fallbackLoad();
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        LazyLoad.loadImage(img);
                        observer.unobserve(img);
                    }
                });
            },
            { rootMargin, threshold }
        );

        // 观察所有懒加载图片
        document.querySelectorAll(selector).forEach(img => {
            observer.observe(img);
        });
    },

    /**
     * 加载单张图片
     */
    loadImage: (img) => {
        const src = img.getAttribute('data-src');
        const srcset = img.getAttribute('data-srcset');

        if (!src) return;

        const image = new Image();
        
        if (srcset) {
            image.srcset = srcset;
        }
        image.src = src;

        image.onload = () => {
            img.src = src;
            if (srcset) img.srcset = srcset;
            img.classList.add('loaded');
        };

        image.onerror = () => {
            img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"%3E%3Crect fill="%23333" width="100" height="100"/%3E%3Ctext fill="%23666" font-family="sans-serif" font-size="12" x="50%" y="50%" text-anchor="middle" dominant-baseline="middle"%3EImage%3C/text%3E%3C/svg%3E';
            img.classList.add('loaded');
        };
    },

    /**
     * 降级方案：不支持Intersection Observer时使用
     */
    fallbackLoad: () => {
        document.querySelectorAll('.lazy-image').forEach(img => {
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.classList.add('loaded');
            }
        });
    },

    /**
     * 懒加载组件
     */
    renderLazyImage: (options = {}) => {
        const {
            src,
            alt = '',
            className = '',
            width = '100%',
            height = 'auto'
        } = options;

        return `
            <img 
                class="lazy-image ${className}"
                data-src="${src}"
                alt="${alt}"
                style="width: ${width}; height: ${height};"
            />
        `;
    }
};

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    LazyLoad.init();
});

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LazyLoad;
} else {
    window.LazyLoad = LazyLoad;
}