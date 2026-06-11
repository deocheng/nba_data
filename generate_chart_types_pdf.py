"""
图表类型指南 PDF 生成器
使用 Playwright 将 chart_types_guide.html 转换为 PDF
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import sys

BASE_DIR = Path(__file__).parent
HTML_FILE = BASE_DIR / "static" / "chart_types_guide.html"
OUTPUT_DIR = BASE_DIR / "static" / "charts"
PDF_OUTPUT = OUTPUT_DIR / "nba_chart_types_guide.pdf"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def html_to_pdf():
    """将 HTML 页面转换为 PDF"""
    
    print("=" * 70)
    print("🏀 NBA图表类型指南 - PDF 生成器")
    print("=" * 70)
    print(f"\n📄 源文件: {HTML_FILE.name}")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📄 输出文件: {PDF_OUTPUT.name}")
    
    async with async_playwright() as p:
        print("\n🚀 启动浏览器...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080}
        )
        
        file_url = f'file://{HTML_FILE.resolve()}'
        print(f"🌐 打开页面: {file_url}")
        
        await page.goto(file_url, wait_until='networkidle')
        
        # 等待所有 Chart.js 图表渲染完成
        await asyncio.sleep(3)
        
        print(f"📄 正在生成 PDF...")
        
        # 生成 PDF
        await page.pdf(
            path=str(PDF_OUTPUT),
            format='A4',
            landscape=True,
            print_background=True,
            margin={
                'top': '1.0cm',
                'bottom': '1.0cm',
                'left': '1.0cm',
                'right': '1.0cm'
            }
        )
        
        await browser.close()
        
        print(f"\n✅ PDF 生成成功！")
        print(f"📍 文件位置: {PDF_OUTPUT}")
        print(f"📊 文件大小: {PDF_OUTPUT.stat().st_size / 1024:.2f} KB")
        
        return True

def generate_pdf_with_matplotlib():
    """备用方案：使用 matplotlib 生成 PDF"""
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
    
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    print("\n⚠️ 使用备用方案：matplotlib 生成")
    
    with PdfPages(PDF_OUTPUT) as pdf:
        # 封面
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.set_axis_off()
        ax.text(0.5, 0.6, 'NBA数据可视化图表类型指南', 
                ha='center', fontsize=32, fontweight='bold')
        ax.text(0.5, 0.5, 'Chart.js 4.x', ha='center', fontsize=18, color='#555')
        ax.text(0.5, 0.4, 'v1.0 | 2026年5月', ha='center', fontsize=14, color='#666')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # 基础图表类型
        fig, axes = plt.subplots(2, 3, figsize=(14, 10))
        fig.suptitle('基础图表类型', fontsize=18, fontweight='bold')
        
        # 条形图
        teams = ['SAS', 'OKC', 'MIN', 'DEN', 'GSW', 'BOS']
        scores = [115.3, 118.5, 112.8, 114.2, 113.5, 115.8]
        axes[0,0].bar(teams, scores, color='#3b82f6')
        axes[0,0].set_title('条形图 - 球队得分排名')
        axes[0,0].set_ylim(100, 125)
        
        # 折线图
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        trend = [112, 115, 118, 120, 117, 119]
        axes[0,1].plot(months, trend, marker='o', linewidth=2, color='#3b82f6')
        axes[0,1].set_title('折线图 - 得分趋势')
        axes[0,1].set_ylim(110, 122)
        
        # 饼图
        labels = ['两分球', '三分球', '罚球']
        sizes = [52, 32, 16]
        axes[0,2].pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#3b82f6', '#22c55e', '#f97316'])
        axes[0,2].set_title('饼图 - 得分分布')
        
        # 环形图
        labels = ['进攻篮板', '防守篮板']
        sizes = [218, 633]
        axes[1,0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#ef4444', '#3b82f6'], wedgeprops=dict(width=0.4))
        axes[1,0].set_title('环形图 - 篮板分布')
        
        # 雷达图（示意）
        axes[1,1].set_title('雷达图 - 球员能力')
        axes[1,1].text(0.5, 0.5, '雷达图', ha='center', fontsize=16)
        axes[1,1].set_axis_off()
        
        # 散点图
        x = [25.0, 22.1, 21.8, 18.9, 11.2]
        y = [3.1, 3.1, 3.2, 2.8, 5.1]
        axes[1,2].scatter(x, y, s=100, alpha=0.7, color='#3b82f6')
        axes[1,2].set_title('散点图 - 得分vs助攻')
        axes[1,2].set_xlabel('场均得分')
        axes[1,2].set_ylabel('场均助攻')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # 马刺季后赛数据
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('真实数据 - 马刺2026季后赛', fontsize=18, fontweight='bold')
        
        games = [f'G{i}' for i in range(1, 19)]
        spurs_scores = [111, 103, 120, 114, 114, 102, 133, 115, 109, 126, 139, 122, 113, 108, 103, 114, 118, 111]
        opp_scores = [98, 106, 108, 93, 95, 104, 95, 108, 114, 97, 109, 115, 122, 123, 82, 127, 91, 103]
        
        axes[0,0].plot(games, spurs_scores, label='马刺', marker='o', color='#3b82f6', linewidth=2)
        axes[0,0].plot(games, opp_scores, label='对手', marker='s', color='#ef4444', linewidth=2)
        axes[0,0].set_title('季后赛得分趋势')
        axes[0,0].legend()
        axes[0,0].tick_params(axis='x', rotation=45)
        
        axes[0,1].bar(games, spurs_scores, alpha=0.7, label='马刺', color='#3b82f6')
        axes[0,1].bar(games, opp_scores, alpha=0.5, label='对手', color='#ef4444')
        axes[0,1].set_title('得分对比')
        axes[0,1].legend()
        axes[0,1].tick_params(axis='x', rotation=45)
        
        opponents = ['POR', 'MIN', 'OKC']
        wins = [4, 4, 2]
        losses = [1, 2, 5]
        x = np.arange(len(opponents))
        width = 0.35
        axes[1,0].bar(x - width/2, wins, width, label='胜', color='#22c55e')
        axes[1,0].bar(x + width/2, losses, width, label='负', color='#ef4444')
        axes[1,0].set_xticks(x)
        axes[1,0].set_xticklabels(opponents)
        axes[1,0].set_title('对阵各队战绩')
        axes[1,0].legend()
        
        fg_pcts = [47.6, 44.2, 47.1, 49.4, 54.7, 44.8, 50.0, 45.9, 47.7, 52.8, 55.7, 42.7, 48.8, 42.5, 38.9, 40.2, 46.6, 45.5]
        three_pcts = [45.5, 29.2, 48.5, 42.4, 40.0, 27.8, 41.0, 36.4, 23.1, 34.4, 47.4, 30.2, 40.0, 31.7, 27.3, 29.3, 36.6, 42.5]
        axes[1,1].plot(games, fg_pcts, label='投篮%', marker='o', color='#3b82f6')
        axes[1,1].plot(games, three_pcts, label='三分%', marker='s', color='#22c55e')
        axes[1,1].set_title('命中率变化')
        axes[1,1].legend()
        axes[1,1].tick_params(axis='x', rotation=45)
        axes[1,1].set_ylim(20, 60)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # 功能特性页
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.set_axis_off()
        
        text = """
