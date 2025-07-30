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

function displayColorOnMatrix(hex, warmCool, lightDeep) {
    const productsContainer = document.querySelector('.color-matrix-container');
    if (!productsContainer) return;

    // 기존에 표시된 색상 점 제거 - 버튼 누를 때마다 새로 표시
    const existingColorPoint = productsContainer.querySelector('.temp-color-point');
    if (existingColorPoint) {
        existingColorPoint.remove();
    }

    const colorPoint = document.createElement('div');
    colorPoint.classList.add('product-circle', 'temp-color-point');
    colorPoint.style.backgroundColor = hex;
    colorPoint.style.left = `${warmCool}%`;
    colorPoint.style.top = `${lightDeep}%`;
    colorPoint.title = `선택된 색상: ${hex}`;

    colorPoint.style.transform = 'translate(-50%, -50%)';

    colorPoint.style.border = '3px solid #8A2BE2';
    colorPoint.style.boxShadow = '0 0 10px rgba(138, 43, 226, 0.6)';

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

document.addEventListener('DOMContentLoaded', () => {
    const hexCodeDisplay = document.getElementById('hex-code-display');
    const analyzeColorButton = document.getElementById('analyze-color-button'); 

    function analyzeSelectedColor() {
        const hex = hexCodeDisplay.textContent.trim(); // #FFFFFF 형태
        if (hex && hex !== '#FFFFFF') { // 초기값이 아니거나 유효한 경우
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
                    }
                }
            }
        }
    }

    if (analyzeColorButton) {
        analyzeColorButton.addEventListener('click', analyzeSelectedColor);
    }
});