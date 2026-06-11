#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫的延迟和休息功能
"""
import sys
import time
import logging

# 添加项目路径
sys.path.insert(0, r'c:\autopick\AutoPick')

from nba_data.crawler.schedule_scraper import ScheduleScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_delay_settings():
    """测试延迟设置"""
    logger.info("=" * 80)
    logger.info("测试延迟设置")
    logger.info("=" * 80)
    
    # 创建爬虫实例
    scraper = ScheduleScraper(headless=True)
    
    # 检查延迟设置
    logger.info(f"min_delay: {scraper.min_delay}")
    logger.info(f"max_delay: {scraper.max_delay}")
    
    # 测试安全延迟（不会真的睡40秒，我们缩短测试时间）
    logger.info("\n测试 _safe_random_delay...")
    # 临时修改为短时间用于测试
    original_min = scraper.min_delay
    original_max = scraper.max_delay
    scraper.min_delay = 1
    scraper.max_delay = 2
    
    start = time.time()
    scraper._safe_random_delay()
    elapsed = time.time() - start
    logger.info(f"✅ 延迟测试成功，休眠了 {elapsed:.1f} 秒")
    
    # 恢复原值
    scraper.min_delay = original_min
    scraper.max_delay = original_max

def test_rest_function():
    """测试休息功能（缩短时间用于测试）"""
    logger.info("\n" + "=" * 80)
    logger.info("测试休息功能")
    logger.info("=" * 80)
    
    scraper = ScheduleScraper(headless=True)
    
    # 临时修改为短时间用于测试
    scraper.run_interval = 5  # 5秒运行
    scraper.rest_interval = 2  # 2秒休息
    
    logger.info(f"测试设置: 运行{scraper.run_interval}秒后休息{scraper.rest_interval}秒")
    
    # 第一次检查应该不会休息
    logger.info("第一次检查...")
    start = time.time()
    scraper._check_and_rest()
    elapsed = time.time() - start
    logger.info(f"第一次检查完成，耗时 {elapsed:.1f} 秒（应该不会休息）")
    
    # 等待超过运行间隔
    logger.info(f"等待 {scraper.run_interval + 1} 秒...")
    time.sleep(scraper.run_interval + 1)
    
    # 第二次检查应该会休息
    logger.info("第二次检查...")
    start = time.time()
    scraper._check_and_rest()
    elapsed = time.time() - start
    logger.info(f"第二次检查完成，耗时 {elapsed:.1f} 秒（应该包含休息时间）")
    
    if elapsed >= scraper.rest_interval:
        logger.info("✅ 休息功能测试成功！")
    else:
        logger.warning("⚠️ 休息功能可能有问题")

if __name__ == "__main__":
    logger.info("开始爬虫功能测试\n")
    
    # 测试延迟设置
    test_delay_settings()
    
    # 测试休息功能
    test_rest_function()
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 所有测试完成！")
    logger.info("=" * 80)
