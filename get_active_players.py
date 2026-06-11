import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from tqdm import tqdm
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

def get_active_players():
    """只获取现役球员的姓名和个人页面链接"""
    url = "https://www.basketball-reference.com/players/"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    active_players = []
    
    # 遍历所有字母分区
    for section in soup.find_all('div', id=lambda x: x and x.startswith('players_')):
        for a_tag in section.find_all('a', href=True):
            if '/players/' in a_tag['href'] and a_tag['href'].endswith('.html'):
                # 检查是否为现役（名字被加粗）
                parent = a_tag.parent
                is_active = False
                
                # 检查 <strong> 或 <b> 标签
                if a_tag.find('strong') or parent.find('strong') or a_tag.find('b'):
                    is_active = True
                # 有些是直接在 a 标签外包 strong
                elif parent.name in ['strong', 'b']:
                    is_active = True
                
                if is_active:
                    name = a_tag.text.strip()
                    link = "https://www.basketball-reference.com" + a_tag['href']
                    active_players.append({
                        'player_name': name,
                        'url': link
                    })
    
    df = pd.DataFrame(active_players)
    return df

# ==================== 主程序 ====================
if __name__ == "__main__":
    print("正在爬取现役球员列表...")
    df_active = get_active_players()
    
    print(f"✅ 共找到 {len(df_active)} 名现役球员")
    print(df_active.head(10))
    
    # 保存结果
    df_active.to_csv("nba_active_players_2026.csv", index=False, encoding='utf-8-sig')
    print("✅ 现役球员列表已保存为 nba_active_players_2026.csv")