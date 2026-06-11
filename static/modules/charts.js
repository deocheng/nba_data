/**
 * NBA Data Module - 图表模块
 * 提供数据可视化功能
 */

const Charts = {
    /**
     * 渲染雷达图
     */
    renderRadarChart: (canvasId, data, options = {}) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element ${canvasId} not found`);
            return null;
        }

        const {
            size = 400,
            labelColor = '#333',
            bgColor = 'rgba(255, 255, 255, 0.9)',
            gridColor = 'rgba(0, 0, 0, 0.1)',
            topTierColor = Constants.CHART_COLORS.gold,
            normalColor = 'rgba(0, 123, 255, 0.5)',
            topTierBorderColor = Constants.CHART_COLORS.gold,
            normalBorderColor = 'rgba(0, 123, 255, 0.8)',
            showLabels = true,
            showValues = true,
            showThresholds = true,
            animation = true
        } = options;

        const ctx = canvas.getContext('2d');
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = size * 0.35;

        // 设置canvas尺寸
        canvas.width = size;
        canvas.height = size;

        // 清除画布
        ctx.clearRect(0, 0, size, size);

        // 绘制背景
        ctx.fillStyle = bgColor;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * 1.2, 0, Math.PI * 2);
        ctx.fill();

        const numPoints = data.length;
        const angleStep = (Math.PI * 2) / numPoints;

        // 绘制背景网格
        const levels = 5;
        for (let level = 1; level <= levels; level++) {
            const levelRadius = (radius * level) / levels;
            
            ctx.strokeStyle = gridColor;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            
            for (let i = 0; i <= numPoints; i++) {
                const angle = (i * angleStep) - Math.PI / 2;
                const x = centerX + Math.cos(angle) * levelRadius;
                const y = centerY + Math.sin(angle) * levelRadius;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            ctx.stroke();

            // 绘制径向线
            for (let i = 0; i < numPoints; i++) {
                const angle = (i * angleStep) - Math.PI / 2;
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;
                
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(x, y);
                ctx.stroke();
            }
        }

        // 绘制数据区域
        const points = [];
        for (let i = 0; i < numPoints; i++) {
            const point = data[i];
            const angle = (i * angleStep) - Math.PI / 2;
            const valueRadius = (point.normalized / 100) * radius;
            
            const x = centerX + Math.cos(angle) * valueRadius;
            const y = centerY + Math.sin(angle) * valueRadius;
            points.push({ x, y, ...point });
        }

        // 绘制数据填充
        ctx.beginPath();
        points.forEach((point, index) => {
            if (index === 0) {
                ctx.moveTo(point.x, point.y);
            } else {
                ctx.lineTo(point.x, point.y);
            }
        });
        ctx.closePath();

        const isTopTier = data.some(d => d.isTopTier);
        ctx.fillStyle = isTopTier ? 
            'rgba(255, 215, 0, 0.3)' : 
            'rgba(0, 123, 255, 0.2)';
        ctx.fill();

        ctx.strokeStyle = isTopTier ? topTierBorderColor : normalBorderColor;
        ctx.lineWidth = 2;
        ctx.stroke();

        // 绘制数据点
        points.forEach(point => {
            ctx.beginPath();
            ctx.arc(point.x, point.y, point.isTopTier ? 6 : 4, 0, Math.PI * 2);
            ctx.fillStyle = point.isTopTier ? topTierColor : normalColor;
            ctx.fill();
            ctx.strokeStyle = point.isTopTier ? topTierBorderColor : normalBorderColor;
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        // 绘制标签
        if (showLabels) {
            for (let i = 0; i < numPoints; i++) {
                const point = data[i];
                const angle = (i * angleStep) - Math.PI / 2;
                const labelRadius = radius + 30;
                
                const x = centerX + Math.cos(angle) * labelRadius;
                const y = centerY + Math.sin(angle) * labelRadius;
                
                ctx.font = point.isTopTier ? 'bold 14px Arial' : '12px Arial';
                ctx.fillStyle = point.isTopTier ? topTierColor : labelColor;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(point.label, x, y);

                // 显示数值
                if (showValues) {
                    ctx.font = '11px Arial';
                    ctx.fillStyle = point.isTopTier ? topTierColor : '#666';
                    ctx.fillText(Utils.formatNumber(point.value, 1), x, y + 16);
                }

                // 显示阈值标记
                if (showThresholds && point.threshold) {
                    ctx.font = '10px Arial';
                    ctx.fillStyle = '#999';
                    ctx.fillText(`(${point.threshold}+)`, x, y + 30);
                }
            }
        }

        return { canvas, ctx, points };
    },

    /**
     * 创建雷达图HTML容器
     */
    createRadarContainer: (id, title = '', options = {}) => {
        const {
            width = 450,
            height = 450
        } = options;

        return `
            <div class="radar-chart-container">
                ${title ? `<h3 class="radar-title">${title}</h3>` : ''}
                <div class="radar-chart-wrapper">
                    <canvas id="${id}"></canvas>
                </div>
                <div class="radar-legend">
                    <div class="legend-item">
                        <span class="legend-icon" style="background: ${Constants.CHART_COLORS.gold}"></span>
                        <span>顶级表现</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-icon" style="background: rgba(0, 123, 255, 0.5)"></span>
                        <span>普通表现</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 渲染趋势线图
     */
    renderLineChart: (canvasId, data, options = {}) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const {
            width = 600,
            height = 300,
            lineColor = Constants.CHART_COLORS.primary,
            pointColor = Constants.CHART_COLORS.primary,
            bgColor = '#fff',
            showGrid = true,
            showValues = true
        } = options;

        const ctx = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;

        ctx.clearRect(0, 0, width, height);

        // 背景
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, width, height);

        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        // 计算数据范围
        const values = data.map(d => d.value);
        const maxValue = Math.max(...values) * 1.1;
        const minValue = Math.min(...values) * 0.9;

        // 绘制网格
        if (showGrid) {
            const gridLines = 5;
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.lineWidth = 1;

            for (let i = 0; i <= gridLines; i++) {
                const y = padding + (chartHeight * i) / gridLines;
                ctx.beginPath();
                ctx.moveTo(padding, y);
                ctx.lineTo(width - padding, y);
                ctx.stroke();
            }
        }

        // 绘制折线
        const stepX = chartWidth / (data.length - 1 || 1);
        
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 2;
        ctx.beginPath();

        data.forEach((point, index) => {
            const x = padding + index * stepX;
            const y = padding + chartHeight - ((point.value - minValue) / (maxValue - minValue)) * chartHeight;

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();

        // 绘制数据点
        data.forEach((point, index) => {
            const x = padding + index * stepX;
            const y = padding + chartHeight - ((point.value - minValue) / (maxValue - minValue)) * chartHeight;

            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fillStyle = pointColor;
            ctx.fill();

            // 显示标签
            if (showValues && point.label) {
                ctx.font = '10px Arial';
                ctx.fillStyle = '#666';
                ctx.textAlign = 'center';
                ctx.fillText(point.label, x, height - 10);
            }
        });

        return { canvas, ctx };
    },

    /**
     * 渲染柱状图
     */
    renderBarChart: (canvasId, data, options = {}) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const {
            width = 600,
            height = 300,
            barColor = Constants.CHART_COLORS.primary,
            bgColor = '#fff',
            showValues = true
        } = options;

        const ctx = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;

        ctx.clearRect(0, 0, width, height);

        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        const values = data.map(d => d.value);
        const maxValue = Math.max(...values) * 1.1;

        const barWidth = (chartWidth / data.length) * 0.7;
        const gap = (chartWidth / data.length) * 0.3;

        data.forEach((item, index) => {
            const barHeight = (item.value / maxValue) * chartHeight;
            const x = padding + index * (barWidth + gap) + gap / 2;
            const y = padding + chartHeight - barHeight;

            ctx.fillStyle = item.color || barColor;
            ctx.fillRect(x, y, barWidth, barHeight);

            // 显示标签
            if (item.label) {
                ctx.font = '10px Arial';
                ctx.fillStyle = '#666';
                ctx.textAlign = 'center';
                ctx.fillText(item.label, x + barWidth / 2, height - 10);
            }

            // 显示数值
            if (showValues) {
                ctx.font = '11px Arial';
                ctx.fillStyle = '#333';
                ctx.textAlign = 'center';
                ctx.fillText(Utils.formatNumber(item.value, 1), x + barWidth / 2, y - 5);
            }
        });

        return { canvas, ctx };
    }
};

window.Charts = Charts;
