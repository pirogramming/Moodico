// 추출한 HEX -> RGB 코드로 변환하는 함수
function hexToRgb(hex) {
    if (!hex || typeof hex !== 'string') {
        return null;
    }

    hex = hex.startsWith('#') ? hex.slice(1) : hex;

    // HEX 코드 길이 확인 (3자리 또는 6자리)
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    } else if (hex.length !== 6) {
        return null; // 유효하지 않은 HEX 코드 길이
    }

    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    // 유효한 숫자인지 확인
    if (isNaN(r) || isNaN(g) || isNaN(b)) {
        return null;
    }

    return [r, g, b];
}


// RGB -> HSL(Hue, Saturation, Lightness) 변환하는 함수
function rgbToHsl(r, g, b) {
    if (r === null || g === null || b === null || r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255) {
        return null;
    }

    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = 0; // 회색조 (hue는 0)
        s = 0; // 채도 0
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

        switch (max) {
            case r:
                h = (g - b) / d + (g < b ? 6 : 0);
                break;
            case g:
                h = (b - r) / d + 2;
                break;
            case b:
                h = (r - g) / d + 4;
                break;
        }
        h /= 6;
    }


    return [h * 360, s, l];
}

function rgbToLab(r, g, b) {
    // Normalize RGB
    r /= 255; g /= 255; b /= 255;

    // Linearize sRGB
    const toLinear = c => (c <= 0.04045) ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    r = toLinear(r); g = toLinear(g); b = toLinear(b);

    // Convert to XYZ
    const x = r * 0.4124 + g * 0.3576 + b * 0.1805;
    const y = r * 0.2126 + g * 0.7152 + b * 0.0722;
    const z = r * 0.0193 + g * 0.1192 + b * 0.9505;

    // Normalize for D65 white point
    const X = x / 0.95047;
    const Y = y / 1.00000;
    const Z = z / 1.08883;

    const f = t => (t > 0.008856) ? Math.cbrt(t) : (903.3 * t + 16) / 116;

    const fx = f(X), fy = f(Y), fz = f(Z);

    const L = 116 * fy - 16;
    const A = 500 * (fx - fy);
    const B = 200 * (fy - fz);

    return [L, A, B];
}


function displayColorOnMatrix(hex, warmCool, lightDeep) {
    const productsContainer = document.querySelector('.color-matrix-container');
    if (!productsContainer) return;

    // 기존에 표시된 색상 점 제거 - 버튼 누를 때마다 새로 표시
    const existingColorPoint = productsContainer.querySelector('.user-color-point');
    if (existingColorPoint){ 
        existingColorPoint.remove();
    }

    const colorPoint = document.createElement('div');
    colorPoint.classList.add('product-circle', 'user-color-point');
    colorPoint.style.backgroundColor = hex;
    colorPoint.style.left = `${warmCool}%`;
    colorPoint.style.top = `${lightDeep}%`;
    colorPoint.title = `선택된 색상: ${hex}`;

    colorPoint.style.transform = 'translate(-50%, -50%)';

    colorPoint.style.border = '3px solid #8A2BE2';
    colorPoint.style.boxShadow = '0 0 10px rgba(138, 43, 226, 0.6)';
    colorPoint.style.zIndex = '20'; 
    colorPoint.style.opacity = '0.8';

    productsContainer.appendChild(colorPoint);
}


