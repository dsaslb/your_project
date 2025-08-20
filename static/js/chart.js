// Chart.js 대체 라이브러리 - 기본 차트 기능 제공
class Chart {
    constructor(ctx, config) {
        this.ctx = ctx;
        this.config = config;
        this.canvas = ctx.canvas;
        this.type = config.type || 'line';
        this.data = config.data || {};
        this.options = config.options || {};
        
        this.init();
    }
    
    init() {
        // 캔버스 크기 설정
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        
        // 차트 타입에 따른 렌더링
        switch(this.type) {
            case 'line':
                this.renderLineChart();
                break;
            case 'bar':
                this.renderBarChart();
                break;
            case 'pie':
                this.renderPieChart();
                break;
            case 'doughnut':
                this.renderDoughnutChart();
                break;
            default:
                this.renderLineChart();
        }
    }
    
    renderLineChart() {
        const datasets = this.data.datasets || [];
        const labels = this.data.labels || [];
        
        if (datasets.length === 0) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 40;
        
        // 배경 지우기
        ctx.clearRect(0, 0, width, height);
        
        // 데이터 범위 계산
        let minValue = Infinity;
        let maxValue = -Infinity;
        
        datasets.forEach(dataset => {
            dataset.data.forEach(value => {
                if (value < minValue) minValue = value;
                if (value > maxValue) maxValue = value;
            });
        });
        
        const range = maxValue - minValue;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;
        
        // 그리드 그리기
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        
        // 수직 그리드
        for (let i = 0; i <= labels.length; i++) {
            const x = padding + (i * chartWidth) / labels.length;
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            ctx.stroke();
        }
        
        // 수평 그리드
        const gridLines = 5;
        for (let i = 0; i <= gridLines; i++) {
            const y = padding + (i * chartHeight) / gridLines;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // 데이터 라인 그리기
        datasets.forEach((dataset, datasetIndex) => {
            ctx.strokeStyle = dataset.borderColor || '#ff6b35';
            ctx.lineWidth = dataset.borderWidth || 2;
            ctx.fillStyle = dataset.backgroundColor || 'rgba(255, 107, 53, 0.1)';
            
            ctx.beginPath();
            
            dataset.data.forEach((value, index) => {
                const x = padding + (index * chartWidth) / (labels.length - 1);
                const y = height - padding - ((value - minValue) * chartHeight) / range;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // 영역 채우기
            if (dataset.fill !== false) {
                ctx.lineTo(width - padding, height - padding);
                ctx.lineTo(padding, height - padding);
                ctx.closePath();
                ctx.fill();
            }
        });
        
        // 라벨 그리기
        ctx.fillStyle = '#888';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        labels.forEach((label, index) => {
            const x = padding + (index * chartWidth) / (labels.length - 1);
            ctx.fillText(label, x, height - padding + 20);
        });
    }
    
    renderBarChart() {
        const datasets = this.data.datasets || [];
        const labels = this.data.labels || [];
        
        if (datasets.length === 0) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 40;
        
        // 배경 지우기
        ctx.clearRect(0, 0, width, height);
        
        // 데이터 범위 계산
        let maxValue = 0;
        datasets.forEach(dataset => {
            dataset.data.forEach(value => {
                if (value > maxValue) maxValue = value;
            });
        });
        
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;
        const barWidth = chartWidth / (labels.length * datasets.length);
        
        // 바 그리기
        datasets.forEach((dataset, datasetIndex) => {
            ctx.fillStyle = dataset.backgroundColor || '#ff6b35';
            ctx.strokeStyle = dataset.borderColor || '#ff6b35';
            ctx.lineWidth = dataset.borderWidth || 1;
            
            dataset.data.forEach((value, index) => {
                const barHeight = (value / maxValue) * chartHeight;
                const x = padding + (index * chartWidth) / labels.length + (datasetIndex * barWidth);
                const y = height - padding - barHeight;
                
                ctx.fillRect(x, y, barWidth - 2, barHeight);
                ctx.strokeRect(x, y, barWidth - 2, barHeight);
            });
        });
        
        // 라벨 그리기
        ctx.fillStyle = '#888';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        labels.forEach((label, index) => {
            const x = padding + (index * chartWidth) / labels.length + (chartWidth / labels.length) / 2;
            ctx.fillText(label, x, height - padding + 20);
        });
    }
    
    renderPieChart() {
        const datasets = this.data.datasets || [];
        
        if (datasets.length === 0 || !datasets[0].data) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        
        // 배경 지우기
        ctx.clearRect(0, 0, width, height);
        
        const data = datasets[0].data;
        const total = data.reduce((sum, value) => sum + value, 0);
        let currentAngle = -Math.PI / 2;
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            const backgroundColor = datasets[0].backgroundColor || '#ff6b35';
            const colors = Array.isArray(backgroundColor) ? backgroundColor : [backgroundColor];
            
            ctx.fillStyle = colors[index % colors.length];
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            
            currentAngle += sliceAngle;
        });
    }
    
    renderDoughnutChart() {
        this.renderPieChart();
        
        // 중앙에 구멍 만들기
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        const innerRadius = radius * 0.6;
        
        ctx.fillStyle = '#1a1a1a';
        ctx.beginPath();
        ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    update() {
        this.init();
    }
    
    destroy() {
        // 캔버스 지우기
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// 전역 객체에 Chart 추가
if (typeof window !== 'undefined') {
    window.Chart = Chart;
}
