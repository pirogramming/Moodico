document.addEventListener('DOMContentLoaded', function() {
    // 좋아요 버튼 이벤트 리스너 추가
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('like-button')) {
            e.preventDefault();
            e.stopPropagation();
            
            const likeButton = e.target;
            const productCard = likeButton.closest('.product-card, .recommended-product-card');
            
            if (productCard) {
                // 제품 정보 가져오기
                const productInfo = {
                    product_id: productCard.dataset.productId || getProductName(productCard),
                    product_name: getProductName(productCard),
                    product_brand: getProductBrand(productCard),
                    product_price: getProductPrice(productCard),
                    product_image: getProductImage(productCard)
                };
                
                // AJAX로 좋아요 토글 요청
                toggleLike(likeButton, productInfo);
            }
        }
    });
    
    // AJAX 좋아요 토글 함수
    async function toggleLike(likeButton, productInfo) {
        try {
            // 버튼 비활성화 (중복 클릭 방지)
            likeButton.disabled = true;
            
            const response = await fetch('/products/toggle_product_like/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(productInfo)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 캐시 무효화
                invalidateLikesCache();
                
                // 좋아요 상태 업데이트
                if (data.is_liked) {
                    likeButton.classList.add('liked');
                    likeButton.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        likeButton.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    likeButton.classList.remove('liked');
                }
                
                // 메시지 표시
                showLikeMessage(data.message);
            } else {
                // 에러 처리
                if (response.status === 401) {
                    showLikeMessage('로그인이 필요합니다.');
                    // 로그인 페이지로 리다이렉트 옵션
                    setTimeout(() => {
                        window.location.href = '/login/';
                    }, 2000);
                } else {
                    showLikeMessage(data.message || '오류가 발생했습니다.');
                }
            }
        } catch (error) {
            console.error('좋아요 토글 오류:', error);
            showLikeMessage('네트워크 오류가 발생했습니다.');
        } finally {
            // 버튼 다시 활성화
            likeButton.disabled = false;
        }
    }
    
    // CSRF 토큰 가져오기
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // 제품 정보 추출 함수들
    function getProductName(card) {
        const nameElement = card.querySelector('.product-name, .name');
        return nameElement ? nameElement.textContent.trim() : 'Unknown Product';
    }
    
    function getProductBrand(card) {
        const brandElement = card.querySelector('.brand-name, .brand');
        return brandElement ? brandElement.textContent.trim() : 'Unknown Brand';
    }
    
    function getProductPrice(card) {
        const priceElement = card.querySelector('.price');
        return priceElement ? priceElement.textContent.trim() : 'Unknown Price';
    }
    
    function getProductImage(card) {
        const imgElement = card.querySelector('img');
        return imgElement ? imgElement.src : '';
    }
    
    // 좋아요 목록 캐시
    let likesCache = null;
    let cacheTimestamp = 0;
    const CACHE_DURATION = 30000; // 30초 캐시
    
    // 서버에서 좋아요 상태 가져오기 (캐싱 적용)
    async function loadUserLikes() {
        const now = Date.now();
        
        // 캐시가 유효한 경우 캐시된 데이터 반환
        if (likesCache && (now - cacheTimestamp) < CACHE_DURATION) {
            return likesCache;
        }
        
        try {
            const response = await fetch('/products/get_user_likes/', {
                method: 'GET',
                credentials: 'include' 
            });

            const data = await response.json();
            
            if (data.success) {
                // 캐시 업데이트
                likesCache = data.likes;
                cacheTimestamp = now;
                return data.likes;
            } else {
                console.error('좋아요 목록 로드 실패:', data.message);
                return [];
            }
        } catch (error) {
            console.error('좋아요 목록 로드 오류:', error);
            return [];
        }
    }
    
    // 캐시 무효화 (좋아요 상태 변경 시)
    function invalidateLikesCache() {
        likesCache = null;
        cacheTimestamp = 0;
    }
    
    // 좋아요 메시지 표시
    function showLikeMessage(message) {
        // 기존 메시지 제거
        const existingMessage = document.querySelector('.like-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // 새 메시지 생성
        const messageElement = document.createElement('div');
        messageElement.className = 'like-message';
        messageElement.textContent = message;
        messageElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: mediumpurple;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        `;
        
        document.body.appendChild(messageElement);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            messageElement.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // 페이지 로드 시 기존 좋아요 상태 복원
    async function restoreLikeStates() {
        try {
            const likes = await loadUserLikes();
            const productCards = document.querySelectorAll('.product-card, .recommended-product-card');
            
            productCards.forEach(card => {
                const productId = card.dataset.productId || getProductName(card);
                const likeButton = card.querySelector('.like-button');
                
                if (likeButton && likes.some(item => item.product_id === productId)) {
                    likeButton.classList.add('liked');
                }
            });
        } catch (error) {
            console.error('좋아요 상태 복원 오류:', error);
        }
    }
    
    // 동적으로 추가되는 제품 카드들의 좋아요 상태 복원
    async function restoreLikeStateForCard(card) {
        try {
            const likes = await loadUserLikes();
            const productId = card.dataset.productId || getProductName(card);
            const likeButton = card.querySelector('.like-button');
            
            if (likeButton && likes.some(item => item.product_id === productId)) {
                likeButton.classList.add('liked');
            }
        } catch (error) {
            console.error('개별 카드 좋아요 상태 복원 오류:', error);
        }
    }
    
    // MutationObserver로 동적 콘텐츠 감지
    function setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 새로 추가된 제품 카드들 찾기
                        const newCards = node.querySelectorAll 
                            ? Array.from(node.querySelectorAll('.product-card, .recommended-product-card')) 
                            : [];
                        
                        // 노드 자체가 제품 카드인 경우도 포함
                        if (node.classList && 
                            (node.classList.contains('product-card') || 
                             node.classList.contains('recommended-product-card'))) {
                            newCards.push(node);
                        }
                        
                        // 각 새 카드에 대해 좋아요 상태 복원
                        newCards.forEach(card => {
                            if (card.querySelector('.like-button')) {
                                restoreLikeStateForCard(card);
                            }
                        });
                    }
                });
            });
        });
        
        // 전체 문서 감시
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        return observer;
    }
    
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
    
    // 초기화
    restoreLikeStates();
    setupMutationObserver();
    
    // 전역 함수로 노출 (다른 스크립트에서 사용 가능)
    window.restoreLikeStateForCard = restoreLikeStateForCard;
});

// 좋아요 목록 조회 함수 (다른 스크립트에서 사용 가능)
async function getLikedProducts() {
    try {
        const response = await fetch('/products/get_user_likes/');
        const data = await response.json();
        return data.success ? data.likes : [];
    } catch (error) {
        console.error('좋아요 목록 조회 오류:', error);
        return [];
    }
}

// 좋아요 목록 초기화 함수 (관리자용)
async function clearLikedProducts() {
    try {
        const response = await fetch('/products/clear_likes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        const data = await response.json();
        return data.success;
    } catch (error) {
        console.error('좋아요 목록 초기화 오류:', error);
        return false;
    }
} 