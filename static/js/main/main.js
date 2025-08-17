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
    
    // 24시간마다 투표 세션 생성
    //console.log('투표 기능 초기화 시작');
    
    const voteCards = document.querySelectorAll('.vote-product-card');
    const progressBars = document.querySelectorAll('.progress-fill');
    const votePercentages = document.querySelectorAll('.vote-percentage');
    const totalVotes = document.querySelector('.voting-stats strong');
    
    // console.log('찾은 투표 카드 수:', voteCards.length);
    
    // if (voteCards.length === 0) {
    //     console.log('투표 카드가 없습니다.');
    //     return;
    // }
    
    // 투표 데이터 초기화
    let voteData = {};
    let totalVoteCount = 0;
    let hasVoted = false;
    let currentSelectedId = null; // 현재 선택된 카드

    voteCards.forEach((card) => {
        const productId = card.dataset.productId;
        const likeCount = parseInt(card.dataset.like_count, 10) || 0;
        const productVotes = parseInt(card.dataset.votes, 10) || 0;
        
        console.log(`제품 ${productId}: 좋아요 ${likeCount}개 (순위 결정용)`);
        
        voteData[productId] = { 
            likes: likeCount,
            votes: productVotes,
            percentage: 0
        };
        totalVoteCount += productVotes;
    });
    
    // console.log('투표 시작 - 모든 제품 0표');
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

                voteData[productId].votes -= 1;
                totalVoteCount -= 1;
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
                voteData[currentSelectedId].votes += 1;
            }

            // 3) 신규 선택
            this.classList.add('selected');
            currentSelectedId = productId;
            voteData[productId].votes += 1;
            totalVoteCount += 1;
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
    lovely: {
      title:'러블리 무드 · 추천 팔레트',
      chips:[['#ff8a65','코랄'],['#f4a7b9','로즈핑크'],['#e1f5fe','베이비블루'],['#fff4e6','크림아이보리']],
      tips:['피치/핑크톤 블러셔 넓게','글로시 립으로 생기있게','미니멀한 주얼리']
    },
    chic: {
      title:'시크 무드 · 추천 팔레트',
      chips:[['#000000','블랙'],['#4b4b5b','다크네이비'],['#a0a3a7','스톤그레이'],['#ffffff','화이트']],
      tips:['모노톤 의상으로 톤온톤 스타일링','립은 딥한 버건디/레드','실버 또는 플래티넘 주얼리']
    },
    natural: {
      title:'내추럴 무드 · 추천 팔레트',
      chips:[['#c8e6c9','민트'],['#a67c52','카멜'],['#d2b48c','베이지'],['#c8d5b9','세이지그린']],
      tips:['자연스러운 채도의 옷으로 톤 맞추기','누드/코랄 계열 립','골드 또는 원석 액세서리']
    },
    casual: {
      title:'캐주얼 무드 · 추천 팔레트',
      chips:[['#ffb300','머스타드옐로'],['#3d5afe','로얄블루'],['#e53935','레드'],['#fff4e6','아이보리']],
      tips:['비비드 컬러로 한두 곳 포인트','스니커즈/캡모자로 활동성 강조','귀엽고 작은 액세서리']
    },
    elegant: {
      title:'고급스러운 무드 · 추천 팔레트',
      chips:[['#9e3c3e','와인'],['#3b3b3c','차콜'],['#bfa57f','브론즈'],['#d4c4b6','베이지']],
      tips:['실크/새틴 등 고급 소재 활용','입술은 딥레드/말린장미','진주 또는 골드 주얼리']
    },
    modern: {
      title:'모던 무드 · 추천 팔레트',
      chips:[['#78909C','스모키블루'],['#4b4b5b','다크그레이'],['#9aa0a6','쿨그레이'],['#ffffff','화이트']],
      tips:['절제된 실루엣의 의상','립은 로즈 또는 모브 MLBB','미니멀한 실버 주얼리']
    },
    purity: {
      title:'청순 무드 · 추천 팔레트',
      chips:[['#e1f5fe','스카이블루'],['#f8bbd0','라이트핑크'],['#b19cd9','라벤더'],['#fff8e1','아이보리']],
      tips:['투명한 피부 표현에 집중','수채화처럼 연한 핑크 블러셔','글로시한 립 연출']
    },
    hip: {
      title:'힙 무드 · 추천 팔레트',
      chips:[['#b39ddb','바이올렛'],['#c0c0c0','실버'],['#6c757d','그레이'],['#f44336','강렬한레드']],
      tips:['오버사이즈 핏 의상 활용','유니크한 패턴이나 프린팅','과감한 액세서리 매치']
    }
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
