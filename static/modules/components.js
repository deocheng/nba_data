/**
 * NBA Data Module - 组件模块
 * 提供可复用的UI组件
 */

const Components = {
    /**
     * 渲染导航栏
     */
    renderNavbar: (containerId, activePage = '') => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const navItems = [
            { id: 'home', label: '首页', icon: '🏠', href: '/' },
            { id: 'spurs', label: '马刺队', icon: '🏀', href: '/spurs' },
            { id: 'players', label: '球员', icon: '👤', href: '/players' },
            { id: 'stats', label: '数据', icon: '📊', href: '/stats' }
        ];

        const html = `
            <nav class="navbar">
                <div class="nav-container">
                    <div class="nav-brand">
                        <span class="nav-logo">🏀</span>
                        <span class="nav-title">NBA Data</span>
                    </div>
                    <ul class="nav-menu">
                        ${navItems.map(item => `
                            <li class="nav-item">
                                <a href="${item.href}" 
                                   class="nav-link ${activePage === item.id ? 'active' : ''}"
                                   data-page="${item.id}">
                                    <span class="nav-icon">${item.icon}</span>
                                    <span class="nav-text">${item.label}</span>
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </nav>
        `;

        container.innerHTML = html;
    },

    /**
     * 渲染球员卡片
     */
    renderPlayerCard: (player, options = {}) => {
        const {
            showStats = true,
            clickable = true,
            size = 'normal'  // small, normal, large
        } = options;

        const cardClass = `player-card player-card-${size}`;
        const clickAttr = clickable ? `onclick="window.location.href='/player-profile?id=${player.player_id}'"` : '';
        
        const statsHtml = showStats && player.career_summary ? `
            <div class="player-card-stats">
                <div class="stat">
                    <span class="stat-value">${Utils.formatNumber(player.career_summary.avg_points)}</span>
                    <span class="stat-label">场均得分</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${Utils.formatNumber(player.career_summary.avg_rebounds, 1)}</span>
                    <span class="stat-label">场均篮板</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${Utils.formatNumber(player.career_summary.avg_assists, 1)}</span>
                    <span class="stat-label">场均助攻</span>
                </div>
            </div>
        ` : '';

        return `
            <div class="${cardClass}" ${clickAttr} data-player-id="${player.player_id}">
                <div class="player-card-header">
                    <div class="player-avatar">
                        ${player.player_name ? player.player_name.charAt(0) : '?'}
                    </div>
                    <div class="player-info">
                        <h3 class="player-name">${player.player_name || '未知球员'}</h3>
                        <p class="player-meta">
                            ${player.position || ''} ${player.position ? '|' : ''} ${player.age ? player.age + '岁' : ''}
                        </p>
                    </div>
                </div>
                ${statsHtml}
            </div>
        `;
    },

    /**
     * 渲染球员卡片列表
     */
    renderPlayerCardList: (containerId, players, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!players || players.length === 0) {
            Utils.showEmpty(container, '暂无球员数据');
            return;
        }

        container.innerHTML = players.map(player => Components.renderPlayerCard(player, options)).join('');
    },

    /**
     * 渲染统计表格
     */
    renderStatsTable: (containerId, stats, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const { category = 'all', showLabels = true } = options;
        
        let fields = Object.entries(Constants.STAT_FIELDS);
        
        if (category !== 'all') {
            fields = fields.filter(([key, config]) => config.category === category);
        }

        const headerHtml = showLabels ? `
            <thead>
                <tr>
                    <th>统计项</th>
                    <th>数值</th>
                </tr>
            </thead>
        ` : '';

        const rowsHtml = fields.map(([key, config]) => {
            const value = stats[key];
            if (value === null || value === undefined) return '';
            
            return `
                <tr>
                    <td class="stat-label">${config.label}</td>
                    <td class="stat-value">${Utils.formatStat(value, key)}</td>
                </tr>
            `;
        }).join('');

        container.innerHTML = `
            <table class="stats-table">
                ${headerHtml}
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;
    },

    /**
     * 渲染赛季选择器
     */
    renderSeasonSelector: (containerId, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            currentSeason = Constants.DEFAULT_SEASON,
            seasons = ['2025-26', '2024-25', '2023-24', '2022-23'],
            onChange = null
        } = options;

        const html = `
            <div class="season-selector">
                <button class="season-btn prev" onclick="Components.changeSeason(-1)">◀</button>
                <select class="season-select" id="season-select" onchange="Components.onSeasonChange(this.value)">
                    ${seasons.map(season => `
                        <option value="${season}" ${season === currentSeason ? 'selected' : ''}>
                            ${season}
                        </option>
                    `).join('')}
                </select>
                <button class="season-btn next" onclick="Components.changeSeason(1)">▶</button>
            </div>
        `;

        container.innerHTML = html;

        if (onChange) {
            container.dataset.onChange = onChange;
        }
    },

    /**
     * 赛季切换事件
     */
    onSeasonChange: (season) => {
        const container = document.querySelector('.season-selector');
        if (container && container.dataset.onChange) {
            const callback = window[container.dataset.onChange];
            if (typeof callback === 'function') {
                callback(season);
            }
        }
    },

    /**
     * 切换赛季
     */
    changeSeason: (direction) => {
        const select = document.getElementById('season-select');
        if (!select) return;

        const options = Array.from(select.options);
        const currentIndex = options.findIndex(opt => opt.value === select.value);
        const newIndex = currentIndex + direction;

        if (newIndex >= 0 && newIndex < options.length) {
            select.selectedIndex = newIndex;
            Components.onSeasonChange(select.value);
        }
    },

    /**
     * 渲染比赛日志表格
     */
    renderGameLogTable: (containerId, games, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!games || games.length === 0) {
            Utils.showEmpty(container, '暂无比赛记录');
            return;
        }

        const html = `
            <table class="game-log-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>对手</th>
                        <th>结果</th>
                        <th>得分</th>
                        <th>篮板</th>
                        <th>助攻</th>
                        <th>时间</th>
                        <th>备注</th>
                    </tr>
                </thead>
                <tbody>
                    ${games.map(game => `
                        <tr class="${game.note ? 'has-note' : ''}">
                            <td>${Utils.formatDate(game.game_date)}</td>
                            <td>${game.opponent || '-'}</td>
                            <td class="${game.result === 'W' ? 'win' : 'loss'}">${game.result || '-'}</td>
                            <td>${Utils.formatNumber(game.points)}</td>
                            <td>${Utils.formatNumber(game.rebounds, 1)}</td>
                            <td>${Utils.formatNumber(game.assists, 1)}</td>
                            <td>${Utils.formatMinutes(game.minutes_played)}</td>
                            <td class="note">${game.note || ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    },

    /**
     * 渲染Tabs组件
     */
    renderTabs: (containerId, tabs, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const { activeTab = tabs[0]?.id, onChange = null } = options;

        const html = `
            <div class="tabs-container">
                <div class="tabs-header">
                    ${tabs.map(tab => `
                        <button class="tab-btn ${tab.id === activeTab ? 'active' : ''}" 
                                data-tab="${tab.id}"
                                onclick="Components.switchTab('${tab.id}')">
                            ${tab.icon || ''} ${tab.label}
                        </button>
                    `).join('')}
                </div>
                <div class="tabs-content">
                    ${tabs.map(tab => `
                        <div class="tab-panel ${tab.id === activeTab ? 'active' : ''}" id="tab-${tab.id}">
                            ${tab.content || ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;

        if (onChange) {
            container.dataset.onChange = onChange;
        }
    },

    /**
     * 切换Tab
     */
    switchTab: (tabId) => {
        const container = document.querySelector('.tabs-container');
        if (!container) return;

        // 更新按钮状态
        container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });

        // 更新面板显示
        container.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `tab-${tabId}`);
        });

        // 触发回调
        if (container.dataset.onChange) {
            const callback = window[container.dataset.onChange];
            if (typeof callback === 'function') {
                callback(tabId);
            }
        }
    },

    /**
     * 渲染荣誉列表
     */
    renderAwards: (containerId, awards) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!awards || awards.length === 0) {
            container.innerHTML = '<div class="empty-message">暂无荣誉</div>';
            return;
        }

        const html = awards.map(award => `
            <div class="award-item">
                <span class="award-icon">🏆</span>
                <span class="award-text">${award}</span>
            </div>
        `).join('');

        container.innerHTML = html;
    },

    /**
     * 渲染进度条
     */
    renderProgressBar: (containerId, value, max, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            label = '',
            color = 'primary',
            showValue = true,
            thresholds = []
        } = options;

        const percentage = (value / max) * 100;
        let dynamicColor = color;
        
        for (const threshold of thresholds) {
            if (percentage >= threshold.percent) {
                dynamicColor = threshold.color;
            }
        }

        const html = `
            <div class="progress-container">
                ${label ? `<span class="progress-label">${label}</span>` : ''}
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%; background-color: ${dynamicColor};"></div>
                </div>
                ${showValue ? `<span class="progress-value">${Utils.formatNumber(value)}</span>` : ''}
            </div>
        `;

        container.innerHTML = html;
    },

    /**
     * 渲染骨架屏 - 球员卡片
     */
    renderSkeletonPlayerCard: (count = 3) => {
        const cards = [];
        for (let i = 0; i < count; i++) {
            cards.push(`
                <div class="player-card skeleton-card">
                    <div class="player-card-header">
                        <div class="player-avatar skeleton-avatar"></div>
                        <div class="player-info">
                            <h3 class="player-name skeleton-text skeleton-text-sm"></h3>
                            <p class="player-meta skeleton-text skeleton-text-xs"></p>
                        </div>
                    </div>
                    <div class="player-card-stats">
                        <div class="stat">
                            <span class="stat-value skeleton-text skeleton-text-md"></span>
                            <span class="stat-label skeleton-text skeleton-text-xs"></span>
                        </div>
                        <div class="stat">
                            <span class="stat-value skeleton-text skeleton-text-md"></span>
                            <span class="stat-label skeleton-text skeleton-text-xs"></span>
                        </div>
                        <div class="stat">
                            <span class="stat-value skeleton-text skeleton-text-md"></span>
                            <span class="stat-label skeleton-text skeleton-text-xs"></span>
                        </div>
                    </div>
                </div>
            `);
        }
        return cards.join('');
    },

    /**
     * 渲染骨架屏 - 统计表格
     */
    renderSkeletonTable: (rows = 5, columns = 8) => {
        const cells = [];
        for (let i = 0; i < columns; i++) {
            cells.push('<th class="skeleton-text skeleton-text-xs"></th>');
        }
        
        const rowCells = [];
        for (let i = 0; i < columns; i++) {
            rowCells.push('<td class="skeleton-text skeleton-text-xs"></td>');
        }
        
        const rowsHtml = [];
        for (let i = 0; i < rows; i++) {
            rowsHtml.push(`<tr>${rowCells.join('')}</tr>`);
        }
        
        return `
            <table class="stats-table skeleton-table">
                <thead>
                    <tr>${cells.join('')}</tr>
                </thead>
                <tbody>
                    ${rowsHtml.join('')}
                </tbody>
            </table>
        `;
    },

    /**
     * 渲染骨架屏 - 图表
     */
    renderSkeletonChart: (type = 'radar') => {
        return `
            <div class="chart-container skeleton-chart">
                <div class="skeleton-chart-placeholder">
                    <div class="skeleton-circle ${type === 'radar' ? 'radar' : 'line'}"></div>
                </div>
            </div>
        `;
    },

    /**
     * 渲染骨架屏 - 数据卡片
     */
    renderSkeletonStatCard: (count = 6) => {
        const cards = [];
        for (let i = 0; i < count; i++) {
            cards.push(`
                <div class="stat-card skeleton-stat-card">
                    <span class="label skeleton-text skeleton-text-xs"></span>
                    <span class="value skeleton-text skeleton-text-lg"></span>
                </div>
            `);
        }
        return cards.join('');
    },

    /**
     * 显示加载状态
     */
    showLoading: (containerId, message = '加载中...') => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <span class="loading-text">${message}</span>
            </div>
        `;
    },

    /**
     * 隐藏加载状态
     */
    hideLoading: (containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
    }
};

window.Components = Components;
