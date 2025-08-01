
//  이미지 크기를 캔버스 최대 크기에 맞게 비율 유지하며 계산

function calculateCanvasSize(imgWidth, imgHeight, maxWidth, maxHeight) {
    const scale = Math.min(maxWidth / imgWidth, maxHeight / imgHeight, 1);
    return {
        width: imgWidth * scale,
        height: imgHeight * scale,
    };
}


// * 캔버스에 이미지 그리기 (기존 내용 클리어 후)

function drawImageOnCanvas(ctx, img, width, height) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.drawImage(img, 0, 0, width, height);
}

//캔버스에서 클릭한 위치의 픽셀 색상을 HEX 코드로 추출

function getClickedPixelColor(ctx, canvas, event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const pixel = ctx.getImageData(x, y, 1, 1).data;
    return rgbToHex(pixel[0], pixel[1], pixel[2]);
}

// RGB 값을 HEX 색상 문자열로 변환

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}

//이미지 URL을 받아 캔버스에 그리기 및 클릭 이벤트 설정

function setupImageCanvas(imageSrc) {
    const uploadedImage = document.getElementById('uploaded-image');
    const imageCanvas = document.getElementById('image-canvas');
    const ctx = imageCanvas.getContext('2d', { willReadFrequently: true });
    const colorDisplayBox = document.getElementById('color-display-box');
    const clickInstruction = document.getElementById('click-instruction');
    const imagePreviewArea = document.getElementById('image-preview-area');
    const selectedColorSwatch = document.getElementById('selected-color-swatch');
    const hexCodeDisplay = document.getElementById('hex-code-display');

    const img = new Image();
    img.crossOrigin = "Anonymous";

    img.onload = function () {
        // 캔버스 최대 크기 설정 (가로 최대 너비, 세로 최대 높이)
        const maxWidth = imagePreviewArea.offsetWidth - 30;
        const maxHeight = 500;

        // 이미지 크기 조정 비율 계산 후 적용
        const { width, height } = calculateCanvasSize(img.width, img.height, maxWidth, maxHeight);

        imageCanvas.width = width;
        imageCanvas.height = height;

        // 캔버스에 이미지 그리기
        drawImageOnCanvas(ctx, img, width, height);

        // UI 요소 표시
        imageCanvas.style.display = 'block';
        colorDisplayBox.style.display = 'flex';
        clickInstruction.style.display = 'block';
        imageCanvas.classList.add('color-picker-active');

        // 캔버스 클릭 시 픽셀 색상 추출 및 표시
        imageCanvas.onclick = function (e) {
            const hex = getClickedPixelColor(ctx, imageCanvas, e);
            selectedColorSwatch.style.backgroundColor = hex;
            hexCodeDisplay.textContent = hex;
        };
    };

    img.src = imageSrc;
}

// 페이지 로딩 후 이미지 업로드 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function () {
    const imageUploadInput = document.getElementById('image-upload-input');

    imageUploadInput?.addEventListener('change', function (event) {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                setupImageCanvas(e.target.result);
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    });
});
