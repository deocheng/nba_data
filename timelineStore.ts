import { create } from 'zustand';
import type { GameNode, GameLog } from '../data/mockData';

interface TimelineState {
  // 当前选中的比赛
  selectedGame: GameNode | null;
  selectedGameLog: GameLog | null;

  // 时间线数据
  games: GameNode[];
  loading: boolean;
  error: string | null;

  // Actions
  setSelectedGame: (game: GameNode | null, gameLog?: GameLog) => void;
  setGames: (games: GameNode[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // 导航相关
  goToPrevGame: () => void;
  goToNextGame: () => void;
  clearSelection: () => void;
}

export const useTimelineStore = create<TimelineState>((set, get) => ({
  selectedGame: null,
  selectedGameLog: null,
  games: [],
  loading: false,
  error: null,

  setSelectedGame: (game, gameLog) => {
    set({
      selectedGame: game,
      selectedGameLog: gameLog || null,
    });
  },

  setGames: (games) => set({ games }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  clearSelection: () => set({
    selectedGame: null,
    selectedGameLog: null,
  }),

  // 前一场比赛
  goToPrevGame: () => {
    const { selectedGame, games } = get();
    if (!selectedGame) return;

    const currentIndex = games.findIndex(g => g.game_id === selectedGame.game_id);
    if (currentIndex <= 0) return;

    const prevGame = games[currentIndex - 1];
    // 这里你可以根据需要加载对应的 gameLog
    set({ 
      selectedGame: prevGame,
      // selectedGameLog: fetchGameLog(prevGame.game_id) 
    });
  },

  // 后一场比赛
  goToNextGame: () => {
    const { selectedGame, games } = get();
    if (!selectedGame) return;

    const currentIndex = games.findIndex(g => g.game_id === selectedGame.game_id);
    if (currentIndex === -1 || currentIndex >= games.length - 1) return;

    const nextGame = games[currentIndex + 1];
    set({ 
      selectedGame: nextGame,
      // selectedGameLog: fetchGameLog(nextGame.game_id)
    });
  },
}));