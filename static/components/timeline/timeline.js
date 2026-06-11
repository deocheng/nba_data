/**
 * 时间轴组件 - 纯JavaScript模块（优化版）
 * 用于展示球队历史时间轴数据
 */

class TimelineComponent {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Timeline: Container not found:', containerId);
            return;
        }

        this.options = {
            apiBase: options.apiBase || this.getApiBase(),
            defaultTeam: options.defaultTeam || 'CHI',
            onTeamChange: options.onTeamChange || null,
            onFilterChange: options.onFilterChange || null
        };

        this.currentTeam = this.options.defaultTeam;
        this.currentFilter = 'all';
        
        this.init();
    }

    getApiBase() {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:8000';
        }
        return '';
    }

    init() {
        this.loadStyles();
        this.renderTemplate();
        this.bindEvents();
        this.loadTimeline();
    }

    loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/components/timeline/timeline.css';
        if (!document.querySelector(`link[href="${link.href}"]`)) {
            document.head.appendChild(link);
        }
    }

    renderTemplate() {
        this.container.innerHTML = `
            <div class="timeline-header">
                <h2 class="timeline-title">🏀 球队历史时间轴</h2>
                <div class="team-selector">
                    <button class="team-btn active" data-team="CHI">芝加哥公牛</button>
                    <button class="team-btn" data-team="LAL">洛杉矶湖人</button>
                    <button class="team-btn" data-team="BOS">波士顿凯尔特人</button>
                    <button class="team-btn" data-team="SAS">圣安东尼奥马刺</button>
                    <button class="team-btn" data-team="HOU">休斯顿火箭</button>
                </div>
                <div class="filter-bar">
                    <button class="filter-btn active" data-filter="all">全部年份</button>
                    <button class="filter-btn" data-filter="champion">总冠军年份</button>
                    <button class="filter-btn" data-filter="playoff">季后赛年份</button>
                </div>
            </div>
            <div class="timeline" id="timeline">
                <div class="loading">
                    <div class="loading-spinner"></div>
                    <p>加载中...</p>
                </div>
            </div>
        `;
    }

    bindEvents() {
        this.container.querySelectorAll('.team-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleTeamChange(e.target);
            });
        });

        this.container.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFilterChange(e.target);
            });
        });
    }

    handleTeamChange(btn) {
        this.container.querySelectorAll('.team-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentTeam = btn.dataset.team;
        this.loadTimeline();

        if (this.options.onTeamChange) {
            this.options.onTeamChange(this.currentTeam);
        }
    }

    handleFilterChange(btn) {
        this.container.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentFilter = btn.dataset.filter;
        this.loadTimeline();

        if (this.options.onFilterChange) {
            this.options.onFilterChange(this.currentFilter);
        }
    }

    async loadTimeline() {
        const timeline = this.container.querySelector('#timeline');
        timeline.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>
        `;

        try {
            const response = await fetch(`${this.options.apiBase}/api/team_timeline/${this.currentTeam}`);
            const data = await response.json();
            this.renderTimeline(data);
        } catch (error) {
            console.error('Timeline: Load error', error);
            timeline.innerHTML = `
                <div class="loading">
                    <p style="color: #ff6b6b;">加载失败: ${error.message}</p>
                </div>
            `;
        }
    }

    renderTimeline(data) {
        const timeline = this.container.querySelector('#timeline');
        
        let items = data;
        
        if (this.currentFilter === 'champion') {
            items = items.filter(item => item.champion);
        }

        if (items.length === 0) {
            timeline.innerHTML = `
                <div class="loading">
                    <p style="color: #aaa;">暂无数据</p>
                </div>
            `;
            return;
        }

        timeline.innerHTML = items.map(item => this.renderTimelineItem(item)).join('');
    }

    renderTimelineItem(item) {
        const wins = item.wins || 0;
        const losses = item.losses || 0;
        const winRate = item.win_rate || 0;
        const players = this.parsePlayers(item.notable_players);
        const coaches = this.getCoaches(item.year);

        return `
            <div class="timeline-item ${item.champion ? 'champion' : ''}">
                <div class="timeline-node">${item.year}</div>
                
                <!-- 战绩卡片 - 左侧 -->
                <div class="timeline-record">
                    <div class="record-header">
                        <div class="record-season">${item.year - 1}-${item.year} 赛季</div>
                        <div class="record-title">常规赛战绩</div>
                    </div>
                    
                    <div class="record-stats">
                        <div class="stat-item">
                            <div class="stat-value">${wins}</div>
                            <div class="stat-label">胜场</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${losses}</div>
                            <div class="stat-label">负场</div>
                        </div>
                    </div>
                    
                    <div class="record-winrate">
                        <div class="winrate-bar">
                            <div class="winrate-fill" style="width: ${winRate}%"></div>
                        </div>
                        <div class="winrate-text">${winRate}%</div>
                    </div>
                    
                    <div class="honors">
                        ${item.champion ? `
                            <div class="honor-badge champion">
                                🏆 NBA总冠军
                            </div>
                        ` : ''}
                        ${item.milestones ? `
                            <div class="honor-badge">
                                ⭐ ${item.milestones}
                            </div>
                        ` : ''}
                        ${this.getPlayoffResult(item.year)}
                    </div>
                </div>
                
                <!-- 阵容卡片 - 右侧 -->
                <div class="timeline-roster">
                    <div class="roster-header">
                        <span class="roster-icon">👥</span>
                        <span class="roster-title">主要阵容</span>
                    </div>
                    
                    <div class="players-grid">
                        ${players.map(player => this.renderPlayerCard(player)).join('')}
                    </div>
                    
                    <div class="coach-info">
                        <div class="coach-avatar">${coaches.name.charAt(0)}</div>
                        <div class="coach-details">
                            <div class="coach-name">${coaches.name}</div>
                            <div class="coach-title">主教练</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    parsePlayers(playersString) {
        if (!playersString) return [];
        
        return playersString.split(',').map(p => {
            const name = p.trim();
            if (!name) return null;
            
            return {
                name: name,
                initials: name.split(' ').map(n => n.charAt(0)).join('').substring(0, 2),
                stats: this.getPlayerStats(name)
            };
        }).filter(p => p !== null).slice(0, 6);
    }

    getPlayerStats(name) {
        const stats = {
            'Michael Jordan': { pts: 31.5, reb: 6.3, ast: 5.4 },
            'Scottie Pippen': { pts: 17.7, reb: 6.7, ast: 5.0 },
            'Tim Duncan': { pts: 19.0, reb: 10.8, ast: 3.0 },
            'Manu Ginobili': { pts: 13.3, reb: 3.8, ast: 3.7 },
            'Tony Parker': { pts: 15.5, reb: 2.7, ast: 5.6 },
            'Kobe Bryant': { pts: 25.0, reb: 5.2, ast: 4.7 },
            'LeBron James': { pts: 27.2, reb: 7.5, ast: 7.3 },
            'Magic Johnson': { pts: 19.5, reb: 7.2, ast: 11.2 },
            'Kareem Abdul-Jabbar': { pts: 24.6, reb: 11.2, ast: 3.6 },
            'Hakeem Olajuwon': { pts: 21.8, reb: 11.1, ast: 2.5 },
            'James Harden': { pts: 25.1, reb: 5.3, ast: 6.7 },
            'Yao Ming': { pts: 19.0, reb: 9.2, ast: 1.6 },
            'Kawhi Leonard': { pts: 19.2, reb: 6.4, ast: 2.9 },
            'LaMarcus Aldridge': { pts: 19.5, reb: 8.3, ast: 2.0 },
            'David Robinson': { pts: 21.1, reb: 10.6, ast: 2.5 },
            'George Gervin': { pts: 25.6, reb: 4.2, ast: 2.8 },
            'Larry Bird': { pts: 24.3, reb: 10.0, ast: 6.3 },
            'Bill Russell': { pts: 15.1, reb: 22.5, ast: 4.3 },
            'Wilt Chamberlain': { pts: 30.1, reb: 22.9, ast: 4.4 },
            'Kevin Garnett': { pts: 17.8, reb: 10.0, ast: 3.7 },
            'Paul Pierce': { pts: 19.7, reb: 5.6, ast: 3.5 },
            'Ray Allen': { pts: 18.9, reb: 4.1, ast: 3.4 }
        };

        return stats[name] || { pts: 15.0, reb: 5.0, ast: 3.0 };
    }

    renderPlayerCard(player) {
        return `
            <div class="player-card">
                <div class="player-avatar">
                    ${player.initials}
                </div>
                <div class="player-info">
                    <div class="player-name">${player.name}</div>
                    <div class="player-stats">
                        <span class="pts">${player.stats.pts}分</span>
                        <span>${player.stats.reb}板</span>
                        <span>${player.stats.ast}助</span>
                    </div>
                </div>
            </div>
        `;
    }

    getCoaches(year) {
        const coaches = {
            'CHI': {
                default: { name: 'Phil Jackson', years: '1989-1998' },
                1998: { name: 'Tim Floyd', years: '1998-2001' },
                2001: { name: 'Bill Berry', years: '2001-2003' }
            },
            'LAL': {
                default: { name: 'Phil Jackson', years: '1999-2004' },
                2004: { name: 'Mike D\'Antoni', years: '2004-2005' },
                2005: { name: 'Phil Jackson', years: '2005-2011' },
                2011: { name: 'Mike Brown', years: '2011-2012' },
                2012: { name: 'Mike D\'Antoni', years: '2012-2014' },
                2014: { name: 'Byron Scott', years: '2014-2016' },
                2016: { name: 'Luke Walton', years: '2016-2019' },
                2019: { name: 'Frank Vogel', years: '2019-2022' },
                2022: { name: 'Darvin Ham', years: '2022-2024' }
            },
            'SAS': {
                default: { name: 'Gregg Popovich', years: '1996-2023' },
                2023: { name: 'Mike Budenholzer', years: '2023-2024' }
            },
            'BOS': {
                default: { name: 'Red Auerbach', years: '1950-1966' },
                1997: { name: 'Rick Pitino', years: '1997-2001' },
                2001: { name: 'Jim O\'Brien', years: '2001-2004' },
                2004: { name: 'Doc Rivers', years: '2004-2013' },
                2013: { name: 'Brad Stevens', years: '2013-2021' },
                2021: { name: 'Joe Mazzulla', years: '2021-现在' }
            },
            'HOU': {
                default: { name: 'Rudy Tomjanovich', years: '1992-2003' },
                2003: { name: 'Jeff Van Gundy', years: '2003-2007' },
                2007: { name: 'Rick Adelman', years: '2007-2011' },
                2011: { name: 'Kevin McHale', years: '2011-2015' },
                2015: { name: 'Mike D\'Antoni', years: '2016-2020' },
                2020: { name: 'Stephen Silas', years: '2020-2023' },
                2023: { name: 'Ime Udoka', years: '2023-2024' }
            }
        };

        const teamCoaches = coaches[this.currentTeam] || { default: { name: '待定', years: '' } };
        
        const years = Object.keys(teamCoaches)
            .filter(k => k !== 'default')
            .map(k => parseInt(k))
            .sort((a, b) => a - b);
        
        for (let i = years.length - 1; i >= 0; i--) {
            if (year >= years[i]) {
                return teamCoaches[years[i]];
            }
        }
        
        return teamCoaches.default;
    }

    getPlayoffResult(year) {
        const playoffResults = {
            'CHI': {
                1991: '🏆 总决赛冠军',
                1992: '🏆 总决赛冠军',
                1993: '🏆 总决赛冠军',
                1996: '🏆 总决赛冠军',
                1997: '🏆 总决赛冠军',
                1998: '🏆 总决赛冠军'
            },
            'SAS': {
                1999: '🏆 总决赛冠军',
                2003: '🏆 总决赛冠军',
                2005: '🏆 总决赛冠军',
                2007: '🏆 总决赛冠军',
                2014: '🏆 总决赛冠军'
            }
        };

        const teamResults = playoffResults[this.currentTeam] || {};
        const result = teamResults[year];
        
        if (result) {
            return `<div class="honor-badge champion">${result}</div>`;
        }
        
        return '';
    }

    setTeam(teamId) {
        const btn = this.container.querySelector(`[data-team="${teamId}"]`);
        if (btn) {
            this.handleTeamChange(btn);
        }
    }

    setFilter(filter) {
        const btn = this.container.querySelector(`[data-filter="${filter}"]`);
        if (btn) {
            this.handleFilterChange(btn);
        }
    }

    refresh() {
        this.loadTimeline();
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('timeline-container')) {
        window.timeline = new TimelineComponent('timeline-container');
    }
});

// 导出为全局变量
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimelineComponent;
}