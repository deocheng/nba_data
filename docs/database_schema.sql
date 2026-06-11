-- NBA数据管理项目 - 数据库表结构
-- 版本: v2.0
-- 创建日期: 2026-05-13

-- ============================================
-- 维度表
-- ============================================

-- 球员基础信息表
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR(50) PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    player_name_en VARCHAR(100),
    position VARCHAR(20),
    position_cn VARCHAR(20),
    height VARCHAR(20),
    weight VARCHAR(20),
    jersey_number VARCHAR(10),
    birth_date DATE,
    birth_place VARCHAR(100),
    draft_year INT,
    draft_pick VARCHAR(50),
    retire_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 球队信息表
CREATE TABLE IF NOT EXISTS teams (
    team_id VARCHAR(50) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_name_en VARCHAR(100),
    team_abbr VARCHAR(10) NOT NULL,
    conference VARCHAR(20),
    conference_cn VARCHAR(20),
    division VARCHAR(50),
    division_cn VARCHAR(50),
    city VARCHAR(50),
    arena VARCHAR(100),
    founded_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 赛季维度表
CREATE TABLE IF NOT EXISTS seasons (
    season_id VARCHAR(20) PRIMARY KEY,
    season_type VARCHAR(20) DEFAULT 'regular',
    season_type_cn VARCHAR(20) DEFAULT '常规赛',
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 事实表
-- ============================================

-- 球员-球队-赛季汇总表（核心）
CREATE TABLE IF NOT EXISTS player_team_seasons (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    season_id VARCHAR(20) NOT NULL,
    games_played INT DEFAULT 0,
    minutes_played FLOAT DEFAULT 0,
    points INT DEFAULT 0,
    rebounds INT DEFAULT 0,
    assists INT DEFAULT 0,
    steals INT DEFAULT 0,
    blocks INT DEFAULT 0,
    fg_made INT DEFAULT 0,
    fg_att INT DEFAULT 0,
    three_made INT DEFAULT 0,
    three_att INT DEFAULT 0,
    ft_made INT DEFAULT 0,
    ft_att INT DEFAULT 0,
    -- 高阶指标
    per FLOAT,
    ts_pct FLOAT,
    usg_pct FLOAT,
    ws FLOAT,
    ws_per_48 FLOAT,
    bpm FLOAT,
    vorp FLOAT,
    offensive_rating FLOAT,
    defensive_rating FLOAT,
    assist_ratio FLOAT,
    turnover_ratio FLOAT,
    rebound_rate FLOAT,
    -- 场均数据（预计算）
    avg_points FLOAT,
    avg_rebounds FLOAT,
    avg_assists FLOAT,
    avg_steals FLOAT,
    avg_blocks FLOAT,
    fg_pct FLOAT,
    three_pct FLOAT,
    ft_pct FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, team_id, season_id)
);

-- 球员逐场比赛明细表
CREATE TABLE IF NOT EXISTS player_game_logs (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    game_id VARCHAR(50) NOT NULL,
    season_id VARCHAR(20) NOT NULL,
    game_date DATE NOT NULL,
    game_number INT,
    is_home BOOLEAN,
    opp_team_id VARCHAR(50),
    opp_team_abbr VARCHAR(10),
    result VARCHAR(10),
    minutes_played FLOAT,
    points INT,
    rebounds INT,
    assists INT,
    steals INT,
    blocks INT,
    fg_made INT,
    fg_att INT,
    three_made INT,
    three_att INT,
    ft_made INT,
    ft_att INT,
    plus_minus INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 球队逐场比赛数据表
CREATE TABLE IF NOT EXISTS team_games (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    season_id VARCHAR(20) NOT NULL,
    game_date DATE NOT NULL,
    game_number INT,
    is_home BOOLEAN,
    opp_team_id VARCHAR(50),
    opp_team_abbr VARCHAR(10),
    opp_team_name VARCHAR(100),
    result VARCHAR(10),
    team_score INT,
    opp_score INT,
    ot_flag VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, team_id)
);

-- ============================================
-- 索引优化
-- ============================================

-- 球员-球队-赛季汇总表索引
CREATE INDEX IF NOT EXISTS idx_pts_player_id ON player_team_seasons(player_id);
CREATE INDEX IF NOT EXISTS idx_pts_team_id ON player_team_seasons(team_id);
CREATE INDEX IF NOT EXISTS idx_pts_season_id ON player_team_seasons(season_id);
CREATE INDEX IF NOT EXISTS idx_pts_player_season ON player_team_seasons(player_id, season_id);

-- 球员比赛日志索引
CREATE INDEX IF NOT EXISTS idx_pgl_player_id ON player_game_logs(player_id);
CREATE INDEX IF NOT EXISTS idx_pgl_game_id ON player_game_logs(game_id);
CREATE INDEX IF NOT EXISTS idx_pgl_season_id ON player_game_logs(season_id);
CREATE INDEX IF NOT EXISTS idx_pgl_game_date ON player_game_logs(game_date);

-- 球队比赛索引
CREATE INDEX IF NOT EXISTS idx_tg_team_id ON team_games(team_id);
CREATE INDEX IF NOT EXISTS idx_tg_game_id ON team_games(game_id);
CREATE INDEX IF NOT EXISTS idx_tg_season_id ON team_games(season_id);
CREATE INDEX IF NOT EXISTS idx_tg_game_date ON team_games(game_date);

-- ============================================
-- 初始数据
-- ============================================

-- 插入赛季数据
INSERT INTO seasons (season_id, season_type, season_type_cn) VALUES
('2025-26', 'regular', '常规赛'),
('2024-25', 'regular', '常规赛'),
('2023-24', 'regular', '常规赛'),
('2022-23', 'regular', '常规赛'),
('2021-22', 'regular', '常规赛'),
('2020-21', 'regular', '常规赛')
ON CONFLICT DO NOTHING;
