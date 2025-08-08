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

    //페이지 접속하면 밑에서 올라오는듯한 애니메이션
    const explorationModels = document.querySelector('.exploration-models');
    if (explorationModels) {

        setTimeout(() => {
            explorationModels.classList.add('is-visible');
        }, 100);
    }

    //이건 헤더 위에서 아래로 내려오는 애니메이션
    const header = document.querySelector('header');
    if (header) {
        setTimeout(() => {
            header.classList.add('is-visible');
        }, 100);
    }
});