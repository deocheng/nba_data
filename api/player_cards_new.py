from fastapi import APIRouter, HTTPException, Query
import psycopg2
import os
import json

router = APIRouter(prefix="/api", tags=["球员卡片"])

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    return conn

# 预加载的位置映射（从player_profiles表获取）
position_map = {}

def load_position_map():
    """预加载球员位置映射"""
    global position_map
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT player_name, position FROM player_profiles WHERE position IS NOT NULL")
        for row in cursor.fetchall():
            player_name = row[0].lower()
            position_map[player_name] = row[1]
            # 也添加姓氏匹配
            last_name = player_name.split()[-1]
            position_map[last_name] = row[1]
        conn.close()
        print(f"Loaded {len(position_map)} positions")
    except Exception as e:
        print(f"Error loading position map: {e}")

# 初始化位置映射
load_position_map()

def get_position_by_name(name):
    """根据球员名字获取位置"""
    name_lower = name.lower()
    # 精确匹配
    if name_lower in position_map:
        return position_map[name_lower]
    # 尝试姓氏匹配
    last_name = name_lower.split()[-1]
    if last_name in position_map:
        return position_map[last_name]
    # 尝试包含匹配
    for key in position_map:
        if key in name_lower or name_lower in key:
            return position_map[key]
    return None

@router.get("/player-cards")
def get_player_cards(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    team_id: str = None,
    position: str = None,
    include_avatar: bool = False
):
    """获取球员卡片信息（支持分页和筛选）"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        conditions = ["p.name IS NOT NULL"]
        params = []
        
        if team_id:
            conditions.append("p.team_id = %s")
            params.append(team_id)
        
        if position:
            conditions.append("pr.position = %s")
            params.append(position)
        
        query = f"""
            SELECT 
                p.player_id,
                p.name,
                p.nickname,
                {'p.avatar_url' if include_avatar else 'NULL as avatar_url'},
                pr.position,
                p.jersey_numbers,
                p.body_info,
                p.team_id,
                COALESCE(pr.career_teams, '[]'::jsonb) as career_teams,
                pr.height,
                pr.weight,
                pr.college
            FROM players p
            LEFT JOIN player_profiles pr 
                ON CAST(p.player_id AS VARCHAR) = pr.player_id
            WHERE {' AND '.join(conditions)}
            ORDER BY p.name
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        
        columns = [
            'player_id', 'name', 'nickname', 'avatar_url', 'position',
            'jersey_numbers', 'body_info', 'team_id', 'career_teams',
            'height', 'weight', 'college'
        ]
        
        results = []
        for row in cursor.fetchall():
            player_data = dict(zip(columns, row))
            
            # 如果位置为空，从映射中查找
            if not player_data['position']:
                player_data['position'] = get_position_by_name(player_data['name'])
            
            # 处理career_teams
            ct = player_data['career_teams']
            if ct and isinstance(ct, str):
                try:
                    player_data['career_teams'] = json.loads(ct)
                except:
                    player_data['career_teams'] = []
            
            # 提取球衣号码
            jn = player_data['jersey_numbers']
            if jn:
                numbers = jn.split(',')
                player_data['primary_number'] = numbers[0].strip() if numbers else None
            else:
                player_data['primary_number'] = None
            
            # 提取身体数据
            bi = player_data['body_info']
            if bi:
                parts = bi.split(',')
                if len(parts) > 0 and parts[0].strip():
                    player_data['height'] = parts[0].strip()
                if len(parts) > 1 and parts[1].strip():
                    player_data['weight'] = parts[1].strip()
            
            results.append(player_data)
        
        # 获取总数
        count_query = f"""
            SELECT COUNT(*) FROM players p
            LEFT JOIN player_profiles pr ON CAST(p.player_id AS VARCHAR) = pr.player_id
            WHERE {' AND '.join(conditions)}
        """
        cursor.execute(count_query, params[:-2])
        total = cursor.fetchone()[0]
        
        return {
            "success": True,
            "count": len(results),
            "total": total,
            "limit": limit,
            "offset": offset,
            "players": results
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@router.get("/player-cards/{player_id}")
def get_player_card_by_id(player_id: int):
    """根据ID获取单个球员卡片信息"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.player_id,
                p.name,
                p.nickname,
                p.avatar_url,
                pr.position,
                p.jersey_numbers,
                p.body_info,
                p.team_id,
                COALESCE(pr.career_teams, '[]'::jsonb) as career_teams,
                pr.height,
                pr.weight,
                pr.college
            FROM players p
            LEFT JOIN player_profiles pr 
                ON CAST(p.player_id AS VARCHAR) = pr.player_id
            WHERE p.player_id = %s
        """, (player_id,))
        
        columns = [
            'player_id', 'name', 'nickname', 'avatar_url', 'position',
            'jersey_numbers', 'body_info', 'team_id', 'career_teams',
            'height', 'weight', 'college'
        ]
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="球员未找到")
        
        player_data = dict(zip(columns, row))
        
        # 如果位置为空，从映射中查找
        if not player_data['position']:
            player_data['position'] = get_position_by_name(player_data['name'])
        
        # 处理career_teams
        ct = player_data['career_teams']
        if ct and isinstance(ct, str):
            try:
                player_data['career_teams'] = json.loads(ct)
            except:
                player_data['career_teams'] = []
        
        # 提取球衣号码
        jn = player_data['jersey_numbers']
        if jn:
            numbers = jn.split(',')
            player_data['primary_number'] = numbers[0].strip() if numbers else None
        else:
            player_data['primary_number'] = None
        
        # 提取身体数据
        bi = player_data['body_info']
        if bi:
            parts = bi.split(',')
            if len(parts) > 0 and parts[0].strip():
                player_data['height'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                player_data['weight'] = parts[1].strip()
        
        return {
            "success": True,
            "player": player_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
