document.addEventListener('DOMContentLoaded', function() {
    const imageUploadInput = document.getElementById('image-upload-input');
    const uploadedImage = document.getElementById('uploaded-image');
    const imageCanvas = document.getElementById('image-canvas');

    const ctx = imageCanvas.getContext('2d', { willReadFrequently: true }); 
    const colorDisplayBox = document.getElementById('color-display-box');
    const selectedColorSwatch = document.getElementById('selected-color-swatch');
    const hexCodeDisplay = document.getElementById('hex-code-display');
    const clickInstruction = document.getElementById('click-instruction');
    const imagePreviewArea = document.getElementById('image-preview-area');

    let currentImage = null;

    imageUploadInput.addEventListener('change', function(event) {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();

            reader.onload = function(e) {
                uploadedImage.src = e.target.result;
                uploadedImage.style.display = 'block';
                imageCanvas.style.display = 'none';

                currentImage = new Image();
                currentImage.onload = function() {
                    
                    const maxWidth = imagePreviewArea.offsetWidth - 30; 
                    const maxHeight = 500; 

                    let width = currentImage.width;
                    let height = currentImage.height;

                    if (width > maxWidth) {
                        height = height * (maxWidth / width);
                        width = maxWidth;
                    }
                    if (height > maxHeight) {
                        width = width * (maxHeight / height);
                        height = maxHeight;
                    }

                    imageCanvas.width = width;
                    imageCanvas.height = height;
                    
                    ctx.drawImage(currentImage, 0, 0, width, height);

                    
                    imageCanvas.style.display = 'block';
                    uploadedImage.style.display = 'none';
                    colorDisplayBox.style.display = 'flex';
                    clickInstruction.style.display = 'block';

                   
                    imageCanvas.classList.add('color-picker-active');
                };
                currentImage.src = e.target.result;
            };
            reader.readAsDataURL(event.target.files[0]);
        } else {
            uploadedImage.style.display = 'none';
            imageCanvas.style.display = 'none';
            colorDisplayBox.style.display = 'none';
            clickInstruction.style.display = 'none';
            imageCanvas.classList.remove('color-picker-active');
        }
    });

    imageCanvas.addEventListener('click', function(e) {
        if (!currentImage) return;

        const rect = imageCanvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const r = pixel[0];
        const g = pixel[1];
        const b = pixel[2];

        const hex = rgbToHex(r, g, b);

        selectedColorSwatch.style.backgroundColor = hex;
        hexCodeDisplay.textContent = hex;
    });

    function rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
    }

    uploadedImage.style.display = 'none';
    imageCanvas.style.display = 'none';
    colorDisplayBox.style.display = 'none';
    clickInstruction.style.display = 'none';
});