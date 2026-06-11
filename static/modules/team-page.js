/**
 * NBA Data Module - 通用球队页面
 * 提供可复用的球队页面功能
 */

const TeamPage = {
    currentTeam: null,
    currentSeason: '2025-2026',
    teamData: null,
    seasons: [],
    chart: null,

    /**
     * 初始化球队页面
     */
    async init(teamAbbr) {
        this.currentTeam = teamAbbr.toUpperCase();
        
        // 获取球队配置
        const teamConfig = Constants.TEAMS[this.currentTeam];
        if (!teamConfig) {
            console.error('Team not found:', this.currentTeam);
            return;
        }

        // 应用球队主题
        this.applyTeamTheme(teamConfig);

        // 设置页面标题
        document.title = `${teamConfig.nameCn} - NBA数据`;

        // 加载数据
        await Promise.all([
            this.loadSeasons(),
            this.loadTeamInfo()
        ]);

        // 加载初始赛季数据
        await this.loadSeasonData(this.currentSeason);

        // 加载队史名宿
        this.loadLegends(teamConfig);

        // 绑定事件
        this.bindEvents();

        // 显示页面
        document.getElementById('team-page').style.display = 'block';
    },

    /**
     * 应用球队主题
     */
    applyTeamTheme(teamConfig) {
        const root = document.documentElement;
        
        // 设置CSS变量
        root.style.setProperty('--team-primary', teamConfig.primary);
        root.style.setProperty('--team-secondary', teamConfig.secondary);
        root.style.setProperty('--team-color', teamConfig.color);
        root.style.setProperty('--team-bg', teamConfig.secondary);
        
        // 使用Navbar组件
        Navbar.init(this.currentTeam, teamConfig);
        
        // 更新页面元素
        document.getElementById('team-championships').textContent = teamConfig.championships;
        document.getElementById('team-conference').textContent = teamConfig.conference === 'Western' ? '西部' : '东部';
        document.getElementById('team-division').textContent = this.getDivisionName(teamConfig.division);
    },

    /**
     * 获取分区中文名
     */
    getDivisionName(division) {
        const divisions = {
            'Pacific': '太平洋',
            'Southwest': '西南',
            'Northwest': '西北',
            'Atlantic': '大西洋',
            'Central': '中部',
            'Southeast': '东南'
        };
        return divisions[division] || division;
    },

    /**
     * 加载赛季列表
     */
    async loadSeasons() {
        try {
            const result = await API.getSeasons();
            if (result.success && result.data) {
                this.seasons = result.data;
                this.renderSeasonSelectors();
                return;
            }
        } catch (error) {
            console.log('Using default seasons:', error);
        }
        // 使用默认赛季
        this.seasons = ['2025-2026', '2024-2025', '2023-2024'];
        this.renderSeasonSelectors();
    },

    /**
     * 渲染赛季选择器
     */
    renderSeasonSelectors() {
        const scheduleSelect = document.getElementById('schedule-season-select');
        const statsSelector = document.getElementById('stats-season-selector');

        if (scheduleSelect) {
            scheduleSelect.innerHTML = this.seasons.map(season => 
                `<option value="${season}">${season}</option>`
            ).join('');
            scheduleSelect.value = this.currentSeason;
        }

        if (statsSelector) {
            statsSelector.innerHTML = this.seasons.map((season, index) => 
                `<button class="season-btn ${index === 0 ? 'active' : ''}" data-season="${season}">${season}</button>`
            ).join('');
        }
    },

    /**
     * 加载球队基本信息
     */
    async loadTeamInfo() {
        try {
            const result = await API.getTeamInfo(this.currentTeam);
            if (result.success && result.data) {
                this.teamData = result.data;
            }
        } catch (error) {
            console.error('Error loading team info:', error);
        }
    },

    /**
     * 加载赛季数据
     */
    async loadSeasonData(season) {
        this.currentSeason = season;
        
        await Promise.all([
            this.loadRoster(),
            this.loadSchedule(season),
            this.loadSeasonStats(season)
        ]);
    },

    /**
     * 加载球队阵容
     */
    async loadRoster() {
        const container = document.getElementById('roster-grid');
        if (!container) return;

        try {
            let players = [];
            
            // 尝试从API获取
            try {
                const result = await API.getTeamRoster(this.currentTeam);
                if (result.success && result.data) {
                    players = result.data;
                }
            } catch (error) {
                console.log('Using mock roster data');
            }

            // 如果没有数据，使用模拟数据
            if (players.length === 0) {
                players = this.getMockRoster();
            }

            container.innerHTML = players.map(player => this.renderPlayerCard(player)).join('');
        } catch (error) {
            console.error('Error loading roster:', error);
            container.innerHTML = '<div class="empty-message">暂无阵容数据</div>';
        }
    },

    /**
     * 获取模拟阵容数据
     */
    getMockRoster() {
        return [
            { number: '0', name: '球员A', position: 'PG', height: '188cm', weight: '85kg', experience: '3年', college: '杜克大学', player_id: 'player1' },
            { number: '1', name: '球员B', position: 'SG', height: '198cm', weight: '90kg', experience: '5年', college: '北卡大学', player_id: 'player2' },
            { number: '3', name: '球员C', position: 'SF', height: '203cm', weight: '95kg', experience: '2年', college: 'UCLA', player_id: 'player3' },
            { number: '11', name: '球员D', position: 'PF', height: '211cm', weight: '109kg', experience: '7年', college: '肯塔基大学', player_id: 'player4' },
            { number: '13', name: '球员E', position: 'C', height: '216cm', weight: '120kg', experience: '1年', college: '海外', player_id: 'player5' },
            { number: '22', name: '球员F', position: 'SG', height: '196cm', weight: '88kg', experience: '4年', college: '堪萨斯大学', player_id: 'player6' },
            { number: '23', name: '球员G', position: 'PG', height: '191cm', weight: '86kg', experience: '6年', college: '亚利桑那大学', player_id: 'player7' },
            { number: '34', name: '球员H', position: 'PF', height: '208cm', weight: '104kg', experience: '8年', college: '雪城大学', player_id: 'player8' }
        ];
    },

    /**
     * 渲染球员卡片
     */
    renderPlayerCard(player) {
        return `
            <div class="player-card" onclick="window.location.href='/player-profile?id=${player.player_id}'" style="cursor: pointer;">
                <div class="player-number">${player.number || '?'}</div>
                <div class="player-name">${player.name || player.player_name || '未知'}</div>
                <div class="player-position">${player.position || ''}</div>
                <div class="player-info">
                    ${player.height ? `<div>身高: ${player.height}</div>` : ''}
                    ${player.weight ? `<div>体重: ${player.weight}</div>` : ''}
                    ${player.experience ? `<div>经验: ${player.experience}</div>` : ''}
                    ${player.college ? `<div>大学: ${player.college}</div>` : ''}
                </div>
            </div>
        `;
    },

    /**
     * 加载赛程
     */
    async loadSchedule(season) {
        const container = document.getElementById('schedule-list');
        if (!container) return;

        try {
            let games = [];
            
            // 尝试从API获取
            try {
                const result = await API.getTeamSchedule(this.currentTeam, season);
                if (result.success && result.data && result.data.games) {
                    games = result.data.games;
                }
            } catch (error) {
                console.log('Using mock schedule data');
            }

            // 如果没有数据，使用模拟数据
            if (games.length === 0) {
                games = this.getMockSchedule();
            }

            container.innerHTML = games.map(game => this.renderGameItem(game)).join('');
        } catch (error) {
            console.error('Error loading schedule:', error);
            container.innerHTML = '<div class="empty-message">暂无赛程数据</div>';
        }
    },

    /**
     * 获取模拟赛程数据
     */
    getMockSchedule() {
        return [
            { Date: '2025-10-29', Opp: 'LAL', Tm: 108, Opp_1: 102 },
            { Date: '2025-10-31', Opp: 'GSW', Tm: 112, Opp_1: 105 },
            { Date: '2025-11-02', Opp: 'BOS', Tm: 98, Opp_1: 104 },
            { Date: '2025-11-04', Opp: 'MIA', Tm: 115, Opp_1: 108 },
            { Date: '2025-11-06', Opp: 'DEN', Tm: 102, Opp_1: 110 },
        ];
    },

    /**
     * 渲染比赛项
     */
    renderGameItem(game) {
        const teamScore = game.Tm !== undefined ? game.Tm : game.team_score;
        const oppScore = game.Opp_1 !== undefined ? game.Opp_1 : game.opp_score;
        const isWin = teamScore > oppScore;
        const opponent = game.Opp || game.opponent || '未知对手';
        const date = game.Date || game.game_date || '';

        return `
            <div class="game-item ${isWin ? 'win' : 'loss'}">
                <div class="game-score ${isWin ? 'win' : 'loss'}">
                    <span class="team-score">${teamScore}</span>
                    <span class="opp-score">${oppScore}</span>
                </div>
                <div class="game-info">
                    <div class="game-opponent">${opponent}</div>
                    <div class="game-date">${date}</div>
                </div>
            </div>
        `;
    },

    /**
     * 加载赛季统计
     */
    async loadSeasonStats(season) {
        const grid = document.getElementById('season-stats');
        if (!grid) return;

        try {
            let stats = null;
            
            // 尝试从API获取
            try {
                const result = await API.getTeamSeasonSummary(this.currentTeam, season);
                if (result.success && result.data) {
                    stats = result.data;
                }
            } catch (error) {
                console.log('Using mock season stats');
            }

            // 如果没有数据，使用模拟数据
            if (!stats) {
                stats = this.getMockSeasonStats();
            }

            grid.innerHTML = `
                <div class="stat-item"><div class="value">${stats.wins}</div><div class="label">胜场</div></div>
                <div class="stat-item"><div class="value">${stats.losses}</div><div class="label">负场</div></div>
                <div class="stat-item"><div class="value">${stats.win_rate}%</div><div class="label">胜率</div></div>
                <div class="stat-item"><div class="value">${stats.avg_points}</div><div class="label">场均得分</div></div>
                <div class="stat-item"><div class="value">${stats.avg_opp_points}</div><div class="label">场均失分</div></div>
                <div class="stat-item"><div class="value">${stats.avg_fg_pct}%</div><div class="label">投篮命中率</div></div>
                <div class="stat-item"><div class="value">${stats.avg_three_pct}%</div><div class="label">三分命中率</div></div>
                <div class="stat-item"><div class="value">${stats.avg_rebounds}</div><div class="label">场均篮板</div></div>
            `;

            // 渲染图表
            this.renderTrendChart(stats);
        } catch (error) {
            console.error('Error loading season stats:', error);
        }
    },

    /**
     * 获取模拟赛季统计数据
     */
    getMockSeasonStats() {
        return {
            wins: 55,
            losses: 27,
            win_rate: 67.1,
            avg_points: 112.5,
            avg_opp_points: 105.2,
            avg_fg_pct: 46.8,
            avg_three_pct: 36.2,
            avg_rebounds: 45.3,
            points_trend: [108, 112, 98, 115, 102, 105, 110],
            opp_points_trend: [102, 105, 104, 108, 110, 98, 103]
        };
    },

    /**
     * 渲染趋势图
     */
    renderTrendChart(stats) {
        const canvas = document.getElementById('trend-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // 销毁旧图表
        if (this.chart) {
            this.chart.destroy();
        }

        const pointsTrend = stats.points_trend || [];
        const oppPointsTrend = stats.opp_points_trend || [];
        const labels = pointsTrend.map((_, i) => `G${i + 1}`);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '得分',
                        data: pointsTrend,
                        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--team-primary') || '#FFD700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '对手得分',
                        data: oppPointsTrend,
                        borderColor: '#EF4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#ffffff' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#ffffff', maxTicksLimit: 10 }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#ffffff' } }
                }
            }
        });
    },

    /**
     * 加载队史名宿
     */
    loadLegends(teamConfig) {
        const container = document.getElementById('legends-grid');
        if (!container) return;

        const legends = teamConfig.legendaryPlayers || [];
        
        if (legends.length === 0) {
            container.innerHTML = '<div class="empty-message">暂无队史名宿数据</div>';
            return;
        }

        container.innerHTML = legends.map(legend => this.renderLegendCard(legend)).join('');
    },

    /**
     * 渲染传奇球员卡片
     */
    renderLegendCard(legend) {
        const stats = legend.stats || {};
        
        return `
            <div class="legend-card">
                <div class="legend-name">${legend.name}</div>
                <div class="legend-position">${Constants.POSITIONS[legend.position] || legend.position}</div>
                <div class="legend-years">${legend.years}</div>
                <div class="legend-honors">
                    ${(legend.honors || []).map(honor => `<span class="honor">${honor}</span>`).join('')}
                </div>
                <div class="legend-stats">
                    <div class="legend-stat">
                        <div class="value">${stats.ppg || '-'}</div>
                        <div class="label">得分</div>
                    </div>
                    <div class="legend-stat">
                        <div class="value">${stats.rpg || '-'}</div>
                        <div class="label">篮板</div>
                    </div>
                    <div class="legend-stat">
                        <div class="value">${stats.apg || '-'}</div>
                        <div class="label">助攻</div>
                    </div>
                    <div class="legend-stat">
                        <div class="value">${stats.bpg || stats.spg || '-'}</div>
                        <div class="label">${stats.bpg ? '盖帽' : '抢断'}</div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 绑定事件
     */
    bindEvents() {
        // Tab切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // 赛程赛季选择
        const scheduleSelect = document.getElementById('schedule-season-select');
        if (scheduleSelect) {
            scheduleSelect.addEventListener('change', (e) => {
                this.loadSchedule(e.target.value);
            });
        }

        // 统计赛季选择
        const statsSelector = document.getElementById('stats-season-selector');
        if (statsSelector) {
            statsSelector.addEventListener('click', (e) => {
                const btn = e.target.closest('.season-btn');
                if (btn) {
                    statsSelector.querySelectorAll('.season-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.loadSeasonStats(btn.dataset.season);
                }
            });
        }

        // 上/下赛季按钮
        document.getElementById('prev-season-btn')?.addEventListener('click', () => this.changeSeason(-1));
        document.getElementById('next-season-btn')?.addEventListener('click', () => this.changeSeason(1));
    },

    /**
     * 切换Tab
     */
    switchTab(tabId) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === tabId);
        });
    },

    /**
     * 切换赛季
     */
    changeSeason(direction) {
        const currentIndex = this.seasons.indexOf(this.currentSeason);
        const newIndex = currentIndex + direction;
        
        if (newIndex >= 0 && newIndex < this.seasons.length) {
            const newSeason = this.seasons[newIndex];
            const scheduleSelect = document.getElementById('schedule-season-select');
            if (scheduleSelect) {
                scheduleSelect.value = newSeason;
            }
            this.loadSchedule(newSeason);
        }
    }
};

window.TeamPage = TeamPage;
