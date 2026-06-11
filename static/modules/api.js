/**
 * NBA Data Module - API调用模块
 */

class NBAAPI {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    async get(endpoint, params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = queryString
                ? `${this.baseUrl}${endpoint}?${queryString}`
                : `${this.baseUrl}${endpoint}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.warn(`API请求失败 [${endpoint}]:`, error.message);
            throw error;
        }
    }

    async getPlayerProfile(playerId) {
        return this.get(`/player/${playerId}/profile`);
    }

    async getPlayerCareer(playerId, season = null) {
        const params = season ? { season } : {};
        return this.get(`/player/${playerId}/career`, params);
    }

    async getPlayerGameLogs(playerId, season = null, playoffs = false) {
        const params = { playoffs: playoffs };
        if (season) params.season = season;
        return this.get(`/player/${playerId}/gamelogs`, params);
    }

    async getTeamRoster(teamAbbr) {
        return this.get(`/teams/${teamAbbr}/roster`);
    }

    async getTeamSchedule(teamAbbr, season = null) {
        const params = { team: teamAbbr };
        if (season) params.season = season;
        return this.get('/team/season', params);
    }

    async getTeamSeasonSummary(teamAbbr, season) {
        return this.get('/team/season_summary', { team: teamAbbr, season: season });
    }

    async getTeamInfo(teamAbbr) {
        return this.get(`/team/info/${teamAbbr}`);
    }

    async getSeasons() {
        return this.get('/seasons');
    }

    async getTeamGames(teamAbbr, season = null) {
        const params = { team: teamAbbr };
        if (season) params.season = season;
        return this.get('/team/season', params);
    }

    async getAdvancedStats(playerId, season = null) {
        const params = season ? { season } : {};
        return this.get(`/player/${playerId}/advanced`, params);
    }

    async searchPlayers(query) {
        return this.get('/players/search', { q: query });
    }
}

window.NBAAPI = new NBAAPI();

window.API = {
    getPlayerProfile: (id) => window.NBAAPI.getPlayerProfile(id),
    getPlayerCareer: (id, season) => window.NBAAPI.getPlayerCareer(id, season),
    getPlayerGameLogs: (id, season, playoffs) => window.NBAAPI.getPlayerGameLogs(id, season, playoffs),
    getTeamRoster: (team) => window.NBAAPI.getTeamRoster(team),
    getTeamSchedule: (team, season) => window.NBAAPI.getTeamSchedule(team, season),
    getTeamSeasonSummary: (team, season) => window.NBAAPI.getTeamSeasonSummary(team, season),
    getTeamInfo: (team) => window.NBAAPI.getTeamInfo(team),
    getSeasons: () => window.NBAAPI.getSeasons(),
    getTeamGames: (team, season) => window.NBAAPI.getTeamGames(team, season),
    getAdvancedStats: (id, season) => window.NBAAPI.getAdvancedStats(id, season),
    searchPlayers: (query) => window.NBAAPI.searchPlayers(query)
};
