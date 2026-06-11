/**
 * NBA数据 - 导航栏组件
 * 可复用的球队主题导航栏
 */

const Navbar = {
    navbarElement: null,
    isMinimized: false,

    /**
     * 初始化导航栏
     */
    init(teamAbbr, teamConfig) {
        this.navbarElement = document.getElementById('navbar');
        if (!this.navbarElement) {
            console.error('Navbar element not found');
            return;
        }

        this.setTeamInfo(teamConfig);
        this.setTeamLogo(teamAbbr);
        this.bindEvents();
    },

    /**
     * 设置球队信息
     */
    setTeamInfo(teamConfig) {
        const nameCn = document.getElementById('team-name-cn');
        const nameEn = document.getElementById('team-name-en');
        const alias = document.getElementById('team-alias');

        if (nameCn) nameCn.textContent = teamConfig.nameCn;
        if (nameEn) nameEn.textContent = teamConfig.name;
        if (alias) alias.textContent = teamConfig.alias;
    },

    /**
     * 设置球队logo
     */
    setTeamLogo(teamAbbr) {
        const logo = document.getElementById('team-logo');
        if (logo) {
            logo.style.backgroundImage = `url('/nbalogo/${teamAbbr}.svg')`;
        }
    },

    /**
     * 绑定事件
     */
    bindEvents() {
        if (this.navbarElement) {
            this.navbarElement.addEventListener('click', () => {
                this.toggleMinimize();
            });
        }
    },

    /**
     * 切换最小化状态
     */
    toggleMinimize() {
        if (this.navbarElement) {
            this.isMinimized = !this.isMinimized;
            this.navbarElement.classList.toggle('minimized', this.isMinimized);
        }
    },

    /**
     * 设置最小化状态
     */
    setMinimized(minimized) {
        this.isMinimized = minimized;
        if (this.navbarElement) {
            this.navbarElement.classList.toggle('minimized', minimized);
        }
    }
};

window.Navbar = Navbar;
