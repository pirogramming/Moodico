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

document.addEventListener('DOMContentLoaded', function () {
    // 좋아요 버튼 이벤트 리스너 추가
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('like-button')) {
            e.preventDefault();
            e.stopPropagation();

            const likeButton = e.target;
            const productCard = likeButton.closest('.product-card, .recommended-product-card');

            if (productCard) {
                // 제품 정보 가져오기
                // const productInfo = {
                //     product_id: productCard.dataset.productId || generateUniqueProductId(productCard),
                //     product_name: getProductName(productCard),
                //     product_brand: getProductBrand(productCard),
                //     product_price: getProductPrice(productCard),
                //     product_image: getProductImage(productCard)
                // };
                const productId = productCard.dataset.productId;

                if (!productId) {
                    console.error('Error: product-card missing data-product-id attribute.');
                    return;  
                }

                const productInfo = {
                    product_id: productId,
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
                // console.log(`❤️ Like toggled for ${productInfo.product_id}: ${data.is_liked ? 'LIKED' : 'UNLIKED'}`); // 디버깅용

                // 캐시 무효화
                invalidateLikesCache();

                // 좋아요 상태 업데이트 - 같은 product_id를 가진 모든 버튼 업데이트
                const allSameProductButtons = document.querySelectorAll(`[data-product-id="${productInfo.product_id}"] .like-button`);
                allSameProductButtons.forEach(btn => {
                    if (data.is_liked) {
                        btn.classList.add('liked');
                    } else {
                        btn.classList.remove('liked');
                    }
                });

                // 현재 버튼에 애니메이션 효과
                if (data.is_liked) {
                    likeButton.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        likeButton.style.transform = 'scale(1)';
                    }, 200);
                }

                // 찜 개수 업데이트
                updateLikeCount(productInfo.product_id);

                // 메시지 표시
                showLikeMessage(data.message);
            } else {
                // 에러 처리
                if (response.status === 401) {
                    showLikeMessage('로그인이 필요합니다.');
                    // 로그인 페이지로 리다이렉트 옵션
                    setTimeout(() => {
                        window.location.href = '/';
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

    // 더 고유한 제품 ID 생성 함수
    function generateUniqueProductId(card) {
        const brand = getProductBrand(card).replace(/\s+/g, '-').toLowerCase();
        const name = getProductName(card).replace(/\s+/g, '-').toLowerCase();
        const price = getProductPrice(card).replace(/[^\d]/g, '');

        // 카드의 DOM 위치나 이미지 URL도 고유성에 추가
        const imgSrc = getProductImage(card);
        const imgHash = imgSrc ? imgSrc.split('/').pop().split('.')[0] : '';

        // 브랜드 + 제품명 + 가격 + 이미지해시로 고유 ID 생성
        const uniqueId = `${brand}-${name}-${price}-${imgHash}`.substring(0, 60);

        // console.log(`🔧 Generated unique ID: ${uniqueId} (for: ${name})`); // 디버깅용
        return uniqueId;
    }

    function getProductBrand(card) {
        const brandElement = card.querySelector('.brand-name, .brand, .product-brand');
        let brand = brandElement ? brandElement.textContent.trim() : '';

        // 브랜드 텍스트에서 태그 부분 제거 (예: "ROMAND glossy" -> "ROMAND")
        if (brand && brand.includes(' ')) {
            const parts = brand.split(' ');
            // 첫 번째 부분이 브랜드명인 경우가 많음
            brand = parts[0];
        }

        return brand || 'Unknown Brand';
    }

    function getProductPrice(card) {
        const priceElement = card.querySelector('.price, .product-price');
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

    // 찜 개수 업데이트 함수
    async function updateLikeCount(productId) {
        try {
            const response = await fetch(`/products/like_count/?product_id=${encodeURIComponent(productId)}`);
            const data = await response.json();

            if (data.success) {
                // 해당 제품의 모든 좋아요 카운터 업데이트
                const likeCountElements = document.querySelectorAll(`[data-product-id="${productId}"] .like-count`);
                likeCountElements.forEach(element => {
                    element.textContent = data.like_count;

                    // 개수가 0이면 숨김, 1 이상이면 표시
                    if (data.like_count > 0) {
                        element.style.display = 'inline-block';
                    } else {
                        element.style.display = 'none';
                    }
                });
            }
        } catch (error) {
            console.error('찜 개수 업데이트 오류:', error);
        }
    }

    // 여러 제품의 찜 정보를 한 번에 로드
    async function loadMultipleProductsLikeInfo() {
        try {
            const productCards = document.querySelectorAll('.product-card, .recommended-product-card');
            // const productIds = Array.from(productCards).map(card =>
            //     card.dataset.productId || generateUniqueProductId(card)
            // ).filter(Boolean);
            const productIds = Array.from(productCards).map(card => {
                const id = card.dataset.productId;
                if (!id) {
                    console.warn('Product card without valid product ID found, skipping:', card);
                    return null;
                }
                return id;
            }).filter(Boolean);

            if (productIds.length === 0) return;

            const params = new URLSearchParams();
            productIds.forEach(id => params.append('product_ids[]', id));

            const response = await fetch(`/products/multiple_like_info/?${params}`);
            const data = await response.json();

            if (data.success) {
                // 각 제품 카드에 찜 정보 적용
                Object.entries(data.products).forEach(([productId, info]) => {
                    // console.log(`Restoring like state for ${productId}: liked=${info.is_liked}, count=${info.like_count}`); // 디버깅용

                    const cards = document.querySelectorAll(`[data-product-id="${productId}"]`);
                    // console.log(`Found ${cards.length} cards with ID ${productId}`); // 디버깅용

                    cards.forEach(card => {
                        const likeButton = card.querySelector('.like-button');
                        const likeCountElement = card.querySelector('.like-count');

                        if (likeButton) {
                            if (info.is_liked) {
                                likeButton.classList.add('liked');
                            } else {
                                likeButton.classList.remove('liked');
                            }
                        }

                        if (likeCountElement) {
                            likeCountElement.textContent = info.like_count;
                            if (info.like_count > 0) {
                                likeCountElement.style.display = 'inline-block';
                            } else {
                                likeCountElement.style.display = 'none';
                            }
                        }
                    });
                });
            }
        } catch (error) {
            console.error('여러 제품 찜 정보 로드 오류:', error);
        }
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

    // 페이지 로드 시 기존 좋아요 상태 복원 (개선된 버전)
    async function restoreLikeStates() {
        try {
            // 여러 제품의 찜 정보를 한 번에 로드 (성능 개선)
            await loadMultipleProductsLikeInfo();
        } catch (error) {
            console.error('좋아요 상태 복원 오류:', error);
            // 실패 시 기존 방식으로 폴백
            try {
                const likes = await loadUserLikes();
                const productCards = document.querySelectorAll('.product-card, .recommended-product-card');

                productCards.forEach(card => {
                    // const productId = card.dataset.productId || generateUniqueProductId(card);
                    const productId = card.dataset.productId;
                    if (!productId) {
                        console.error('Missing product ID on card:', card);
                        return; // skip this card
                    }
                    const likeButton = card.querySelector('.like-button');

                    if (likeButton && likes.some(item => item.product_id === productId)) {
                        likeButton.classList.add('liked');
                    }
                });
            } catch (fallbackError) {
                console.error('폴백 좋아요 상태 복원도 실패:', fallbackError);
            }
        }
    }

    // 동적으로 추가되는 제품 카드들의 좋아요 상태 복원
    async function restoreLikeStateForCard(card) {
        try {
            // const productId = card.dataset.productId || generateUniqueProductId(card);
            const productId = card.dataset.productId;
            if (!productId) return;

            const response = await fetch(`/products/like_count/?product_id=${encodeURIComponent(productId)}`);
            const data = await response.json();

            if (data.success) {
                const likeButton = card.querySelector('.like-button');
                const likeCountElement = card.querySelector('.like-count');

                if (likeButton) {
                    if (data.is_liked) {
                        likeButton.classList.add('liked');
                    } else {
                        likeButton.classList.remove('liked');
                    }
                }

                if (likeCountElement) {
                    likeCountElement.textContent = data.like_count;
                    if (data.like_count > 0) {
                        likeCountElement.style.display = 'inline-block';
                    } else {
                        likeCountElement.style.display = 'none';
                    }
                }
            }
        } catch (error) {
            console.error('개별 카드 좋아요 상태 복원 오류:', error);
            // 실패 시 기존 방식으로 폴백
            try {
                const likes = await loadUserLikes();
                // const productId = card.dataset.productId || generateUniqueProductId(card);
                const productId = card.dataset.productId;
                if (!productId) {
                    console.error('Missing product ID on card:', card);
                    return; // skip this card
                }
                const likeButton = card.querySelector('.like-button');

                if (likeButton && likes.some(item => item.product_id === productId)) {
                    likeButton.classList.add('liked');
                }
            } catch (fallbackError) {
                console.error('폴백 개별 카드 복원도 실패:', fallbackError);
            }
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
    window.restoreLikeStates = restoreLikeStates;
    window.setupMutationObserver = setupMutationObserver;
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

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function () {
    // console.log('좋아요 시스템 초기화 중...');

    // 현재 페이지의 모든 제품 카드 정보 출력 (디버깅용)
    const allCards = document.querySelectorAll('.product-card, .recommended-product-card');
    // console.log(`페이지에서 발견된 제품 카드 수: ${allCards.length}`);

    allCards.forEach((card, index) => {
        // const productId = card.dataset.productId || generateUniqueProductId(card);
        const productId = card.dataset.productId;
        if (!productId) {
            console.error('Missing product ID on card:', card);
            return; // skip this card
        }
        const productName = getProductName(card);
        // console.log(`Card ${index + 1}: ID=${productId}, Name=${productName}`);
    });

    restoreLikeStates();
    // setupMutationObserver는 이미 위에서 호출되었으므로 여기서는 호출하지 않음
}); 