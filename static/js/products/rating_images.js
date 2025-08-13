window.reviewImageFiles = new Map();

function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (csrfInput) {
    return csrfInput.value;
  }
  return '';
}

window.createImagePreviewBox = (id, url, isExisting = false) => {
    const imageUploadContainer = document.getElementById('image-upload-container');
    const addImageBox = document.getElementById('add-image-box');

    const imgBox = document.createElement('div');
    imgBox.classList.add('image-box', 'image-preview'); 
    imgBox.dataset.id = id; 
    imgBox.dataset.isExisting = isExisting;

    imgBox.innerHTML = `
        <button type="button" class="delete-image-btn">&times;</button>
        <img src="${url}" alt="리뷰 이미지 미리보기">
    `;
    
    if (imageUploadContainer && addImageBox) {
        imageUploadContainer.insertBefore(imgBox, addImageBox);
    }
    
    // 삭제 버튼 이벤트 리스너
    imgBox.querySelector('.delete-image-btn').addEventListener('click', async (event) => {
        const boxToRemove = event.target.closest('.image-box');
        const imageId = boxToRemove.dataset.id;
        const wasExisting = boxToRemove.dataset.isExisting === 'true';

        if (wasExisting) {
            // DB에 저장된 기존 이미지 삭제
            if (!confirm('이 이미지를 영구적으로 삭제하시겠습니까?')) return;

            try {
                const response = await fetch(`/products/delete_review_image/${imageId}/`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                });

                if (response.ok) {
                    boxToRemove.remove();
                    alert('이미지가 삭제되었습니다.');
                } else {
                    alert('이미지 삭제에 실패했습니다.');
                }
            } catch (error) {
                console.error('이미지 삭제 오류:', error);
                alert('이미지 삭제 중 오류가 발생했습니다.');
            }
        } else {
            window.reviewImageFiles.delete(imageId);
            boxToRemove.remove();
        }
    });
};

document.addEventListener('DOMContentLoaded', () => {
    const addImageBox = document.getElementById('add-image-box');
    const imageInput = document.getElementById('image-input');

    if (addImageBox){
        addImageBox.addEventListener('click', () => {
            if (imageInput) {
                imageInput.click();
            }
        });
    }

    if (imageInput){
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

                    window.createImagePreviewBox(fileId, e.target.result);
                };
                reader.readAsDataURL(file);
            }
            // 선택 초기화
            imageInput.value = '';
        });
    }
})
