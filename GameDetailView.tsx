'use client';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import PlayerParallelTracks from './PlayerParallelTracks';
import type { GameNode, GameLog } from '../data/mockData';

interface GameDetailViewProps {
  game: GameNode;
  gameLog: GameLog;
  onClose: () => void;
  onPrevGame?: () => void;
  onNextGame?: () => void;
}

export default function GameDetailView({
  game,
  gameLog,
  onClose,
  onPrevGame,
  onNextGame,
}: GameDetailViewProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-white z-50 overflow-auto"
      >
        {/* 返回按钮 */}
        <motion.button
          onClick={onClose}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="fixed top-6 left-8 z-50 flex items-center gap-2 px-5 py-3 bg-white rounded-2xl shadow-lg border border-gray-100 hover:border-gray-200 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <ChevronLeft size={20} />
          <span className="font-medium">返回时间线</span>
        </motion.button>

        <div className="max-w-7xl mx-auto px-8 py-16">
          {/* ==================== 顶部比赛信息 ==================== */}
          <div className="flex flex-col items-center mb-12">
            <div className="text-sm text-gray-500 mb-2">
              {new Date(game.date).toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </div>

            <div className="flex items-center gap-8">
              {/* 主队 */}
              <div className="text-right">
                <div className="text-4xl font-bold">{game.homeTeam}</div>
                <div className="text-6xl font-bold text-blue-600 mt-2">{game.homeScore}</div>
              </div>

              <div className="text-5xl font-light text-gray-300">VS</div>

              {/* 客队 */}
              <div>
                <div className="text-4xl font-bold">{game.awayTeam}</div>
                <div className="text-6xl font-bold text-red-600 mt-2">{game.awayScore}</div>
              </div>
            </div>

            <div className="mt-4 text-gray-500">
              {game.venue || 'Crypto.com Arena'} • Regular Season
            </div>
          </div>

          {/* ==================== 球员平行轨道 ==================== */}
          <PlayerParallelTracks game={game} gameLog={gameLog} />

          {/* ==================== PBP 逐球数据（占位）=================== */}
          <div className="mt-16">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold">Play-by-Play</h3>
              <div className="flex gap-2 text-sm">
                <button className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200">全部</button>
                <button className="px-4 py-2 rounded-xl hover:bg-gray-100">第一节</button>
                <button className="px-4 py-2 rounded-xl hover:bg-gray-100">第二节</button>
                <button className="px-4 py-2 rounded-xl hover:bg-gray-100">第三节</button>
                <button className="px-4 py-2 rounded-xl hover:bg-gray-100">第四节</button>
              </div>
            </div>

            <div className="bg-gray-50 border border-gray-100 rounded-3xl p-8 min-h-[400px] text-gray-400">
              Play-by-Play 数据即将在这里展示...
              <br />
              （你可以后续接入真实的 PBP 数据）
            </div>
          </div>

          {/* ==================== 底部导航 ==================== */}
          <div className="mt-20 pt-10 border-t border-gray-200 flex items-center justify-between">
            <button
              onClick={onPrevGame}
              className="flex items-center gap-3 px-6 py-4 hover:bg-gray-100 rounded-2xl transition-colors group"
            >
              <ChevronLeft className="group-hover:-translate-x-1 transition-transform" />
              <div className="text-left">
                <div className="text-sm text-gray-500">前一场比赛</div>
                <div className="font-medium">2024-10-20 vs Warriors</div>
              </div>
            </button>

            <div className="flex gap-6">
              <button className="flex flex-col items-center hover:text-blue-600 transition-colors">
                <Calendar size={22} />
                <span className="text-xs mt-1.5">当日其他比赛</span>
              </button>

              <button className="flex flex-col items-center hover:text-blue-600 transition-colors">
                <span className="text-lg">→</span>
                <span className="text-xs mt-1.5">{game.homeTeam} 下一场</span>
              </button>

              <button className="flex flex-col items-center hover:text-blue-600 transition-colors">
                <span className="text-lg">→</span>
                <span className="text-xs mt-1.5">{game.awayTeam} 下一场</span>
              </button>
            </div>

            <button
              onClick={onNextGame}
              className="flex items-center gap-3 px-6 py-4 hover:bg-gray-100 rounded-2xl transition-colors group"
            >
              <div className="text-right">
                <div className="text-sm text-gray-500">后一场比赛</div>
                <div className="font-medium">2024-10-24 vs Clippers</div>
              </div>
              <ChevronRight className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}