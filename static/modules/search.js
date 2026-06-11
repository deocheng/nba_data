/**
 * NBA Data Module - 搜索模块
 * 提供球员搜索和自动完成功能
 */

const Search = {
    /**
     * 搜索配置
     */
    config: {
        debounceDelay: 300,
        maxResults: 8,
        minInputLength: 2
    },

    /**
     * 初始化搜索组件
     */
    init: (inputSelector, resultsSelector, options = {}) => {
        const input = document.querySelector(inputSelector);
        const resultsContainer = document.querySelector(resultsSelector);
        
        if (!input || !resultsContainer) return;

        const {
            onSelect = null,
            placeholder = '搜索球员...',
            dataSource = null
        } = options;

        input.placeholder = placeholder;
        
        // 防抖搜索
        const debouncedSearch = Utils.debounce((query) => {
            Search.performSearch(query, resultsContainer, dataSource, onSelect);
        }, Search.config.debounceDelay);

        // 输入事件
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length >= Search.config.minInputLength) {
                debouncedSearch(query);
            } else {
                Search.hideResults(resultsContainer);
            }
        });

        // 点击外部关闭
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
                Search.hideResults(resultsContainer);
            }
        });

        // 键盘导航
        input.addEventListener('keydown', (e) => {
            Search.handleKeydown(e, resultsContainer);
        });
    },

    /**
     * 执行搜索
     */
    performSearch: async (query, resultsContainer, dataSource, onSelect) => {
        let results = [];

        if (dataSource && typeof dataSource === 'function') {
            results = await dataSource(query);
        } else {
            results = Search.searchPlayers(query);
        }

        results = results.slice(0, Search.config.maxResults);
        Search.displayResults(results, resultsContainer, onSelect);
    },

    /**
     * 搜索球员（本地数据）
     */
    searchPlayers: (query) => {
        const players = [
            { id: 'victor_wembanyama', name: '维克托·文班亚马', team: '马刺', position: 'C' },
            { id: 'devin_vassell', name: '德文·瓦塞尔', team: '马刺', position: 'SG' },
            { id: 'keldon_johnson', name: '凯尔登·约翰逊', team: '马刺', position: 'SF' },
            { id: 'chet_holmgren', name: '切特·霍姆格伦', team: '雷霆', position: 'C' },
            { id: 'dylan_harper', name: '迪伦·哈珀', team: '马刺', position: 'PG' },
            { id: 'stephon_castle', name: '斯蒂芬·卡斯尔', team: '马刺', position: 'PG' },
            { id: 'lebron_james', name: '勒布朗·詹姆斯', team: '湖人', position: 'SF' },
            { id: 'kevin_durant', name: '凯文·杜兰特', team: '太阳', position: 'PF' },
            { id: 'stephen_curry', name: '斯蒂芬·库里', team: '勇士', position: 'PG' },
            { id: 'giannis_antetokounmpo', name: '扬尼斯·阿德托昆博', team: '雄鹿', position: 'PF' },
            { id: 'nikola_jokic', name: '尼古拉·约基奇', team: '掘金', position: 'C' },
            { id: 'joel_embiid', name: '乔尔·恩比德', team: '76人', position: 'C' },
            { id: 'luka_doncic', name: '卢卡·东契奇', team: '独行侠', position: 'PG' },
            { id: 'jayson_tatum', name: '杰森·塔图姆', team: '凯尔特人', position: 'SF' },
            { id: 'shai_gilgeous-alexander', name: '谢伊·吉尔杰斯-亚历山大', team: '雷霆', position: 'PG' }
        ];

        const lowerQuery = query.toLowerCase();
        return players.filter(p => 
            p.name.toLowerCase().includes(lowerQuery) ||
            p.team.toLowerCase().includes(lowerQuery) ||
            p.position.toLowerCase().includes(lowerQuery)
        );
    },

    /**
     * 显示搜索结果
     */
    displayResults: (results, container, onSelect) => {
        if (results.length === 0) {
            container.innerHTML = `
                <div class="search-no-results">
                    <span>未找到匹配的球员</span>
                </div>
            `;
            container.style.display = 'block';
            return;
        }

        const html = results.map((player, index) => `
            <div class="search-result-item" 
                 data-player-id="${player.id}" 
                 data-index="${index}"
                 onclick="Search.selectResult(this, ${JSON.stringify(player)}, ${typeof onSelect === 'function' ? 'true' : 'false'})">
                <div class="search-result-avatar">${player.name.charAt(0)}</div>
                <div class="search-result-info">
                    <div class="search-result-name">${player.name}</div>
                    <div class="search-result-meta">${player.team} | ${player.position}</div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
        container.style.display = 'block';
    },

    /**
     * 隐藏搜索结果
     */
    hideResults: (container) => {
        container.style.display = 'none';
        container.innerHTML = '';
    },

    /**
     * 选择结果
     */
    selectResult: (element, player, hasCallback) => {
        // 更新输入框
        const input = document.querySelector('.search-input');
        if (input) {
            input.value = player.name;
        }

        // 隐藏结果
        const container = element.parentElement;
        Search.hideResults(container);

        // 触发回调
        if (hasCallback) {
            window.location.href = `/player-profile?id=${player.id}`;
        }
    },

    /**
     * 键盘导航处理
     */
    handleKeydown: (e, container) => {
        const items = container.querySelectorAll('.search-result-item');
        if (items.length === 0) return;

        const activeIndex = Array.from(items).findIndex(item => item.classList.contains('active'));

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                items[activeIndex < 0 ? 0 : Math.min(activeIndex + 1, items.length - 1)].classList.add('active');
                if (activeIndex >= 0) items[activeIndex].classList.remove('active');
                break;
            case 'ArrowUp':
                e.preventDefault();
                items[activeIndex <= 0 ? items.length - 1 : activeIndex - 1].classList.add('active');
                if (activeIndex >= 0) items[activeIndex].classList.remove('active');
                break;
            case 'Enter':
                e.preventDefault();
                const selected = items[activeIndex >= 0 ? activeIndex : 0];
                if (selected) selected.click();
                break;
            case 'Escape':
                Search.hideResults(container);
                break;
        }
    },

    /**
     * 渲染搜索框组件
     */
    renderSearchBox: (containerId, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const { placeholder = '搜索球员...' } = options;

        container.innerHTML = `
            <div class="search-container">
                <input type="text" class="search-input" placeholder="${placeholder}" autocomplete="off">
                <button class="search-btn" onclick="Search.triggerSearch()">
                    <span class="search-icon">🔍</span>
                </button>
                <div class="search-results"></div>
            </div>
        `;

        // 初始化搜索功能
        Search.init('.search-input', '.search-results', {
            onSelect: true
        });
    },

    /**
     * 触发搜索
     */
    triggerSearch: () => {
        const input = document.querySelector('.search-input');
        if (input && input.value.trim().length >= Search.config.minInputLength) {
            const event = new Event('input');
            input.dispatchEvent(event);
        }
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Search;
} else {
    window.Search = Search;
}