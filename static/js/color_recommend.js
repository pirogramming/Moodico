document.addEventListener('DOMContentLoaded', () => {
  const analyzeColorButton = document.getElementById('analyze-color-button');
  const hexCodeDisplay = document.getElementById('hex-code-display');
  const recommendationBox = document.getElementById('recommendation-box');

  if (analyzeColorButton) {
    analyzeColorButton.addEventListener('click', async () => {
      const hex = hexCodeDisplay.textContent.trim();

      // Frontend color analysis (already runs from color_analyzer.js)
      // Now run backend recommendation
      if (hex && hex !== '#FFFFFF') {
        try {
          const res = await fetch('/compare_color/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ hex })
          });

          if (!res.ok) throw new Error('추천 실패');

          const data = await res.json();
          console.log(data);
          renderRecommendations(data.recommended);
        } catch (err) {
          console.error('추천 에러:', err);
        }
      }
    });
  }

  function renderRecommendations(products) {
    recommendationBox.innerHTML = ''; // Clear old results
    products.forEach(p => {
      const card = document.createElement('div');
      card.classList.add('product-card');
      card.innerHTML = `
        <img src="${p.image}" alt="${p.name}" />
        <div class="product-info">
          <div class="brand">${p.brand} <span class="tag">${p.category}</span></div>
          <div class="name">${p.color_name}</div>
          <div class="price">${p.price}</div>
        </div>
        <a class="recommendation-button" href="${p.url}" target="_blank">보러가기</a>
      `;
      recommendationBox.appendChild(card);
    });
  }

  // Helper to get CSRF
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
});
