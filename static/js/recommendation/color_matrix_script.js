document.addEventListener('DOMContentLoaded', async () => {
    const matrixContainer = document.querySelector('.color-matrix-container');
    const productsContainer = document.getElementById('makeup-products-container');
    const moodSelectionArea = document.getElementById('mood-selection-area');
    const selectedProductsDisplay = document.getElementById('selected-products-display');
    const selectedProductsList = document.getElementById('selected-products-list');
    const noProductsMessage = document.getElementById('no-products-message');
    const moodDropdown = document.getElementById('mood-dropdown');
    const categoryDropdown = document.getElementById('category-dropdown');
    const matrixCube = document.querySelector('.matrix-cube');
    const productsContainerAll = document.getElementById('makeup-products-container-all');
    const productsContainerLips = document.getElementById('makeup-products-container-lips');
    const productsContainerEyeshadow = document.getElementById('makeup-products-container-eyeshadow');
    const productsContainerBlush = document.getElementById('makeup-products-container-blush');
    const productsDataElement = document.getElementById('products-data');
    const makeupProducts = JSON.parse(productsDataElement.textContent);
    /*
    // 무드별 구역 정의 -> mood_zones.json로 이동
    const moodZones = {
        '러블리': {
            name: '러블리',
            area: { left: 60, top: 10, width: 30, height: 40 }, // 웜 라이트 영역
            color: '#FFE5E5',
            description: '상큼하고 기분 좋은 무드'
        },
        '활기찬': {
            name: '활기찬', 
            area: { left: 70, top: 30, width: 25, height: 30 }, // 웜 브라이트 영역
            color: '#FFF2E5',
            description: '밝고 친근한 무드'
        },
        '고급스러운': {
            name: '고급스러운',
            area: { left: 65, top: 60, width: 30, height: 35 }, // 웜 딥 영역
            color: '#E5D4C8',
            description: '포인트 있는 강렬한 무드'
        },
        '내추럴': {
            name: '내추럴',
            area: { left: 20, top: 10, width: 35, height: 40 }, // 쿨 라이트 영역
            color: '#E5F0FF',
            description: '자연스러운 무드'
        },
        '시크': {
            name: '시크',
            area: { left: 15, top: 60, width: 35, height: 35 }, // 쿨 딥 영역
            color: '#E5E5F0',
            description: '스타일리시한 무드'
        }
    };
    */

    let moodZones;
    try{
        const response = await fetch('/static/data/mood_zones.json');
        if (!response.ok){
            throw new Error(`error: ${response.status}`)
        }
        moodZones = await response.json();
    } catch (error){
        console.error("moodZones.json 파일을 불러오는 데 실패했습니다:", error);
        return;
    }


    /*
    // 우선은 기존의 임시 데이터 형식 남겨두겠습니다 -
    const makeupProducts = [ //쥬시래스팅 제품 데이터 임시로 찾아서 넣음
        { id: 'jr01', name: '쥬시래스팅 틴트 #01 쥬시오', color: '#FF8000', warmCool: 90, lightDeep: 45, mood: '맑은 오렌지 (봄웜 브라이트)' },
    { id: 'jr02', name: '쥬시래스팅 틴트 #02 루비 레드', color: '#E0115F', warmCool: 60, lightDeep: 50, mood: '맑은 레드 (봄웜/겨울쿨)' },
    { id: 'jr03', name: '쥬시래스팅 틴트 #03 섬머센트', color: '#FFC0CB', warmCool: 40, lightDeep: 20, mood: '여리여리 핑크 (여름쿨 라이트)' },
    { id: 'jr04', name: '쥬시래스팅 틴트 #04 드래곤 핑크', color: '#FF69B4', warmCool: 30, lightDeep: 35, mood: '쨍한 핑크 (여름쿨 브라이트)' },
    { id: 'jr05', name: '쥬시래스팅 틴트 #05 피치 미', color: '#FFDAB9', warmCool: 85, lightDeep: 15, mood: '청순 피치 (봄웜 라이트)' },
    { id: 'jr06', name: '쥬시래스팅 틴트 #06 피그피그', color: '#9D5870', warmCool: 35, lightDeep: 60, mood: '모브 핑크 베이지 (여름/가을 뮤트)' },
    { id: 'jr07', name: '쥬시래스팅 틴트 #07 쥬쥬브', color: '#884B42', warmCool: 65, lightDeep: 55, mood: '말린 대추 브라운 (가을웜 뮤트)' },
    { id: 'jr08', name: '쥬시래스팅 틴트 #08 핑크 펌킨', color: '#E6998D', warmCool: 70, lightDeep: 30, mood: 'MLBB 핑크 오렌지 (봄웜/가을웜 라이트)' },
    { id: 'jr09', name: '쥬시래스팅 틴트 #09 리치 코랄', color: '#FF7F50', warmCool: 80, lightDeep: 40, mood: '생생한 코랄 오렌지 (봄웜 브라이트)' },
    { id: 'jr10', name: '쥬시래스팅 틴트 #10 똔또마토', color: '#E55B5B', warmCool: 75, lightDeep: 50, mood: '맑은 레드 (봄웜/가을웜)' },
    { id: 'jr11', name: '쥬시래스팅 틴트 #11 핑크 펌킨', color: '#ED8072', warmCool: 70, lightDeep: 35, mood: '따뜻한 핑크 (봄웜 라이트)' },
    { id: 'jr12', name: '쥬시래스팅 틴트 #12 체리 밤', color: '#B23A48', warmCool: 55, lightDeep: 65, mood: '딥한 체리 레드 (겨울쿨/가을딥)' },
    { id: 'jr13', name: '쥬시래스팅 틴트 #13 잇 도토리', color: '#7A5A40', warmCool: 85, lightDeep: 70, mood: '브릭 브라운 (가을웜 딥)' },
    { id: 'jr14', name: '쥬시래스팅 틴트 #14 베리샷', color: '#8B0000', warmCool: 50, lightDeep: 70, mood: '딥 베리 레드 (가을딥/겨울쿨)' },
    { id: 'jr15', name: '쥬시래스팅 틴트 #15 펀치 오렌지', color: '#FF4500', warmCool: 95, lightDeep: 50, mood: '강렬한 오렌지 (봄웜 브라이트/가을웜 스트롱)' },
    { id: 'jr16', name: '쥬시래스팅 틴트 #16 코니 소다', color: '#5F9EA0', warmCool: 10, lightDeep: 30, mood: '쿨한 블루 핑크 (여름쿨)' },
    { id: 'jr17', name: '쥬시래스팅 틴트 #17 플럼 콕', color: '#8B008B', warmCool: 20, lightDeep: 75, mood: '자줏빛 플럼 (겨울쿨 딥)' },
    { id: 'jr18', name: '쥬시래스팅 틴트 #18 멀드 피치', color: '#FFA07A', warmCool: 90, lightDeep: 20, mood: '복숭아 코랄 (봄웜 라이트/브라이트)' },
    { id: 'jr19', name: '쥬시래스팅 틴트 #19 아몬드 로즈', color: '#CD853F', warmCool: 80, lightDeep: 50, mood: '말린 장미 브라운 (가을웜 뮤트)' },
    { id: 'jr20', name: '쥬시래스팅 틴트 #20 다크 코코넛', color: '#5A3D34', warmCool: 95, lightDeep: 85, mood: '고동빛 브라운 (가을웜 딥)' },
    { id: 'jr21', name: '쥬시래스팅 틴트 #21 딥 상그리아', color: '#660033', warmCool: 40, lightDeep: 90, mood: '매혹적인 와인 (겨울쿨 딥)' },
    { id: 'jr22', name: '쥬시래스팅 틴트 #22 포멜로 스킨', color: '#F5C6AA', warmCool: 80, lightDeep: 10, mood: '여리한 누디 베이지 (봄웜 라이트)' },
    { id: 'jr23', name: '쥬시래스팅 틴트 #23 누카다미아', color: '#D2B48C', warmCool: 75, lightDeep: 25, mood: '차분한 누디 로즈 (가을웜 뮤트)' },
    { id: 'jr24', name: '쥬시래스팅 틴트 #24 필링 앵두', color: '#D22323', warmCool: 60, lightDeep: 45, mood: '맑은 앵두 레드 (여름쿨 라이트/봄웜 브라이트)' },
    { id: 'jr25', name: '쥬시래스팅 틴트 #25 베어 그레이프', color: '#A020F0', warmCool: 10, lightDeep: 55, mood: '쿨톤 포도 (여름쿨/겨울쿨)' },
    { id: 'jr26', name: '쥬시래스팅 틴트 #26 베리 베리 핑크', color: '#FF69B4', warmCool: 25, lightDeep: 20, mood: '딸기 우유 핑크 (여름쿨 라이트)' },
    { id: 'jr27', name: '쥬시래스팅 틴트 #27 핑크 팝시클', color: '#FF82A5', warmCool: 30, lightDeep: 15, mood: '밝은 팝 핑크 (봄웜 라이트/여름쿨 라이트)' },
    { id: 'jr28', name: '쥬시래스팅 틴트 #28 베어 피그', color: '#A06A77', warmCool: 45, lightDeep: 40, mood: '뮤트 베이지 핑크 (여름 뮤트)' },
    { id: 'jr29', name: '쥬시래스팅 틴트 #29 파파야 잼', color: '#FFAF7A', warmCool: 90, lightDeep: 30, mood: '생기있는 파파야 오렌지 (봄웜 브라이트)' },
    { id: 'jr30', name: '쥬시래스팅 틴트 #30 카네이션 로즈', color: '#E06666', warmCool: 60, lightDeep: 40, mood: '부드러운 장미 (봄웜/가을웜 뮤트)' },
    { id: 'jr31', name: '쥬시래스팅 틴트 #31 베어 애프리콧', color: '#FFC8B4', warmCool: 88, lightDeep: 12, mood: '누디 살구 (봄웜 라이트)' },
    { id: 'jr32', name: '쥬시래스팅 틴트 #32 베어 베리', color: '#C8A2C8', warmCool: 25, lightDeep: 30, mood: '차분한 베리 핑크 (여름쿨 뮤트)' },
    { id: 'jr33', name: '쥬시래스팅 틴트 #33 베어 포도', color: '#7B68EE', warmCool: 15, lightDeep: 45, mood: '포도빛 모브 (여름쿨/겨울쿨)' },
    { id: 'jr34', name: '쥬시래스팅 틴트 #34 베어 시나몬', color: '#CD853F', warmCool: 85, lightDeep: 60, mood: '따뜻한 시나몬 브라운 (가을웜)' },
    { id: 'jr35', name: '쥬시래스팅 틴트 #35 베어 피치', color: '#FFB680', warmCool: 80, lightDeep: 25, mood: '부드러운 피치 (봄웜 라이트)' },
    { id: 'jr36', name: '쥬시래스팅 틴트 #36 피칸 버치', color: '#8B4513', warmCool: 90, lightDeep: 75, mood: '짙은 피칸 브라운 (가을웜 딥)' },
    { id: 'jr37', name: '쥬시래스팅 틴트 #37 메타코랄', color: '#FF7F50', warmCool: 92, lightDeep: 40, mood: '화사한 오렌지 코랄 (봄웜 브라이트)' },
    { id: 'jr38', name: '쥬시래스팅 틴트 #38 베어 애플', color: '#FF6347', warmCool: 70, lightDeep: 38, mood: '맑은 사과 레드 (봄웜/가을웜)' },
    { id: 'jr39', name: '쥬시래스팅 틴트 #39 오드 그레이프', color: '#800080', warmCool: 20, lightDeep: 65, mood: '독특한 포도 퍼플 (겨울쿨)' },
    { id: 'jr40', name: '쥬시래스팅 틴트 #40 루비 슬립', color: '#DC143C', warmCool: 65, lightDeep: 55, mood: '클래식 루비 레드 (모든 톤)' },
    { id: 'jr41', name: '쥬시래스팅 틴트 #41 멜로우 듀', color: '#F0E68C', warmCool: 70, lightDeep: 5, mood: '투명한 베이지 (뉴트럴/봄웜 라이트)' },
    { id: 'jr42', name: '쥬시래스팅 틴트 #42 펀치 키스', color: '#FF7F50', warmCool: 80, lightDeep: 40, mood: '생기 코랄 오렌지 (봄웜)' },
    ];
    */

    /*
    // 무드 구역 렌더링
    const renderMoodZones = () => {
        // 기존 무드 구역 제거
        const existingZones = productsContainer.querySelectorAll('.mood-zone');
        existingZones.forEach(zone => zone.remove());
        
        Object.values(moodZones).forEach(zone => {
            const zoneElement = document.createElement('div');
            zoneElement.classList.add('mood-zone');
            zoneElement.dataset.mood = zone.name;
            zoneElement.style.left = `${zone.area.left}%`;
            zoneElement.style.top = `${zone.area.top}%`;
            zoneElement.style.width = `${zone.area.width}%`;
            zoneElement.style.height = `${zone.area.height}%`;
            zoneElement.style.backgroundColor = zone.color;
            zoneElement.style.opacity = '0.3';
            zoneElement.style.border = '2px dashed #666';
            zoneElement.style.position = 'absolute';
            zoneElement.style.borderRadius = '10px';
            zoneElement.style.display = 'none'; // 초기에는 숨김
            zoneElement.title = `${zone.name}: ${zone.description}`;
            
            // 구역 라벨 추가
            const label = document.createElement('div');
            label.textContent = zone.name;
            label.style.position = 'absolute';
            label.style.top = '5px';
            label.style.left = '5px';
            label.style.fontSize = '12px';
            label.style.fontWeight = 'bold';
            label.style.color = '#333';
            label.style.backgroundColor = 'rgba(255,255,255,0.8)';
            label.style.padding = '2px 6px';
            label.style.borderRadius = '4px';
            
            zoneElement.appendChild(label);
            productsContainer.appendChild(zoneElement);
        });
    };

    // 선택된 무드 구역만 표시
    const showSelectedMoodZone = (selectedMood) => {
        const allZones = productsContainer.querySelectorAll('.mood-zone');
        
        allZones.forEach(zone => {
            if (selectedMood === '') {
                // 모든 무드 보기 선택 시 모든 구역 숨김
                zone.style.display = 'none';
            } else if (zone.dataset.mood === selectedMood) {
                // 선택된 무드 구역만 표시
                zone.style.display = 'block';
                zone.style.opacity = '0.7';
                zone.style.borderColor = '#ff6b6b';
                zone.style.borderWidth = '3px';
            } else {
                // 다른 구역들은 숨김
                zone.style.display = 'none';
            }
        });
    };
    */
    const renderProducts = (category = '') => {
        productsContainerAll.innerHTML = '';
        productsContainerLips.innerHTML = '';
        productsContainerEyeshadow.innerHTML = '';
        productsContainerBlush.innerHTML = '';

        let productsToRender = makeupProducts;

        // 좋아요 필터링
        if (isLikeFilterActive) {
            productsToRender = productsToRender.filter(p => p.is_liked === true);
        }
        
        // 필터링할 제품 목록
        if (category) {
            productsToRender = productsToRender.filter(p => p.category === category);
        }
        const targetContainer = category === 'Lips' ? productsContainerLips
                              : category === 'eyeshadow' ? productsContainerEyeshadow
                              : category === 'blush' ? productsContainerBlush
                              : productsContainerAll;

        
        productsToRender.forEach(product => {
            const coords = calculateCoordinatesFromLAB(product.lab_l, product.lab_a, product.lab_b);
            if (!coords) return false;

            const productCircle = document.createElement('a');
            productCircle.classList.add('product-circle');
            productCircle.style.backgroundColor = product.hex;
            productCircle.style.left = `${coords.warmCool}%`;
            productCircle.style.top = `${coords.lightDeep}%`;
            productCircle.dataset.productId = product.id;

            productCircle.dataset.liked = product.is_liked ? 'true' : 'false';
            productCircle.title = `${product.name} (${product.mood})`;

            productCircle.href = product.url;
            productCircle.target = "_blank";

            productCircle.style.transform = 'translate(-50%, -50%)';

            targetContainer.appendChild(productCircle);
        });
    };

    // 무드별 제품 필터링 함수
    const getProductsByMood = (mood) => {
        if (!moodZones[mood]) return [];
        
        const zone = moodZones[mood];
        const zoneLeft = zone.area.left;
        const zoneTop = zone.area.top;
        const zoneRight = zoneLeft + zone.area.width;
        const zoneBottom = zoneTop + zone.area.height;
        
        return makeupProducts.filter(product => {
            const coords = calculateCoordinatesFromLAB(product.lab_l, product.lab_a, product.lab_b);
            if (!coords) return false;

            return coords.warmCool >= zoneLeft && coords.warmCool <= zoneRight &&
                   coords.lightDeep >= zoneTop && coords.lightDeep <= zoneBottom;
        });
    };

    const updateSelectedProducts = () => {
        selectedProductsList.innerHTML = ''; 
        const selectedCategory = categoryDropdown.value;
        const currentProductsContainer = selectedCategory === 'Lips' ? productsContainerLips
                                   : selectedCategory === 'eyeshadow' ? productsContainerEyeshadow
                                   : selectedCategory === 'blush' ? productsContainerBlush
                                   : productsContainerAll;
        const filteredProducts = [];
        const containerRect = matrixContainer.getBoundingClientRect();
        const moodAreaRect = moodSelectionArea.getBoundingClientRect();
        const relativeLeft = moodAreaRect.left - containerRect.left;
        const relativeTop = moodAreaRect.top - containerRect.top;
        const relativeRight = relativeLeft + moodAreaRect.width;
        const relativeBottom = relativeTop + moodAreaRect.height;

        const productCircles = currentProductsContainer.querySelectorAll('.product-circle');
        productCircles.forEach(circle => {
            const productCircleRect = circle.getBoundingClientRect();
            const productCenterX = (productCircleRect.left + productCircleRect.right) / 2 - containerRect.left;
            const productCenterY = (productCircleRect.top + productCircleRect.bottom) / 2 - containerRect.top;

            if (productCenterX >= relativeLeft && productCenterX <= relativeRight &&
                productCenterY >= relativeTop && productCenterY <= relativeBottom) {
                
                const productId = circle.dataset.productId;
                const product = makeupProducts.find(p => p.id === productId);
                if (product) {
                    filteredProducts.push(product);
                }
            }
        });

        if (filteredProducts.length > 0) {
            noProductsMessage.classList.add('hidden');
            filteredProducts.forEach(product => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <div class="product-color-swatch" style="background-color: ${product.hex};"></div>
                    <span>${product.name}</span>
                    <span class="product-category">${product.category}</span>
                `;

                listItem.addEventListener('click', () => {
                    window.open(product.url, '_blank');
                });

                selectedProductsList.appendChild(listItem);

                const circle = currentProductsContainer.querySelector(`[data-product-id="${product.id}"]`);
                if (circle) circle.classList.add('selected');
            });
        } else {
            noProductsMessage.classList.remove('hidden');
        }

        currentProductsContainer.querySelectorAll('.product-circle').forEach(circle => {
            const productId = circle.dataset.productId;
            if (!filteredProducts.some(p => p.id === productId)) {
                circle.classList.remove('selected');
            }
        });
    };

    // 좋아요 토글 필터링
    function filterLikedProducts() {
        const selectedCategory = categoryDropdown.value;

        renderProducts(selectedCategory);
        updateSelectedProducts(); // 오른쪽 선택 목록도 업데이트
    }

    const likeToggleCheckbox = document.getElementById('like-toggle-checkbox');
    let isLikeFilterActive = false;
    if (likeToggleCheckbox) {
        likeToggleCheckbox.addEventListener('change', () => {
            isLikeFilterActive = likeToggleCheckbox.checked;
            filterLikedProducts();
        });
    }

    let isDragging = false;
    let isResizing = false;
    let startX, startY, startWidth, startHeight, startLeft, startTop;
    let activeResizer = null;

    moodSelectionArea.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('resizer')) {
            isResizing = true;
            activeResizer = e.target;
            startX = e.clientX;
            startY = e.clientY;
            startWidth = moodSelectionArea.offsetWidth;
            startHeight = moodSelectionArea.offsetHeight;
            startLeft = moodSelectionArea.offsetLeft;
            startTop = moodSelectionArea.offsetTop;
            e.preventDefault(); 
        } else {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = moodSelectionArea.offsetLeft;
            startTop = moodSelectionArea.offsetTop;
            moodSelectionArea.style.cursor = 'grabbing';
            e.preventDefault();
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            let newLeft = startLeft + dx;
            let newTop = startTop + dy;

            const maxX = matrixContainer.offsetWidth - moodSelectionArea.offsetWidth;
            const maxY = matrixContainer.offsetHeight - moodSelectionArea.offsetHeight;

            newLeft = Math.max(0, Math.min(newLeft, maxX));
            newTop = Math.max(0, Math.min(newTop, maxY));

            moodSelectionArea.style.left = `${newLeft}px`;
            moodSelectionArea.style.top = `${newTop}px`;
            updateSelectedProducts();
        } else if (isResizing) {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            let newWidth = startWidth;
            let newHeight = startHeight;
            let newLeft = startLeft;
            let newTop = startTop;

            const minSize = 50; 

            if (activeResizer.classList.contains('bottom-right-resizer')) {
                newWidth = Math.max(minSize, startWidth + dx);
                newHeight = Math.max(minSize, startHeight + dy);
            } else if (activeResizer.classList.contains('bottom-left-resizer')) {
                newWidth = Math.max(minSize, startWidth - dx);
                newHeight = Math.max(minSize, startHeight + dy);
                newLeft = startLeft + dx;
            } else if (activeResizer.classList.contains('top-right-resizer')) {
                newWidth = Math.max(minSize, startWidth + dx);
                newHeight = Math.max(minSize, startHeight - dy);
                newTop = startTop + dy;
            } else if (activeResizer.classList.contains('top-left-resizer')) {
                newWidth = Math.max(minSize, startWidth - dx);
                newHeight = Math.max(minSize, startHeight - dy);
                newLeft = startLeft + dx;
                newTop = startTop + dy;
            }

            const maxRight = matrixContainer.offsetWidth;
            const maxBottom = matrixContainer.offsetHeight;

            if (newLeft < 0) {
                newWidth += newLeft;
                newLeft = 0;
            }
            if (newTop < 0) {
                newHeight += newTop;
                newTop = 0;
            }
            if (newLeft + newWidth > maxRight) {
                newWidth = maxRight - newLeft;
            }
            if (newTop + newHeight > maxBottom) {
                newHeight = maxBottom - newTop;
            }

            moodSelectionArea.style.width = `${newWidth}px`;
            moodSelectionArea.style.height = `${newHeight}px`;
            moodSelectionArea.style.left = `${newLeft}px`;
            moodSelectionArea.style.top = `${newTop}px`;

            updateSelectedProducts();
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        isResizing = false;
        activeResizer = null;
        moodSelectionArea.style.cursor = 'grab';
    });

    renderProducts();
    moodSelectionArea.style.width = '200px';
    moodSelectionArea.style.height = '180px';
    moodSelectionArea.style.left = '380px'; 
    moodSelectionArea.style.top = '20px'; 
    updateSelectedProducts(); 


    let updateTimeout;
    const debouncedUpdateProducts = () => {
        clearTimeout(updateTimeout);
        updateTimeout = setTimeout(updateSelectedProducts, 100); 
    };

    moodSelectionArea.addEventListener('mousemove', () => {
        if (isDragging || isResizing) {
            debouncedUpdateProducts();
        }
    });

    window.addEventListener('resize', () => {
        updateSelectedProducts();
    });

    // 드롭다운 이벤트 리스너 추가
    moodDropdown.addEventListener('change', (e) => {
        const selectedMood = e.target.value;

        //선택한 무드에 따라 mood-selection-area의 크기와 위치를 변경
        if (selectedMood && moodZones[selectedMood]) {
            const zone = moodZones[selectedMood].area;
            moodSelectionArea.style.left = `${zone.left}%`;
            moodSelectionArea.style.top = `${zone.top}%`;
            moodSelectionArea.style.width = `${zone.width}%`;
            moodSelectionArea.style.height = `${zone.height}%`;
            moodSelectionArea.style.display = 'block';
            updateSelectedProducts();
        }
    });

    categoryDropdown.addEventListener('change', (e) => {
        const selectedCategory = e.target.value;
        
        matrixCube.classList.remove('show-all', 'show-lips', 'show-eyeshadow', 'show-blush');

        if (selectedCategory === 'Lips') {
            matrixCube.classList.add('show-lips');
        } else if (selectedCategory === 'eyeshadow') {
            matrixCube.classList.add('show-eyeshadow');
        } else if (selectedCategory === 'blush') {
            matrixCube.classList.add('show-blush');
        } else {
            matrixCube.classList.add('show-all');
        }
        
        renderProducts(selectedCategory);
        updateSelectedProducts();
    });

    // 페이지 로드 시 초기 상태 설정
    renderProducts();
    updateSelectedProducts();

    // 전역 변수로 노출 (다른 스크립트에서 사용 가능)
    window.getProductsByMood = getProductsByMood;
    window.moodZones = moodZones;

});