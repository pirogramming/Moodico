from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Create your views here.

def mood_test(request):
    """무드 테스트 페이지 뷰"""
    return render(request, 'moodtest/mood_test.html')

def mood_result(request):
    """무드 테스트 결과 페이지 뷰"""
    if request.method == 'POST':
        mood = request.POST.get('mood', '러블리')
    else:
        mood = '러블리'  # 기본값
    
    # 무드별 결과 데이터 정의
    mood_results = {
        '러블리': {
            'mood_name': '🌿 모리걸 무드',
            'mood_description': '자연 속에서 살 것 같은 따뜻하고 조용한 소녀 같은 분위기',
            'makeup_recommendation': '브라운/코랄 계열, 톤다운 블러셔, 무광 립',
            'keywords': ['내추럴', '잔잔함', '따뜻한 무드'],
            'recommended_products': [
                {
                    'brand': '롬앤',
                    'product_name': '베러댄블러셔 #넛티 누드',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '9,900원'
                },
                {
                    'brand': '웨이크메이크',
                    'product_name': '무드스타일러 #우디브라운',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '12,000원'
                },
                {
                    'brand': '뮤드',
                    'product_name': '글래스팅 멜팅밤 #애쉬로즈',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '8,900원'
                }
            ]
        },
        '시크': {
            'mood_name': '🖤 시크 무드',
            'mood_description': '도시적이고 세련된 분위기의 강렬하고 매력적인 느낌',
            'makeup_recommendation': '딥한 브라운/버건디 계열, 메탈릭 섀도우, 매트 립',
            'keywords': ['세련됨', '강렬함', '도시적'],
            'recommended_products': [
                {
                    'brand': '클리오',
                    'product_name': '프로 아이 팔레트 #브라운',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '15,000원'
                },
                {
                    'brand': '에뛰드',
                    'product_name': '블러셔 #로즈브라운',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '10,000원'
                },
                {
                    'brand': '롬앤',
                    'product_name': '매트 립스틱 #딥브라운',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '11,000원'
                }
            ]
        },
        '내추럴': {
            'mood_name': '🌱 내추럴 무드',
            'mood_description': '자연스럽고 편안한 느낌의 깔끔하고 소박한 분위기',
            'makeup_recommendation': '누드/베이지 계열, 쉬머 블러셔, 글로시 립',
            'keywords': ['자연스러움', '편안함', '깔끔함'],
            'recommended_products': [
                {
                    'brand': '이니스프리',
                    'product_name': '내추럴 블러셔 #베이지',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '8,500원'
                },
                {
                    'brand': '롬앤',
                    'product_name': '글래스팅 멜팅밤 #누드',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '9,900원'
                },
                {
                    'brand': '페리페라',
                    'product_name': '글로시 틴트 #베이지',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '7,500원'
                }
            ]
        },
        '활기찬': {
            'mood_name': '✨ 활기찬 무드',
            'mood_description': '밝고 경쾌한 느낌의 생동감 있고 에너지 넘치는 분위기',
            'makeup_recommendation': '코랄/오렌지 계열, 글로우 블러셔, 글로시 립',
            'keywords': ['밝음', '경쾌함', '에너지'],
            'recommended_products': [
                {
                    'brand': '롬앤',
                    'product_name': '더 쥬시 래스팅 틴트 #코랄',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '9,900원'
                },
                {
                    'brand': '클리오',
                    'product_name': '글로우 블러셔 #피치',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '12,000원'
                },
                {
                    'brand': '에뛰드',
                    'product_name': '글래스 틴트 #오렌지',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '8,000원'
                }
            ]
        },
        '고급스러운': {
            'mood_name': '💎 고급스러운 무드',
            'mood_description': '우아하고 세련된 느낌의 럭셔리하고 매력적인 분위기',
            'makeup_recommendation': '딥레드/버건디 계열, 메탈릭 섀도우, 크림 립',
            'keywords': ['우아함', '세련됨', '럭셔리'],
            'recommended_products': [
                {
                    'brand': '에뛰드',
                    'product_name': '프리미엄 립스틱 #딥레드',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '18,000원'
                },
                {
                    'brand': '클리오',
                    'product_name': '메탈릭 섀도우 #골드',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '15,000원'
                },
                {
                    'brand': '롬앤',
                    'product_name': '크림 블러셔 #버건디',
                    'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
                    'price': '11,000원'
                }
            ]
        }
    }
    
    # 선택된 무드의 결과 데이터 가져오기
    result_data = mood_results.get(mood, mood_results['러블리'])
    
    return render(request, 'moodtest/mood_result.html', result_data)