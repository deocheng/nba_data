const ShootingHeatmap = (function() {
    const DISTANCE_RANGES = [
        { id: 'close', name: '篮下', min: 0, max: 2.4, color: '#ef4444' },
        { id: 'mid', name: '近距', min: 2.4, max: 4.9, color: '#f97316' },
        { id: 'long', name: '中距', min: 4.9, max: 7.3, color: '#eab308' },
        { id: 'three', name: '三分', min: 7.3, max: 10.7, color: '#3b82f6' },
    ];

    function init(containerId, playerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        loadShootingData(playerId).then(data => {
            renderShootingStats(container, data);
        }).catch(err => {
            console.warn('加载投篮数据失败:', err);
            renderShootingStats(container, getMockShootingData(playerId));
        });
    }

    async function loadShootingData(playerId) {
        try {
            const response = await fetch(`/api/player/shooting/${playerId}`);
            const result = await response.json();
            if (result.success) {
                return result.data;
            }
            throw new Error('数据加载失败');
        } catch {
            throw new Error('API不可用');
        }
    }

    function generateMockShots() {
        const shots = [];
        const totalShots = 200;
        
        for (let i = 0; i < totalShots; i++) {
            const range = Math.random();
            let dist, made;
            
            if (range < 0.25) {
                dist = 0.6 + Math.random() * 1.8;
                made = Math.random() > 0.25;
            } else if (range < 0.45) {
                dist = 2.4 + Math.random() * 2.5;
                made = Math.random() > 0.4;
            } else if (range < 0.60) {
                dist = 4.9 + Math.random() * 2.4;
                made = Math.random() > 0.5;
            } else {
                dist = 7.3 + Math.random() * 3.4;
                made = Math.random() > 0.55;
            }
            
            shots.push({ dist, made });
        }
        
        return shots;
    }

    function getMockShootingData(playerId) {
        const shots = generateMockShots();
        const fg = shots.filter(s => s.made).length;
        const fga = shots.length;

        const playerNames = {
            'victor_wembanyama': '维克托·文班亚马',
            'devin_vassell': '德文·瓦塞尔',
            'keldon_johnson': '凯尔登·约翰逊',
            'chet_holmgren': '切特·霍姆格伦',
            'dylan_harper': '迪伦·哈珀',
            'stephon_castle': '斯蒂芬·卡斯尔'
        };

        return {
            player_name: playerNames[playerId] || '维克托·文班亚马',
            season: '2024-25',
            shots: shots,
            overall: { fg, fga, fg_pct: fg / fga }
        };
    }

    function calculateRangeStats(shots) {
        return DISTANCE_RANGES.map(range => {
            const rangeShots = shots.filter(s => s.dist >= range.min && s.dist < range.max);
            const made = rangeShots.filter(s => s.made).length;
            const attempted = rangeShots.length;
            const percentage = attempted > 0 ? made / attempted : 0;
            
            return {
                ...range,
                made,
                attempted,
                percentage,
                proportion: shots.length > 0 ? attempted / shots.length : 0
            };
        });
    }

    function renderShootingStats(container, data) {
        const rangeStats = calculateRangeStats(data.shots);
        
        container.innerHTML = `
            <div class="shooting-stats-container">
                <div class="stats-header">
                    <h4>${data.player_name} - ${data.season}赛季投篮数据分析</h4>
                    <div class="overall-stat">
                        <span class="label">总命中率</span>
                        <span class="value">${(data.overall.fg_pct * 100).toFixed(1)}%</span>
                        <span class="detail">(${data.overall.fg}/${data.overall.fga})</span>
                    </div>
                </div>
                
                <div class="range-cards">
                    ${rangeStats.map(stats => `
                        <div class="range-card" style="border-color: ${stats.color}">
                            <div class="card-header">
                                <span class="range-name">${stats.name}</span>
                                <span class="range-distance">${stats.min}-${stats.max}m</span>
                            </div>
                            <div class="card-body">
                                <div class="percentage-display" style="color: ${stats.color}">
                                    ${(stats.percentage * 100).toFixed(1)}%
                                </div>
                                <div class="shot-count">
                                    ${stats.made} / ${stats.attempted} 命中
                                </div>
                                <div class="shot-proportion">
                                    占比 ${(stats.proportion * 100).toFixed(1)}%
                                </div>
                            </div>
                            <div class="progress-bar">
                                <div 
                                    class="progress-fill made" 
                                    style="width: ${stats.percentage * 100}%; background-color: ${stats.color}"
                                ></div>
                                <div 
                                    class="progress-fill missed" 
                                    style="width: ${(1 - stats.percentage) * 100}%"
                                ></div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div class="distribution-chart">
                    <h5>投篮距离分布</h5>
                    <div class="distribution-bars">
                        ${rangeStats.map(stats => `
                            <div class="dist-bar-item">
                                <span class="dist-label">${stats.name}</span>
                                <div class="dist-bar-container">
                                    <div 
                                        class="dist-bar" 
                                        style="width: ${stats.proportion * 100}%; background-color: ${stats.color}"
                                    ></div>
                                </div>
                                <span class="dist-value">${(stats.proportion * 100).toFixed(0)}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="detailed-stats">
                    <h5>详细数据</h5>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>距离范围</th>
                                <th>命中</th>
                                <th>出手</th>
                                <th>命中率</th>
                                <th>占比</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rangeStats.map(stats => `
                                <tr>
                                    <td><span class="color-dot" style="background-color: ${stats.color}"></span>${stats.min}-${stats.max}m</td>
                                    <td>${stats.made}</td>
                                    <td>${stats.attempted}</td>
                                    <td><span style="color: ${stats.color}">${(stats.percentage * 100).toFixed(1)}%</span></td>
                                    <td>${(stats.proportion * 100).toFixed(1)}%</td>
                                </tr>
                            `).join('')}
                            <tr class="total-row">
                                <td><strong>总计</strong></td>
                                <td><strong>${data.overall.fg}</strong></td>
                                <td><strong>${data.overall.fga}</strong></td>
                                <td><strong>${(data.overall.fg_pct * 100).toFixed(1)}%</strong></td>
                                <td><strong>100%</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    return {
        init,
        getMockShootingData
    };
})();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ShootingHeatmap;
}