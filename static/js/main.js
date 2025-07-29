console.log("Moodico 프로젝트 JavaScript 로드됨.");

document.addEventListener('DOMContentLoaded', function() {
    //여기에 전역적으로 필요한 이벤트 리스너나 초기화 코드 추가  ex) 네비게이션 메뉴 토글, 스크롤 이벤트 등

    //Moodico클릭 시 메인 페이지로 이동
    const logo = document.querySelector('header .logo');
    if (logo) {
        logo.addEventListener('click', function(event) {
            window.location.href = '/';
        });
    }
});