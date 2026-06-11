const Constants = {
    API_BASE: '/api',

    TEAMS: {
        'SAS': {
            name: 'San Antonio Spurs',
            nameCn: '圣安东尼奥马刺',
            alias: '银色军团',
            color: '#C4CED4',
            primary: '#C4CED4',
            secondary: '#000000',
            championships: 5,
            conference: 'Western',
            division: 'Southwest',
            legendaryPlayers: [
                { id: 'tim_duncan', name: '蒂姆·邓肯', position: 'PF/C', years: '1997-2016', honors: ['5次总冠军', '2次MVP', '15次全明星'], stats: { ppg: 19.0, rpg: 10.8, apg: 3.0, bpg: 2.2 } },
                { id: 'manu_ginobili', name: '马努·吉诺比利', position: 'SG', years: '2002-2018', honors: ['4次总冠军', '2次全明星', '最佳第六人'], stats: { ppg: 13.3, rpg: 3.5, apg: 3.8, spg: 1.3 } },
                { id: 'tony_parker', name: '托尼·帕克', position: 'PG', years: '2001-2018', honors: ['4次总冠军', '6次全明星'], stats: { ppg: 15.5, rpg: 2.7, apg: 5.6, spg: 0.9 } },
                { id: 'david_robinson', name: '大卫·罗宾逊', position: 'C', years: '1989-2003', honors: ['2次总冠军', 'MVP', '10次全明星'], stats: { ppg: 21.1, rpg: 10.6, apg: 2.5, bpg: 2.5 } },
                { id: 'george_gervin', name: '乔治·格文', position: 'SG', years: '1974-1985', honors: ['9次全明星', '4次得分王'], stats: { ppg: 26.2, rpg: 4.6, apg: 2.8, spg: 1.2 } }
            ]
        },
        'LAL': {
            name: 'Los Angeles Lakers',
            nameCn: '洛杉矶湖人',
            alias: '紫金王朝',
            color: '#552583',
            primary: '#FDB927',
            secondary: '#552583',
            championships: 17,
            conference: 'Western',
            division: 'Pacific',
            legendaryPlayers: [
                { id: 'kobe_bryant', name: '科比·布莱恩特', position: 'SG', years: '1996-2016', honors: ['5次总冠军', '2次FMVP', '1次MVP', '18次全明星'], stats: { ppg: 25.0, rpg: 5.2, apg: 4.7, spg: 1.4 } },
                { id: 'magic_johnson', name: '魔术师约翰逊', position: 'PG', years: '1979-1991', honors: ['5次总冠军', '3次MVP', '12次全明星'], stats: { ppg: 19.5, rpg: 7.2, apg: 11.2, spg: 1.9 } },
                { id: 'kareem_abdul_jabbar', name: '卡里姆·贾巴尔', position: 'C', years: '1975-1989', honors: ['5次总冠军', '6次MVP', '19次全明星'], stats: { ppg: 22.1, rpg: 9.4, apg: 3.6, bpg: 2.4 } },
                { id: 'shaquille_oneal', name: '沙奎尔·奥尼尔', position: 'C', years: '1996-2011', honors: ['3次总冠军', 'FMVP', '8次全明星'], stats: { ppg: 23.7, rpg: 10.9, apg: 2.5, bpg: 2.3 } },
                { id: 'lebron_james', name: '勒布朗·詹姆斯', position: 'SF', years: '2018-至今', honors: ['4次总冠军', '4次MVP', '20次全明星'], stats: { ppg: 27.2, rpg: 7.5, apg: 7.3, spg: 1.5 } },
                { id: 'elgin_baylor', name: '埃尔金·贝勒', position: 'SF', years: '1958-1971', honors: ['11次全明星', '名人堂成员'], stats: { ppg: 27.4, rpg: 13.5, apg: 4.3 } }
            ]
        },
        'BOS': {
            name: 'Boston Celtics',
            nameCn: '波士顿凯尔特人',
            alias: '绿衫军',
            color: '#007A33',
            primary: '#BA9653',
            secondary: '#007A33',
            championships: 18,
            conference: 'Eastern',
            division: 'Atlantic',
            legendaryPlayers: [
                { id: 'bill_russell', name: '比尔·拉塞尔', position: 'C', years: '1956-1969', honors: ['11次总冠军', '5次MVP', '12次全明星'], stats: { ppg: 15.1, rpg: 22.5, apg: 4.3 } },
                { id: 'larry_bird', name: '拉里·伯德', position: 'SF', years: '1979-1992', honors: ['3次总冠军', '2次FMVP', '3次MVP', '12次全明星'], stats: { ppg: 24.3, rpg: 10.0, apg: 6.3, spg: 1.7 } },
                { id: 'bob_cousy', name: '鲍勃·库西', position: 'PG', years: '1950-1963', honors: ['6次总冠军', 'MVP', '13次全明星'], stats: { ppg: 18.4, rpg: 5.2, apg: 7.6 } }
            ]
        },
        'GSW': {
            name: 'Golden State Warriors',
            nameCn: '金州勇士',
            alias: '勇士王朝',
            color: '#1D428A',
            primary: '#FFC72C',
            secondary: '#1D428A',
            championships: 7,
            conference: 'Western',
            division: 'Pacific',
            legendaryPlayers: [
                { id: 'stephen_curry', name: '斯蒂芬·库里', position: 'PG', years: '2009-至今', honors: ['4次总冠军', '2次MVP', '10次全明星'], stats: { ppg: 24.8, rpg: 4.7, apg: 6.4, spg: 1.5 } },
                { id: 'klay_thompson', name: '克莱·汤普森', position: 'SG', years: '2011-至今', honors: ['4次总冠军', '5次全明星'], stats: { ppg: 19.5, rpg: 3.5, apg: 2.3, spg: 0.9 } },
                { id: 'draymond_green', name: '德雷蒙德·格林', position: 'PF', years: '2012-至今', honors: ['4次总冠军', 'DPOY', '4次全明星'], stats: { ppg: 8.7, rpg: 7.0, apg: 5.6, spg: 1.3 } },
                { id: 'wilt_chamberlain', name: '威尔特·张伯伦', position: 'C', years: '1959-1965', honors: ['2次总冠军', '4次MVP'], stats: { ppg: 30.1, rpg: 22.9, apg: 4.4 } }
            ]
        },
        'CHI': {
            name: 'Chicago Bulls',
            nameCn: '芝加哥公牛',
            alias: '公牛王朝',
            color: '#CE1141',
            primary: '#000000',
            secondary: '#CE1141',
            championships: 6,
            conference: 'Eastern',
            division: 'Central',
            legendaryPlayers: [
                { id: 'michael_jordan', name: '迈克尔·乔丹', position: 'SG', years: '1984-1998', honors: ['6次总冠军', '6次FMVP', '5次MVP', '14次全明星'], stats: { ppg: 30.1, rpg: 6.2, apg: 5.3, spg: 2.3 } },
                { id: 'scottie_pippen', name: '斯科蒂·皮蓬', position: 'SF', years: '1987-2004', honors: ['6次总冠军', '7次全明星', '名人堂成员'], stats: { ppg: 17.7, rpg: 6.7, apg: 5.3, spg: 2.0 } },
                { id: 'dennis_rodman', name: '丹尼斯·罗德曼', position: 'PF', years: '1986-2000', honors: ['5次总冠军', '2次DPOY', '8次篮板王'], stats: { ppg: 7.3, rpg: 13.1, apg: 1.8 } }
            ]
        },
        'MIA': {
            name: 'Miami Heat',
            nameCn: '迈阿密热火',
            alias: '热火三巨头',
            color: '#98002E',
            primary: '#F9A01B',
            secondary: '#98002E',
            championships: 3,
            conference: 'Eastern',
            division: 'Southeast',
            legendaryPlayers: [
                { id: 'dwyane_wade', name: '德韦恩·韦德', position: 'SG', years: '2003-2019', honors: ['3次总冠军', 'FMVP', '13次全明星'], stats: { ppg: 22.0, rpg: 4.7, apg: 5.4, spg: 1.5 } },
                { id: 'lebron_james_heat', name: '勒布朗·詹姆斯', position: 'SF', years: '2010-2014', honors: ['2次总冠军', '2次FMVP', '2次MVP'], stats: { ppg: 26.9, rpg: 7.6, apg: 6.7, spg: 1.7 } },
                { id: 'chris_bosh', name: '克里斯·波什', position: 'PF/C', years: '2003-2016', honors: ['2次总冠军', '11次全明星'], stats: { ppg: 19.2, rpg: 8.5, apg: 2.0 } }
            ]
        },
        'MIL': {
            name: 'Milwaukee Bucks',
            nameCn: '密尔沃基雄鹿',
            alias: '字母哥时代',
            color: '#004E21',
            primary: '#C4CED4',
            secondary: '#004E21',
            championships: 2,
            conference: 'Eastern',
            division: 'Central',
            legendaryPlayers: [
                { id: 'giannis_antetokounmpo', name: '扬尼斯·阿德托昆博', position: 'PF', years: '2013-至今', honors: ['2次总冠军', '2次MVP', 'FMVP', 'DPOY'], stats: { ppg: 22.6, rpg: 9.6, apg: 4.7, spg: 1.1 } },
                { id: 'kareem_jabbar_bucks', name: '卡里姆·贾巴尔', position: 'C', years: '1971-1975', honors: ['3次MVP', '得分王'], stats: { ppg: 30.4, rpg: 15.3, apg: 4.3, bpg: 3.4 } }
            ]
        },
        'DEN': {
            name: 'Denver Nuggets',
            nameCn: '丹佛掘金',
            alias: '高原球队',
            color: '#0E2240',
            primary: '#FEC524',
            secondary: '#0E2240',
            championships: 1,
            conference: 'Western',
            division: 'Northwest',
            legendaryPlayers: [
                { id: 'nikola_jokic', name: '尼古拉·约基奇', position: 'C', years: '2015-至今', honors: ['3次MVP', '1次总冠军', 'FMVP'], stats: { ppg: 21.0, rpg: 10.7, apg: 7.3, spg: 1.2 } },
                { id: 'alex_english', name: '亚历克斯·英格利什', position: 'SF', years: '1976-1990', honors: ['8次全明星', '2次得分王'], stats: { ppg: 25.9, rpg: 5.6, apg: 3.7 } }
            ]
        },
        'DAL': {
            name: 'Dallas Mavericks',
            nameCn: '达拉斯独行侠',
            alias: '诺维茨基时代',
            color: '#00538C',
            primary: '#003087',
            secondary: '#00538C',
            championships: 2,
            conference: 'Western',
            division: 'Southwest',
            legendaryPlayers: [
                { id: 'dirk_nowitzki', name: '德克·诺维茨基', position: 'PF', years: '1998-2019', honors: ['1次总冠军', '1次MVP', '14次全明星'], stats: { ppg: 20.7, rpg: 7.5, apg: 2.4, spg: 0.8 } },
                { id: 'luka_doncic', name: '卢卡·东契奇', position: 'PG', years: '2018-至今', honors: ['5次全明星', '5次最佳阵容'], stats: { ppg: 28.4, rpg: 8.5, apg: 8.2, spg: 1.3 } }
            ]
        },
        'HOU': {
            name: 'Houston Rockets',
            nameCn: '休斯顿火箭',
            alias: '航天城',
            color: '#000000',
            primary: '#C8102E',
            secondary: '#000000',
            championships: 2,
            conference: 'Western',
            division: 'Southwest',
            legendaryPlayers: [
                { id: 'hakeem_olajuwon', name: '哈基姆·奥拉朱旺', position: 'C', years: '1984-2002', honors: ['2次总冠军', '2次FMVP', 'MVP', '12次全明星'], stats: { ppg: 21.8, rpg: 11.1, apg: 2.5, bpg: 3.1 } },
                { id: 'james_harden', name: '詹姆斯·哈登', position: 'PG', years: '2012-2021', honors: ['1次MVP', '10次全明星', '3次得分王'], stats: { ppg: 29.6, rpg: 6.0, apg: 7.7, spg: 1.5 } },
                { id: 'yao_ming', name: '姚明', position: 'C', years: '2002-2011', honors: ['8次全明星', '名人堂成员'], stats: { ppg: 19.0, rpg: 9.2, apg: 1.6, bpg: 1.9 } },
                { id: 'clement_olajuwon', name: '克莱蒙·奥拉朱旺', position: 'SG', years: '1970-1981', honors: ['2次总冠军', '名人堂成员'], stats: { ppg: 27.4, rpg: 5.0, apg: 6.1 } }
            ]
        },
        'OKC': {
            name: 'Oklahoma City Thunder',
            nameCn: '俄克拉荷马雷霆',
            alias: '青年军',
            color: '#007AC1',
            primary: '#EF3B24',
            secondary: '#007AC1',
            championships: 1,
            conference: 'Western',
            division: 'Northwest',
            legendaryPlayers: [
                { id: 'kevin_durant', name: '凯文·杜兰特', position: 'SF', years: '2007-2016', honors: ['MVP', '4次得分王', '14次全明星'], stats: { ppg: 27.3, rpg: 7.1, apg: 4.3, spg: 1.1 } },
                { id: 'russell_westbrook', name: '拉塞尔·威斯布鲁克', position: 'PG', years: '2008-2019', honors: ['MVP', '9次全明星', '2次得分王'], stats: { ppg: 23.2, rpg: 7.1, apg: 8.3, spg: 1.8 } },
                { id: 'james_harden_rockets', name: '詹姆斯·哈登', position: 'PG', years: '2012-2021', honors: ['1次MVP', '10次全明星', '3次得分王'], stats: { ppg: 29.6, rpg: 6.0, apg: 7.7, spg: 1.5 } }
            ]
        },
        'PHX': {
            name: 'Phoenix Suns',
            nameCn: '菲尼克斯太阳',
            alias: '炮轰时代',
            color: '#1D1160',
            primary: '#E56020',
            secondary: '#1D1160',
            championships: 0,
            conference: 'Western',
            division: 'Pacific',
            legendaryPlayers: [
                { id: 'steve_nash', name: '史蒂夫·纳什', position: 'PG', years: '1996-2012', honors: ['2次MVP', '8次全明星'], stats: { ppg: 14.3, rpg: 3.0, apg: 8.5, spg: 0.7 } },
                { id: 'charles_barkley', name: '查尔斯·巴克利', position: 'PF', years: '1992-2000', honors: ['MVP', '11次全明星'], stats: { ppg: 22.1, rpg: 11.5, apg: 3.9, spg: 1.5 } },
                { id: 'devin_booker', name: '德文·布克', position: 'SG', years: '2015-至今', honors: ['7次全明星'], stats: { ppg: 24.4, rpg: 4.8, apg: 5.0, spg: 0.9 } }
            ]
        },
        'PHI': {
            name: 'Philadelphia 76ers',
            nameCn: '费城76人',
            alias: '过程还在继续',
            color: '#006BB6',
            primary: '#ED174C',
            secondary: '#006BB6',
            championships: 3,
            conference: 'Eastern',
            division: 'Atlantic',
            legendaryPlayers: [
                { id: 'allen_iverson', name: '阿伦·艾弗森', position: 'SG', years: '1996-2010', honors: ['MVP', '11次全明星', '4次得分王'], stats: { ppg: 26.7, rpg: 3.7, apg: 6.2, spg: 2.3 } },
                { id: 'joel_embiid', name: '乔尔·恩比德', position: 'C', years: '2014-至今', honors: ['2次MVP', '7次全明星'], stats: { ppg: 27.9, rpg: 11.2, apg: 3.6, bpg: 1.7 } },
                { id: 'wilt_chamberlain_76ers', name: '威尔特·张伯伦', position: 'C', years: '1965-1968', honors: ['总冠军', 'MVP', '名人堂成员'], stats: { ppg: 33.5, rpg: 24.6, apg: 5.2 } }
            ]
        },
        'LAC': {
            name: 'Los Angeles Clippers',
            nameCn: '洛杉矶快船',
            alias: '空接之城',
            color: '#000000',
            primary: '#C8102E',
            secondary: '#000000',
            championships: 0,
            conference: 'Western',
            division: 'Pacific',
            legendaryPlayers: [
                { id: 'kawhi_leonard', name: '科怀·莱昂纳德', position: 'SF', years: '2019-至今', honors: ['2次总冠军', '2次FMVP', '2次DPOY'], stats: { ppg: 20.8, rpg: 6.4, apg: 3.4, spg: 1.4 } },
                { id: 'chris_paul', name: '克里斯·保罗', position: 'PG', years: '2011-2017', honors: ['6次抢断王', '11次全明星'], stats: { ppg: 18.8, rpg: 4.5, apg: 9.7, spg: 2.2 } },
                { id: 'blake_griffin', name: '布雷克·格里芬', position: 'PF', years: '2011-2018', honors: ['6次全明星'], stats: { ppg: 21.6, rpg: 8.1, apg: 4.1 } },
                { id: 'deandre_jordan', name: '德安德烈·乔丹', position: 'C', years: '2009-2018', honors: ['2次篮板王'], stats: { ppg: 9.4, rpg: 10.7, apg: 0.9, bpg: 1.7 } }
            ]
        },
        'SAC': {
            name: 'Sacramento Kings',
            nameCn: '萨克拉门托国王',
            alias: '国王队',
            color: '#5B2D8E',
            primary: '#8E9090',
            secondary: '#5B2D8E',
            championships: 1,
            conference: 'Western',
            division: 'Pacific',
            legendaryPlayers: [
                { id: 'peja_stojakovic', name: '佩贾·斯托亚科维奇', position: 'SF', years: '1998-2006', honors: ['3次全明星', '2次三分王'], stats: { ppg: 20.2, rpg: 5.0, apg: 2.1, spg: 1.0 } },
                { id: 'vlade_divac', name: '弗拉德·迪瓦茨', position: 'C', years: '1989-2005', honors: ['名人堂成员'], stats: { ppg: 12.1, rpg: 8.4, apg: 3.3, bpg: 1.2 } },
                { id: 'mitch_richmond', name: '米奇·里奇蒙德', position: 'SG', years: '1991-2001', honors: ['6次全明星', '名人堂成员'], stats: { ppg: 21.0, rpg: 3.9, apg: 3.7, spg: 1.2 } },
                { id: 'domantas_sabonis', name: '多曼塔斯·萨博尼斯', position: 'PF', years: '2016-至今', honors: ['3次全明星', '2次最佳阵容'], stats: { ppg: 16.8, rpg: 10.3, apg: 6.2, spg: 0.8 } }
            ]
        },
        'NOP': {
            name: 'New Orleans Pelicans',
            nameCn: '新奥尔良鹈鹕',
            alias: '鹈鹕队',
            color: '#002B5C',
            primary: '#B4975A',
            secondary: '#002B5C',
            championships: 0,
            conference: 'Western',
            division: 'Southwest',
            legendaryPlayers: [
                { id: 'chris_paul_hornets', name: '克里斯·保罗', position: 'PG', years: '2007-2011', honors: ['4次全明星', '4次抢断王'], stats: { ppg: 18.7, rpg: 4.6, apg: 9.9, spg: 2.3 } },
                { id: 'anthony_davis', name: '安东尼·戴维斯', position: 'PF/C', years: '2012-2019', honors: ['4次全明星', '3次盖帽王'], stats: { ppg: 24.0, rpg: 10.4, apg: 2.2, bpg: 2.4 } },
                { id: 'zyon_williamson', name: '蔡恩·威廉森', position: 'PF', years: '2019-至今', honors: ['全明星'], stats: { ppg: 25.4, rpg: 7.0, apg: 3.6, spg: 1.1 } }
            ]
        },
        'MEM': {
            name: 'Memphis Grizzlies',
            nameCn: '孟菲斯灰熊',
            alias: '磨砺与绞杀',
            color: '#5D76A9',
            primary: '#12173F',
            secondary: '#5D76A9',
            championships: 0,
            conference: 'Western',
            division: 'Southwest',
            legendaryPlayers: [
                { id: 'mike_conley', name: '迈克·康利', position: 'PG', years: '2007-2019', honors: ['1次体育道德风尚奖'], stats: { ppg: 14.1, rpg: 3.0, apg: 5.7, spg: 1.4 } },
                { id: 'marc_gasol', name: '马克·加索尔', position: 'C', years: '2008-2019', honors: ['3次全明星', '1次DPOY'], stats: { ppg: 15.2, rpg: 7.7, apg: 3.4, bpg: 1.5 } },
                { id: 'zach_randolph', name: '扎克·兰多夫', position: 'PF', years: '2009-2017', honors: ['2次全明星'], stats: { ppg: 16.8, rpg: 9.6, apg: 1.8, spg: 1.0 } },
                { id: 'ja_morant', name: '贾·莫兰特', position: 'PG', years: '2019-至今', honors: ['2次全明星'], stats: { ppg: 21.3, rpg: 4.7, apg: 7.1, spg: 1.2 } }
            ]
        },
        'MIN': {
            name: 'Minnesota Timberwolves',
            nameCn: '明尼苏达森林狼',
            alias: '狼群',
            color: '#0C2340',
            primary: '#78BE20',
            secondary: '#0C2340',
            championships: 0,
            conference: 'Western',
            division: 'Northwest',
            legendaryPlayers: [
                { id: 'kevin_garnett', name: '凯文·加内特', position: 'PF', years: '1995-2007', honors: ['MVP', '15次全明星', 'DPOY'], stats: { ppg: 19.8, rpg: 11.0, apg: 4.2, spg: 1.3, bpg: 1.6 } },
                { id: 'latrell_sprewell', name: '拉特里尔·斯普雷威尔', position: 'SG', years: '1997-2005', honors: ['4次全明星'], stats: { ppg: 20.7, rpg: 3.7, apg: 4.0, spg: 1.2 } },
                { id: 'stefon_dillon', name: '斯蒂芬·迪林厄姆', position: 'PG', years: '1996-2002', honors: ['抢断王', '最佳第六人'], stats: { ppg: 13.8, rpg: 2.6, apg: 6.3, spg: 1.7 } },
                { id: 'karl_anthony_towns', name: '卡尔-安东尼·唐斯', position: 'C', years: '2015-至今', honors: ['4次全明星'], stats: { ppg: 23.0, rpg: 10.8, apg: 3.0, bpg: 1.3 } }
            ]
        },
        'UTA': {
            name: 'Utah Jazz',
            nameCn: '犹他爵士',
            alias: '盐湖城之声',
            color: '#002B5C',
            primary: '#00471B',
            secondary: '#002B5C',
            championships: 0,
            conference: 'Western',
            division: 'Northwest',
            legendaryPlayers: [
                { id: 'karl_malone', name: '卡尔·马龙', position: 'PF', years: '1985-2003', honors: ['2次MVP', '14次全明星'], stats: { ppg: 25.0, rpg: 10.1, apg: 3.6, spg: 1.4 } },
                { id: 'john_stockton', name: '约翰·斯托克顿', position: 'PG', years: '1984-2003', honors: ['9次助攻王', '2次抢断王'], stats: { ppg: 13.1, rpg: 2.7, apg: 10.5, spg: 2.2 } },
                { id: 'peter Maravich', name: '皮特·马拉维奇', position: 'SG', years: '1980-1989', honors: ['5次全明星', '名人堂成员'], stats: { ppg: 24.2, rpg: 4.2, apg: 5.6 } },
                { id: 'deron_williams', name: '德隆·威廉姆斯', position: 'PG', years: '2005-2011', honors: ['3次全明星'], stats: { ppg: 18.4, rpg: 3.0, apg: 8.9, spg: 1.0 } }
            ]
        },
        'POR': {
            name: 'Portland Trail Blazers',
            nameCn: '波特兰开拓者',
            alias: '撕裂之城',
            color: '#000000',
            primary: '#E0163B',
            secondary: '#000000',
            championships: 1,
            conference: 'Western',
            division: 'Northwest',
            legendaryPlayers: [
                { id: 'bill_walton', name: '比尔·沃尔顿', position: 'C', years: '1974-1979', honors: ['1次总冠军', 'MVP', '名人堂成员'], stats: { ppg: 13.3, rpg: 10.5, apg: 3.4, bpg: 2.6 } },
                { id: 'clifford_robinson', name: '克里福德·罗宾逊', position: 'PF/C', years: '1989-2003', honors: ['2次全明星', '最佳第六人'], stats: { ppg: 15.8, rpg: 6.9, apg: 2.6, bpg: 1.2 } },
                { id: 'damian_lillard', name: '达米安·利拉德', position: 'PG', years: '2012-至今', honors: ['7次全明星', '1次得分王'], stats: { ppg: 25.2, rpg: 4.2, apg: 6.7, spg: 1.0 } },
                { id: 'clyde_drexler', name: '克莱德·德雷克斯勒', position: 'SG', years: '1983-1998', honors: ['1次总冠军', '10次全明星', '名人堂成员'], stats: { ppg: 20.4, rpg: 6.1, apg: 5.6, spg: 2.0 } }
            ]
        },
        'TOR': {
            name: 'Toronto Raptors',
            nameCn: '多伦多猛龙',
            alias: '北境之王',
            color: '#000000',
            primary: '#CE1141',
            secondary: '#000000',
            championships: 1,
            conference: 'Eastern',
            division: 'Atlantic',
            legendaryPlayers: [
                { id: 'kawhi_leonard_raptors', name: '科怀·莱昂纳德', position: 'SF', years: '2018-2019', honors: ['1次总冠军', '1次FMVP'], stats: { ppg: 26.6, rpg: 7.3, apg: 3.3, spg: 1.8 } },
                { id: 'kyle_lowry', name: '凯尔·洛瑞', position: 'PG', years: '2012-2021', honors: ['6次全明星'], stats: { ppg: 17.4, rpg: 5.4, apg: 7.4, spg: 1.3 } },
                { id: 'demar_deRozan', name: '德马尔·德罗赞', position: 'SG', years: '2013-2018', honors: ['4次全明星'], stats: { ppg: 23.4, rpg: 4.5, apg: 4.1, spg: 1.1 } },
                { id: 'vince_carter', name: '文斯·卡特', position: 'SG', years: '1998-2004', honors: ['8次全明星', '扣篮王'], stats: { ppg: 23.4, rpg: 5.2, apg: 3.9, spg: 1.3 } }
            ]
        },
        'BKN': {
            name: 'Brooklyn Nets',
            nameCn: '布鲁克林篮网',
            alias: '布鲁克林篮网',
            color: '#000000',
            primary: '#FFFFFF',
            secondary: '#000000',
            championships: 0,
            conference: 'Eastern',
            division: 'Atlantic',
            legendaryPlayers: [
                { id: 'jason_kidd', name: '贾森·基德', position: 'PG', years: '2001-2008', honors: ['6次全明星', '名人堂成员'], stats: { ppg: 13.3, rpg: 6.4, apg: 8.8, spg: 1.9 } },
                { id: 'kevin_durant_nets', name: '凯文·杜兰特', position: 'SF', years: '2019-至今', honors: ['MVP', '4次得分王', '14次全明星'], stats: { ppg: 27.3, rpg: 7.1, apg: 4.3, spg: 1.1 } },
                { id: 'kyrie_irving', name: '凯里·欧文', position: 'PG', years: '2019-至今', honors: ['8次全明星'], stats: { ppg: 23.4, rpg: 3.9, apg: 5.7, spg: 1.3 } }
            ]
        },
        'NYK': {
            name: 'New York Knicks',
            nameCn: '纽约尼克斯',
            alias: '篮球麦加',
            color: '#006BB6',
            primary: '#F58426',
            secondary: '#006BB6',
            championships: 2,
            conference: 'Eastern',
            division: 'Atlantic',
            legendaryPlayers: [
                { id: 'patrick_ewing', name: '帕特里克·尤因', position: 'C', years: '1985-2000', honors: ['11次全明星', '名人堂成员'], stats: { ppg: 22.8, rpg: 10.1, apg: 2.4, bpg: 2.8 } },
                { id: 'walt_frazier', name: '沃尔特·弗雷泽', position: 'PG', years: '1970-1977', honors: ['2次总冠军', '7次全明星', '名人堂成员'], stats: { ppg: 21.9, rpg: 5.8, apg: 6.9, spg: 2.0 } },
                { id: 'bernard_king', name: '伯纳德·金', position: 'SF', years: '1980-1994', honors: ['4次全明星', '名人堂成员'], stats: { ppg: 24.2, rpg: 5.8, apg: 3.3 } },
                { id: 'ewing_anthony', name: '安东尼·戴维斯', position: 'PF', years: '2012-至今', honors: ['MVP', '8次全明星'], stats: { ppg: 24.0, rpg: 10.4, apg: 2.2, bpg: 2.4 } }
            ]
        },
        'CLE': {
            name: 'Cleveland Cavaliers',
            nameCn: '克利夫兰骑士',
            alias: '骑士精神',
            color: '#000000',
            primary: '#860038',
            secondary: '#000000',
            championships: 1,
            conference: 'Eastern',
            division: 'Central',
            legendaryPlayers: [
                { id: 'lebron_james_cavs', name: '勒布朗·詹姆斯', position: 'SF', years: '2003-2010, 2014-2018', honors: ['1次总冠军', '4次MVP'], stats: { ppg: 27.2, rpg: 7.5, apg: 7.3, spg: 1.5 } },
                { id: 'kyrie_irving_cavs', name: '凯里·欧文', position: 'PG', years: '2011-2017', honors: ['1次总冠军', '7次全明星'], stats: { ppg: 22.4, rpg: 3.7, apg: 5.4, spg: 1.3 } },
                { id: 'zydrunas_ilgauskas', name: '扎伊德鲁纳斯·伊尔戈斯卡斯', position: 'C', years: '1996-2010', honors: ['2次全明星'], stats: { ppg: 13.0, rpg: 7.3, apg: 1.6, bpg: 1.6 } }
            ]
        },
        'IND': {
            name: 'Indiana Pacers',
            nameCn: '印第安纳步行者',
            alias: '印第安纳',
            color: '#000000',
            primary: '#FDBB30',
            secondary: '#000000',
            championships: 0,
            conference: 'Eastern',
            division: 'Central',
            legendaryPlayers: [
                { id: 'paul_george', name: '保罗·乔治', position: 'SF', years: '2010-2017', honors: ['6次全明星'], stats: { ppg: 21.2, rpg: 5.5, apg: 3.3, spg: 1.7 } },
                { id: 'reggie_miller', name: '雷吉·米勒', position: 'SG', years: '1987-2005', honors: ['5次全明星'], stats: { ppg: 18.2, rpg: 3.0, apg: 3.0, spg: 1.1 } },
                { id: 'danny_granger', name: '丹尼·格兰杰', position: 'SF', years: '2005-2014', honors: ['1次进步最快球员', '3次全明星'], stats: { ppg: 18.1, rpg: 5.4, apg: 2.4 } },
                { id: 'victor_oladipo', name: '维克托·奥拉迪波', position: 'SG', years: '2017-至今', honors: ['2次全明星', '1次抢断王'], stats: { ppg: 20.4, rpg: 5.2, apg: 4.5, spg: 1.6 } }
            ]
        },
        'DET': {
            name: 'Detroit Pistons',
            nameCn: '底特律活塞',
            alias: '坏孩子军团',
            color: '#000000',
            primary: '#C8102E',
            secondary: '#000000',
            championships: 3,
            conference: 'Eastern',
            division: 'Central',
            legendaryPlayers: [
                { id: 'isiah_thomas', name: '伊塞亚·托马斯', position: 'PG', years: '1981-1991', honors: ['2次总冠军', '12次全明星', '名人堂成员'], stats: { ppg: 19.2, rpg: 3.6, apg: 9.3, spg: 1.9 } },
                { id: 'joe_dumars', name: '乔·杜马斯', position: 'SG', years: '1985-1999', honors: ['2次总冠军', '4次全明星'], stats: { ppg: 16.1, rpg: 2.2, apg: 4.5, spg: 0.9 } },
                { id: 'chauncey_billups', name: '昌西·比卢普斯', position: 'PG', years: '2002-2014', honors: ['1次总冠军', '5次全明星'], stats: { ppg: 15.3, rpg: 2.9, apg: 5.4, spg: 1.0 } },
                { id: 'draymond_dwight_howard', name: '德怀特·霍华德', position: 'C', years: '2013-2016', honors: ['3次DPOY', '8次全明星'], stats: { ppg: 16.3, rpg: 11.8, apg: 1.4, bpg: 1.5 } }
            ]
        },
        'ATL': {
            name: 'Atlanta Hawks',
            nameCn: '亚特兰大老鹰',
            alias: '鹰击长空',
            color: '#000000',
            primary: '#C8102E',
            secondary: '#000000',
            championships: 0,
            conference: 'Eastern',
            division: 'Southeast',
            legendaryPlayers: [
                { id: 'dom Wilkins', name: '多米尼克·威尔金斯', position: 'SF', years: '1982-1994', honors: ['7次全明星', '名人堂成员'], stats: { ppg: 24.8, rpg: 6.1, apg: 3.0, spg: 1.3 } },
                { id: 'pete_maravich_hawks', name: '皮特·马拉维奇', position: 'SG', years: '1970-1974', honors: ['5次全明星', '名人堂成员'], stats: { ppg: 26.8, rpg: 3.8, apg: 5.3 } },
                { id: 'ted_turner', name: '特德·特纳', position: 'SG', years: '1982-1994', honors: ['名人堂成员'], stats: { ppg: 12.5, rpg: 2.4, apg: 5.3 } }
            ]
        },
        'CHA': {
            name: 'Charlotte Hornets',
            nameCn: '夏洛特黄蜂',
            alias: '黄蜂队',
            color: '#000000',
            primary: '#00788C',
            secondary: '#000000',
            championships: 0,
            conference: 'Eastern',
            division: 'Southeast',
            legendaryPlayers: [
                { id: 'kemba_walker', name: '肯巴·沃克', position: 'PG', years: '2011-2019', honors: ['4次全明星'], stats: { ppg: 19.6, rpg: 3.8, apg: 5.5, spg: 1.2 } },
                { id: 'gerald_wallace', name: '杰拉德·华莱士', position: 'SF', years: '2004-2013', honors: ['1次全明星', '1次抢断王'], stats: { ppg: 11.8, rpg: 5.1, apg: 2.0, spg: 1.4 } },
                { id: 'lamarcus_aldridge', name: '拉马库斯·阿尔德里奇', position: 'PF', years: '2006-2015', honors: ['7次全明星'], stats: { ppg: 21.0, rpg: 8.3, apg: 1.9 } }
            ]
        },
        'ORL': {
            name: 'Orlando Magic',
            nameCn: '奥兰多魔术',
            alias: '魔术队',
            color: '#000000',
            primary: '#0077C0',
            secondary: '#000000',
            championships: 1,
            conference: 'Eastern',
            division: 'Southeast',
            legendaryPlayers: [
                { id: 'dwight_howard', name: '德怀特·霍华德', position: 'C', years: '2004-2012', honors: ['1次总冠军', '8次全明星', '3次DPOY'], stats: { ppg: 18.4, rpg: 12.9, apg: 1.5, bpg: 2.1 } },
                { id: 'tracy_mcgrady', name: '特雷西·麦克格雷迪', position: 'SG/SF', years: '2000-2009', honors: ['7次全明星', '2次得分王'], stats: { ppg: 19.6, rpg: 5.6, apg: 4.4, spg: 1.2 } },
                { id: 'grant_hill', name: '格兰特·希尔', position: 'SF', years: '1995-2012', honors: ['7次全明星'], stats: { ppg: 16.7, rpg: 6.1, apg: 4.1, spg: 1.0 } },
                { id: 'nick_andoff', name: '尼古拉·武切维奇', position: 'C', years: '2012-2021', honors: ['4次全明星'], stats: { ppg: 16.8, rpg: 10.4, apg: 2.8 } }
            ]
        },
        'WAS': {
            name: 'Washington Wizards',
            nameCn: '华盛顿奇才',
            alias: '首都球队',
            color: '#000000',
            primary: '#E31837',
            secondary: '#002B5C',
            championships: 0,
            conference: 'Eastern',
            division: 'Southeast',
            legendaryPlayers: [
                { id: 'wes_unseld', name: '韦斯·昂塞尔德', position: 'C', years: '1968-1981', honors: ['1次总冠军', 'MVP', '名人堂成员'], stats: { ppg: 10.9, rpg: 14.0, apg: 3.9 } },
                { id: 'elvin_hayes', name: '埃尔文·海耶斯', position: 'PF/C', years: '1972-1984', honors: ['6次全明星', '名人堂成员'], stats: { ppg: 21.0, rpg: 12.5, apg: 1.8 } },
                { id: 'dominique_wizards', name: '多米尼克·威尔金斯', position: 'SF', years: '1982-1994', honors: ['7次全明星', '名人堂成员'], stats: { ppg: 24.8, rpg: 6.1, apg: 3.0, spg: 1.3 } },
                { id: 'bradley_beal', name: '布拉德利·比尔', position: 'SG', years: '2012-至今', honors: ['3次全明星'], stats: { ppg: 22.1, rpg: 4.0, apg: 4.3, spg: 1.1 } }
            ]
        }
    },

    POSITIONS: {
        'PG': '控球后卫',
        'SG': '得分后卫',
        'SF': '小前锋',
        'PF': '大前锋',
        'C': '中锋',
        'G': '后卫',
        'F': '前锋',
        'F/C': '前锋/中锋',
        'G/F': '后卫/前锋'
    },

    STAT_FIELDS: {
        'games': { label: '场次', abbr: 'G', category: 'basic', format: 'number' },
        'games_started': { label: '首发', abbr: 'GS', category: 'basic', format: 'number' },
        'minutes_played': { label: '分钟', abbr: 'MP', category: 'basic', format: 'time' },
        'points': { label: '得分', abbr: 'PTS', category: 'basic', format: 'decimal1' },
        'rebounds': { label: '篮板', abbr: 'TRB', category: 'basic', format: 'decimal1' },
        'assists': { label: '助攻', abbr: 'AST', category: 'basic', format: 'decimal1' },
        'steals': { label: '抢断', abbr: 'STL', category: 'basic', format: 'decimal1' },
        'blocks': { label: '盖帽', abbr: 'BLK', category: 'basic', format: 'decimal1' },
        'turnovers': { label: '失误', abbr: 'TOV', category: 'basic', format: 'decimal1' },
        'fg_made': { label: '投篮命中', abbr: 'FG', category: 'shooting', format: 'decimal1' },
        'fg_att': { label: '投篮出手', abbr: 'FGA', category: 'shooting', format: 'decimal1' },
        'fg_pct': { label: '投篮命中率', abbr: 'FG%', category: 'shooting', format: 'percent' },
        'three_made': { label: '三分命中', abbr: '3P', category: 'shooting', format: 'decimal1' },
        'three_att': { label: '三分出手', abbr: '3PA', category: 'shooting', format: 'decimal1' },
        'three_pct': { label: '三分命中率', abbr: '3P%', category: 'shooting', format: 'percent' },
        'ft_made': { label: '罚球命中', abbr: 'FT', category: 'shooting', format: 'decimal1' },
        'ft_att': { label: '罚球出手', abbr: 'FTA', category: 'shooting', format: 'decimal1' },
        'ft_pct': { label: '罚球命中率', abbr: 'FT%', category: 'shooting', format: 'percent' },
        'per': { label: '效率值', abbr: 'PER', category: 'advanced', format: 'decimal1' },
        'ts_pct': { label: '真实命中率', abbr: 'TS%', category: 'advanced', format: 'percent' },
        'ws': { label: '胜利贡献值', abbr: 'WS', category: 'advanced', format: 'decimal1' },
        'ws_48': { label: '每48分钟WS', abbr: 'WS/48', category: 'advanced', format: 'decimal2' },
        'bpm': { label: '每百回合正负值', abbr: 'BPM', category: 'advanced', format: 'decimal1' },
        'vorp': { label: '可替代值', abbr: 'VORP', category: 'advanced', format: 'decimal1' },
        'usg_pct': { label: '使用率', abbr: 'USG%', category: 'advanced', format: 'percent' },
        'ast_pct': { label: '助攻率', abbr: 'AST%', category: 'advanced', format: 'percent' },
        'trb_pct': { label: '篮板率', abbr: 'TRB%', category: 'advanced', format: 'percent' },
        'ows': { label: '进攻胜利贡献', abbr: 'OWS', category: 'advanced', format: 'decimal1' },
        'dws': { label: '防守胜利贡献', abbr: 'DWS', category: 'advanced', format: 'decimal1' },
        'obpm': { label: '进攻正负值', abbr: 'OBPM', category: 'advanced', format: 'decimal1' },
        'dbpm': { label: '防守正负值', abbr: 'DBPM', category: 'advanced', format: 'decimal1' }
    },

    RADAR_METRICS: {
        scoring: { label: '得分', fields: ['points'], weight: 1.0, threshold: 20 },
        rebounding: { label: '篮板', fields: ['rebounds'], weight: 0.8, threshold: 8 },
        assisting: { label: '助攻', fields: ['assists'], weight: 0.9, threshold: 8 },
        defense: { label: '防守', fields: ['steals', 'blocks'], weight: 1.0, threshold: 2.5 },
        shooting: { label: '投篮', fields: ['fg_pct'], weight: 0.7, threshold: 0.50 },
        efficiency: { label: '效率', fields: ['per'], weight: 0.9, threshold: 20 }
    },

    STAT_CATEGORIES: {
        basic: { label: '基础统计', order: 1 },
        shooting: { label: '投篮统计', order: 2 },
        advanced: { label: '高阶统计', order: 3 }
    },

    DEFAULT_SEASON: '2025-2026',

    CHART_COLORS: {
        primary: '#007bff',
        gold: '#FFD700',
        silver: '#C0C0C0',
        bronze: '#CD7F32',
        green: '#28a745',
        red: '#dc3545'
    }
};

window.Constants = Constants;
