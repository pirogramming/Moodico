// 별점 기능 JavaScript
class ProductRating {
    constructor() {
        this.currentRating = 0;
        this.isSubmitted = false;
        this.imageFiles = window.reviewImageFiles;
        this.init();
    }

    init() {
        this.loadRatingData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 별점 입력 이벤트
        const starsInput = document.getElementById('stars-input');
        if (starsInput) {
            starsInput.addEventListener('click', (e) => {
                if (e.target.classList.contains('star')) {
                    const rating = parseInt(e.target.dataset.rating);
                    this.setRating(rating);
                }
            });

            // 호버 이벤트
            starsInput.addEventListener('mouseover', (e) => {
                if (e.target.classList.contains('star')) {
                    const rating = parseInt(e.target.dataset.rating);
                    this.showHoverRating(rating);
                }
            });

            starsInput.addEventListener('mouseout', () => {
                this.showCurrentRating();
            });
        }

        // 별점 제출 버튼
        const submitBtn = document.getElementById('submit-rating');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                this.submitRating();
            });
        }
    }

    setRating(rating) {
        this.currentRating = rating;
        this.showCurrentRating();
        this.updateSubmitButton();
    }

    showHoverRating(rating) {
        const stars = document.querySelectorAll('#stars-input .star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.textContent = '★';
                star.classList.add('active');
            } else {
                star.textContent = '☆';
                star.classList.remove('active');
            }
        });
    }

    showCurrentRating() {
        const stars = document.querySelectorAll('#stars-input .star');
        stars.forEach((star, index) => {
            if (index < this.currentRating) {
                star.textContent = '★';
                star.classList.add('filled');
            } else {
                star.textContent = '☆';
                star.classList.remove('filled');
            }
        });
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('submit-rating');
        if (submitBtn) {
            if (this.currentRating > 0) {
                submitBtn.disabled = false;
                submitBtn.textContent = this.isSubmitted ? '별점 수정하기' : '별점 남기기';
            } else {
                submitBtn.disabled = true;
                submitBtn.textContent = '별점을 선택해주세요';
            }
        }
    }

    async loadRatingData() {
        try {
            const response = await fetch(`/products/get_rating/?product_id=${productId}`);
            if (response.ok) {
                const data = await response.json();
                this.updateRatingDisplay(data);
                this.loadRatingsList();
            }
        } catch (error) {
            console.error('별점 데이터 로드 실패:', error);
        }
    }

    updateRatingDisplay(data) {
        // 평균 별점 표시
        const avgRating = document.getElementById('average-rating');
        if (avgRating) {
            avgRating.textContent = data.average_rating;
        }

        // 평균 별점 별표 표시
        this.updateAverageStars(data.average_rating);

        // 평가 개수 표시
        const ratingCount = document.getElementById('rating-count');
        if (ratingCount) {
            ratingCount.textContent = `(${data.total_ratings}개 평가)`;
        }

        // 사용자 별점 표시
        if (data.user_rating) {
            this.currentRating = data.user_rating;
            this.isSubmitted = true;
            this.showCurrentRating();
            this.updateSubmitButton();

            // 코멘트 표시
            const commentArea = document.getElementById('rating-comment');
            if (commentArea && data.user_comment) {
                commentArea.value = data.user_comment;
            }
        }
    }

    updateAverageStars(averageRating) {
        const stars = document.querySelectorAll('#average-stars .star');
        const fullStars = Math.floor(averageRating);
        const hasHalfStar = averageRating % 1 >= 0.5;

        stars.forEach((star, index) => {
            if (index < fullStars) {
                star.textContent = '★';
            } else if (index === fullStars && hasHalfStar) {
                star.textContent = '★';
                star.style.opacity = '0.6';
            } else {
                star.textContent = '☆';
            }
        });
    }

    async submitRating() {
        if (this.currentRating === 0) {
            alert('별점을 선택해주세요.');
            return;
        }

        const comment = document.getElementById('rating-comment').value;
        const submitBtn = document.getElementById('submit-rating');

        // const response = await fetch('/products/submit_rating/', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'X-CSRFToken': this.getCSRFToken()
        //     },
        //     body: JSON.stringify({
        //         product_id: productId,
        //         product_name: productName,
        //         product_brand: productBrand,
        //         rating: this.currentRating,
        //         comment: comment
        //     })
        // });

        // 기존의 json 전달 방식에서 formData 전송방식으로 변경
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('product_name', productName);
        formData.append('product_brand', productBrand);
        formData.append('rating', this.currentRating);
        formData.append('comment', comment);

        if (this.imageFiles && this.imageFiles.size > 0) {
            for (const file of this.imageFiles.values()) {
                formData.append('images', file);
            }
        }

        try {
            submitBtn.disabled = true;
            submitBtn.textContent = '저장 중...';

            const response = await fetch('/products/submit_rating/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken() // CSRF 토큰 추가
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.isSubmitted = true;
                this.updateSubmitButton();
                alert(data.message);
                
                // 데이터 새로고침
                this.loadRatingData();
                document.getElementById('image-upload-container').innerHTML = '';
                this.imageFiles.clear();
            } else {
                const errorData = await response.json();
                alert(errorData.error || '별점 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('별점 제출 실패:', error);
            alert('별점 저장 중 오류가 발생했습니다.');
        } finally {
            submitBtn.disabled = false;
            this.updateSubmitButton();
        }
    }

    async loadRatingsList() {
        try {
            const response = await fetch(`/products/get_ratings_list/?product_id=${productId}`);
            if (response.ok) {
                const data = await response.json();
                this.displayRatingsList(data.ratings);
            }
        } catch (error) {
            console.error('별점 목록 로드 실패:', error);
        }
    }

    displayRatingsList(ratings) {
        const ratingsList = document.getElementById('ratings-list');
        if (!ratingsList) return;

        if (ratings.length === 0) {
            ratingsList.innerHTML = '<div class="no-ratings">아직 리뷰가 없습니다.</div>';
            return;
        }

        const ratingsHTML = ratings.map(rating => {
            let imagesHTML = '';
            if (rating.images && rating.images.length > 0){
                const imagesToShow = rating.images.slice(0, 4);
                imagesHTML=`
                    <div class="rating-item-images">
                        ${imagesToShow.map(imgUrl => `
                            <img src="${imgUrl}" alt="리뷰 이미지" class="rating-image">
                        `).join('')}
                    </div>
                `;
            }
        
            return `
                <div class="rating-item">
                    <div class="rating-item-header">
                        <div class="rating-item-stars">
                            ${'★'.repeat(rating.rating)}${'☆'.repeat(5 - rating.rating)}
                        </div>
                        <span class="rating-item-date">${rating.created_at}</span>
                    </div>
                    <div class="rating-item-user">${rating.user_name}</div>
                    <div class="rating-item-body">
                        ${rating.comment ? `<div class="rating-item-comment">${rating.comment}</div>` : '<div></div>' /* 댓글이 없을 때도 그리드 구조 유지를 위해 빈 div 추가 */}
                        ${imagesHTML}
                    </div>
            </div>
        `}).join('');

        ratingsList.innerHTML = ratingsHTML;
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// 페이지 로드 시 별점 기능 초기화
document.addEventListener('DOMContentLoaded', () => {
    if (typeof productId !== 'undefined') {
        new ProductRating();
    }
});
