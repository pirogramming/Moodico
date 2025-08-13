window.reviewImageFiles = new Map();

document.addEventListener('DOMContentLoaded', () => {
    const addImageBox = document.getElementById('add-image-box');
    const imageInput = document.getElementById('image-input');
    const imageUploadContainer = document.getElementById('image-upload-container');

    addImageBox.addEventListener('click', () => {
        imageInput.click();
    });

    imageInput.addEventListener('change', (event) => {
        const files = event.target.files;

        for (const file of files) {
            if (window.reviewImageFiles.size >= 10) {
                alert('리뷰 이미지는 최대 10개까지 추가 가능합니다.');
                break;
            }

            const reader = new FileReader();

            reader.onload = (e) => {
                const fileId = `${Date.now()}-${file.name}`;
                window.reviewImageFiles.set(fileId, file);

                // 이미지 박스 객체 생성 - 미리보기
                const imgBox = document.createElement('div');
                imgBox.classList.add('image-box');
                imgBox.innerHTML = `
                <button type="button" class="delete-image-btn">&times;</button>
                <img src="${e.target.result}" alt="리뷰 이미지">
                `;

                imageUploadContainer.insertBefore(imgBox, addImageBox);

                imgBox.querySelector('.delete-image-btn').addEventListener('click', (event) => {
                    const boxToRemove = event.target.closest('.image-box');
                    const idToRemove = boxToRemove.dataset.fileId;

                    window.reviewImageFiles.delete(idToRemove);
                    boxToRemove.remove();
                });
            };
            reader.readAsDataURL(file);
        }
    
        // 선택 초기화
        imageInput.value = '';
    });
})
