from fastapi import APIRouter, HTTPException
import psycopg2
import os

router = APIRouter(prefix="/api", tags=["球员卡片"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@router.get("/player-cards-light")
def get_player_cards_light(limit: int = 100, offset: int = 0, include_avatar: bool = False):
    """获取简化版球员卡片信息（不包含头像以减小数据量）"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        actual_limit = min(limit, 100)
        
        cursor.execute("""
            SELECT player_id, name, nickname, bio, 
                   body_info, draft_info, jersey_numbers, is_coach
            FROM players
            WHERE name IS NOT NULL
            ORDER BY name
            LIMIT %s OFFSET %s
        """, (actual_limit, offset))
        
        columns = ['player_id', 'name', 'nickname', 'bio', 
                   'body_info', 'draft_info', 'jersey_numbers', 'is_coach']
        
        results = []
        for row in cursor.fetchall():
            player_data = dict(zip(columns, row))
            
            if player_data['bio'] and len(player_data['bio']) > 500:
                player_data['bio'] = player_data['bio'][:500] + '...'
            
            results.append(player_data)
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE name IS NOT NULL")
        total = cursor.fetchone()[0]
        
        return {
            "success": True,
            "count": len(results),
            "total": total,
            "limit": actual_limit,
            "offset": offset,
            "players": results
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
