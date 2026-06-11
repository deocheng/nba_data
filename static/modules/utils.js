/**
 * NBA Data Module - 工具函数
 * 提供通用的数据处理和格式化函数
 */

const Utils = {
    /**
     * 空值处理
     */
    nullValue: (value, defaultValue = 0) => {
        if (value === null || value === undefined || value === '') {
            return defaultValue;
        }
        return value;
    },

    /**
     * 格式化数字
     */
    formatNumber: (value, decimals = 0) => {
        const num = Utils.nullValue(value, 0);
        return Number(num).toFixed(decimals);
    },

    /**
     * 格式化百分比
     */
    formatPercent: (value, decimals = 1) => {
        const num = Utils.nullValue(value, 0);
        return (Number(num) * 100).toFixed(decimals) + '%';
    },

    /**
     * 格式化时间（分钟）
     */
    formatMinutes: (value) => {
        const num = Utils.nullValue(value, 0);
        const minutes = Math.floor(num);
        const seconds = Math.round((num - minutes) * 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    },

    /**
     * 格式化统计数值（根据字段类型自动选择格式）
     */
    formatStat: (value, field, statFields = Constants.STAT_FIELDS) => {
        const fieldConfig = statFields[field];
        if (!fieldConfig) {
            return Utils.formatNumber(value);
        }

        switch (fieldConfig.format) {
            case 'percent':
                return Utils.formatPercent(value, fieldConfig.decimals || 1);
            case 'time':
                return Utils.formatMinutes(value);
            case 'decimal1':
                return Utils.formatNumber(value, 1);
            case 'decimal2':
                return Utils.formatNumber(value, 2);
            case 'number':
            default:
                return Utils.formatNumber(value);
        }
    },

    /**
     * 格式化日期
     */
    formatDate: (dateString, format = 'short') => {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
            return dateString;
        }
        
        if (format === 'short') {
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } else if (format === 'long') {
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        
        return date.toLocaleDateString();
    },

    /**
     * 计算赛季范围
     */
    getSeasonRange: (season) => {
        if (!season) return '';
        const [start, end] = season.split('-');
        return `${start}-${end}`;
    },

    /**
     * 获取球队缩写
     */
    getTeamAbbr: (fullName) => {
        for (const [abbr, info] of Object.entries(Constants.TEAMS)) {
            if (info.name.toLowerCase() === fullName.toLowerCase()) {
                return abbr;
            }
        }
        return fullName;
    },

    /**
     * 获取球队名称
     */
    getTeamName: (abbr) => {
        const team = Constants.TEAMS[abbr];
        return team ? team.name : abbr;
    },

    /**
     * 获取球队颜色
     */
    getTeamColor: (abbr) => {
        const team = Constants.TEAMS[abbr];
        return team ? team.color : '#666666';
    },

    /**
     * 获取位置中文名
     */
    getPositionName: (pos) => {
        return Constants.POSITIONS[pos] || pos;
    },

    /**
     * 防抖函数
     */
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     */
    throttle: (func, limit) => {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * 深拷贝
     */
    deepClone: (obj) => {
        return JSON.parse(JSON.stringify(obj));
    },

    /**
     * 判断是否为顶级（用于雷达图）
     */
    isTopTier: (value, threshold) => {
        return Utils.nullValue(value, 0) >= threshold;
    },

    /**
     * 计算雷达图数据
     */
    calculateRadarData: (stats, radarMetrics = Constants.RADAR_METRICS) => {
        const data = [];
        
        for (const [key, metric] of Object.entries(radarMetrics)) {
            let sum = 0;
            let count = 0;
            
            for (const field of metric.fields) {
                const value = stats[field];
                if (value !== null && value !== undefined) {
                    sum += Number(value);
                    count++;
                }
            }
            
            const avg = count > 0 ? sum / count : 0;
            const normalizedValue = Math.min(avg / metric.threshold * 100, 100);
            
            data.push({
                label: metric.label,
                value: avg,
                normalized: normalizedValue,
                isTopTier: avg >= metric.threshold,
                threshold: metric.threshold
            });
        }
        
        return data;
    },

    /**
     * 显示加载状态
     */
    showLoading: (element) => {
        if (!element) return;
        element.innerHTML = '<div class="loading-spinner">加载中...</div>';
        element.style.display = 'block';
    },

    /**
     * 隐藏加载状态
     */
    hideLoading: (element) => {
        if (!element) return;
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    /**
     * 显示错误信息
     */
    showError: (element, message) => {
        if (!element) return;
        element.innerHTML = `<div class="error-message">${message}</div>`;
        element.style.display = 'block';
    },

    /**
     * 显示空数据提示
     */
    showEmpty: (element, message = '暂无数据') => {
        if (!element) return;
        element.innerHTML = `<div class="empty-message">${message}</div>`;
        element.style.display = 'block';
    },

    /**
     * 获取URL参数
     */
    getUrlParam: (name) => {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    },

    /**
     * 设置URL参数
     */
    setUrlParam: (name, value) => {
        const url = new URL(window.location);
        url.searchParams.set(name, value);
        window.history.pushState({}, '', url);
    },

    /**
     * 生成球员ID
     */
    generatePlayerId: (name, teamAbbr = 'SAS') => {
        const normalized = name.toLowerCase()
            .replace(/\s+/g, '_')
            .replace(/[^a-z0-9_]/g, '');
        return `${teamAbbr.toLowerCase()}_${normalized}`;
    }
};

window.Utils = Utils;
