import React, { useState } from 'react';
import { Users, Repeat, BarChart3, X } from 'lucide-react';

// 模拟数据结构
const NBA_SCHEDULE = {
  "2024-06-20": {
    type: "DRAFT",
    title: "2024 NBA Draft 第一轮",
    location: "巴克莱中心"
  },
  "2024-06-21": {
    games: [
      { id: 1, home: "LAL", away: "BOS", time: "08:00", homeStats: "50-32", awayStats: "64-18" },
      { id: 2, home: "GSW", away: "PHX", time: "10:30", homeStats: "46-36", awayStats: "49-33" }
    ]
  },
  "2024-06-24": {
    type: "TRADE",
    title: "交易窗口开启",
    detail: "自由球员谈判正式开始"
  },
  "2024-06-26": {
    games: [
      { id: 3, home: "DAL", away: "DEN", time: "09:00", homeStats: "50-32", awayStats: "57-25" }
    ]
  }
};

const NBACalendar = () => {
  const [selectedGame, setSelectedGame] = useState(null);

  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white font-sans">
      <h1 className="text-2xl font-bold mb-8 flex items-center gap-2">
        <BarChart3 className="text-blue-500" /> NBA 赛季动态看板
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(NBA_SCHEDULE).map(([date, data]) => (
          <div key={date} className="bg-gray-800 rounded-xl p-4 border border-gray-700 shadow-lg">
            {/* 日期头部 */}
            <div className="text-gray-400 text-sm font-mono mb-3 border-b border-gray-700 pb-2 flex justify-between">
              <span>{date}</span>
              {data.type && <span className="text-yellow-500 font-bold">重要日程</span>}
            </div>

            {/* 选秀/交易展示 */}
            {data.type === 'DRAFT' && (
              <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-3 rounded-lg flex items-center gap-3">
                <Users size={24} />
                <div>
                  <div className="font-bold text-sm">选秀日</div>
                  <div className="text-xs opacity-90">{data.title}</div>
                </div>
              </div>
            )}

            {data.type === 'TRADE' && (
              <div className="bg-gradient-to-r from-orange-600 to-red-700 p-3 rounded-lg flex items-center gap-3">
                <Repeat size={24} />
                <div>
                  <div className="font-bold text-sm">交易动态</div>
                  <div className="text-xs opacity-90">{data.title}</div>
                </div>
              </div>
            )}

            {/* 比赛列表展示 */}
            {data.games && (
              <div className="space-y-2">
                {data.games.map(game => (
                  <div 
                    key={game.id}
                    onClick={() => setSelectedGame(game)}
                    className="flex justify-between items-center p-3 bg-gray-700 hover:bg-gray-600 rounded-lg cursor-pointer transition-all border-l-4 border-blue-500"
                  >
                    <div className="flex flex-col">
                      <span className="font-bold text-lg">{game.away} @ {game.home}</span>
                      <span className="text-xs text-gray-400">{game.time} ET</span>
                    </div>
                    <div className="text-xs bg-gray-900 px-2 py-1 rounded text-blue-300 italic">
                      点击查看数据
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 数据详情悬浮框 (Modal) */}
      {selectedGame && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 border border-gray-600 rounded-2xl w-full max-w-md p-6 relative animate-in fade-in zoom-in duration-200">
            <button 
              onClick={() => setSelectedGame(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X size={24} />
            </button>
            
            <h2 className="text-xl font-bold mb-6 text-center">赛前详报</h2>
            
            <div className="flex justify-between items-center mb-8">
              <div className="text-center">
                <div className="text-3xl font-black mb-1 text-blue-400">{selectedGame.away}</div>
                <div className="text-xs text-gray-400">客队胜率: {selectedGame.awayStats}</div>
              </div>
              <div className="text-gray-500 font-italic text-xl">VS</div>
              <div className="text-center">
                <div className="text-3xl font-black mb-1 text-red-400">{selectedGame.home}</div>
                <div className="text-xs text-gray-400">主队胜率: {selectedGame.homeStats}</div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-900 p-4 rounded-xl">
                <div className="text-xs text-gray-500 uppercase mb-2 text-center tracking-widest">关键数据对比 (场均)</div>
                <div className="flex justify-between text-sm mb-1">
                  <span>115.4</span><span className="text-gray-500 text-[10px]">得分</span><span>112.1</span>
                </div>
                <div className="w-full bg-gray-700 h-2 rounded-full flex overflow-hidden">
                  <div className="bg-blue-500 h-full" style={{width: '52%'}}></div>
                  <div className="bg-red-500 h-full" style={{width: '48%'}}></div>
                </div>
              </div>
              <button className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-colors">
                查看球员伤病名单报告
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NBACalendar;