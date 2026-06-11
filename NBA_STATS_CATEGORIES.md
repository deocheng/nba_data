# NBA League Leaders 2025-26 统计类别说明

## 📊 数据概览

- **数据来源**: league leaders 1955-2026 .xlsx
- **数据赛季**: 2025-26
- **可生成的图表种类**: **75 种**
- **PDF文件**: nba_league_leaders_2025-26_all_charts.pdf

## 📋 统计类别列表（75种）

### 基础统计类（7种）
1. Points (得分)
2. Rebounds (篮板)
3. Assists (助攻)
4. Steals (抢断)
5. Blocks (盖帽)
6. Minutes Played (出场时间)
7. Games (比赛场次)

### 场均数据类（7种）
8. Points Per Game (场均得分)
9. Rebounds Per Game (场均篮板)
10. Assists Per Game (场均助攻)
11. Steals Per Game (场均抢断)
12. Blocks Per Game (场均盖帽)
13. Minutes Per Game (场均时间)
14. Personal Fouls (犯规)

### 投篮统计类（12种）
15. Field Goals (投篮命中)
16. Field Goal Attempts (投篮出手)
17. Field Goal Pct (投篮命中率)
18. Field Goals Per Game (场均投篮命中)
19. Field Goal Attempts Per Game (场均投篮出手)
20. Field Goals Missed (投篮打铁)
21. Field Goals Per 36 Minutes (每36分钟投篮命中)
22. Field Goals Per 100 Possessions (每100回合投篮命中)
23. Field Goal Attempts Per 36 Minutes (每36分钟投篮出手)
24. Field Goal Attempts Per 100 Possessions (每100回合投篮出手)
25. Effective Field Goal Pct (有效命中率)
26. True Shooting Pct (真实命中率)

### 三分统计类（6种）
27. Three Pointers (三分命中)
28. Three Point Attempts (三分出手)
29. Three Point Pct (三分命中率)
30. Three Pointers Per Game (场均三分命中)
31. Three Point Attempts Per Game (场均三分出手)

### 罚球统计类（8种）
32. Free Throws (罚球命中)
33. Free Throw Attempts (罚球出手)
34. Free Throw Pct (罚球命中率)
35. Free Throws Per Game (场均罚球命中)
36. Free Throw Attempts Per Game (场均罚球出手)
37. Free Throws Per 36 Minutes (每36分钟罚球命中)
38. Free Throws Per 100 Possessions (每100回合罚球命中)
39. Free Throw Attempts Per 36 Minutes (每36分钟罚球出手)
40. Free Throw Attempts Per 100 Possessions (每100回合罚球出手)

### 篮板统计类（12种）
41. Offensive Rebounds (进攻篮板)
42. Defensive Rebounds (防守篮板)
43. Total Rebounds (总篮板)
44. Offensive Rebounds Per Game (场均进攻篮板)
45. Defensive Rebounds Per Game (场均防守篮板)
46. Rebounds Per Game (场均篮板)
47. Offensive Rebounds Per 36 Minutes (每36分钟进攻篮板)
48. Defensive Rebounds Per 36 Minutes (每36分钟防守篮板)
49. Total Rebounds Per 36 Minutes (每36分钟总篮板)
50. Offensive Rebounds Per 100 Possessions (每100回合进攻篮板)
51. Defensive Rebounds Per 100 Possessions (每100回合防守篮板)
52. Total Rebounds Per 100 Possessions (每100回合总篮板)
53. Offensive Rebound Pct (进攻篮板率)
54. Defensive Rebound Pct (防守篮板率)
55. Total Rebound Pct (总篮板率)

### 助攻统计类（5种）
56. Assists (助攻)
57. Assists Per Game (场均助攻)
58. Assist Pct (助攻率)
59. Assists Per 36 Minutes (每36分钟助攻)
60. Assists Per 100 Possessions (每100回合助攻)

### 抢断统计类（5种）
61. Steals (抢断)
62. Steals Per Game (场均抢断)
63. Steal Pct (抢断率)
64. Steals Per 36 Minutes (每36分钟抢断)
65. Steals Per 100 Possessions (每100回合抢断)

### 盖帽统计类（5种）
66. Blocks (盖帽)
67. Blocks Per Game (场均盖帽)
68. Block Pct (盖帽率)
69. Blocks Per 36 Minutes (每36分钟盖帽)
70. Blocks Per 100 Possessions (每100回合盖帽)

### 失误统计类（4种）
71. Turnovers (失误)
72. Turnovers Per Game (场均失误)
73. Turnover Pct (失误率)
74. Turnovers Per 36 Minutes (每36分钟失误)
75. Turnovers Per 100 Possessions (每100回合失误)

### 进攻/防守效率类（6种）
76. Offensive Rating (进攻效率)
77. Defensive Rating (防守效率)
78. Offensive Win Shares (进攻胜利贡献)
79. Defensive Win Shares (防守胜利贡献)
80. Win Shares (总胜利贡献)
81. Win Shares Per 48 Minutes (每48分钟胜利贡献)

### 高阶数据类（6种）
82. Player Efficiency Rating (球员效率值)
83. Usage Pct (使用率)
84. Box Plus/Minus (box正负值)
85. Offensive Box Plus/Minus (进攻box正负值)
86. Defensive Box Plus/Minus (防守box正负值)
87. Value Over Replacement Player (替代者价值)

### 其他统计类（3种）
88. Personal Fouls Per 36 Minutes (每36分钟犯规)
89. Personal Fouls Per 100 Possessions (每100回合犯规)

## 📁 文件位置

- **PDF文件**: `nba_data/static/charts/nba_league_leaders_2025-26_all_charts.pdf`
- **单独PNG图表**: `nba_data/static/charts/` 目录下
- **JSON数据**: `nba_data/CSV_Clean/league_leaders_parsed.csv`
- **统计类别列表**: `nba_data/statistics_categories.txt`

## 🎯 PDF内容说明

PDF文件包含75页，每页展示一个统计类别的联盟前10名球员，包含：
- 球员姓名和球队
- 该项统计数据
- 柱状图可视化
- 数值标注

## 💡 使用建议

1. **查看单个图表**: 访问 `http://localhost:8000/league-leaders-charts`
2. **查看综合得分排名**: 访问 `http://localhost:8000/top-scorers`
3. **下载完整PDF**: 下载 `nba_data/static/charts/nba_league_leaders_2025-26_all_charts.pdf`
4. **查看特定赛季数据**: 修改脚本中的赛季参数，重新生成图表