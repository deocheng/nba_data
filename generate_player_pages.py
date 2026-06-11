import os
import json

IMAGES_DIR = 'images'
STATIC_DIR = 'static'

PLAYER_DATA = {
    "Victor Wembanyama": {
        "id": "wembanyama",
        "player_id": 446,
        "position": "中锋/C",
        "height": "7' 4\" (2.24m)",
        "weight": "210 lbs (95kg)",
        "college": "海外联赛",
        "draft_info": {"year": 2023, "round": 1, "pick": 1, "team": "圣安东尼奥马刺"},
        "bio": "维克托·文班亚马是一位法国职业篮球运动员，现效力于NBA圣安东尼奥马刺队。他以其惊人的身高、运动能力和全面的技术闻名于世。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 2023, "end_year": None, "stats": {"games": 211, "avg_points": 22.7, "avg_rebounds": 10.8, "avg_assists": 3.1}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 2024, "note": "全票当选"},
            {"award": "最佳防守球员", "year": 2025, "note": "历史最年轻DPOY"},
            {"award": "全明星", "year": 2025, "note": "西部首发"},
            {"award": "全明星", "year": 2026, "note": "西部首发"}
        ]
    },
    "LeBron James": {
        "id": "lebron",
        "player_id": 2544,
        "position": "前锋/F",
        "height": "6' 9\" (2.06m)",
        "weight": "250 lbs (113kg)",
        "college": "圣文森特-圣玛丽高中",
        "draft_info": {"year": 2003, "round": 1, "pick": 1, "team": "克利夫兰骑士"},
        "bio": "勒布朗·詹姆斯是NBA历史上最伟大的球员之一，拥有4座总冠军、4个MVP和4个FMVP。他以全能的比赛风格和惊人的运动能力著称。",
        "career_teams": [
            {"team": "克利夫兰骑士", "start_year": 2003, "end_year": 2010, "stats": {"games": 541, "avg_points": 27.8, "avg_rebounds": 7.0, "avg_assists": 7.0}},
            {"team": "迈阿密热火", "start_year": 2010, "end_year": 2014, "stats": {"games": 294, "avg_points": 26.9, "avg_rebounds": 7.6, "avg_assists": 6.7}},
            {"team": "克利夫兰骑士", "start_year": 2014, "end_year": 2018, "stats": {"games": 310, "avg_points": 26.1, "avg_rebounds": 7.7, "avg_assists": 8.0}},
            {"team": "洛杉矶湖人", "start_year": 2018, "end_year": None, "stats": {"games": 422, "avg_points": 27.2, "avg_rebounds": 8.2, "avg_assists": 8.4}}
        ],
        "awards": [
            {"award": "常规赛MVP", "year": 2009, "note": "骑士队史首座MVP"},
            {"award": "常规赛MVP", "year": 2010, "note": "蝉联MVP"},
            {"award": "总冠军", "year": 2012, "note": "热火首冠"},
            {"award": "总决赛MVP", "year": 2012, "note": ""},
            {"award": "常规赛MVP", "year": 2012, "note": "年度三双"},
            {"award": "总冠军", "year": 2013, "note": "连冠"},
            {"award": "总决赛MVP", "year": 2013, "note": ""},
            {"award": "总冠军", "year": 2016, "note": "骑士队史首冠"},
            {"award": "总决赛MVP", "year": 2016, "note": "1-3逆转"},
            {"award": "总冠军", "year": 2020, "note": "湖人总冠军"},
            {"award": "总决赛MVP", "year": 2020, "note": ""},
            {"award": "全明星MVP", "year": 2006, "note": ""},
            {"award": "全明星MVP", "year": 2008, "note": ""},
            {"award": "全明星MVP", "year": 2018, "note": ""},
            {"award": "全明星MVP", "year": 2023, "note": "家乡克利夫兰"}
        ]
    },
    "Michael Jordan": {
        "id": "jordan",
        "player_id": 893,
        "position": "后卫/G",
        "height": "6' 6\" (1.98m)",
        "weight": "216 lbs (98kg)",
        "college": "北卡罗来纳大学",
        "draft_info": {"year": 1984, "round": 1, "pick": 3, "team": "芝加哥公牛"},
        "bio": "迈克尔·乔丹被广泛认为是NBA历史上最伟大的球员。他带领芝加哥公牛队获得6座总冠军，拥有5个MVP和6个FMVP。",
        "career_teams": [
            {"team": "芝加哥公牛", "start_year": 1984, "end_year": 1993, "stats": {"games": 667, "avg_points": 32.3, "avg_rebounds": 6.3, "avg_assists": 5.9}},
            {"team": "芝加哥公牛", "start_year": 1995, "end_year": 1998, "stats": {"games": 308, "avg_points": 29.6, "avg_rebounds": 5.3, "avg_assists": 4.8}},
            {"team": "华盛顿奇才", "start_year": 2001, "end_year": 2003, "stats": {"games": 142, "avg_points": 20.0, "avg_rebounds": 6.1, "avg_assists": 3.8}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1985, "note": ""},
            {"award": "常规赛MVP", "year": 1988, "note": ""},
            {"award": "常规赛MVP", "year": 1991, "note": ""},
            {"award": "总冠军", "year": 1991, "note": ""},
            {"award": "总决赛MVP", "year": 1991, "note": ""},
            {"award": "常规赛MVP", "year": 1992, "note": ""},
            {"award": "总冠军", "year": 1992, "note": ""},
            {"award": "总决赛MVP", "year": 1992, "note": ""},
            {"award": "常规赛MVP", "year": 1993, "note": ""},
            {"award": "总冠军", "year": 1993, "note": ""},
            {"award": "总决赛MVP", "year": 1993, "note": ""},
            {"award": "常规赛MVP", "year": 1996, "note": ""},
            {"award": "总冠军", "year": 1996, "note": "72胜赛季"},
            {"award": "总决赛MVP", "year": 1996, "note": ""},
            {"award": "常规赛MVP", "year": 1997, "note": ""},
            {"award": "总冠军", "year": 1997, "note": ""},
            {"award": "总决赛MVP", "year": 1997, "note": ""},
            {"award": "总冠军", "year": 1998, "note": ""},
            {"award": "总决赛MVP", "year": 1998, "note": ""},
            {"award": "全明星MVP", "year": 1988, "note": ""},
            {"award": "全明星MVP", "year": 1996, "note": ""},
            {"award": "全明星MVP", "year": 1998, "note": ""},
            {"award": "最佳防守球员", "year": 1988, "note": ""}
        ]
    },
    "Kobe Bryant": {
        "id": "kobe",
        "player_id": 977,
        "position": "后卫/G",
        "height": "6' 6\" (1.98m)",
        "weight": "205 lbs (93kg)",
        "college": "劳尔梅里恩高中",
        "draft_info": {"year": 1996, "round": 1, "pick": 13, "team": "夏洛特黄蜂"},
        "bio": "科比·布莱恩特是洛杉矶湖人队的传奇球星，职业生涯获得5座总冠军，以其曼巴精神和出色的得分能力闻名。",
        "career_teams": [
            {"team": "洛杉矶湖人", "start_year": 1996, "end_year": 2016, "stats": {"games": 1346, "avg_points": 25.0, "avg_rebounds": 5.2, "avg_assists": 4.7}}
        ],
        "awards": [
            {"award": "总冠军", "year": 2000, "note": ""},
            {"award": "总冠军", "year": 2001, "note": ""},
            {"award": "总冠军", "year": 2002, "note": "三连冠"},
            {"award": "常规赛MVP", "year": 2008, "note": ""},
            {"award": "总冠军", "year": 2009, "note": ""},
            {"award": "总决赛MVP", "year": 2009, "note": ""},
            {"award": "总冠军", "year": 2010, "note": ""},
            {"award": "总决赛MVP", "year": 2010, "note": ""},
            {"award": "全明星MVP", "year": 2002, "note": ""},
            {"award": "全明星MVP", "year": 2007, "note": ""},
            {"award": "全明星MVP", "year": 2009, "note": "与奥尼尔共享"},
            {"award": "全明星MVP", "year": 2011, "note": ""}
        ]
    },
    "Tim Duncan": {
        "id": "duncan",
        "player_id": 1495,
        "position": "前锋/C",
        "height": "6' 11\" (2.11m)",
        "weight": "250 lbs (113kg)",
        "college": "维克森林大学",
        "draft_info": {"year": 1997, "round": 1, "pick": 1, "team": "圣安东尼奥马刺"},
        "bio": "蒂姆·邓肯是马刺队史最伟大的球员，带领球队获得5座总冠军，以其稳定的表现和低调的性格闻名。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 1997, "end_year": 2016, "stats": {"games": 1392, "avg_points": 19.0, "avg_rebounds": 10.8, "avg_assists": 3.0}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1998, "note": ""},
            {"award": "常规赛MVP", "year": 2002, "note": ""},
            {"award": "常规赛MVP", "year": 2003, "note": ""},
            {"award": "总冠军", "year": 1999, "note": ""},
            {"award": "总决赛MVP", "year": 1999, "note": ""},
            {"award": "总冠军", "year": 2003, "note": ""},
            {"award": "总决赛MVP", "year": 2003, "note": ""},
            {"award": "总冠军", "year": 2005, "note": ""},
            {"award": "总决赛MVP", "year": 2005, "note": ""},
            {"award": "总冠军", "year": 2007, "note": ""},
            {"award": "总冠军", "year": 2014, "note": ""}
        ]
    },
    "Stephen Curry": {
        "id": "curry",
        "player_id": 201939,
        "position": "后卫/G",
        "height": "6' 2\" (1.88m)",
        "weight": "185 lbs (84kg)",
        "college": "戴维森学院",
        "draft_info": {"year": 2009, "round": 1, "pick": 7, "team": "金州勇士"},
        "bio": "斯蒂芬·库里是NBA历史上最伟大的三分球射手，带领勇士队获得4座总冠军，拥有2个MVP。",
        "career_teams": [
            {"team": "金州勇士", "start_year": 2009, "end_year": None, "stats": {"games": 984, "avg_points": 24.6, "avg_rebounds": 4.7, "avg_assists": 6.5}}
        ],
        "awards": [
            {"award": "常规赛MVP", "year": 2015, "note": ""},
            {"award": "常规赛MVP", "year": 2016, "note": "全票当选"},
            {"award": "总冠军", "year": 2015, "note": ""},
            {"award": "总冠军", "year": 2017, "note": ""},
            {"award": "总冠军", "year": 2018, "note": ""},
            {"award": "总冠军", "year": 2022, "note": ""},
            {"award": "总决赛MVP", "year": 2022, "note": ""},
            {"award": "全明星MVP", "year": 2021, "note": ""}
        ]
    },
    "Kevin Durant": {
        "id": "durant",
        "player_id": 201142,
        "position": "前锋/F",
        "height": "6' 11\" (2.11m)",
        "weight": "240 lbs (109kg)",
        "college": "德克萨斯大学",
        "draft_info": {"year": 2007, "round": 1, "pick": 2, "team": "西雅图超音速"},
        "bio": "凯文·杜兰特是NBA历史上最伟大的得分手之一，拥有2个总冠军和1个MVP，以其无解的投篮能力著称。",
        "career_teams": [
            {"team": "西雅图超音速/俄克拉荷马城雷霆", "start_year": 2007, "end_year": 2016, "stats": {"games": 641, "avg_points": 27.4, "avg_rebounds": 7.0, "avg_assists": 3.7}},
            {"team": "金州勇士", "start_year": 2016, "end_year": 2019, "stats": {"games": 208, "avg_points": 25.8, "avg_rebounds": 7.1, "avg_assists": 5.1}},
            {"team": "布鲁克林篮网", "start_year": 2019, "end_year": 2023, "stats": {"games": 183, "avg_points": 29.9, "avg_rebounds": 7.1, "avg_assists": 5.8}},
            {"team": "菲尼克斯太阳", "start_year": 2023, "end_year": None, "stats": {"games": 109, "avg_points": 27.0, "avg_rebounds": 7.0, "avg_assists": 5.5}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 2008, "note": ""},
            {"award": "常规赛MVP", "year": 2014, "note": ""},
            {"award": "总冠军", "year": 2017, "note": ""},
            {"award": "总决赛MVP", "year": 2017, "note": ""},
            {"award": "总冠军", "year": 2018, "note": ""},
            {"award": "总决赛MVP", "year": 2018, "note": ""},
            {"award": "全明星MVP", "year": 2012, "note": ""},
            {"award": "全明星MVP", "year": 2024, "note": ""}
        ]
    },
    "Nikola Jokić": {
        "id": "jokic",
        "player_id": 203999,
        "position": "中锋/C",
        "height": "6' 11\" (2.11m)",
        "weight": "284 lbs (129kg)",
        "college": "海外联赛",
        "draft_info": {"year": 2014, "round": 2, "pick": 41, "team": "丹佛掘金"},
        "bio": "尼古拉·约基奇是NBA历史上最具传球能力的中锋之一，带领掘金队获得首座总冠军，拥有2个MVP。",
        "career_teams": [
            {"team": "丹佛掘金", "start_year": 2015, "end_year": None, "stats": {"games": 767, "avg_points": 20.2, "avg_rebounds": 10.5, "avg_assists": 6.6}}
        ],
        "awards": [
            {"award": "常规赛MVP", "year": 2021, "note": ""},
            {"award": "常规赛MVP", "year": 2022, "note": ""},
            {"award": "总冠军", "year": 2023, "note": "掘金队史首冠"},
            {"award": "总决赛MVP", "year": 2023, "note": ""}
        ]
    },
    "Giannis Antetokounmpo": {
        "id": "giannis",
        "player_id": 203507,
        "position": "前锋/F",
        "height": "6' 11\" (2.11m)",
        "weight": "243 lbs (110kg)",
        "college": "海外联赛",
        "draft_info": {"year": 2013, "round": 1, "pick": 15, "team": "密尔沃基雄鹿"},
        "bio": "扬尼斯·阿德托昆博是NBA最具统治力的球员之一，带领雄鹿队获得总冠军，拥有2个MVP和1个FMVP。",
        "career_teams": [
            {"team": "密尔沃基雄鹿", "start_year": 2013, "end_year": None, "stats": {"games": 845, "avg_points": 22.9, "avg_rebounds": 9.6, "avg_assists": 4.8}}
        ],
        "awards": [
            {"award": "常规赛MVP", "year": 2019, "note": ""},
            {"award": "常规赛MVP", "year": 2020, "note": ""},
            {"award": "总冠军", "year": 2021, "note": "雄鹿队史首冠"},
            {"award": "总决赛MVP", "year": 2021, "note": ""},
            {"award": "最佳防守球员", "year": 2020, "note": ""},
            {"award": "全明星MVP", "year": 2021, "note": ""}
        ]
    },
    "Hakeem Olajuwon": {
        "id": "olajuwon",
        "player_id": 264,
        "position": "中锋/C",
        "height": "7' 0\" (2.13m)",
        "weight": "255 lbs (116kg)",
        "college": "休斯顿大学",
        "draft_info": {"year": 1984, "round": 1, "pick": 1, "team": "休斯顿火箭"},
        "bio": "哈基姆·奥拉朱旺是NBA历史上最伟大的中锋之一，带领火箭队获得2座总冠军，以其梦幻脚步闻名于世。",
        "career_teams": [
            {"team": "休斯顿火箭", "start_year": 1984, "end_year": 2001, "stats": {"games": 1177, "avg_points": 21.8, "avg_rebounds": 11.1, "avg_assists": 2.5}},
            {"team": "多伦多猛龙", "start_year": 2001, "end_year": 2002, "stats": {"games": 61, "avg_points": 7.1, "avg_rebounds": 6.0, "avg_assists": 1.1}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1985, "note": ""},
            {"award": "常规赛MVP", "year": 1994, "note": ""},
            {"award": "总冠军", "year": 1994, "note": ""},
            {"award": "总决赛MVP", "year": 1994, "note": ""},
            {"award": "最佳防守球员", "year": 1993, "note": ""},
            {"award": "最佳防守球员", "year": 1994, "note": ""},
            {"award": "总冠军", "year": 1995, "note": ""},
            {"award": "总决赛MVP", "year": 1995, "note": ""}
        ]
    },
    "Shaquille O'Neal": {
        "id": "shaq",
        "player_id": 893,
        "position": "中锋/C",
        "height": "7' 1\" (2.16m)",
        "weight": "325 lbs (147kg)",
        "college": "路易斯安那州立大学",
        "draft_info": {"year": 1992, "round": 1, "pick": 1, "team": "奥兰多魔术"},
        "bio": "沙奎尔·奥尼尔是NBA历史上最具统治力的中锋之一，获得4座总冠军，以其强大的内线进攻和幽默性格闻名。",
        "career_teams": [
            {"team": "奥兰多魔术", "start_year": 1992, "end_year": 1996, "stats": {"games": 349, "avg_points": 27.2, "avg_rebounds": 12.5, "avg_assists": 2.8}},
            {"team": "洛杉矶湖人", "start_year": 1996, "end_year": 2004, "stats": {"games": 514, "avg_points": 27.0, "avg_rebounds": 11.8, "avg_assists": 3.1}},
            {"team": "迈阿密热火", "start_year": 2004, "end_year": 2008, "stats": {"games": 205, "avg_points": 19.6, "avg_rebounds": 9.1, "avg_assists": 1.9}},
            {"team": "菲尼克斯太阳", "start_year": 2008, "end_year": 2009, "stats": {"games": 81, "avg_points": 17.8, "avg_rebounds": 8.4, "avg_assists": 1.7}},
            {"team": "克里夫兰骑士", "start_year": 2009, "end_year": 2010, "stats": {"games": 53, "avg_points": 12.0, "avg_rebounds": 6.7, "avg_assists": 1.5}},
            {"team": "波士顿凯尔特人", "start_year": 2010, "end_year": 2011, "stats": {"games": 37, "avg_points": 9.2, "avg_rebounds": 4.8, "avg_assists": 0.7}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1993, "note": ""},
            {"award": "常规赛MVP", "year": 2000, "note": ""},
            {"award": "总冠军", "year": 2000, "note": ""},
            {"award": "总决赛MVP", "year": 2000, "note": ""},
            {"award": "总冠军", "year": 2001, "note": ""},
            {"award": "总决赛MVP", "year": 2001, "note": ""},
            {"award": "总冠军", "year": 2002, "note": ""},
            {"award": "总决赛MVP", "year": 2002, "note": ""},
            {"award": "总冠军", "year": 2006, "note": ""},
            {"award": "全明星MVP", "year": 2000, "note": ""},
            {"award": "全明星MVP", "year": 2004, "note": ""},
            {"award": "全明星MVP", "year": 2009, "note": "与科比共享"}
        ]
    },
    "Yao Ming": {
        "id": "yao",
        "player_id": 2108,
        "position": "中锋/C",
        "height": "7' 6\" (2.29m)",
        "weight": "310 lbs (141kg)",
        "college": "海外联赛",
        "draft_info": {"year": 2002, "round": 1, "pick": 1, "team": "休斯顿火箭"},
        "bio": "姚明是中国篮球的传奇人物，NBA历史上最伟大的国际球员之一，以其出色的技术和对中国篮球的推广贡献闻名。",
        "career_teams": [
            {"team": "休斯顿火箭", "start_year": 2002, "end_year": 2011, "stats": {"games": 486, "avg_points": 19.0, "avg_rebounds": 9.2, "avg_assists": 1.6}}
        ],
        "awards": [
            {"award": "最佳新秀一阵", "year": 2003, "note": ""},
            {"award": "全明星", "year": 2003, "note": "西部首发"},
            {"award": "全明星", "year": 2004, "note": "西部首发"},
            {"award": "全明星", "year": 2005, "note": "西部首发"},
            {"award": "全明星", "year": 2006, "note": "西部首发"},
            {"award": "全明星", "year": 2007, "note": "西部首发"},
            {"award": "全明星", "year": 2008, "note": "西部首发"},
            {"award": "全明星", "year": 2009, "note": "西部首发"},
            {"award": "全明星", "year": 2010, "note": "西部首发"},
            {"award": "奈史密斯名人堂", "year": 2016, "note": ""}
        ]
    },
    "Allen Iverson": {
        "id": "iverson",
        "player_id": 947,
        "position": "后卫/G",
        "height": "6' 0\" (1.83m)",
        "weight": "165 lbs (75kg)",
        "college": "乔治城大学",
        "draft_info": {"year": 1996, "round": 1, "pick": 1, "team": "费城76人"},
        "bio": "阿伦·艾弗森是NBA历史上最具影响力的球员之一，以其出色的得分能力和独特的个性闻名，拥有1个MVP。",
        "career_teams": [
            {"team": "费城76人", "start_year": 1996, "end_year": 2006, "stats": {"games": 711, "avg_points": 28.1, "avg_rebounds": 3.8, "avg_assists": 6.1}},
            {"team": "丹佛掘金", "start_year": 2006, "end_year": 2008, "stats": {"games": 130, "avg_points": 26.4, "avg_rebounds": 3.0, "avg_assists": 7.2}},
            {"team": "底特律活塞", "start_year": 2008, "end_year": 2009, "stats": {"games": 54, "avg_points": 17.4, "avg_rebounds": 3.1, "avg_assists": 4.9}},
            {"team": "孟菲斯灰熊", "start_year": 2009, "end_year": 2010, "stats": {"games": 3, "avg_points": 12.3, "avg_rebounds": 1.0, "avg_assists": 3.7}},
            {"team": "费城76人", "start_year": 2010, "end_year": 2010, "stats": {"games": 25, "avg_points": 13.9, "avg_rebounds": 2.8, "avg_assists": 4.1}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1997, "note": ""},
            {"award": "常规赛MVP", "year": 2001, "note": ""},
            {"award": "全明星MVP", "year": 2001, "note": ""},
            {"award": "全明星MVP", "year": 2005, "note": ""}
        ]
    },
    "Chris Paul": {
        "id": "paul",
        "player_id": 101108,
        "position": "后卫/G",
        "height": "6' 0\" (1.83m)",
        "weight": "175 lbs (79kg)",
        "college": "维克森林大学",
        "draft_info": {"year": 2005, "round": 1, "pick": 4, "team": "新奥尔良黄蜂"},
        "bio": "克里斯·保罗是NBA历史上最伟大的控球后卫之一，以其出色的传球和防守能力闻名，拥有多个助攻王和抢断王头衔。",
        "career_teams": [
            {"team": "新奥尔良黄蜂", "start_year": 2005, "end_year": 2011, "stats": {"games": 425, "avg_points": 18.7, "avg_rebounds": 4.1, "avg_assists": 9.8}},
            {"team": "洛杉矶快船", "start_year": 2011, "end_year": 2017, "stats": {"games": 409, "avg_points": 18.8, "avg_rebounds": 4.4, "avg_assists": 9.9}},
            {"team": "休斯顿火箭", "start_year": 2017, "end_year": 2019, "stats": {"games": 154, "avg_points": 17.1, "avg_rebounds": 5.0, "avg_assists": 8.0}},
            {"team": "俄克拉荷马城雷霆", "start_year": 2019, "end_year": 2020, "stats": {"games": 70, "avg_points": 17.6, "avg_rebounds": 5.0, "avg_assists": 6.7}},
            {"team": "菲尼克斯太阳", "start_year": 2020, "end_year": 2023, "stats": {"games": 191, "avg_points": 14.8, "avg_rebounds": 4.5, "avg_assists": 9.4}},
            {"team": "金州勇士", "start_year": 2023, "end_year": None, "stats": {"games": 111, "avg_points": 10.1, "avg_rebounds": 3.7, "avg_assists": 4.7}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 2006, "note": ""},
            {"award": "全明星MVP", "year": 2013, "note": ""},
            {"award": "全明星MVP", "year": 2024, "note": ""}
        ]
    },
    "James Harden": {
        "id": "harden",
        "player_id": 201935,
        "position": "后卫/G",
        "height": "6' 5\" (1.96m)",
        "weight": "220 lbs (100kg)",
        "college": "亚利桑那州立大学",
        "draft_info": {"year": 2009, "round": 1, "pick": 3, "team": "俄克拉荷马城雷霆"},
        "bio": "詹姆斯·哈登是NBA历史上最出色的得分手之一，以其独特的后撤步三分和造犯规能力闻名，拥有1个MVP。",
        "career_teams": [
            {"team": "俄克拉荷马城雷霆", "start_year": 2009, "end_year": 2012, "stats": {"games": 259, "avg_points": 12.2, "avg_rebounds": 3.2, "avg_assists": 2.5}},
            {"team": "休斯顿火箭", "start_year": 2012, "end_year": 2021, "stats": {"games": 621, "avg_points": 29.6, "avg_rebounds": 6.0, "avg_assists": 7.7}},
            {"team": "布鲁克林篮网", "start_year": 2021, "end_year": 2022, "stats": {"games": 80, "avg_points": 22.0, "avg_rebounds": 7.0, "avg_assists": 10.3}},
            {"team": "费城76人", "start_year": 2022, "end_year": 2023, "stats": {"games": 80, "avg_points": 21.0, "avg_rebounds": 6.1, "avg_assists": 10.5}},
            {"team": "洛杉矶快船", "start_year": 2023, "end_year": None, "stats": {"games": 82, "avg_points": 18.6, "avg_rebounds": 5.6, "avg_assists": 8.5}}
        ],
        "awards": [
            {"award": "最佳第六人", "year": 2012, "note": ""},
            {"award": "常规赛MVP", "year": 2018, "note": ""},
            {"award": "全明星MVP", "year": 2018, "note": ""}
        ]
    },
    "Russell Westbrook": {
        "id": "westbrook",
        "player_id": 201566,
        "position": "后卫/G",
        "height": "6' 3\" (1.91m)",
        "weight": "200 lbs (91kg)",
        "college": "加州大学洛杉矶分校",
        "draft_info": {"year": 2008, "round": 1, "pick": 4, "team": "西雅图超音速"},
        "bio": "拉塞尔·威斯布鲁克是NBA历史上最具爆发力的球员之一，以其全能的表现和多次三双纪录闻名，拥有1个MVP。",
        "career_teams": [
            {"team": "俄克拉荷马城雷霆", "start_year": 2008, "end_year": 2019, "stats": {"games": 821, "avg_points": 23.0, "avg_rebounds": 7.0, "avg_assists": 8.4}},
            {"team": "休斯顿火箭", "start_year": 2019, "end_year": 2020, "stats": {"games": 57, "avg_points": 27.2, "avg_rebounds": 7.9, "avg_assists": 7.0}},
            {"team": "华盛顿奇才", "start_year": 2020, "end_year": 2021, "stats": {"games": 65, "avg_points": 22.2, "avg_rebounds": 11.5, "avg_assists": 11.7}},
            {"team": "洛杉矶湖人", "start_year": 2021, "end_year": 2023, "stats": {"games": 130, "avg_points": 17.4, "avg_rebounds": 7.9, "avg_assists": 7.5}},
            {"team": "洛杉矶快船", "start_year": 2023, "end_year": 2024, "stats": {"games": 21, "avg_points": 15.9, "avg_rebounds": 4.3, "avg_assists": 7.5}},
            {"team": "丹佛掘金", "start_year": 2024, "end_year": None, "stats": {"games": 1, "avg_points": 0.0, "avg_rebounds": 0.0, "avg_assists": 0.0}}
        ],
        "awards": [
            {"award": "最佳新秀一阵", "year": 2009, "note": ""},
            {"award": "常规赛MVP", "year": 2017, "note": "场均三双"},
            {"award": "全明星MVP", "year": 2015, "note": ""},
            {"award": "全明星MVP", "year": 2016, "note": ""}
        ]
    },
    "Kawhi Leonard": {
        "id": "kawhi",
        "player_id": 202695,
        "position": "前锋/F",
        "height": "6' 7\" (2.01m)",
        "weight": "225 lbs (102kg)",
        "college": "圣迭戈州立大学",
        "draft_info": {"year": 2011, "round": 1, "pick": 15, "team": "圣安东尼奥马刺"},
        "bio": "科怀·伦纳德是NBA最出色的双向球员之一，以其出色的防守和关键时刻的表现闻名，拥有2个总冠军和2个FMVP。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 2011, "end_year": 2018, "stats": {"games": 407, "avg_points": 15.2, "avg_rebounds": 6.0, "avg_assists": 2.3}},
            {"team": "多伦多猛龙", "start_year": 2018, "end_year": 2019, "stats": {"games": 60, "avg_points": 26.6, "avg_rebounds": 7.3, "avg_assists": 3.3}},
            {"team": "洛杉矶快船", "start_year": 2019, "end_year": None, "stats": {"games": 334, "avg_points": 24.8, "avg_rebounds": 6.5, "avg_assists": 4.6}}
        ],
        "awards": [
            {"award": "最佳新秀一阵", "year": 2012, "note": ""},
            {"award": "总冠军", "year": 2014, "note": ""},
            {"award": "总决赛MVP", "year": 2014, "note": ""},
            {"award": "最佳防守球员", "year": 2015, "note": ""},
            {"award": "最佳防守球员", "year": 2016, "note": ""},
            {"award": "总冠军", "year": 2019, "note": "猛龙队史首冠"},
            {"award": "总决赛MVP", "year": 2019, "note": ""}
        ]
    },
    "Devin Booker": {
        "id": "booker",
        "player_id": 203952,
        "position": "后卫/G",
        "height": "6' 6\" (1.98m)",
        "weight": "206 lbs (93kg)",
        "college": "肯塔基大学",
        "draft_info": {"year": 2015, "round": 1, "pick": 13, "team": "菲尼克斯太阳"},
        "bio": "德文·布克是NBA最出色的年轻得分手之一，以其出色的投篮能力和关键时刻的表现闻名。",
        "career_teams": [
            {"team": "菲尼克斯太阳", "start_year": 2015, "end_year": None, "stats": {"games": 699, "avg_points": 23.4, "avg_rebounds": 4.1, "avg_assists": 4.6}}
        ],
        "awards": [
            {"award": "最佳新秀一阵", "year": 2016, "note": ""},
            {"award": "全明星", "year": 2020, "note": ""},
            {"award": "全明星", "year": 2021, "note": ""},
            {"award": "全明星", "year": 2022, "note": ""},
            {"award": "全明星", "year": 2023, "note": ""},
            {"award": "全明星", "year": 2024, "note": ""},
            {"award": "全明星MVP", "year": 2024, "note": ""}
        ]
    },
    "Kyrie Irving": {
        "id": "kyrie",
        "player_id": 202681,
        "position": "后卫/G",
        "height": "6' 2\" (1.88m)",
        "weight": "195 lbs (88kg)",
        "college": "杜克大学",
        "draft_info": {"year": 2011, "round": 1, "pick": 1, "team": "克利夫兰骑士"},
        "bio": "凯里·欧文是NBA最出色的控球手之一，以其华丽的运球和关键时刻的表现闻名，拥有1个总冠军。",
        "career_teams": [
            {"team": "克利夫兰骑士", "start_year": 2011, "end_year": 2017, "stats": {"games": 416, "avg_points": 21.6, "avg_rebounds": 3.4, "avg_assists": 5.5}},
            {"team": "波士顿凯尔特人", "start_year": 2017, "end_year": 2019, "stats": {"games": 127, "avg_points": 22.2, "avg_rebounds": 4.8, "avg_assists": 5.6}},
            {"team": "布鲁克林篮网", "start_year": 2019, "end_year": 2023, "stats": {"games": 193, "avg_points": 27.1, "avg_rebounds": 4.6, "avg_assists": 5.8}},
            {"team": "达拉斯独行侠", "start_year": 2023, "end_year": None, "stats": {"games": 80, "avg_points": 25.0, "avg_rebounds": 5.1, "avg_assists": 5.6}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 2012, "note": ""},
            {"award": "总冠军", "year": 2016, "note": ""},
            {"award": "全明星MVP", "year": 2014, "note": ""}
        ]
    },
    "Draymond Green": {
        "id": "draymond",
        "player_id": 202696,
        "position": "前锋/F",
        "height": "6' 6\" (1.98m)",
        "weight": "230 lbs (104kg)",
        "college": "密歇根州立大学",
        "draft_info": {"year": 2012, "round": 2, "pick": 35, "team": "金州勇士"},
        "bio": "德雷蒙德·格林是NBA最出色的防守球员之一，以其全能的表现和领导能力闻名，拥有4个总冠军。",
        "career_teams": [
            {"team": "金州勇士", "start_year": 2012, "end_year": None, "stats": {"games": 825, "avg_points": 8.7, "avg_rebounds": 6.9, "avg_assists": 5.4}}
        ],
        "awards": [
            {"award": "总冠军", "year": 2015, "note": ""},
            {"award": "总冠军", "year": 2017, "note": ""},
            {"award": "总冠军", "year": 2018, "note": ""},
            {"award": "最佳防守球员", "year": 2017, "note": ""},
            {"award": "总冠军", "year": 2022, "note": ""}
        ]
    },
    "Klay Thompson": {
        "id": "klay",
        "player_id": 202691,
        "position": "后卫/G",
        "height": "6' 6\" (1.98m)",
        "weight": "215 lbs (98kg)",
        "college": "华盛顿州立大学",
        "draft_info": {"year": 2011, "round": 1, "pick": 11, "team": "金州勇士"},
        "bio": "克莱·汤普森是NBA历史上最伟大的三分球射手之一，以其出色的投篮能力和防守闻名，拥有4个总冠军。",
        "career_teams": [
            {"team": "金州勇士", "start_year": 2011, "end_year": None, "stats": {"games": 741, "avg_points": 19.5, "avg_rebounds": 3.5, "avg_assists": 2.2}}
        ],
        "awards": [
            {"award": "总冠军", "year": 2015, "note": ""},
            {"award": "总冠军", "year": 2017, "note": ""},
            {"award": "总冠军", "year": 2018, "note": ""},
            {"award": "总冠军", "year": 2022, "note": ""},
            {"award": "全明星MVP", "year": 2024, "note": ""}
        ]
    },
    "Tony Parker": {
        "id": "tony_parker",
        "player_id": 1545,
        "position": "后卫/G",
        "height": "6' 2\" (1.88m)",
        "weight": "185 lbs (84kg)",
        "college": "海外联赛",
        "draft_info": {"year": 2001, "round": 1, "pick": 28, "team": "圣安东尼奥马刺"},
        "bio": "托尼·帕克是NBA历史上最伟大的国际控卫之一，以其出色的速度和关键球能力闻名，拥有4个总冠军。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 2001, "end_year": 2018, "stats": {"games": 1198, "avg_points": 15.5, "avg_rebounds": 2.7, "avg_assists": 5.6}},
            {"team": "夏洛特黄蜂", "start_year": 2018, "end_year": 2019, "stats": {"games": 56, "avg_points": 9.5, "avg_rebounds": 1.8, "avg_assists": 3.7}}
        ],
        "awards": [
            {"award": "总冠军", "year": 2003, "note": ""},
            {"award": "总冠军", "year": 2005, "note": ""},
            {"award": "总冠军", "year": 2007, "note": ""},
            {"award": "总决赛MVP", "year": 2007, "note": ""},
            {"award": "总冠军", "year": 2014, "note": ""}
        ]
    },
    "Manu Ginóbili": {
        "id": "manu",
        "player_id": 1547,
        "position": "后卫/G",
        "height": "6' 6\" (1.98m)",
        "weight": "200 lbs (91kg)",
        "college": "海外联赛",
        "draft_info": {"year": 1999, "round": 2, "pick": 57, "team": "圣安东尼奥马刺"},
        "bio": "马努·吉诺比利是NBA历史上最伟大的第六人之一，以其出色的传球和关键时刻的表现闻名，拥有4个总冠军。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 2002, "end_year": 2018, "stats": {"games": 1057, "avg_points": 13.3, "avg_rebounds": 3.5, "avg_assists": 3.8}}
        ],
        "awards": [
            {"award": "最佳第六人", "year": 2008, "note": ""},
            {"award": "总冠军", "year": 2003, "note": ""},
            {"award": "总冠军", "year": 2005, "note": ""},
            {"award": "总冠军", "year": 2007, "note": ""},
            {"award": "总冠军", "year": 2014, "note": ""}
        ]
    },
    "David Robinson": {
        "id": "david_robinson",
        "player_id": 1479,
        "position": "中锋/C",
        "height": "7' 1\" (2.16m)",
        "weight": "235 lbs (107kg)",
        "college": "海军学院",
        "draft_info": {"year": 1987, "round": 1, "pick": 1, "team": "圣安东尼奥马刺"},
        "bio": "大卫·罗宾逊是NBA历史上最伟大的中锋之一，以其出色的防守和全能表现闻名，拥有2个总冠军。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 1989, "end_year": 2003, "stats": {"games": 987, "avg_points": 21.1, "avg_rebounds": 10.6, "avg_assists": 2.5}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1990, "note": ""},
            {"award": "常规赛MVP", "year": 1995, "note": ""},
            {"award": "最佳防守球员", "year": 1992, "note": ""},
            {"award": "总冠军", "year": 1999, "note": ""},
            {"award": "总冠军", "year": 2003, "note": ""},
            {"award": "全明星MVP", "year": 1996, "note": ""}
        ]
    },
    "George Gervin": {
        "id": "gervin",
        "player_id": 1455,
        "position": "后卫/G",
        "height": "6' 7\" (2.01m)",
        "weight": "180 lbs (82kg)",
        "college": "东密歇根大学",
        "draft_info": {"year": 1974, "round": 3, "pick": 40, "team": "菲尼克斯太阳"},
        "bio": "乔治·格文是NBA历史上最伟大的得分手之一，以其优雅的finger roll投篮闻名，是马刺队史传奇球星。",
        "career_teams": [
            {"team": "圣安东尼奥马刺", "start_year": 1976, "end_year": 1985, "stats": {"games": 791, "avg_points": 26.2, "avg_rebounds": 4.6, "avg_assists": 2.8}},
            {"team": "芝加哥公牛", "start_year": 1985, "end_year": 1986, "stats": {"games": 41, "avg_points": 16.2, "avg_rebounds": 2.9, "avg_assists": 2.5}}
        ],
        "awards": [
            {"award": "全明星MVP", "year": 1980, "note": ""},
            {"award": "全明星MVP", "year": 1984, "note": ""}
        ]
    },
    "Bill Russell": {
        "id": "bill_russell",
        "player_id": 94,
        "position": "中锋/C",
        "height": "6' 10\" (2.08m)",
        "weight": "215 lbs (98kg)",
        "college": "旧金山大学",
        "draft_info": {"year": 1956, "round": 1, "pick": 2, "team": "波士顿凯尔特人"},
        "bio": "比尔·拉塞尔是NBA历史上最伟大的赢家，带领凯尔特人队获得11座总冠军，以其出色的防守和领导能力闻名。",
        "career_teams": [
            {"team": "波士顿凯尔特人", "start_year": 1956, "end_year": 1969, "stats": {"games": 963, "avg_points": 15.1, "avg_rebounds": 22.5, "avg_assists": 4.3}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1957, "note": ""},
            {"award": "常规赛MVP", "year": 1958, "note": ""},
            {"award": "常规赛MVP", "year": 1961, "note": ""},
            {"award": "常规赛MVP", "year": 1962, "note": ""},
            {"award": "常规赛MVP", "year": 1963, "note": ""},
            {"award": "常规赛MVP", "year": 1965, "note": ""},
            {"award": "总冠军", "year": 1957, "note": ""},
            {"award": "总冠军", "year": 1959, "note": ""},
            {"award": "总冠军", "year": 1960, "note": ""},
            {"award": "总冠军", "year": 1961, "note": ""},
            {"award": "总冠军", "year": 1962, "note": ""},
            {"award": "总冠军", "year": 1963, "note": ""},
            {"award": "总冠军", "year": 1964, "note": ""},
            {"award": "总冠军", "year": 1965, "note": ""},
            {"award": "总冠军", "year": 1966, "note": ""},
            {"award": "总冠军", "year": 1968, "note": ""},
            {"award": "总冠军", "year": 1969, "note": ""},
            {"award": "全明星MVP", "year": 1963, "note": ""},
            {"award": "全明星MVP", "year": 1965, "note": ""}
        ]
    },
    "Wilt Chamberlain": {
        "id": "wilt",
        "player_id": 100,
        "position": "中锋/C",
        "height": "7' 1\" (2.16m)",
        "weight": "275 lbs (125kg)",
        "college": "堪萨斯大学",
        "draft_info": {"year": 1959, "round": 1, "pick": 1, "team": "费城勇士"},
        "bio": "威尔特·张伯伦是NBA历史上最具统治力的球员之一，保持着多项NBA纪录，包括单场100分。",
        "career_teams": [
            {"team": "费城/旧金山勇士", "start_year": 1959, "end_year": 1965, "stats": {"games": 455, "avg_points": 38.4, "avg_rebounds": 22.3, "avg_assists": 3.1}},
            {"team": "费城76人", "start_year": 1965, "end_year": 1968, "stats": {"games": 246, "avg_points": 26.4, "avg_rebounds": 22.3, "avg_assists": 6.8}},
            {"team": "洛杉矶湖人", "start_year": 1968, "end_year": 1973, "stats": {"games": 360, "avg_points": 17.7, "avg_rebounds": 19.2, "avg_assists": 4.3}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1960, "note": ""},
            {"award": "常规赛MVP", "year": 1960, "note": ""},
            {"award": "常规赛MVP", "year": 1966, "note": ""},
            {"award": "常规赛MVP", "year": 1967, "note": ""},
            {"award": "常规赛MVP", "year": 1968, "note": ""},
            {"award": "总冠军", "year": 1967, "note": ""},
            {"award": "总冠军", "year": 1972, "note": ""},
            {"award": "全明星MVP", "year": 1960, "note": ""},
            {"award": "全明星MVP", "year": 1966, "note": ""}
        ]
    },
    "Kareem Abdul-Jabbar": {
        "id": "kareem",
        "player_id": 101,
        "position": "中锋/C",
        "height": "7' 2\" (2.18m)",
        "weight": "225 lbs (102kg)",
        "college": "加州大学洛杉矶分校",
        "draft_info": {"year": 1969, "round": 1, "pick": 1, "team": "密尔沃基雄鹿"},
        "bio": "卡里姆·阿卜杜尔-贾巴尔是NBA历史得分王，以其标志性的天勾投篮闻名，拥有6个总冠军和6个MVP。",
        "career_teams": [
            {"team": "密尔沃基雄鹿", "start_year": 1969, "end_year": 1975, "stats": {"games": 467, "avg_points": 30.4, "avg_rebounds": 15.3, "avg_assists": 4.3}},
            {"team": "洛杉矶湖人", "start_year": 1975, "end_year": 1989, "stats": {"games": 1093, "avg_points": 22.1, "avg_rebounds": 9.4, "avg_assists": 3.0}}
        ],
        "awards": [
            {"award": "最佳新秀", "year": 1970, "note": ""},
            {"award": "常规赛MVP", "year": 1971, "note": ""},
            {"award": "常规赛MVP", "year": 1972, "note": ""},
            {"award": "常规赛MVP", "year": 1974, "note": ""},
            {"award": "常规赛MVP", "year": 1976, "note": ""},
            {"award": "常规赛MVP", "year": 1977, "note": ""},
            {"award": "常规赛MVP", "year": 1980, "note": ""},
            {"award": "总冠军", "year": 1971, "note": ""},
            {"award": "总冠军", "year": 1980, "note": ""},
            {"award": "总决赛MVP", "year": 1980, "note": ""},
            {"award": "总冠军", "year": 1982, "note": ""},
            {"award": "总冠军", "year": 1985, "note": ""},
            {"award": "总决赛MVP", "year": 1985, "note": ""},
            {"award": "总冠军", "year": 1987, "note": ""},
            {"award": "总冠军", "year": 1988, "note": ""},
            {"award": "全明星MVP", "year": 1972, "note": ""},
            {"award": "全明星MVP", "year": 1973, "note": ""},
            {"award": "全明星MVP", "year": 1974, "note": ""}
        ]
    },
    "Scottie Pippen": {
        "id": "pippen",
        "player_id": 910,
        "position": "前锋/F",
        "height": "6' 8\" (2.03m)",
        "weight": "210 lbs (95kg)",
        "college": "中阿肯色大学",
        "draft_info": {"year": 1987, "round": 1, "pick": 5, "team": "西雅图超音速"},
        "bio": "斯科蒂·皮蓬是NBA历史上最伟大的二当家球员之一，以其出色的防守和全能表现闻名，拥有6个总冠军。",
        "career_teams": [
            {"team": "芝加哥公牛", "start_year": 1987, "end_year": 1998, "stats": {"games": 856, "avg_points": 17.6, "avg_rebounds": 6.4, "avg_assists": 5.2}},
            {"team": "休斯顿火箭", "start_year": 1999, "end_year": 1999, "stats": {"games": 50, "avg_points": 14.5, "avg_rebounds": 6.0, "avg_assists": 5.9}},
            {"team": "波特兰开拓者", "start_year": 1999, "end_year": 2003, "stats": {"games": 214, "avg_points": 11.3, "avg_rebounds": 5.2, "avg_assists": 4.3}},
            {"team": "芝加哥公牛", "start_year": 2003, "end_year": 2004, "stats": {"games": 23, "avg_points": 5.9, "avg_rebounds": 3.0, "avg_assists": 2.2}}
        ],
        "awards": [
            {"award": "总冠军", "year": 1991, "note": ""},
            {"award": "总冠军", "year": 1992, "note": ""},
            {"award": "总冠军", "year": 1993, "note": ""},
            {"award": "总冠军", "year": 1996, "note": ""},
            {"award": "总冠军", "year": 1997, "note": ""},
            {"award": "总冠军", "year": 1998, "note": ""}
        ]
    }
}

