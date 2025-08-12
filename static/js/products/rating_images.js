const addImageBox = document.getElementById('add-image-box');
const imageInput = document.getElementById('image-input');
const imageUploadContainer = document.getElementById('image-upload-container');
const submitBtn = document.getElementById('submit-rating');
const deleteBtn = document.getElementsByClassName('image-delete-btn')

addImageBox.addEventListener('click', () => {
    imageInput.click();
});

imageInput.addEventListener('change', (event) => {
    const files = event.target.files;

    for (let file of files) {
        const reader = new FileReader();
        reader.onload = (e) => {
            // 이미지 박스 객체 생성
            const imgBox = document.createElement('div');
            imgBox.classList.add('image-box');
            imgBox.innerHTML = `
            <button type="button" class="delete-image-btn">&times;</button>
            <img src="${e.target.result}" alt="리뷰 이미지">
            `;

            imageUploadContainer.insertBefore(imgBox, addImageBox);

            const deleteBtn = imgBox.querySelector('.delete-image-btn');
            deleteBtn.addEventListener('click', () => {
                imgBox.remove();
            });
        };
        reader.readAsDataURL(file);
    }
  
    // 선택 초기화
    imageInput.value = '';
});

submitBtn.addEventListener('click', () => {
    const formData = new FormData();

    for (let file of files){
        formData.append('images', file)
    }

    fetch(`/reviews/${reviewId}/images/`, {
        method: 'POST',
        body: formData
    });
});

deleteBtn.addEventListener('click', () => {
    fetch(`/reviews/images/${imageId}/`, {
        method: 'DELETE'
    });
});
