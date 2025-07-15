/**
 * 주소 검색 기능 - 개선된 버전
 * 카카오 주소 검색 API를 활용한 주소 검색 및 자동 입력
 */

class AddressSearch {
    constructor(options = {}) {
        this.options = {
            apiKey: options.apiKey || 'YOUR_KAKAO_API_KEY', // 카카오 API 키
            searchButtonId: options.searchButtonId || 'address-search-btn',
            addressInputId: options.addressInputId || 'address-input',
            detailAddressId: options.detailAddressId || 'detail-address-input',
            zipCodeId: options.zipCodeId || 'zipcode-input',
            roadAddressId: options.roadAddressId || 'road-address-input',
            jibunAddressId: options.jibunAddressId || 'jibun-address-input',
            latitudeId: options.latitudeId || 'latitude-input',
            longitudeId: options.longitudeId || 'longitude-input',
            onAddressSelected: options.onAddressSelected || null,
            onError: options.onError || null,
            enableAutoComplete: options.enableAutoComplete !== false, // 자동완성 활성화
            enableValidation: options.enableValidation !== false, // 실시간 검증 활성화
            enableCoordinates: options.enableCoordinates !== false, // 좌표 자동 조회 활성화
            debounceDelay: options.debounceDelay || 300, // 디바운스 지연시간
            maxSuggestions: options.maxSuggestions || 5 // 최대 제안 수
        };
        
        this.debounceTimer = null;
        this.isLoading = false;
        this.suggestions = [];
        this.currentSuggestionIndex = -1;
        
        this.init();
    }

    init() {
        // 카카오 주소 검색 API 스크립트 로드
        this.loadKakaoScript();
        
        // 이벤트 리스너 등록
        this.bindEvents();
        
        // 자동완성 초기화
        if (this.options.enableAutoComplete) {
            this.initAutoComplete();
        }
    }

