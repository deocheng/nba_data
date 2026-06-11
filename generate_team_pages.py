import os

TEAMS = [
    {"abbr": "ATL", "name": "亚特兰大老鹰", "name_en": "Atlanta Hawks", "motto": "True to Atlanta", "champs": 1},
    {"abbr": "BOS", "name": "波士顿凯尔特人", "name_en": "Boston Celtics", "motto": "Banner 18", "champs": 18},
    {"abbr": "BKN", "name": "布鲁克林篮网", "name_en": "Brooklyn Nets", "motto": "The Bridge", "champs": 2},
    {"abbr": "CHA", "name": "夏洛特黄蜂", "name_en": "Charlotte Hornets", "motto": "Buzz City", "champs": 0},
    {"abbr": "CHI", "name": "芝加哥公牛", "name_en": "Chicago Bulls", "motto": "City of Champions", "champs": 6},
    {"abbr": "CLE", "name": "克利夫兰骑士", "name_en": "Cleveland Cavaliers", "motto": "All For One", "champs": 1},
    {"abbr": "DAL", "name": "达拉斯独行侠", "name_en": "Dallas Mavericks", "motto": "MFFL", "champs": 1},
    {"abbr": "DEN", "name": "丹佛掘金", "name_en": "Denver Nuggets", "motto": "Mile High Basketball", "champs": 1},
    {"abbr": "DET", "name": "底特律活塞", "name_en": "Detroit Pistons", "motto": "Motor City Basketball", "champs": 3},
    {"abbr": "GSW", "name": "金州勇士", "name_en": "Golden State Warriors", "motto": "Strength in Numbers", "champs": 7},
    {"abbr": "HOU", "name": "休斯顿火箭", "name_en": "Houston Rockets", "motto": "Red Nation", "champs": 2},
    {"abbr": "IND", "name": "印第安纳步行者", "name_en": "Indiana Pacers", "motto": "Blue & Gold", "champs": 0},
    {"abbr": "LAC", "name": "洛杉矶快船", "name_en": "LA Clippers", "motto": "Clipper Nation", "champs": 0},
    {"abbr": "LAL", "name": "洛杉矶湖人", "name_en": "Los Angeles Lakers", "motto": "Lake Show", "champs": 17},
    {"abbr": "MEM", "name": "孟菲斯灰熊", "name_en": "Memphis Grizzlies", "motto": "Grit and Grind", "champs": 0},
    {"abbr": "MIA", "name": "迈阿密热火", "name_en": "Miami Heat", "motto": "Heat Culture", "champs": 3},
    {"abbr": "MIL", "name": "密尔沃基雄鹿", "name_en": "Milwaukee Bucks", "motto": "Fear the Deer", "champs": 2},
    {"abbr": "MIN", "name": "明尼苏达森林狼", "name_en": "Minnesota Timberwolves", "motto": "Pack Mentality", "champs": 0},
    {"abbr": "NOP", "name": "新奥尔良鹈鹕", "name_en": "New Orleans Pelicans", "motto": "Growl", "champs": 1},
    {"abbr": "NYK", "name": "纽约尼克斯", "name_en": "New York Knicks", "motto": "New York Basketball", "champs": 2},
    {"abbr": "OKC", "name": "俄克拉荷马城雷霆", "name_en": "Oklahoma City Thunder", "motto": "Thunder Up", "champs": 1},
    {"abbr": "ORL", "name": "奥兰多魔术", "name_en": "Orlando Magic", "motto": "Magic Basketball", "champs": 0},
    {"abbr": "PHI", "name": "费城76人", "name_en": "Philadelphia 76ers", "motto": "Trust the Process", "champs": 3},
    {"abbr": "PHX", "name": "菲尼克斯太阳", "name_en": "Phoenix Suns", "motto": "Valley Boyz", "champs": 0},
    {"abbr": "POR", "name": "波特兰开拓者", "name_en": "Portland Trail Blazers", "motto": "Rip City", "champs": 1},
    {"abbr": "SAC", "name": "萨克拉门托国王", "name_en": "Sacramento Kings", "motto": "Sacramento Proud", "champs": 1},
    {"abbr": "SAS", "name": "圣安东尼奥马刺", "name_en": "San Antonio Spurs", "motto": "Go Spurs Go", "champs": 5},
    {"abbr": "TOR", "name": "多伦多猛龙", "name_en": "Toronto Raptors", "motto": "We The North", "champs": 1},
    {"abbr": "UTA", "name": "犹他爵士", "name_en": "Utah Jazz", "motto": "Take Note", "champs": 0},
    {"abbr": "WAS", "name": "华盛顿奇才", "name_en": "Washington Wizards", "motto": "DC Basketball", "champs": 1}
]

