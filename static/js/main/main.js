console.log("Moodico 프로젝트 JavaScript 로드됨.");

document.addEventListener('DOMContentLoaded', function() {
    //여기에 전역적으로 필요한 이벤트 리스너나 초기화 코드 추가  ex) 네비게이션 메뉴 토글, 스크롤 이벤트 등

    //Moodico 클릭 시 메인 페이지로 이동
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

    //헤더 위에서 아래로 내려오는 애니메이션
    const header = document.querySelector('header');
    if (header) {
        setTimeout(() => {
            header.classList.add('is-visible');
        }, 100);
    }

    // =============================
    // 컬러 투표 기능
    // =============================
    console.log('투표 기능 초기화 시작');
    
    const voteCards = document.querySelectorAll('.vote-product-card');
    const progressBars = document.querySelectorAll('.progress-fill');
    const votePercentages = document.querySelectorAll('.vote-percentage');
    const totalVotes = document.querySelector('.voting-stats strong');
    
    console.log('찾은 투표 카드 수:', voteCards.length);
    
    if (voteCards.length === 0) {
        console.log('투표 카드가 없습니다.');
        return;
    }
    
    // 투표 데이터 초기화
    let voteData = {};
    let totalVoteCount = 0;
    let hasVoted = false;
    let currentSelectedId = null; // 현재 선택된 카드
    
    voteCards.forEach((card) => {
        const productId = card.dataset.productId;
        const likeCount = parseInt(card.querySelector('.vote-count').textContent.match(/\d+/)[0]);
        
        console.log(`제품 ${productId}: 좋아요 ${likeCount}개 (순위 결정용)`);
        
        voteData[productId] = { 
            likes: likeCount,
            votes: 0,
            percentage: 0
        };
    });
    
    console.log('투표 시작 - 모든 제품 0표');
    updateVoteResults();
    
    // 이벤트 리스너 (다시 누르면 취소 / 다른 카드 선택하면 이전 해제 후 이동)
    voteCards.forEach(card => {
        card.addEventListener('click', function() {
            const productId = this.dataset.productId;

            // 1) 같은 카드를 다시 클릭 → 취소
            if (currentSelectedId === productId) {
                this.classList.remove('selected');
                this.style.transform = '';
                this.style.boxShadow = '';

                voteData[productId].votes = 0;
                totalVoteCount = 0;
                hasVoted = false;
                currentSelectedId = null;

                updateVoteResults();
                showVoteMessage('투표가 취소되었습니다.', 'info');
                return;
            }

            // 2) 다른 카드 클릭 → 기존 해제 후 새 카드 선택
            if (hasVoted && currentSelectedId && currentSelectedId !== productId) {
                const prevCard = document.querySelector(`.vote-product-card[data-product-id="${currentSelectedId}"]`);
                if (prevCard) {
                    prevCard.classList.remove('selected');
                    prevCard.style.transform = '';
                    prevCard.style.boxShadow = '';
                }
                voteData[currentSelectedId].votes = 0;
            }

            // 3) 신규 선택
            this.classList.add('selected');
            currentSelectedId = productId;
            voteData[productId].votes = 1;
            totalVoteCount = 1;
            hasVoted = true;

            updateVoteResults();
            showVoteStatus();
            showVoteMessage('투표가 완료되었습니다! 🎉', 'success');
        });
    });
    
    // =============================
    // 결과 업데이트 함수
    // =============================
    function updateVoteResults() {
        console.log('투표 결과 업데이트 중...');
        
        Object.keys(voteData).forEach(productId => {
            const percentage = totalVoteCount > 0 ? Math.round((voteData[productId].votes / totalVoteCount) * 100) : 0;
            voteData[productId].percentage = percentage;
            console.log(`제품 ${productId}: 좋아요 ${voteData[productId].likes}개, 투표 ${voteData[productId].votes}표 (${percentage}%)`);
        });
        
        progressBars.forEach((bar, index) => {
            if (index < voteCards.length) {
                const productId = voteCards[index].dataset.productId;
                const percentage = voteData[productId].percentage;
                bar.style.width = percentage + '%';
            }
        });
        
        votePercentages.forEach((percentage, index) => {
            if (index < voteCards.length) {
                const productId = voteCards[index].dataset.productId;
                percentage.textContent = voteData[productId].percentage + '%';
            }
        });
        
        if (totalVotes) {
            totalVotes.textContent = totalVoteCount;
        }
        
        const voteOverlays = document.querySelectorAll('.vote-count');
        voteOverlays.forEach((overlay, index) => {
            if (index < voteCards.length) {
                const productId = voteCards[index].dataset.productId;
                const data = voteData[productId];
                
                if (data.votes > 0) {
                    overlay.textContent = `❤️ ${data.likes} | 🗳️ 투표완료`;
                    overlay.style.color = '#e91e63';
                    overlay.style.fontWeight = 'bold';
                } else {
                    overlay.textContent = `❤️ ${data.likes} | 🗳️ 투표하기`;
                    overlay.style.color = '#666';
                    overlay.style.fontWeight = 'normal';
                }
            }
        });
        
        console.log('투표 결과 업데이트 완료');
    }
    
    function showVoteStatus() {
        const selectedCard = document.querySelector('.vote-product-card.selected');
        if (selectedCard) {
            const productId = selectedCard.dataset.productId;
            const productName = selectedCard.querySelector('h4').textContent;
            const data = voteData[productId];
            console.log(`🎉 현재 투표된 제품: ${productName} (${productId}) - 좋아요 ${data.likes}개, 투표 ${data.votes}표`);
            
            selectedCard.style.transform = 'scale(1.02)';
            selectedCard.style.boxShadow = '0 8px 25px rgba(255, 107, 155, 0.3)';
        }
    }
    
    function showVoteMessage(message, type) {
        const existingMessage = document.querySelector('.vote-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `vote-message vote-message-${type}`;
        messageDiv.textContent = message;
        
        const votingCard = document.querySelector('.voting-card');
        votingCard.appendChild(messageDiv);
        
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 3000);
    }
    const splashContainer = document.querySelector('.moodico-splash-container');

    //5초후에 무디코 소개멘트 숨기는거
    setTimeout(() => {
        if (splashContainer) {
            splashContainer.classList.add('hidden');
        }
    }, 2500);
});


  // reveal
  const _io = new IntersectionObserver((entries)=>entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('on');}),{threshold:.15});
  document.querySelectorAll('.pc-reveal').forEach(el=>_io.observe(el));

  // mood palettes
  const PC_MOOD = {
    excited: { title:'설레는 무드 · 추천 팔레트',
      chips:[['#ff8a65','코랄'],['#ffc1a6','피치'],['#ff7eb6','핑크'],['#fff4e6','아이보리']],
      tips:['볼에 코랄-피치','립은 글로시','악세서리는 골드'] },
    focus: { title:'집중 무드 · 추천 팔레트',
      chips:[['#1f2a44','네이비'],['#3d5afe','블루'],['#c8b6ff','라일락'],['#e5e7eb','쿨그레이']],
      tips:['상하의 톤 맞추기','립 로즈/모브 MLBB','실버 주얼리'] },
    calm: { title:'차분 무드 · 추천 팔레트',
      chips:[['#6b8b66','카키'],['#a67c52','카멜'],['#d2b48c','탠'],['#c8d5b9','세이지']],
      tips:['채도 낮춘 웜 뉴트럴','브릭/테라코타 소프트','브론즈 포인트'] },
    chic: { title:'시크 무드 · 추천 팔레트',
      chips:[['#000','블랙'],['#fff','화이트'],['#9aa0a6','쿨그레이'],['#3d5afe','블루']],
      tips:['하이컨트라스트','립 체리/버건디','실버/플래티넘'] },
    vivid: { title:'활기찬 무드 · 추천 팔레트',
      chips:[['#e53935','레드'],['#ffb300','옐로'],['#00a896','에메랄드'],['#3d5afe','블루']],
      tips:['포인트 한 곳만 비비드','나머지는 뉴트럴','액세서리는 미니멀'] },
    romantic: { title:'로맨틱 무드 · 추천 팔레트',
      chips:[['#f4a7b9','로즈'],['#f6c1d8','핑크베일'],['#c8b6ff','라일락'],['#fff4e6','아이보리']],
      tips:['블러셔 넓게','립 글로시/틴트','펄은 미세입자'] },
  };
  const moodBoard = document.getElementById('pcMoodBoard');
  if (moodBoard){
    const chipsBox = document.getElementById('pcMoodChips');
    const tipsBox = document.getElementById('pcMoodTips');
    const titleEl = document.getElementById('pcMoodTitle');
    function renderMood(key){
      const d = PC_MOOD[key]; if(!d) return;
      titleEl.textContent = d.title;
      chipsBox.innerHTML = d.chips.map(([c,l])=>`<span class="pc-chip" style="--c:${c};--label:'${l}';"></span>`).join('');
      tipsBox.innerHTML = d.tips.map(t=>`<li>${t}</li>`).join('');
    }
    renderMood('excited');
    moodBoard.querySelectorAll('[data-mood]').forEach(btn=>{
      btn.addEventListener('click', ()=> renderMood(btn.dataset.mood));
    });
  }