    loadKakaoScript() {
        // 이미 로드된 경우 스킵
        if (window.daum && window.daum.Postcode) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = '//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js';
            script.async = true;
            script.onload = () => {
                console.log('카카오 주소 검색 API 로드 완료');
                resolve();
            };
            script.onerror = () => {
                console.error('카카오 주소 검색 API 로드 실패');
                reject(new Error('주소 검색 API를 로드할 수 없습니다.'));
            };
            document.head.appendChild(script);
        });
    }

    bindEvents() {
        // 주소 검색 버튼 클릭 이벤트
        const searchButton = document.getElementById(this.options.searchButtonId);
        if (searchButton) {
            searchButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.openAddressSearch();
            });
        }

        // 주소 입력 필드 클릭 이벤트 (자동 검색)
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.addEventListener('click', (e) => {
                e.preventDefault();
                this.openAddressSearch();
            });
            
            // 실시간 검증
            if (this.options.enableValidation) {
                addressInput.addEventListener('input', (e) => {
                    this.debounceValidation(e.target.value);
                });
                
                addressInput.addEventListener('blur', (e) => {
                    this.validateAddressOnBlur(e.target.value);
                });
            }
        }

        // 상세주소 필드 이벤트
        const detailAddressInput = document.getElementById(this.options.detailAddressId);
        if (detailAddressInput) {
            detailAddressInput.addEventListener('input', (e) => {
                this.updateFullAddress();
            });
        }
    }

    initAutoComplete() {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (!addressInput) return;

        // 자동완성 컨테이너 생성
        const autocompleteContainer = document.createElement('div');
        autocompleteContainer.id = 'address-autocomplete';
        autocompleteContainer.className = 'address-autocomplete-container';
        autocompleteContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        addressInput.parentNode.style.position = 'relative';
        addressInput.parentNode.appendChild(autocompleteContainer);

        // 키보드 이벤트 처리
        addressInput.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // 자동완성 제안 클릭 이벤트
        autocompleteContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-item')) {
                this.selectSuggestion(e.target.dataset.address);
            }
        });
    }

    async debounceValidation(address) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.validateAddress(address);
        }, this.options.debounceDelay);
    }

    async validateAddress(address) {
        if (!address || address.trim().length < 2) {
            this.hideAutoComplete();
            return;
        }

        try {
            this.isLoading = true;
            this.showLoadingIndicator();

            const response = await fetch('/api/admin/address-suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    query: address,
                    limit: this.options.maxSuggestions
                })
            });

            const data = await response.json();
            
            if (data.success && data.suggestions.length > 0) {
                this.suggestions = data.suggestions;
                this.showAutoComplete();
            } else {
                this.hideAutoComplete();
            }

        } catch (error) {
            console.warn('주소 제안 조회 실패:', error);
            this.hideAutoComplete();
        } finally {
            this.isLoading = false;
            this.hideLoadingIndicator();
        }
    }

    async validateAddressOnBlur(address) {
        if (!address || address.trim().length === 0) return;

        // 주소 유효성 검증
        fetch('/api/admin/validate-address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ address })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.hideValidationError();
            } else {
                this.showValidationError(data.error || '유효하지 않은 주소입니다.');
            }
        })
        .catch(error => {
            this.showValidationError('주소 검증 중 오류가 발생했습니다.');
        });
    }

    showAutoComplete() {
        const container = document.getElementById('address-autocomplete');
        if (!container) return;

        const suggestionsHtml = this.suggestions.map((suggestion, index) => `
            <div class="suggestion-item" data-address="${suggestion}" style="
                padding: 8px 12px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                background: ${index === this.currentSuggestionIndex ? '#f0f0f0' : 'white'};
            ">
                <i class="fas fa-map-marker-alt" style="margin-right: 8px; color: #666;"></i>
                ${suggestion}
            </div>
        `).join('');

        container.innerHTML = suggestionsHtml;
        container.style.display = 'block';
    }

    hideAutoComplete() {
        const container = document.getElementById('address-autocomplete');
        if (container) {
            container.style.display = 'none';
        }
        this.currentSuggestionIndex = -1;
    }

    selectSuggestion(address) {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.value = address;
        }
        this.hideAutoComplete();
        this.updateFullAddress();
    }

    handleKeyboardNavigation(e) {
        const container = document.getElementById('address-autocomplete');
        if (!container || container.style.display === 'none') return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentSuggestionIndex = Math.min(this.currentSuggestionIndex + 1, this.suggestions.length - 1);
                this.updateSuggestionHighlight();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.currentSuggestionIndex = Math.max(this.currentSuggestionIndex - 1, -1);
                this.updateSuggestionHighlight();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.currentSuggestionIndex >= 0) {
                    this.selectSuggestion(this.suggestions[this.currentSuggestionIndex]);
                }
                break;
            case 'Escape':
                this.hideAutoComplete();
                break;
        }
    }

    updateSuggestionHighlight() {
        const items = document.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.style.background = index === this.currentSuggestionIndex ? '#f0f0f0' : 'white';
        });
    }

    showLoadingIndicator() {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'20\' height=\'20\' viewBox=\'0 0 20 20\'%3E%3Cpath fill=\'%23999\' d=\'M10 3.5A1.5 1.5 0 0 1 11.5 5v2a1.5 1.5 0 0 1-3 0V5A1.5 1.5 0 0 1 10 3.5z\'/%3E%3Cpath fill=\'%23999\' d=\'M10 8.5a1.5 1.5 0 0 1 1.5 1.5v2a1.5 1.5 0 0 1-3 0v-2A1.5 1.5 0 0 1 10 8.5z\'/%3E%3C/svg%3E")';
            addressInput.style.backgroundRepeat = 'no-repeat';
            addressInput.style.backgroundPosition = 'right 8px center';
        }
    }

    hideLoadingIndicator() {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.style.backgroundImage = '';
        }
    }

    showValidationError(message) {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.style.borderColor = '#dc3545';
            
            // 기존 에러 메시지 제거
            const existingError = addressInput.parentNode.querySelector('.validation-error');
            if (existingError) {
                existingError.remove();
            }
            
            // 새 에러 메시지 추가
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-error';
            errorDiv.style.cssText = 'color: #dc3545; font-size: 12px; margin-top: 4px;';
            errorDiv.textContent = message;
            addressInput.parentNode.appendChild(errorDiv);
        }
    }

    hideValidationError() {
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.style.borderColor = '';
            
            const existingError = addressInput.parentNode.querySelector('.validation-error');
            if (existingError) {
                existingError.remove();
            }
        }
    }

    updateFullAddress() {
        const addressInput = document.getElementById(this.options.addressInputId);
        const detailAddressInput = document.getElementById(this.options.detailAddressId);
        
        if (addressInput && detailAddressInput) {
            const baseAddress = addressInput.value;
            const detailAddress = detailAddressInput.value;
            
            if (baseAddress && detailAddress) {
                // 전체 주소 필드 업데이트 (필요한 경우)
                const fullAddressInput = document.getElementById('full-address-input');
                if (fullAddressInput) {
                    fullAddressInput.value = `${baseAddress} ${detailAddress}`;
                }
            }
        }
    }

    openAddressSearch() {
        this.loadKakaoScript().then(() => {
            if (!window.daum || !window.daum.Postcode) {
                throw new Error('카카오 주소 검색 API를 로드할 수 없습니다.');
            }

            new window.daum.Postcode({
                oncomplete: (data) => {
                    this.handleAddressSelected(data);
                },
                onclose: (state) => {
                    if (state === 'FORCE_CLOSE') {
                        console.log('사용자가 주소 검색을 취소했습니다.');
                    }
                },
                width: '100%',
                height: '100%',
                animation: true,
                hideMapBtn: false,
                hideEngBtn: false,
                pleaseReadGuide: 0
            }).open();
        }).catch(error => {
            console.error('주소 검색 오류:', error);
            if (this.options.onError) {
                this.options.onError(error.message);
            }
        });
    }

    handleAddressSelected(data) {
        try {
            // 주소 정보를 각 필드에 자동 입력
            this.fillAddressFields(data);
            
            // 위도/경도 정보 자동 조회 (활성화된 경우)
            if (this.options.enableCoordinates) {
                this.getCoordinates(data.address);
            }
            
            // 전체 주소 업데이트
            this.updateFullAddress();
            
            // 콜백 함수 실행
            if (this.options.onAddressSelected) {
                this.options.onAddressSelected(data);
            }
            
            // 성공 메시지 표시
            this.showMessage('주소가 성공적으로 입력되었습니다.', 'success');
            
            // 자동완성 숨기기
            this.hideAutoComplete();
            
        } catch (error) {
            console.error('주소 처리 중 오류:', error);
            if (this.options.onError) {
                this.options.onError('주소 처리 중 오류가 발생했습니다.');
            }
        }
    }

    fillAddressFields(data) {
        // 우편번호
        const zipCodeInput = document.getElementById(this.options.zipCodeId);
        if (zipCodeInput) {
            zipCodeInput.value = data.zonecode || '';
        }

        // 도로명주소
        const roadAddressInput = document.getElementById(this.options.roadAddressId);
        if (roadAddressInput) {
            roadAddressInput.value = data.roadAddress || '';
        }

        // 지번주소
        const jibunAddressInput = document.getElementById(this.options.jibunAddressId);
        if (jibunAddressInput) {
            jibunAddressInput.value = data.jibunAddress || '';
        }

        // 기본 주소 입력 필드 (도로명주소 우선)
        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.value = data.roadAddress || data.jibunAddress || '';
        }

        // 상세주소 필드 포커스
        const detailAddressInput = document.getElementById(this.options.detailAddressId);
        if (detailAddressInput) {
            detailAddressInput.focus();
        }
    }

    async getCoordinates(address) {
        try {
            const response = await fetch('/api/admin/geocode-address', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ address: address })
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // 위도/경도 필드에 입력
                    const latitudeInput = document.getElementById(this.options.latitudeId);
                    const longitudeInput = document.getElementById(this.options.longitudeId);
                    
                    if (latitudeInput) {
                        latitudeInput.value = data.latitude || '';
                    }
                    if (longitudeInput) {
                        longitudeInput.value = data.longitude || '';
                    }
                }
            }
        } catch (error) {
            console.warn('위도/경도 조회 실패:', error);
        }
    }

    showMessage(message, type = 'info') {
        // Toast 메시지 표시 (개선된 버전)
        const toast = document.createElement('div');
        toast.className = `address-toast address-toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-size: 14px;
            z-index: 10000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            ${type === 'success' ? 'background: #28a745;' : 
              type === 'error' ? 'background: #dc3545;' : 
              'background: #17a2b8;'}
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        // 애니메이션
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 100);

        // 자동 제거
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // 주소 유효성 검증
    validateAddress(address) {
        if (!address || address.trim().length === 0) {
            return { valid: false, message: '주소를 입력해주세요.' };
        }
        
        // 기본적인 주소 형식 검증
        const addressPattern = /^[가-힣0-9\s\-()]+$/;
        if (!addressPattern.test(address)) {
            return { valid: false, message: '올바른 주소 형식이 아닙니다.' };
        }
        
        return { valid: true, message: '유효한 주소입니다.' };
    }

    // 주소 중복 체크
    async checkAddressDuplicate(address, excludeId = null) {
        try {
            const response = await fetch('/api/admin/check-address-duplicate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    address: address,
                    exclude_id: excludeId
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('주소 중복 체크 실패:', error);
            return { duplicate: false, message: '중복 체크 중 오류가 발생했습니다.' };
        }
    }

    // CSRF 토큰 가져오기
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    // 주소 필드 초기화
    clearAddressFields() {
        const fields = [
            this.options.addressInputId,
            this.options.detailAddressId,
            this.options.zipCodeId,
            this.options.roadAddressId,
            this.options.jibunAddressId,
            this.options.latitudeId,
            this.options.longitudeId
        ];

        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = '';
            }
        });

        this.hideAutoComplete();
        this.hideValidationError();
    }

    // 주소 정보 가져오기
    getAddressData() {
        return {
            zipcode: document.getElementById(this.options.zipCodeId)?.value || '',
            roadAddress: document.getElementById(this.options.roadAddressId)?.value || '',
            jibunAddress: document.getElementById(this.options.jibunAddressId)?.value || '',
            detailAddress: document.getElementById(this.options.detailAddressId)?.value || '',
            fullAddress: document.getElementById(this.options.addressInputId)?.value || '',
            latitude: document.getElementById(this.options.latitudeId)?.value || '',
            longitude: document.getElementById(this.options.longitudeId)?.value || ''
        };
    }

    // 설정 업데이트
    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
    }

    // 인스턴스 제거
    destroy() {
        // 이벤트 리스너 제거
        const searchButton = document.getElementById(this.options.searchButtonId);
        if (searchButton) {
            searchButton.replaceWith(searchButton.cloneNode(true));
        }

        const addressInput = document.getElementById(this.options.addressInputId);
        if (addressInput) {
            addressInput.replaceWith(addressInput.cloneNode(true));
        }

        // 자동완성 컨테이너 제거
        const autocompleteContainer = document.getElementById('address-autocomplete');
        if (autocompleteContainer) {
            autocompleteContainer.remove();
        }

        // 타이머 정리
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
    }

    // 예시: 브랜드 생성 fetch에도 CSRF 토큰 추가
    async createBrand(data) {
        try {
            const response = await fetch('/api/admin/brands', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            return { success: false, error: '브랜드 생성 오류' };
        }
    }
}

// 전역 함수로 등록 (기존 코드와의 호환성을 위해)
window.AddressSearch = AddressSearch;

// 자동 초기화 (페이지 로드 시)
document.addEventListener('DOMContentLoaded', function() {
    // 기본 주소 검색 인스턴스 생성
    if (document.getElementById('address-search-btn')) {
        window.addressSearch = new AddressSearch({
            apiKey: 'YOUR_KAKAO_API_KEY', // 실제 API 키로 교체 필요
            enableAutoComplete: true,
            enableValidation: true,
            enableCoordinates: true,
            onAddressSelected: function(data) {
                console.log('주소 선택됨:', data);
            },
            onError: function(message) {
                console.error('주소 검색 오류:', message);
            }
        });
    }
});

// 주소 검색 버튼 생성 헬퍼 함수
function createAddressSearchButton(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.id = options.buttonId || 'address-search-btn';
    button.className = options.buttonClass || 'btn btn-secondary';
    button.innerHTML = `
        <i class="fas fa-search"></i>
        주소 검색
    `;

    container.appendChild(button);

    // 주소 검색 인스턴스 생성
    new AddressSearch({
        ...options,
        searchButtonId: button.id
    });
}

// 주소 입력 필드 생성 헬퍼 함수
function createAddressInputFields(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const fieldsHtml = `
        <div class="address-fields">
            <div class="form-group">
                <label for="${options.zipCodeId || 'zipcode-input'}">우편번호</label>
                <input type="text" id="${options.zipCodeId || 'zipcode-input'}" class="form-control" readonly>
            </div>
            
            <div class="form-group">
                <label for="${options.roadAddressId || 'road-address-input'}">도로명주소</label>
                <input type="text" id="${options.roadAddressId || 'road-address-input'}" class="form-control" readonly>
            </div>
            
            <div class="form-group">
                <label for="${options.jibunAddressId || 'jibun-address-input'}">지번주소</label>
                <input type="text" id="${options.jibunAddressId || 'jibun-address-input'}" class="form-control" readonly>
            </div>
            
            <div class="form-group">
                <label for="${options.detailAddressId || 'detail-address-input'}">상세주소</label>
                <input type="text" id="${options.detailAddressId || 'detail-address-input'}" class="form-control" placeholder="상세주소를 입력하세요">
            </div>
            
            <div class="form-group">
                <label for="${options.addressInputId || 'address-input'}">전체주소</label>
                <input type="text" id="${options.addressInputId || 'address-input'}" class="form-control" readonly>
            </div>
            
            <input type="hidden" id="${options.latitudeId || 'latitude-input'}">
            <input type="hidden" id="${options.longitudeId || 'longitude-input'}">
        </div>
    `;

    container.innerHTML = fieldsHtml;
} 