// 가계부 Vue.js 애플리케이션
const { createApp } = Vue;

createApp({
    data() {
        return {
            // 현재 월/년
            currentYear: new Date().getFullYear(),
            currentMonth: new Date().getMonth() + 1,
            
            // 데이터
            items: [],
            summary: {
                total_income: 0,
                total_expense: 0,
                balance: 0,
                income_details: [],
                expense_details: []
            },
            upcoming: [],
            categories: {
                income: ['급여', '용돈', '투자수익', '부업수입', '기타수입'],
                expense: ['주거비', '통신비', '교통비', '식비', '의료비', '교육비', '문화생활', '구독서비스', '기타지출']
            },
            
            // UI 상태
            activeTab: 'items',
            showAddModal: false,
            loading: false,
            
            // 새 항목 폼
            newItem: {
                name: '',
                amount: '',
                item_type: 'expense',
                category: '',
                frequency: 'monthly',
                start_date: new Date().toISOString().split('T')[0],
                memo: ''
            },
            
            // 차트 인스턴스
            monthlyChart: null,
            incomeChart: null,
            expenseChart: null
        }
    },
    
    mounted() {
        this.loadData();
        this.setupCharts();
        this.setupPWA();
    },
    
    methods: {
        // 데이터 로드
        async loadData() {
            this.loading = true;
            try {
                await Promise.all([
                    this.loadItems(),
                    this.loadSummary(),
                    this.loadUpcoming()
                ]);
            } catch (error) {
                console.error('데이터 로드 실패:', error);
                this.showNotification('데이터 로드를 실패했습니다.', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadItems() {
            try {
                const response = await axios.get('/api/ledger/items?user_id=1');
                if (response.data.success) {
                    this.items = response.data.items;
                }
            } catch (error) {
                console.error('항목 로드 실패:', error);
            }
        },
        
        async loadSummary() {
            try {
                const response = await axios.get(`/api/ledger/summary/${this.currentYear}/${this.currentMonth}?user_id=1`);
                if (response.data.success) {
                    this.summary = response.data.summary;
                    this.updateMonthlyChart();
                }
            } catch (error) {
                console.error('요약 로드 실패:', error);
            }
        },
        
        async loadUpcoming() {
            try {
                const response = await axios.get('/api/ledger/upcoming?user_id=1&days=30');
                if (response.data.success) {
                    this.upcoming = response.data.upcoming;
                }
            } catch (error) {
                console.error('예정 로드 실패:', error);
            }
        },
        
        // 월 변경
        previousMonth() {
            if (this.currentMonth === 1) {
                this.currentMonth = 12;
                this.currentYear--;
            } else {
                this.currentMonth--;
            }
            this.loadSummary();
        },
        
        nextMonth() {
            if (this.currentMonth === 12) {
                this.currentMonth = 1;
                this.currentYear++;
            } else {
                this.currentMonth++;
            }
            this.loadSummary();
        },
        
        // 항목 관리
        async addItem() {
            try {
                const response = await axios.post('/api/ledger/items', {
                    ...this.newItem,
                    user_id: 1
                });
                
                if (response.data.success) {
                    this.showNotification('항목이 추가되었습니다.', 'success');
                    this.showAddModal = false;
                    this.resetNewItem();
                    this.loadData();
                }
            } catch (error) {
                console.error('항목 추가 실패:', error);
                this.showNotification('항목 추가에 실패했습니다.', 'error');
            }
        },
        
        async editItem(item) {
            // TODO: 편집 모달 구현
            this.showNotification('편집 기능은 준비 중입니다.', 'info');
        },
        
        async deleteItem(itemId) {
            if (!confirm('정말로 이 항목을 삭제하시겠습니까?')) {
                return;
            }
            
            try {
                const response = await axios.delete(`/api/ledger/items/${itemId}?user_id=1`);
                if (response.data.success) {
                    this.showNotification('항목이 삭제되었습니다.', 'success');
                    this.loadData();
                }
            } catch (error) {
                console.error('항목 삭제 실패:', error);
                this.showNotification('항목 삭제에 실패했습니다.', 'error');
            }
        },
        
        // 폼 관리
        resetNewItem() {
            this.newItem = {
                name: '',
                amount: '',
                item_type: 'expense',
                category: '',
                frequency: 'monthly',
                start_date: new Date().toISOString().split('T')[0],
                memo: ''
            };
        },
        
        getCategories(type) {
            return this.categories[type] || [];
        },
        
        // 차트 설정
        setupCharts() {
            this.setupMonthlyChart();
            this.setupCategoryCharts();
        },
        
        setupMonthlyChart() {
            const ctx = document.getElementById('monthlyChart');
            if (!ctx) return;
            
            this.monthlyChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['수입', '지출', '잔액'],
                    datasets: [{
                        label: '금액',
                        data: [0, 0, 0],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(220, 53, 69, 0.8)',
                            'rgba(0, 123, 255, 0.8)'
                        ],
                        borderColor: [
                            'rgba(40, 167, 69, 1)',
                            'rgba(220, 53, 69, 1)',
                            'rgba(0, 123, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return new Intl.NumberFormat('ko-KR', {
                                        style: 'currency',
                                        currency: 'KRW'
                                    }).format(value);
                                }
                            }
                        }
                    }
                }
            });
        },
        
        setupCategoryCharts() {
            // 수입 카테고리 차트
            const incomeCtx = document.getElementById('incomeChart');
            if (incomeCtx) {
                this.incomeChart = new Chart(incomeCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            backgroundColor: [
                                '#28a745', '#20c997', '#17a2b8', '#007bff', '#6f42c1'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
            
            // 지출 카테고리 차트
            const expenseCtx = document.getElementById('expenseChart');
            if (expenseCtx) {
                this.expenseChart = new Chart(expenseCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            backgroundColor: [
                                '#dc3545', '#fd7e14', '#ffc107', '#28a745', '#17a2b8'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        },
        
        updateMonthlyChart() {
            if (this.monthlyChart) {
                this.monthlyChart.data.datasets[0].data = [
                    this.summary.total_income,
                    this.summary.total_expense,
                    this.summary.balance
                ];
                this.monthlyChart.update();
            }
        },
        
        updateCategoryCharts() {
            // 수입 카테고리 차트 업데이트
            if (this.incomeChart) {
                const incomeData = this.summary.income_details.reduce((acc, item) => {
                    acc[item.category] = (acc[item.category] || 0) + item.amount;
                    return acc;
                }, {});
                
                this.incomeChart.data.labels = Object.keys(incomeData);
                this.incomeChart.data.datasets[0].data = Object.values(incomeData);
                this.incomeChart.update();
            }
            
            // 지출 카테고리 차트 업데이트
            if (this.expenseChart) {
                const expenseData = this.summary.expense_details.reduce((acc, item) => {
                    acc[item.category] = (acc[item.category] || 0) + item.amount;
                    return acc;
                }, {});
                
                this.expenseChart.data.labels = Object.keys(expenseData);
                this.expenseChart.data.datasets[0].data = Object.values(expenseData);
                this.expenseChart.update();
            }
        },
        
        // 유틸리티 함수
        formatCurrency(amount) {
            return new Intl.NumberFormat('ko-KR', {
                style: 'currency',
                currency: 'KRW'
            }).format(amount);
        },
        
        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('ko-KR');
        },
        
        getFrequencyText(frequency) {
            const texts = {
                'daily': '일별',
                'weekly': '주별',
                'monthly': '월별',
                'yearly': '연별'
            };
            return texts[frequency] || frequency;
        },
        
        getDaysUntilClass(days) {
            if (days <= 3) return 'urgent';
            if (days <= 7) return 'warning';
            return 'normal';
        },
        
        refreshData() {
            this.loadData();
            this.showNotification('데이터가 새로고침되었습니다.', 'success');
        },
        
        // 알림
        showNotification(message, type = 'info') {
            // 간단한 토스트 알림
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                animation: slideIn 0.3s ease;
            `;
            
            // 타입별 색상
            const colors = {
                success: '#28a745',
                error: '#dc3545',
                warning: '#ffc107',
                info: '#17a2b8'
            };
            toast.style.backgroundColor = colors[type] || colors.info;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            }, 3000);
        },
        
        // PWA 설정
        setupPWA() {
            // 서비스 워커 등록
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW 등록 성공:', registration);
                    })
                    .catch(error => {
                        console.log('SW 등록 실패:', error);
                    });
            }
            
            // 설치 프롬프트
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;
                
                // 설치 버튼 표시 (선택사항)
                this.showInstallButton();
            });
        },
        
        showInstallButton() {
            // 설치 버튼을 헤더에 추가
            const installBtn = document.createElement('button');
            installBtn.className = 'btn btn-secondary';
            installBtn.innerHTML = '<i class="fas fa-download"></i> 설치';
            installBtn.onclick = this.installPWA;
            
            const headerRight = document.querySelector('.header-right');
            if (headerRight) {
                headerRight.appendChild(installBtn);
            }
        },
        
        async installPWA() {
            if (window.deferredPrompt) {
                window.deferredPrompt.prompt();
                const { outcome } = await window.deferredPrompt.userChoice;
                console.log(`사용자 선택: ${outcome}`);
                window.deferredPrompt = null;
            }
        }
    },
    
    watch: {
        summary: {
            handler() {
                this.updateCategoryCharts();
            },
            deep: true
        }
    }
}).mount('#app');

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 