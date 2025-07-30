function drawImageToCanvas(imageSrc) {
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
        const maxWidth = imagePreviewArea.offsetWidth - 30;
        const maxHeight = 500;

        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
            height *= (maxWidth / width);
            width = maxWidth;
        }
        if (height > maxHeight) {
            width *= (maxHeight / height);
            height = maxHeight;
        }

        imageCanvas.width = width;
        imageCanvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);

        imageCanvas.style.display = 'block';
        colorDisplayBox.style.display = 'flex';
        clickInstruction.style.display = 'block';
        imageCanvas.classList.add('color-picker-active');

        imageCanvas.onclick = function (e) {
            const rect = imageCanvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const pixel = ctx.getImageData(x, y, 1, 1).data;
            const hex = rgbToHex(pixel[0], pixel[1], pixel[2]);
            selectedColorSwatch.style.backgroundColor = hex;
            hexCodeDisplay.textContent = hex;
        };
    };
    img.src = imageSrc;
}

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}

// Initial logic when new image uploaded
document.addEventListener('DOMContentLoaded', function () {
    const imageUploadInput = document.getElementById('image-upload-input');

    imageUploadInput?.addEventListener('change', function (event) {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                drawImageToCanvas(e.target.result);
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    });
});