def get_html_template():
    template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{player_name} - NBA球员详情</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #000000; 
            min-height: 100vh; 
            color: #C4CED4;
        }}

        :root {{
            --primary-color: #0b3d91;
            --accent-color: #C4CED4;
        }}

        .navbar {{
            background: rgba(0, 0, 0, 0.9);
            padding: 0.75rem 1.5rem;
            box-shadow: 0 2px 12px rgba(196, 206, 212, 0.12);
            position: fixed;
            top: 10px;
            left: 10px;
            right: 10px;
            z-index: 100;
            border-radius: 12px;
            border: 1px solid rgba(196, 206, 212, 0.2);
        }}
        .navbar h1 {{ color: #C4CED4; font-size: 1rem; display: flex; align-items: center; gap: 10px; }}
        .navbar nav {{ margin-top: 0.5rem; }}
        .navbar nav a {{
            color: rgba(196, 206, 212, 0.8);
            text-decoration: none;
            margin-right: 2rem;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            transition: all 0.3s;
            display: inline-block;
        }}
        .navbar nav a:hover {{ background: rgba(196, 206, 212, 0.2); color: #fff; }}
        .navbar nav a.back-btn {{ background: rgba(196, 206, 212, 0.2); }}

        .navbar .team-logo {{
            width: 35px;
            height: 35px;
            background-image: url('/nbalogo/NBA.svg');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }}

        .container {{ max-width: 1400px; margin: 0 auto; padding: 80px 30px 30px; }}

        .player-header {{
            background: linear-gradient(135deg, #0b3d91, #1e4daf);
            color: #fff;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            display: flex;
            gap: 30px;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .player-avatar {{
            width: 180px;
            height: 230px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
            font-weight: bold;
            text-transform: uppercase;
            flex-shrink: 0;
            overflow: hidden;
            background: transparent;
        }}

        .player-avatar img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 15px;
        }}
        .player-info {{ flex: 1; }}
        .player-name {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .player-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        .player-bio {{
            font-size: 1rem;
            line-height: 1.6;
            opacity: 0.95;
        }}

        .draft-info {{
            background: #1a1a2e;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(196, 206, 212, 0.1);
        }}
        .draft-info h2 {{
            color: #C4CED4;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        .draft-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #333;
            padding: 15px 25px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 1.1rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #1a1a2e;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(196, 206, 212, 0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #4cc9f0;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 0.85rem;
            color: #C4CED4;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .career-timeline {{
            background: #1a1a2e;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(196, 206, 212, 0.1);
        }}
        .career-timeline h2 {{
            color: #C4CED4;
            margin-bottom: 25px;
            font-size: 1.3rem;
        }}
        .timeline-item {{
            display: flex;
            gap: 20px;
            padding: 20px 0;
            border-left: 3px solid #4cc9f0;
            margin-left: 15px;
            position: relative;
        }}
        .timeline-item::before {{
            content: '';
            width: 15px;
            height: 15px;
            background: #4cc9f0;
            border-radius: 50%;
            position: absolute;
            left: -9px;
            top: 25px;
        }}
        .timeline-year {{
            min-width: 100px;
            font-weight: 700;
            color: #4cc9f0;
        }}
        .timeline-content {{
            flex: 1;
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
        }}
        .timeline-team {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #C4CED4;
        }}
        .timeline-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            font-size: 0.9rem;
            color: #aaa;
        }}

        .awards-section {{
            background: #1a1a2e;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(196, 206, 212, 0.1);
        }}
        .awards-section h2 {{
            color: #C4CED4;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        .awards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        .award-item {{
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #FFD700;
        }}
        .award-name {{
            font-weight: 600;
            color: #C4CED4;
            margin-bottom: 5px;
        }}
        .award-year {{
            color: #aaa;
            font-size: 0.9rem;
        }}
        .award-note {{
            color: #888;
            font-size: 0.85rem;
            font-style: italic;
            margin-top: 5px;
        }}

        .section {{
            background: #1a1a2e;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(196, 206, 212, 0.1);
        }}
        .section h2 {{
            color: #C4CED4;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid rgba(196, 206, 212, 0.1);
        }}
        th {{
            background: rgba(0,0,0,0.3);
            color: #4cc9f0;
            font-weight: 600;
        }}
        tr:hover {{ background: rgba(76, 201, 240, 0.1); }}

        @media (max-width: 768px) {{
            .navbar {{
                position: relative;
                top: 0;
                left: 0;
                right: 0;
                border-radius: 0;
            }}
            .container {{
                padding: 20px 15px;
            }}
            .player-header {{
                flex-direction: column;
                text-align: center;
            }}
            .player-avatar {{
                width: 150px;
                height: 190px;
                font-size: 3rem;
            }}
            .player-name {{
                font-size: 2rem;
            }}
            .player-meta {{
                justify-content: center;
            }}
            .timeline-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>
            <span class="team-logo"></span>
            <span>NBA球员详情</span>
        </h1>
        <nav>
            <a href="/" class="back-btn">← 返回首页</a>
            <a href="/player-career">球员生涯</a>
            <a href="/player-compare">球员对比</a>
        </nav>
    </nav>

    <div class="container">
        <div class="player-header">
            <div class="player-avatar">
                <img src="/images/{image_filename}" alt="{player_name}" onerror="this.style.display='none'; this.parentElement.innerHTML='{initials}';">
            </div>
            <div class="player-info">
                <div class="player-name">{player_name}</div>
                <div class="player-meta">
                    <div class="meta-item">📍 位置: {position}</div>
                    <div class="meta-item">📏 身高: {height}</div>
                    <div class="meta-item">⚖️ 体重: {weight}</div>
                    <div class="meta-item">🎓 {college}</div>
                </div>
                <div class="player-bio">{bio}</div>
            </div>
        </div>

        <div class="draft-info">
            <h2>🏆 选秀信息</h2>
            <div class="draft-badge">{draft_year}年NBA选秀 - 第{draft_round}轮第{draft_pick}顺位 - {draft_team}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-value">{total_games}</div><div class="stat-label">出场次数</div></div>
            <div class="stat-card"><div class="stat-value">{avg_points}</div><div class="stat-label">场均得分</div></div>
            <div class="stat-card"><div class="stat-value">{avg_rebounds}</div><div class="stat-label">场均篮板</div></div>
            <div class="stat-card"><div class="stat-value">{avg_assists}</div><div class="stat-label">场均助攻</div></div>
        </div>

        <div class="career-timeline">
            <h2>📅 职业生涯履历</h2>
            {timeline_html}
        </div>

        <div class="awards-section">
            <h2>⭐ 个人荣誉</h2>
            {awards_html}
        </div>
    </div>
</body>
</html>"""
    return template

def generate_player_html(player_name, data):
    image_filename = f"{player_name}.jpg"
    
    initials = ''.join([n[0] for n in player_name.split()]).upper()
    
    draft_info = data.get('draft_info', {})
    draft_year = draft_info.get('year', '未知')
    draft_round = draft_info.get('round', '未知')
    draft_pick = draft_info.get('pick', '未知')
    draft_team = draft_info.get('team', '未知')
    
    total_games = sum(team['stats']['games'] for team in data.get('career_teams', []))
    avg_points = round(sum(team['stats']['avg_points'] * team['stats']['games'] for team in data.get('career_teams', [])) / max(total_games, 1), 1)
    avg_rebounds = round(sum(team['stats']['avg_rebounds'] * team['stats']['games'] for team in data.get('career_teams', [])) / max(total_games, 1), 1)
    avg_assists = round(sum(team['stats']['avg_assists'] * team['stats']['games'] for team in data.get('career_teams', [])) / max(total_games, 1), 1)
    
    timeline_html = '\n'.join([f'''
        <div class="timeline-item">
            <div class="timeline-year">{team['start_year']}{team['end_year'] and ' - ' + str(team['end_year']) or ' - 至今'}</div>
            <div class="timeline-content">
                <div class="timeline-team">🏀 {team['team']}</div>
                <div class="timeline-stats">
                    <div>出场: {team['stats']['games']}场</div>
                    <div>场均: {team['stats']['avg_points']}分</div>
                    <div>场均篮板: {team['stats']['avg_rebounds']}</div>
                    <div>场均助攻: {team['stats']['avg_assists']}</div>
                </div>
            </div>
        </div>
    ''' for team in data.get('career_teams', [])])
    
    awards_html = '\n'.join([f'''
        <div class="award-item">
            <div class="award-name">🏅 {award['award']}</div>
            <div class="award-year">{award['year']}年</div>
            {award.get('note') and f"<div class='award-note'>{award['note']}</div>" or ''}
        </div>
    ''' for award in data.get('awards', [])])
    
    template = get_html_template()
    html = template.replace('{player_name}', player_name)
    html = html.replace('{image_filename}', image_filename)
    html = html.replace('{initials}', initials)
    html = html.replace('{position}', data.get('position', '未知'))
    html = html.replace('{height}', data.get('height', '未知'))
    html = html.replace('{weight}', data.get('weight', '未知'))
    html = html.replace('{college}', data.get('college', '未知'))
    html = html.replace('{bio}', data.get('bio', ''))
    html = html.replace('{draft_year}', str(draft_year))
    html = html.replace('{draft_round}', str(draft_round))
    html = html.replace('{draft_pick}', str(draft_pick))
    html = html.replace('{draft_team}', str(draft_team))
    html = html.replace('{total_games}', str(total_games))
    html = html.replace('{avg_points}', str(avg_points))
    html = html.replace('{avg_rebounds}', str(avg_rebounds))
    html = html.replace('{avg_assists}', str(avg_assists))
    html = html.replace('{timeline_html}', timeline_html)
    html = html.replace('{awards_html}', awards_html)
    
    return html

def main():
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    existing_images = set()
    for filename in os.listdir(IMAGES_DIR):
        if filename.endswith('.jpg'):
            existing_images.add(filename.replace('.jpg', ''))
    
    for player_name, data in PLAYER_DATA.items():
        if player_name in existing_images:
            html_content = generate_player_html(player_name, data)
            file_path = os.path.join(STATIC_DIR, f"{data['id']}.html")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Generated: {file_path}")
        else:
            print(f"Skipped {player_name} - no image found")
    
    print(f"\nGenerated {len([p for p in PLAYER_DATA if p in existing_images])} player pages")

if __name__ == '__main__':
    main()