// HSL로부터 waemCool, lightDeep 수치를 계산하는 함수
function calculateCoordinatesFromHsl(h, s, l) {
    if (h === null || s === null || l === null) {
        return null;
    }

    let warmCoolScore;
    if (h >= 330 || h < 60) {
        if (h >= 330) h = h - 360;
        warmCoolScore = (h + 30) / 90;
    } else if (h >= 60 && h < 180) {
        warmCoolScore = 1 - ((h - 60) / 120);
    } else if (h >= 180 && h < 300) {
        warmCoolScore = -((h - 180) / 120);
    } else { // h >= 300 && h < 330
        warmCoolScore = -1 + ((h - 300) / 30);
    }

    if (s < 0.05) {
        warmCoolScore = 0;
    } else {
        warmCoolScore *= Math.pow(s, 0.8);
    }

    if (l < 0.1 || l > 0.9) {
        warmCoolScore *= (1 - Math.pow(Math.abs(0.5 - l) * 2, 2));
    }

    let finalWarmCool = (warmCoolScore + 1) * 50;
    finalWarmCool = Math.max(0, Math.min(100, finalWarmCool));

    const finalLightDeep = (1 - l) * 100;

    return { warmCool: finalWarmCool, lightDeep: finalLightDeep };
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function renderRecommendations(products) {
    const box = document.getElementById("recommendation-box");
    box.innerHTML = "";
    products.forEach((p, index) => {
        const card = document.createElement("div");
        card.classList.add("product-card");
        
        // 제품 정보를 기반으로 고유한 ID 생성
        const brand = (p.brand || 'unknown').replace(/\s+/g, '-').toLowerCase();
        const name = (p.color_name || p.name || 'unknown').replace(/\s+/g, '-').toLowerCase();
        const price = (p.price || '').replace(/[^\d]/g, '');
        const imgHash = p.image ? p.image.split('/').pop().split('.')[0] : `idx${index}`;
        
        const uniqueId = `${brand}-${name}-${price}-${imgHash}`.substring(0, 60);
        card.dataset.productId = p.id || uniqueId;
        
        console.log(`Color analyzer card ${index}: ID=${card.dataset.productId}, Name=${p.color_name || p.name}`);
        
        card.innerHTML = `
            <button class="like-button" title="좋아요"></button>
            <span class="like-count">0</span>
            <img src="${p.image}" alt="${p.name}" />
            <div class="product-info">
                <div class="brand">${p.brand} <span class="tag">${p.category}</span></div>
                <div class="name">${p.color_name}</div>
                <div class="price">${p.price}</div>
            </div>
            <a class="recommendation-button" href="${p.url}" target="_blank">보러가기</a>
        `;
        box.appendChild(card);
        
        // 새로 추가된 카드의 좋아요 상태 복원
        if (window.restoreLikeStateForCard) {
            window.restoreLikeStateForCard(card);
        }
    });
}

function displayRecommendationsOnMatrix(products) {
    const productsContainer = document.querySelector('.color-matrix-container');
    if (!productsContainer) return;

    // 기존의 모든 색상 점 제거 - 버튼 누를 때마다 새로 표시
    const existingColorPoints = productsContainer.querySelectorAll('.temp-color-point');
    existingColorPoints.forEach(point => point.remove());

    products.forEach(p => {
        const colorPoint = document.createElement('div');
        colorPoint.classList.add('product-circle', 'temp-color-point');
        colorPoint.style.backgroundColor = p.hex;
        // colorPoint.style.left = `${p.warmCool}%`;
        colorPoint.style.left = `${parseFloat(p.warmCool)}%`;
        colorPoint.style.top = `${parseFloat(p.lightDeep)}%`;
        // colorPoint.style.top = `${p.lightDeep}%`;
        colorPoint.title = `제품: ${p.name} (${p.brand})`;

        colorPoint.href = p.url;
        colorPoint.target = "_blank"; // 새 탭에서 열기

        colorPoint.style.transform = 'translate(-50%, -50%)';

        colorPoint.style.border = '3px solid #F7F7F7';
        colorPoint.style.boxShadow = '0 0 8px rgba(247, 247, 247, 0.8)';
        colorPoint.style.zIndex = '10'; 

        //툴팁 생성
        const tooltip = document.createElement('div');
        tooltip.classList.add('product-tooltip');
        tooltip.innerHTML = `
            <img src="${p.image}" alt="${p.name}" />
            <div class="tooltip-brand">${p.brand}</div>
            <div class="tooltip-name">${p.name}</div>
            <div class="tooltip-price">${p.price}</div>
        `;
        
        colorPoint.appendChild(tooltip);


        colorPoint.addEventListener('click', (event) => {
            event.preventDefault(); // 기본 링크 동작 방지
            window.open(p.url, '_blank'); // 새 탭에서 URL 열기
        });
        
        productsContainer.appendChild(colorPoint);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const hexCodeDisplay = document.getElementById('hex-code-display');
    const analyzeColorButton = document.getElementById('analyze-color-button'); 


    function analyzeSelectedColor() {
      const hex = hexCodeDisplay.textContent.trim(); // #FFFFFF 형태
      if (hex && hex !== '#FFFFFF') {
          const rgb = hexToRgb(hex);
          if (rgb) {
              const hsl = rgbToHsl(rgb[0], rgb[1], rgb[2]);
              if (hsl) {
                  const coords = calculateCoordinatesFromHsl(hsl[0], hsl[1], hsl[2]);
                  if (coords) {
                      console.log(`Analyzed Color: ${hex}`);
                      console.log(`Warm-Cool: ${coords.warmCool.toFixed(2)}`);
                      console.log(`Light-Deep: ${coords.lightDeep.toFixed(2)}`);
                    
                      // 색상을 매트릭스에 표시
                      displayColorOnMatrix(hex, coords.warmCool, coords.lightDeep);

                      // Send to backend
                      const [lab_l, lab_a, lab_b] = rgbToLab(rgb[0], rgb[1], rgb[2]);
                    fetch("/recommend/recommend_by_color/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCookie("csrftoken"),
                        },
                        body: JSON.stringify({
                            warmCool: coords.warmCool,
                            lightDeep: coords.lightDeep,
                            lab_l: lab_l,
                            lab_a: lab_a,
                            lab_b: lab_b
                        }),
                    })

                      .then(res => res.json())
                      .then(data => {
                          if (data.recommended) {
                              renderRecommendations(data.recommended);
                              displayRecommendationsOnMatrix(data.recommended);
                          } else {
                              console.warn("No recommended field in response", data);
                          }
                    console.log(data.recommended);
                      }
                    )
                      .catch(err => console.error("추천 실패:", err));
                    }
                }
            }
        }
    }
    if (analyzeColorButton) {
        analyzeColorButton.addEventListener('click', analyzeSelectedColor);
    }
});