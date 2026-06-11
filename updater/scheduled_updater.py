#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时更新模块 - 用于定期执行数据更新
"""
import schedule
import time
import logging
import json
from nba_data.updater.incremental_updater import IncrementalUpdater

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScheduledUpdater:
    """定时更新类"""
    
    def __init__(self):
        """
        初始化定时更新器
        """
        self.updater = IncrementalUpdater()
        self.teams_data = self._load_teams_data()
    
    def _load_teams_data(self):
        """
        加载球队数据
        
        Returns:
            球队数据
        """
        try:
            with open('nba_data/teams.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载球队数据失败: {e}")
            return []
    
    def update_daily(self):
        """
        每日更新任务
        """
        logger.info("执行每日更新任务")
        
        # 获取当前赛季
        from datetime import datetime
        current_year = datetime.now().year
        if datetime.now().month >= 10:
            season = f"{current_year}-{str(current_year + 1)[-2:]}"
        else:
            season = f"{current_year - 1}-{str(current_year)[-2:]}"
        
        # 执行增量更新
        self.updater.incremental_update(self.teams_data, season)
    
    def update_weekly(self):
        """
        每周更新任务
        """
        logger.info("执行每周更新任务")
        
        # 获取当前赛季
        from datetime import datetime
        current_year = datetime.now().year
        if datetime.now().month >= 10:
            season = f"{current_year}-{str(current_year + 1)[-2:]}"
        else:
            season = f"{current_year - 1}-{str(current_year)[-2:]}"
        
        # 执行增量更新
        self.updater.incremental_update(self.teams_data, season)
    
    def update_monthly(self):
        """
        每月更新任务
        """
        logger.info("执行每月更新任务")
        
        # 获取当前赛季
        from datetime import datetime
        current_year = datetime.now().year
        if datetime.now().month >= 10:
            season = f"{current_year}-{str(current_year + 1)[-2:]}"
        else:
            season = f"{current_year - 1}-{str(current_year)[-2:]}"
        
        # 执行增量更新
        self.updater.incremental_update(self.teams_data, season)
    
    def start_schedule(self):
        """
        启动定时任务
        """
        # 每天凌晨2点执行更新
        schedule.every().day.at("02:00").do(self.update_daily)
        
        # 每周一凌晨3点执行更新
        schedule.every().monday.at("03:00").do(self.update_weekly)
        
        # 每月1号凌晨4点执行更新
        schedule.every().month.at("04:00").do(self.update_monthly)
        
        logger.info("定时更新任务已启动")
        
        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    # 测试定时更新模块
    updater = ScheduledUpdater()
    
    # 立即执行一次更新
    updater.update_daily()
    
    # 启动定时任务
    # updater.start_schedule()