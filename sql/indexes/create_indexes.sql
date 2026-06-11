-- 球员表索引
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_name_clean ON players(player_name_clean);
CREATE INDEX IF NOT EXISTS idx_players_is_active ON players(is_active);

-- 球队表索引
CREATE INDEX IF NOT EXISTS idx_teams_abbreviation ON teams(team_abbreviation);
CREATE INDEX IF NOT EXISTS idx_teams_conference ON teams(conference);
CREATE INDEX IF NOT EXISTS idx_teams_division ON teams(division);

-- 球员赛季统计表索引
CREATE INDEX IF NOT EXISTS idx_player_season_stats_player_id ON player_season_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_season_stats_season ON player_season_stats(season);
CREATE INDEX IF NOT EXISTS idx_player_season_stats_team_id ON player_season_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_player_season_stats_player_season ON player_season_stats(player_id, season);
CREATE INDEX IF NOT EXISTS idx_player_season_stats_team_season ON player_season_stats(team_id, season);

-- 马刺队相关表索引
CREATE INDEX IF NOT EXISTS idx_spurs_history_seasons_season ON spurs_history_seasons(season);
CREATE INDEX IF NOT EXISTS idx_spurs_history_seasons_wins ON spurs_history_seasons(wins);

CREATE INDEX IF NOT EXISTS idx_spurs_history_year_by_year_season ON spurs_history_year_by_year(season);
CREATE INDEX IF NOT EXISTS idx_spurs_history_year_by_year_per_game_season ON spurs_history_year_by_year_per_game(season);

CREATE INDEX IF NOT EXISTS idx_spurs_career_leaders_stat_name ON spurs_career_leaders(stat_name);
CREATE INDEX IF NOT EXISTS idx_spurs_career_leaders_player_name ON spurs_career_leaders(player_name);

CREATE INDEX IF NOT EXISTS idx_spurs_season_leaders_stat_name ON spurs_season_leaders(stat_name);
CREATE INDEX IF NOT EXISTS idx_spurs_season_leaders_season ON spurs_season_leaders(season);
CREATE INDEX IF NOT EXISTS idx_spurs_season_leaders_player_name ON spurs_season_leaders(player_name);

-- 比赛日志表索引
CREATE INDEX IF NOT EXISTS idx_spurs_basic_game_log_2023_24_date ON spurs_basic_game_log_csv_2023_24(date);
CREATE INDEX IF NOT EXISTS idx_spurs_basic_game_log_2023_24_opponent ON spurs_basic_game_log_csv_2023_24(opponent);

CREATE INDEX IF NOT EXISTS idx_spurs_basic_game_log_2024_25_date ON spurs_basic_game_log_csv_2024_25(date);
CREATE INDEX IF NOT EXISTS idx_spurs_basic_game_log_2024_25_opponent ON spurs_basic_game_log_csv_2024_25(opponent);

CREATE INDEX IF NOT EXISTS idx_spurs_adv_game_log_2023_24_date ON spurs_adv_game_log_csv_2023_24(date);
CREATE INDEX IF NOT EXISTS idx_spurs_adv_game_log_2025_26_date ON spurs_adv_game_log_csv_2025_26(date);

-- 球员统计相关表索引
CREATE INDEX IF NOT EXISTS idx_player_season_stats_name ON player_season_stats(player_name);

CREATE INDEX IF NOT EXISTS idx_player_stats_per36_name ON player_stats_per36(player_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_per100_name ON player_stats_per100(player_name);
CREATE INDEX IF NOT EXISTS idx_player_advanced_stats_name ON player_advanced_stats(player_name);

CREATE INDEX IF NOT EXISTS idx_spurs_per_game_2024_25_name ON spurs_per_game_2024_25(player_name);

-- 季后赛数据索引
CREATE INDEX IF NOT EXISTS idx_playoff_stats_name ON playoff_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_playoff_per_game_name ON playoff_per_game(player_name);

CREATE INDEX IF NOT EXISTS idx_spurs_playoff_pbp_name ON spurs_playoff_pbp(player_name);
CREATE INDEX IF NOT EXISTS idx_spurs_playoff_per100_name ON spurs_playoff_per100(player_name);

-- 球队统计索引
CREATE INDEX IF NOT EXISTS idx_spurs_team_stats_2024_25_type ON spurs_team_stats_2024_25(data_type);
CREATE INDEX IF NOT EXISTS idx_spurs_team_opponent_stats_season ON spurs_team_opponent_stats(season);

-- 花名册索引
CREATE INDEX IF NOT EXISTS idx_spurs_full_roster_name ON spurs_full_roster(player_name);
CREATE INDEX IF NOT EXISTS idx_spurs_full_roster_season ON spurs_full_roster(season);
CREATE INDEX IF NOT EXISTS idx_spurs_full_roster_player_season ON spurs_full_roster(player_name, season);

-- 火箭队相关索引
CREATE INDEX IF NOT EXISTS idx_rockets_roster_name ON rockets_roster(player_name);
CREATE INDEX IF NOT EXISTS idx_rockets_team_stats_type ON rockets_team_stats(stat_type);

-- 联盟排行榜索引
CREATE INDEX IF NOT EXISTS idx_league_leaderboards_category ON league_leaderboards(category);
CREATE INDEX IF NOT EXISTS idx_league_leaderboards_player_name ON league_leaderboards(player_name);