TEAM_COLORS = {
    "ATL": {"primary": "#E03A3E", "secondary": "#1D2D5C", "bg": "#1D2D5C"},
    "BOS": {"primary": "#007A33", "secondary": "#BA0C2F", "bg": "#007A33"},
    "BKN": {"primary": "#000000", "secondary": "#FFFFFF", "bg": "#000000"},
    "CHA": {"primary": "#1D1160", "secondary": "#00788C", "bg": "#1D1160"},
    "CHI": {"primary": "#CE1141", "secondary": "#000000", "bg": "#000000"},
    "CLE": {"primary": "#860038", "secondary": "#FFB81C", "bg": "#1D1160"},
    "DAL": {"primary": "#00538C", "secondary": "#B8C4CA", "bg": "#00538C"},
    "DEN": {"primary": "#0E2240", "secondary": "#FEC524", "bg": "#0E2240"},
    "DET": {"primary": "#006BB6", "secondary": "#C8102E", "bg": "#006BB6"},
    "GSW": {"primary": "#FFC72C", "secondary": "#1D428A", "bg": "#1D428A"},
    "HOU": {"primary": "#CE1141", "secondary": "#FFFFFF", "bg": "#0B3D91"},
    "IND": {"primary": "#002D62", "secondary": "#FFC633", "bg": "#002D62"},
    "LAC": {"primary": "#C8102E", "secondary": "#1D428A", "bg": "#1D428A"},
    "LAL": {"primary": "#552583", "secondary": "#FDB927", "bg": "#552583"},
    "MEM": {"primary": "#5D76A9", "secondary": "#12173F", "bg": "#12173F"},
    "MIA": {"primary": "#98002E", "secondary": "#F9A01B", "bg": "#98002E"},
    "MIL": {"primary": "#00471B", "secondary": "#EEE1C6", "bg": "#00471B"},
    "MIN": {"primary": "#0C2340", "secondary": "#236192", "bg": "#0C2340"},
    "NOP": {"primary": "#0C2340", "secondary": "#C8102E", "bg": "#0C2340"},
    "NYK": {"primary": "#006BB6", "secondary": "#F58426", "bg": "#006BB6"},
    "OKC": {"primary": "#007AC1", "secondary": "#EF3B24", "bg": "#007AC1"},
    "ORL": {"primary": "#0077C0", "secondary": "#C4CED4", "bg": "#0077C0"},
    "PHI": {"primary": "#006BB6", "secondary": "#ED174C", "bg": "#006BB6"},
    "PHX": {"primary": "#1D1160", "secondary": "#E56020", "bg": "#1D1160"},
    "POR": {"primary": "#E03A3E", "secondary": "#000000", "bg": "#E03A3E"},
    "SAC": {"primary": "#5A2D81", "secondary": "#646077", "bg": "#5A2D81"},
    "SAS": {"primary": "#C4CED4", "secondary": "#000000", "bg": "#000000"},
    "TOR": {"primary": "#CE1141", "secondary": "#000000", "bg": "#000000"},
    "UTA": {"primary": "#002B5C", "secondary": "#F9A01B", "bg": "#002B5C"},
    "WAS": {"primary": "#002B5C", "secondary": "#E31837", "bg": "#002B5C"}
}

