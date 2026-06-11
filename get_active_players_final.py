import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

def get_active_players():
    """获取现役球员的姓名和个人页面链接"""
    active_players = []
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        url = f"https://www.basketball-reference.com/players/{letter.lower()}/"
        
        try:
            time.sleep(random.uniform(3, 5))
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                continue
            
            for row in table.find_all('tr'):
                th = row.find('th', {'data-stat': 'player'})
                if th:
                    a_tag = th.find('a')
                    if a_tag and '/players/' in a_tag['href']:
                        name = a_tag.get_text(strip=True)
                        link = "https://www.basketball-reference.com" + a_tag['href']
                        
                        to_year_cell = row.find('td', {'data-stat': 'year_max'})
                        to_year = to_year_cell.get_text(strip=True) if to_year_cell else ''
                        
                        if to_year == '' or int(to_year) >= 2025:
                            active_players.append({
                                'player_name': name,
                                'url': link,
                                'to_year': to_year
                            })
        
        except Exception as e:
            print(f"获取字母 {letter} 失败: {e}")
            time.sleep(10)
    
    df = pd.DataFrame(active_players)
    return df

if __name__ == "__main__":
    print("正在爬取现役球员列表...")
    df_active = get_active_players()
    
    print(f"✅ 共找到 {len(df_active)} 名现役球员")
    print(df_active.head(20))
    
    df_active.to_csv("nba_active_players_2026.csv", index=False, encoding='utf-8-sig')
    print("✅ 现役球员列表已保存为 nba_active_players_2026.csv")