图表功能特性

• 交互功能：支持悬停提示、数据点点击、缩放、平移等操作
• 自定义样式：支持自定义颜色、字体、背景、边框等样式
• 响应式设计：自动适应不同屏幕尺寸，支持移动端展示
• 导出功能：支持导出为PNG、JPG、PDF等格式
• 实时更新：支持从API实时获取最新数据并更新图表
• 数据筛选：支持按时间、类别、球员等条件筛选数据

使用建议

1. 根据数据特点选择合适的图表类型，避免误导性展示
2. 保持图表简洁，避免在一个图表中展示过多数据系列
3. 使用清晰的标题、标签和图例，提高可读性
4. 确保颜色对比度足够，方便色盲用户阅读
5. 在打印或导出PDF时，注意调整页面布局和边距
6. 结合真实数据使用，避免使用虚假或过时的示例数据

数据来源：马刺2026季后赛真实比赛数据
        """
        
        ax.text(0.05, 0.95, text, ha='left', va='top', fontsize=12, 
                linespacing=1.6, transform=ax.transAxes)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"\n✅ PDF已成功保存到: {PDF_OUTPUT}")
    return True

if __name__ == "__main__":
    try:
        # 首先尝试用 Playwright 生成（需要安装 playwright）
        asyncio.run(html_to_pdf())
    except Exception as e:
        print(f"\n⚠️ Playwright方法失败: {e}")
        print("\n📊 尝试备用方案...")
        try:
            generate_pdf_with_matplotlib()
        except Exception as e2:
            print(f"\n❌ 两种方法都失败: {e2}")
            print("请确保安装了所需依赖:")
            print("  - pip install playwright matplotlib")
            print("  - playwright install chromium")
            sys.exit(1)