def get_html_template():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEAM_NAME专区</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --team-primary: PRIMARY_COLOR;
            --team-bg: BACKGROUND_COLOR;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--team-bg); min-height: 100vh; color: #fff; }
        
        .navbar {
            background: rgba(0,0,0,0.85); padding: 0.75rem 1.5rem; position: fixed;
            top: 10px; left: 10px; right: 10px; z-index: 100; border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .navbar.minimized {
            width: 50px; height: 50px; padding: 0; right: 10px; left: auto;
            border-radius: 50%; background: var(--team-bg);
            background-image: url('/nbalogo/TEAM_ABBR.svg');
            background-size: 32px; background-repeat: no-repeat; background-position: center;
            border: 2px solid var(--team-primary); cursor: pointer;
        }
        .navbar h1 { font-size: 1rem; display: flex; align-items: center; gap: 10px; }
        .navbar.minimized h1 { opacity: 0; height: 0; overflow: hidden; }
        .team-logo { width: 35px; height: 35px; background-image: url('/nbalogo/TEAM_ABBR.svg'); background-size: contain; }
        .navbar.minimized .team-logo { display: none; }
        .team-info { font-size: 0.65rem; color: rgba(255,255,255,0.6); margin-left: 45px; display: flex; gap: 10px; }
        .navbar.minimized .team-info { opacity: 0; height: 0; overflow: hidden; }
        .navbar nav { margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .navbar.minimized nav { opacity: 0; height: 0; overflow: hidden; }
        .navbar nav a { color: rgba(255,255,255,0.8); text-decoration: none; padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.75rem; }
        .navbar nav a:hover, .navbar nav a.active { background: rgba(255,255,255,0.2); color: var(--team-primary); }

        .header { background: linear-gradient(135deg, var(--team-bg), rgba(0,0,0,0.8)); padding: 2rem; text-align: center; border-bottom: 3px solid var(--team-primary); }
        .header h1 { font-size: 3rem; margin-bottom: 10px; }
        .header p { color: rgba(255,255,255,0.8); font-size: 1.1rem; }

        .container { max-width: 1400px; margin: 0 auto; padding: 30px; }
        
        .tabs { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }
        .tab-btn {
            padding: 12px 24px; font-size: 14px; font-weight: 600;
            border: 2px solid transparent; border-radius: 25px;
            background: rgba(255,255,255,0.1); color: #fff; cursor: pointer;
        }
        .tab-btn:hover { background: rgba(255,255,255,0.2); border-color: var(--team-primary); }
        .tab-btn.active { background: var(--team-primary); color: var(--team-bg); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .card { background: rgba(0,0,0,0.3); border-radius: 15px; padding: 25px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .card h3 { color: var(--team-primary); margin-bottom: 20px; font-size: 1.3rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }

        .season-selector { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .season-btn { padding: 8px 20px; font-size: 12px; border: 1px solid rgba(255,255,255,0.3); border-radius: 20px; background: transparent; color: #fff; cursor: pointer; }
        .season-btn:hover { border-color: var(--team-primary); }
        .season-btn.active { background: var(--team-primary); color: var(--team-bg); }

        .roster-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .player-card { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1); cursor: pointer; }
        .player-card:hover { transform: translateY(-3px); border-color: var(--team-primary); }
        .player-number { width: 40px; height: 40px; margin: 0 auto 10px; border-radius: 50%; background: var(--team-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2rem; color: var(--team-bg); }
        .player-name { font-weight: 600; margin: 5px 0; }
        .player-position { color: rgba(255,255,255,0.7); font-size: 0.9rem; }
        .player-info { font-size: 0.8rem; color: rgba(255,255,255,0.5); }

        .schedule-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        .game-card { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; border-left: 4px solid var(--team-primary); }
        .game-card.win { border-left-color: #4CAF50; }
        .game-card.loss { border-left-color: #f44336; }
        .game-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .game-date { font-size: 0.85rem; color: rgba(255,255,255,0.6); }
        .game-result { font-size: 0.85rem; font-weight: bold; }
        .game-result.W { color: #4CAF50; }
        .game-result.L { color: #f44336; }
        .game-content { display: flex; justify-content: space-between; align-items: center; }
        .game-score { display: flex; align-items: center; gap: 20px; background: rgba(0,0,0,0.4); border-radius: 8px; padding: 10px 25px; min-width: 160px; }
        .team-score { font-weight: 700; font-size: 1.5rem; color: var(--team-primary); }
        .opp-score { font-weight: 700; font-size: 1.5rem; color: #666; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .stat-card { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
        .stat-value { font-size: 2rem; font-weight: bold; color: var(--team-primary); }
        .stat-label { font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-top: 5px; }

        .chart-container { height: 400px; background: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; }

        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .header h1 { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar minimized" id="navbar">
        <h1><div class="team-logo"></div>TEAM_NAME</h1>
        <div class="team-info">
            <span>TEAM_EN</span><span>|</span><span>TEAM_MOTTO</span><span>|</span><span>TEAM_CHAMPS次总冠军</span>
        </div>
        <nav>
            <a href="/">球队</a>
            <a href="/team-history" target="_blank">球队历史</a>
            <a href="/matchup" target="_blank">球队对阵</a>
            <a href="/player-compare" target="_blank">球员对比</a>
            <a href="/legendary-players" target="_blank">传奇球员</a>
            <a href="/player-radar" target="_blank">能力雷达图</a>
            <a href="/rankings" target="_blank">高阶数据</a>
            <a href="/spurs" target="_blank">马刺专区</a>
            <a href="/lakers" target="_blank">湖人专区</a>
            <a href="/rockets" target="_blank">火箭专区</a>
        </nav>
    </nav>

    <div class="content">
        <div class="header">
            <h1>TEAM_NAME</h1>
            <p>TEAM_EN | TEAM_MOTTO | TEAM_CHAMPS次总冠军</p>
        </div>

        <div class="container">
            <div class="tabs">
                <button class="tab-btn active" onclick="showTab('roster')">球队阵容</button>
                <button class="tab-btn" onclick="showTab('schedule')">赛季赛程</button>
                <button class="tab-btn" onclick="showTab('stats')">赛季统计</button>
            </div>

            <div id="roster" class="tab-content active">
                <div class="card"><h3>球队阵容</h3><div class="roster-grid" id="rosterGrid"></div></div>
            </div>

            <div id="schedule" class="tab-content">
                <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;">
                    <button class="season-btn" onclick="changeScheduleSeason(-1)">◀ 上赛季</button>
                    <select id="scheduleSeasonSelect" onchange="loadSchedule(this.value)" style="padding: 8px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.3); color: #fff; font-size: 14px;">
                        <option value="2023-2024">2023-24</option>
                        <option value="2024-2025">2024-25</option>
                        <option value="2025-2026">2025-26</option>
                    </select>
                    <button class="season-btn" onclick="changeScheduleSeason(1)">下赛季 ▶</button>
                </div>
                <div class="card"><h3>赛季赛程</h3><div class="schedule-grid" id="scheduleGrid"></div></div>
            </div>

            <div id="stats" class="tab-content">
                <div class="season-selector" id="statsSeasonSelector">
                    <button class="season-btn active" data-season="2023-2024">2023-24</button>
                    <button class="season-btn" data-season="2024-2025">2024-25</button>
                    <button class="season-btn" data-season="2025-2026">2025-26</button>
                </div>
                <div class="card"><h3>赛季统计</h3><div class="stats-grid" id="statsGrid"></div></div>
                <div class="card"><h3>得分趋势</h3><div class="chart-container"><canvas id="trendChart"></canvas></div></div>
            </div>
        </div>
    </div>

    <script>
        let trendChart = null;
        const TEAM_ABBR = "TEAM_ABBR";

        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('navbar').addEventListener('click', (e) => {
                e.currentTarget.classList.toggle('minimized');
            });
        });

        function showTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            if (tabId === 'schedule') loadSchedule('2023-2024');
            else if (tabId === 'stats') loadSeasonStats('2023-2024');
        }

        function changeScheduleSeason(direction) {
            const select = document.getElementById('scheduleSeasonSelect');
            if (!select) return;
            const newIndex = select.selectedIndex + direction;
            if (newIndex >= 0 && newIndex < select.options.length) {
                select.selectedIndex = newIndex;
                loadSchedule(select.options[newIndex].value);
            }
        }

        async function loadRoster() {
            try {
                const res = await fetch('/api/team/roster/' + TEAM_ABBR);
                const result = await res.json();
                if (result.success && result.data && result.data.length > 0) {
                    document.getElementById('rosterGrid').innerHTML = result.data.map(p => `
                        <div class="player-card" onclick="window.location.href='/player-profile?id=${p.player_id || p.name.toLowerCase().replace(' ', '_')}'">
                            <div class="player-number">${p.number || '?'}</div>
                            <div class="player-name">${p.name}</div>
                            <div class="player-position">${p.position || ''}</div>
                            <div class="player-info">${p.info || ''}</div>
                        </div>
                    `).join('');
                } else {
                    loadDefaultRoster();
                }
            } catch { loadDefaultRoster(); }
        }

        function loadDefaultRoster() {
            document.getElementById('rosterGrid').innerHTML = [
                {num:'1', name:'明星球员', pos:'SF', info:'球队核心'},
                {num:'10', name:'得分后卫', pos:'SG', info:'外线射手'},
                {num:'23', name:'小前锋', pos:'SF', info:'全能战士'},
                {num:'32', name:'大前锋', pos:'PF', info:'内线支柱'},
                {num:'50', name:'中锋', pos:'C', info:'篮下守护者'}
            ].map(p => `
                <div class="player-card">
                    <div class="player-number">${p.num}</div>
                    <div class="player-name">${p.name}</div>
                    <div class="player-position">${p.pos}</div>
                    <div class="player-info">${p.info}</div>
                </div>
            `).join('');
        }

        async function loadSchedule(season) {
            try {
                const res = await fetch('/api/team/season/' + season + '?team=' + TEAM_ABBR);
                const result = await res.json();
                if (result.success && result.data.games) {
                    document.getElementById('scheduleGrid').innerHTML = result.data.games.map(g => {
                        const win = g.Tm > g.Opp_1;
                        return `
                            <div class="game-card ${win?'win':'loss'}">
                                <div class="game-header"><span class="game-date">${g.Date}</span><span class="game-result ${g.Rslt}">${g.Rslt}</span></div>
                                <div class="game-content">
                                    <div class="game-score ${win?'win':'loss'}">
                                        <span class="team-score">${g.Tm}</span>
                                        <span style="color:rgba(255,255,255,0.3)">-</span>
                                        <span class="opp-score">${g.Opp_1}</span>
                                    </div>
                                    <div style="text-align:center"><div style="font-weight:600">vs ${g.Opp}</div></div>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    document.getElementById('scheduleGrid').innerHTML = '<div style="text-align:center;color:#888;padding:20px;">暂无数据</div>';
                }
            } catch {
                document.getElementById('scheduleGrid').innerHTML = '<div style="text-align:center;color:#888;padding:20px;">加载失败</div>';
            }
        }

        async function loadSeasonStats(season) {
            try {
                const res = await fetch('/api/team/season_summary/' + season + '?team=' + TEAM_ABBR);
                const result = await res.json();
                if (result.success && result.data) {
                    const s = result.data;
                    document.getElementById('statsGrid').innerHTML = `
                        <div class="stat-card"><div class="stat-value">${s.wins}-${s.losses}</div><div class="stat-label">战绩</div></div>
                        <div class="stat-card"><div class="stat-value">${s.win_rate}%</div><div class="stat-label">胜率</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_points}</div><div class="stat-label">场均得分</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_opp_points}</div><div class="stat-label">场均失分</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_fg_pct}%</div><div class="stat-label">投篮命中率</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_three_pct}%</div><div class="stat-label">三分命中率</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_ft_pct}%</div><div class="stat-label">罚球命中率</div></div>
                        <div class="stat-card"><div class="stat-value">${s.avg_rebounds}</div><div class="stat-label">场均篮板</div></div>
                    `;
                    
                    if (trendChart) trendChart.destroy();
                    const ctx = document.getElementById('trendChart').getContext('2d');
                    trendChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: (s.points_trend || []).map((_,i) => 'G'+(i+1)).slice(-20),
                            datasets: [{
                                label: '得分', data: (s.points_trend || []).slice(-20),
                                borderColor: 'var(--team-primary)', backgroundColor: 'var(--team-primary)33',
                                fill: true, tension: 0.4
                            }, {
                                label: '对手得分', data: (s.opp_points_trend || []).slice(-20),
                                borderColor: '#FFD700', backgroundColor: 'rgba(255,215,0,0.1)',
                                fill: true, tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true, maintainAspectRatio: false,
                            scales: {
                                y: { beginAtZero: true, grid: {color:'rgba(255,255,255,0.1)'}, ticks:{color:'#fff'}},
                                x: { grid: {color:'rgba(255,255,255,0.1)'}, ticks:{color:'#fff'}}
                            },
                            plugins: { legend: { labels: {color:'#fff'} } }
                        }
                    });
                } else {
                    document.getElementById('statsGrid').innerHTML = '<div style="text-align:center;color:#888;padding:20px;">暂无数据</div>';
                }
            } catch {
                document.getElementById('statsGrid').innerHTML = '<div style="text-align:center;color:#888;padding:20px;">加载失败</div>';
            }
        }

        document.getElementById('statsSeasonSelector').addEventListener('click', (e) => {
            const btn = e.target.closest('.season-btn');
            if (btn) {
                document.querySelectorAll('#statsSeasonSelector .season-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                loadSeasonStats(btn.dataset.season);
            }
        });

        loadRoster();
        loadSchedule('2023-2024');
        loadSeasonStats('2023-2024');
    </script>
</body>
</html>
'''

def generate_team_html(team):
    template = get_html_template()
    colors = TEAM_COLORS[team["abbr"]]
    
    replacements = {
        "TEAM_ABBR": team["abbr"],
        "TEAM_NAME": team["name"],
        "TEAM_EN": team["name_en"],
        "TEAM_MOTTO": team["motto"],
        "TEAM_CHAMPS": str(team["champs"]),
        "PRIMARY_COLOR": colors["primary"],
        "BACKGROUND_COLOR": colors["bg"]
    }
    
    html = template
    for key, value in replacements.items():
        html = html.replace(key, value)
    
    return html

def main():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    
    for team in TEAMS:
        abbr = team["abbr"].lower()
        filename = f"{abbr}.html"
        filepath = os.path.join(static_dir, filename)
        
        html = generate_team_html(team)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated {filename}")
    
    print("\n所有球队页面已生成完成！")

if __name__ == "__main__":
    main()