'use client';
import { motion } from 'framer-motion';
import Image from 'next/image';

interface Player {
  player_id: number;
  name: string;
  team: 'home' | 'away';
  minutes: number;
  pts: number;
  reb: number;
  ast: number;
  plus_minus: number;
  efficiency: number;
  logo_url?: string;
}

interface PlayerParallelTracksProps {
  game: any;
  homePlayers: Player[];
  awayPlayers: Player[];
}

export function PlayerParallelTracks({ game, homePlayers, awayPlayers }: PlayerParallelTracksProps) {
  // 按出场时间排序
  const sortedHome = [...homePlayers].sort((a, b) => b.minutes - a.minutes);
  const sortedAway = [...awayPlayers].sort((a, b) => b.minutes - a.minutes);

  const maxMinutes = Math.max(
    ...sortedHome.map(p => p.minutes),
    ...sortedAway.map(p => p.minutes)
  );

  return (
    <div className="mt-12">
      <h3 className="text-2xl font-semibold mb-8 text-center">球员出场表现轨道</h3>

      <div className="grid grid-cols-2 gap-16">
        {/* 主队轨道 */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <Image src={game.home_logo} alt={game.home_name} width={32} height={32} />
            <h4 className="text-xl font-semibold">{game.home_name}</h4>
            <div className="text-2xl font-bold text-blue-600 ml-auto">{game.home_score}</div>
          </div>

          <div className="space-y-5">
            {sortedHome.map((player, idx) => (
              <motion.div
                key={player.player_id}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03 }}
                className="group relative"
              >
                <div className="flex items-center gap-4">
                  {/* 球员头像 */}
                  <div className="w-9 h-9 rounded-full overflow-hidden border border-gray-200">
                    <Image 
                      src={player.logo_url || `/player-placeholder.png`} 
                      alt={player.name} 
                      width={36} 
                      height={36} 
                    />
                  </div>

                  {/* 球员信息 */}
                  <div className="flex-1">
                    <div className="flex justify-between items-baseline">
                      <div className="font-medium">{player.name}</div>
                      <div className="text-sm text-gray-500 font-mono">
                        {player.minutes.toFixed(1)} MIN
                      </div>
                    </div>

                    {/* 平行轨道条 */}
                    <div className="mt-2 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(player.minutes / maxMinutes) * 100}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="h-full bg-blue-600 rounded-full group-hover:bg-blue-700 transition-colors"
                      />
                    </div>
                  </div>

                  {/* 数据标签 */}
                  <div className="text-right w-20">
                    <div className="font-semibold text-lg">{player.pts}</div>
                    <div className="text-xs text-gray-500">PTS</div>
                  </div>
                  <div className="text-right w-16">
                    <div className="font-medium">{player.reb}</div>
                    <div className="text-xs text-gray-500">REB</div>
                  </div>
                  <div className="text-right w-16">
                    <div className="font-medium">{player.ast}</div>
                    <div className="text-xs text-gray-500">AST</div>
                  </div>
                  <div className={`text-right w-14 font-mono ${
                    player.plus_minus >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {player.plus_minus > 0 && '+'}{player.plus_minus}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 客队轨道 */}
        <div>
          <div className="flex items-center gap-3 mb-6 justify-end">
            <div className="text-2xl font-bold text-red-600">{game.away_score}</div>
            <h4 className="text-xl font-semibold">{game.away_name}</h4>
            <Image src={game.away_logo} alt={game.away_name} width={32} height={32} />
          </div>

          <div className="space-y-5">
            {sortedAway.map((player, idx) => (
              <motion.div
                key={player.player_id}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03 }}
                className="group relative"
              >
                <div className="flex items-center gap-4 flex-row-reverse">
                  {/* 数据标签 */}
                  <div className="text-left w-14 font-mono">
                    {player.plus_minus > 0 && '+'}{player.plus_minus}
                  </div>
                  <div className="text-left w-16">
                    <div className="font-medium">{player.ast}</div>
                    <div className="text-xs text-gray-500">AST</div>
                  </div>
                  <div className="text-left w-16">
                    <div className="font-medium">{player.reb}</div>
                    <div className="text-xs text-gray-500">REB</div>
                  </div>
                  <div className="text-left w-20">
                    <div className="font-semibold text-lg">{player.pts}</div>
                    <div className="text-xs text-gray-500">PTS</div>
                  </div>

                  {/* 球员信息 */}
                  <div className="flex-1 text-right">
                    <div className="flex justify-between items-baseline">
                      <div className="text-sm text-gray-500 font-mono">
                        {player.minutes.toFixed(1)} MIN
                      </div>
                      <div className="font-medium">{player.name}</div>
                    </div>

                    <div className="mt-2 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(player.minutes / maxMinutes) * 100}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="h-full bg-red-600 rounded-full group-hover:bg-red-700 transition-colors"
                      />
                    </div>
                  </div>

                  {/* 球员头像 */}
                  <div className="w-9 h-9 rounded-full overflow-hidden border border-gray-200">
                    <Image 
                      src={player.logo_url || `/player-placeholder.png`} 
                      alt={player.name} 
                      width={36} 
                      height={36} 
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}