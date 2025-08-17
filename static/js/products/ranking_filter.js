document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filterForm');
    const rankingGrid = document.getElementById('rankingGrid');
  
    filterForm.addEventListener('submit', function(e) {
      e.preventDefault(); // 기본 폼 제출 막기
  
      const formData = new FormData(filterForm);
      const data = Object.fromEntries(formData.entries());
  
      fetch('/products/filter_ranking/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // Django CSRF 처리
        },
        body: JSON.stringify(data)
      })
      .then(response => response.text())
      .then(html => {
        rankingGrid.innerHTML = html; // _ranking_grid.html 내용으로 교체
      })
      .catch(err => console.error('필터 Ajax 오류:', err));
    });
  });
  
  // CSRF token 가져오기 함수
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
  