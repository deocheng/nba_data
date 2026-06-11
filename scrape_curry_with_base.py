import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crawler'))

from base_scraper import BBRefScraper
from bs4 import BeautifulSoup
import pandas as pd
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_curry_data(html_content):
    """解析库里的HTML页面数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    curry_data = {}
    
    meta_div = soup.find('div', id='meta')
    if meta_div:
        name_tag = meta_div.find('h1', itemprop='name')
        if name_tag:
            curry_data['name'] = name_tag.get_text(strip=True)
        
        position_tag = meta_div.find('strong', string='Position:')
        if position_tag:
            curry_data['position'] = position_tag.next_sibling.strip()
        
        height_tag = meta_div.find('span', itemprop='height')
        if height_tag:
            curry_data['height'] = height_tag.get_text(strip=True)
        
        weight_tag = meta_div.find('span', itemprop='weight')
        if weight_tag:
            curry_data['weight'] = weight_tag.get_text(strip=True)
        
        birth_date_tag = meta_div.find('span', itemprop='birthDate')
        if birth_date_tag:
            curry_data['birth_date'] = birth_date_tag.get_text(strip=True)
        
        team_tag = meta_div.find('strong', string='Team:')
        if team_tag:
            team_link = team_tag.find_next('a')
            if team_link:
                curry_data['team'] = team_link.get_text(strip=True)
    
    per_game_table = soup.find('table', id='per_game')
    if per_game_table:
        per_game_data = []
        rows = per_game_table.find('tbody').find_all('tr')
        
        for row in rows:
            if row.get('class') and ('thead' in row.get('class') or 'over_header' in row.get('class')):
                continue
            
            season_data = {}
            for cell in row.find_all(['th', 'td']):
                stat = cell.get('data-stat')
                value = cell.get_text(strip=True)
                season_data[stat] = value
            
            if season_data and 'season' in season_data:
                per_game_data.append(season_data)
        
        curry_data['per_game'] = per_game_data
    
    totals_table = soup.find('table', id='totals')
    if totals_table:
        totals_data = []
        rows = totals_table.find('tbody').find_all('tr')
        
        for row in rows:
            if row.get('class') and ('thead' in row.get('class') or 'over_header' in row.get('class')):
                continue
            
            season_data = {}
            for cell in row.find_all(['th', 'td']):
                stat = cell.get('data-stat')
                value = cell.get_text(strip=True)
                season_data[stat] = value
            
            if season_data and 'season' in season_data:
                totals_data.append(season_data)
        
        curry_data['totals'] = totals_data
    
    advanced_table = soup.find('table', id='advanced')
    if advanced_table:
        advanced_data = []
        rows = advanced_table.find('tbody').find_all('tr')
        
        for row in rows:
            if row.get('class') and ('thead' in row.get('class') or 'over_header' in row.get('class')):
                continue
            
            season_data = {}
            for cell in row.find_all(['th', 'td']):
                stat = cell.get('data-stat')
                value = cell.get_text(strip=True)
                season_data[stat] = value
            
            if season_data and 'season' in season_data:
                advanced_data.append(season_data)
        
        curry_data['advanced'] = advanced_data
    
    return curry_data

def save_curry_data(data):
    """保存库里的数据"""
    output_path = Path('player_data') / 'curry'
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / 'stephen_curry_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    if 'per_game' in data:
        df_per_game = pd.DataFrame(data['per_game'])
        df_per_game.to_csv(output_path / 'curry_per_game.csv', index=False, encoding='utf-8-sig')
    
    if 'totals' in data:
        df_totals = pd.DataFrame(data['totals'])
        df_totals.to_csv(output_path / 'curry_totals.csv', index=False, encoding='utf-8-sig')
    
    if 'advanced' in data:
        df_advanced = pd.DataFrame(data['advanced'])
        df_advanced.to_csv(output_path / 'curry_advanced.csv', index=False, encoding='utf-8-sig')
    
    logger.info(f"数据已保存到: {output_path}")

def display_curry_summary(data):
    """显示库里数据摘要"""
    print("\n" + "=" * 60)
    print(f"🏀 {data.get('name', 'Stephen Curry')}")
    print("=" * 60)
    print(f"位置: {data.get('position', 'N/A')}")
    print(f"身高: {data.get('height', 'N/A')}")
    print(f"体重: {data.get('weight', 'N/A')}")
    print(f"生日: {data.get('birth_date', 'N/A')}")
    print(f"球队: {data.get('team', 'N/A')}")
    print()
    
    if 'per_game' in data:
        print("📊 生涯场均数据:")
        recent_season = data['per_game'][-1] if data['per_game'] else {}
        print(f"  赛季: {recent_season.get('season', 'N/A')}")
        print(f"  场均得分: {recent_season.get('pts', 'N/A')}")
        print(f"  场均助攻: {recent_season.get('ast', 'N/A')}")
        print(f"  场均篮板: {recent_season.get('trb', 'N/A')}")
        print(f"  场均三分: {recent_season.get('fg3', 'N/A')}")
        print(f"  三分命中率: {recent_season.get('fg3_pct', 'N/A')}")
        print(f"  罚球命中率: {recent_season.get('ft_pct', 'N/A')}")
    
    print("\n📈 总三分命中数统计:")
    total_threes = 0
    for season in data.get('totals', []):
        if 'fg3' in season and season['fg3'].isdigit():
            total_threes += int(season['fg3'])
    print(f"  生涯总三分命中: {total_threes:,} 个")

if __name__ == "__main__":
    logger.info("正在爬取斯蒂芬·库里的数据...")
    logger.info("使用爬虫基类，包含3-5秒延迟和User-Agent轮换")
    
    try:
        scraper = BBRefScraper(delay_min=3, delay_max=5)
        html_content = scraper.get_player_page('curryst01')
        
        logger.info("解析数据...")
        curry_data = parse_curry_data(html_content)
        
        save_curry_data(curry_data)
        display_curry_summary(curry_data)
        
        print("\n✅ 数据爬取和解析完成！")
        
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()