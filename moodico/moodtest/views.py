from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from moodico.users.models import UserProfile
from moodico.products.models import ProductLike
from .color_analyzer import product_result_by_mood, get_random_products
import logging
logger = logging.getLogger(__name__)
# Create your views here.

def mood_test(request):
    """무드 테스트 페이지 뷰"""
    return render(request, 'moodtest/mood_test.html')

def mood_result(request):
    """무드 테스트 결과 페이지 뷰"""
    if request.method == 'POST':
        mood = request.POST.get('mood', '캐주얼')
        if request.user.is_authenticated:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                user_profile.mood_result = mood
                user_profile.save()
                logger.info(f"사용자 {request.user.username}의 무드 테스트 결과 '{mood}'가 저장되었습니다.")
            except Exception as e:
                logger.error(f"무드 테스트 결과 저장 실패: {e}")
    else:
        mood = '캐주얼'  # 기본값
    
    mood_filtered_products = product_result_by_mood(mood)

    # 무드별 결과 데이터 정의
    mood_definition = {
        '러블리': {
            'mood_name': '💖 러블리 무드',
            'mood_description': '사랑스럽고 생기 넘치는, 로맨틱하고 귀여운 분위기',
            'makeup_recommendation': '브라운/코랄 계열, 톤다운 블러셔, 무광 립',
            'keywords': ['사랑스러움', '생기', '로맨틱'],
            # 'recommended_products': [
            #     {
            #         'brand': '롬앤',
            #         'product_name': '베러댄블러셔 #넛티 누드',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '9,900원'
            #     },
            #     {
            #         'brand': '웨이크메이크',
            #         'product_name': '무드스타일러 #우디브라운',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '12,000원'
            #     },
            #     {
            #         'brand': '뮤드',
            #         'product_name': '글래스팅 멜팅밤 #애쉬로즈',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '8,900원'
            #     }
            # ]
        },
        '시크': {
            'mood_name': '🖤 시크 무드',
            'mood_description': '도시적이고 세련된 분위기의 강렬하고 매력적인 느낌',
            'makeup_recommendation': '딥한 브라운/버건디 계열, 메탈릭 섀도우, 매트 립',
            'keywords': ['세련됨', '강렬함', '도시적'],
            # 'recommended_products': [
            #     {
            #         'brand': '클리오',
            #         'product_name': '프로 아이 팔레트 #브라운',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '15,000원'
            #     },
            #     {
            #         'brand': '에뛰드',
            #         'product_name': '블러셔 #로즈브라운',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '10,000원'
            #     },
            #     {
            #         'brand': '롬앤',
            #         'product_name': '매트 립스틱 #딥브라운',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '11,000원'
            #     }
            # ]
        },
        '내추럴': {
            'mood_name': '🌱 내추럴 무드',
            'mood_description': '자연스럽고 편안한 느낌의 깔끔하고 소박한 분위기',
            'makeup_recommendation': '누드/베이지 계열, 쉬머 블러셔, 글로시 립',
            'keywords': ['자연스러움', '편안함', '깔끔함'],
            # 'recommended_products': [
            #     {
            #         'brand': '이니스프리',
            #         'product_name': '내추럴 블러셔 #베이지',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '8,500원'
            #     },
            #     {
            #         'brand': '롬앤',
            #         'product_name': '글래스팅 멜팅밤 #누드',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '9,900원'
            #     },
            #     {
            #         'brand': '페리페라',
            #         'product_name': '글로시 틴트 #베이지',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '7,500원'
            #     }
            # ]
        },
        '캐주얼': {
            'mood_name': '👟 캐주얼 무드',
            'mood_description': '편안하고 활동적인, 격식 없는 자유로운 분위기',
            'makeup_recommendation': '생기 있는 립, 자연스러운 아이 메이크업',
            'keywords': ['편안함', '활동적', '자유로움'],
            # 'recommended_products': [
            #     {
            #         'brand': '롬앤',
            #         'product_name': '더 쥬시 래스팅 틴트 #코랄',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '9,900원'
            #     },
            #     {
            #         'brand': '클리오',
            #         'product_name': '글로우 블러셔 #피치',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '12,000원'
            #     },
            #     {
            #         'brand': '에뛰드',
            #         'product_name': '글래스 틴트 #오렌지',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '8,000원'
            #     }
            # ]
        },
        '고급스러운': {
            'mood_name': '💎 고급스러운 무드',
            'mood_description': '우아하고 세련된 느낌의 럭셔리하고 매력적인 분위기',
            'makeup_recommendation': '딥레드/버건디 계열, 메탈릭 섀도우, 크림 립',
            'keywords': ['우아함', '세련됨', '럭셔리'],
            # 'recommended_products': [
            #     {
            #         'brand': '에뛰드',
            #         'product_name': '프리미엄 립스틱 #딥레드',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '18,000원'
            #     },
            #     {
            #         'brand': '클리오',
            #         'product_name': '메탈릭 섀도우 #골드',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '15,000원'
            #     },
            #     {
            #         'brand': '롬앤',
            #         'product_name': '크림 블러셔 #버건디',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '11,000원'
            #     }
            # ]
        },
        '모던': {
            'mood_name': '🏙️ 모던 무드',
            'mood_description': '깔끔하고 정돈된, 도시적이고 세련된 분위기',
            'makeup_recommendation': '뉴트럴/무채색 계열, 깔끔한 쉐딩, 누드 립',
            'keywords': ['깔끔함', '심플함', '도시적'],
            # 'recommended_products': [
            #     {
            #         'brand': '투쿨포스쿨',
            #         'product_name': '아트클래스 바이 로댕 쉐딩',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '16,000원'
            #     },
            #     {
            #         'brand': '헤라',
            #         'product_name': '센슈얼 파우더 매트 립스틱 #테일러',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '38,000원'
            #     },
            #     {
            #         'brand': '에스쁘아',
            #         'product_name': '모던 섀도우 팔레트 #웜톤',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '22,000원'
            #     }
            #]
        },
        '청순': {
            'mood_name': '🤍 청순 무드',
            'mood_description': '맑고 깨끗한, 순수하고 여리여리한 분위기',
            'makeup_recommendation': '살구/피치 계열, 투명한 펄 섀도우, 촉촉한 립밤',
            'keywords': ['맑음', '순수함', '여리여리'],
            # 'recommended_products': [
            #     {
            #         'brand': '롬앤',
            #         'product_name': '베러댄치크 #페어칩',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '9,900원'
            #     },
            #     {
            #         'brand': '클리오',
            #         'product_name': '프리즘 에어 섀도우 스파클링 #코랄',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '14,000원'
            #     },
            #     {
            #         'brand': '이니스프리',
            #         'product_name': '글로우 틴트 #복숭아',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '10,000원'
            #     }
            # ]
        },
        '힙': {
            'mood_name': '😎 힙한 무드',
            'mood_description': '개성 있고 트렌디한, 쿨하고 자유로운 분위기',
            'makeup_recommendation': '유니크한 컬러 아이라이너, 글리터, 오버립',
            'keywords': ['개성', '트렌디함', '쿨시크'],
            # 'recommended_products': [
            #     {
            #         'brand': '홀리카홀리카',
            #         'product_name': '아이 스팽글리터 #문릿',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '8,500원'
            #     },
            #     {
            #         'brand': '힌스',
            #         'product_name': '무드인핸서 립 매트 #얼루어',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '19,000원'
            #     },
            #     {
            #         'brand': '롬앤',
            #         'product_name': '아이라이너 #블랙',
            #         'image': 'https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg',
            #         'price': '11,000원'
            #     }
            # ]
        }
    }
    
    # 선택된 무드의 결과 데이터 가져오기
    result_data = mood_definition.get(mood, mood_definition['캐주얼'])
    result_data['recommended_products'] = get_random_products(mood_filtered_products)
    
    # if request.user.is_authenticated:
    #     liked_product_ids = ProductLike.objects.filter(user=request.user).values_list('product_id', flat=True)
    #     for product in result_data['recommended_products']:
    #         product['is_liked'] = product['id'] in liked_product_ids
    
    return render(request, 'moodtest/mood_result.html', result_data)