from django.shortcuts import render,redirect, get_object_or_404
import requests
from django.http import HttpResponse
from django.http import HttpRequest
from django.conf import settings
from .forms import *
from django.contrib.auth import login
import json
import os
from django.views.decorators.http import require_http_methods
from functools import wraps
from .models import Upload, ProductLike
from PIL import Image
import numpy as np
from skimage import color
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from skimage.color import rgb2lab
import logging
logger = logging.getLogger(__name__)
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth.decorators import login_required


def login_or_kakao_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get("nickname"):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

def color_matrix_explore(request):
    return render(request, 'color_matrix.html')

# Create your views here.

def main(request):
    """메인 페이지 뷰"""
    return render(request, 'main.html')

def signup_view(request):
    """회원가입 페이지 뷰"""
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})

# @login_or_kakao_required
def my_item_recommendation(request):
    """내 아이템 기반 추천 페이지 뷰"""
    # 백엔드 연동을 위해 임시로 빈 리스트 전달
    recommended_items = []
    search_results = []
    return render(request, 'upload.html', {'search_results': search_results, 'recommended_items': recommended_items})

# @login_or_kakao_required
def mood_test(request):
    """무드 테스트 페이지 뷰"""
    return render(request, 'mood_test.html')

# @login_or_kakao_required
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
    
    return render(request, 'mood_result.html', result_data)


def color_matrix_explore(request):
    """색상 매트릭스 페이지 뷰"""
    return render(request, 'color_matrix.html')

def product_detail(request, product_id):
    """제품 상세 페이지 뷰"""
    # 제품 상세 정보 (백엔드에서 받아올 예정)
    product = {
        'id': product_id,
        'name': f'제품 {product_id}',
        'description': '이 제품은 아주 좋은 제품입니다.',
        'price': '30,000원',
        'image': '/static/images/test.jpg', # 임시 이미지
    }
    return render(request, 'detail.html', {'product': product})


def product_list(request):
    json_path = os.path.join('static', 'data', 'products.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    return render(request, 'product_list.html', {'products': products})

# 카카오 로그인 관련 뷰
def kakao_authorize(request):
    scope = "profile_nickname profile_image"
    url = (
        f"{settings.KAKAO_AUTH_HOST}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={settings.KAKAO_CLIENT_ID}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
        f"&scope={scope}"
        f"&prompt=login"  
    )
    return redirect(url)

def kakao_callback(request: HttpRequest):
    code = request.GET.get("code")

    token_url = f"{settings.KAKAO_AUTH_HOST}/oauth/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }

    if hasattr(settings, "KAKAO_CLIENT_SECRET"):
        data["client_secret"] = settings.KAKAO_CLIENT_SECRET

    response = requests.post(token_url, data=data)
    result = response.json()

    access_token = result.get("access_token")
    if not access_token:
        return redirect("/?login=fail")

    # 사용자 정보 요청
    profile_url = f"{settings.KAKAO_API_HOST}/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()

    # 닉네임, 프로필 이미지 가져오기
    nickname = profile_data.get("properties", {}).get("nickname")
    profile_image = profile_data.get("properties", {}).get("profile_image")

    print("DEBUG nickname:", nickname)  # 확인용

    # 세션에 저장
    request.session["access_token"] = access_token
    request.session["nickname"] = nickname
    request.session["profile_image"] = profile_image

    return redirect("main")  # 로그인 페이지에서 프로필 보여주기


def kakao_profile(request):
    access_token = request.session.get("access_token")

    if not access_token:
        return redirect("/?login=fail")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 사용자 정보 요청
    profile_url = f"{settings.KAKAO_API_HOST}/v2/user/me"
    response = requests.get(profile_url, headers=headers)
    result = response.json()

    # 예시: 사용자 정보 추출
    kakao_id = result.get("id")
    nickname = result.get("properties", {}).get("nickname")
    profile_image = result.get("properties", {}).get("profile_image")

    # 템플릿에 넘겨서 렌더링
    context = {
        "kakao_id": kakao_id,
        "nickname": nickname,
        "profile_image": profile_image,
        "raw_json": result  # 디버깅용
    }

    return render(request, "main.html", context)

@require_http_methods(["GET"])
def kakao_logout(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("/?logout=fail")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 카카오 로그아웃
    logout_response = requests.post(
        f"{settings.KAKAO_API_HOST}/v1/user/logout",
        headers=headers
    )
    print("Kakao logout response:", logout_response.status_code, logout_response.text)

    # 카카오 연결 해제 (unlink)
    unlink_response = requests.post(
        f"{settings.KAKAO_API_HOST}/v1/user/unlink",
        headers=headers
    )
    print("Kakao unlink response:", unlink_response.status_code, unlink_response.text)

    # 세션 정리
    request.session.flush()

    return redirect("/?logout=success")

# 이미지 업로드
def upload_color_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)

            if request.user.is_authenticated:
                upload.user = request.user
            else:
                upload.user = None  # or handle anonymous case

            upload.save()
            return render(request, 'upload.html', {
                'form': UploadForm(),
                'uploaded_image_url': upload.image_path.url
            })
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})


@csrf_exempt
def recommend_by_color(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        body = json.loads(request.body)
        warm = body.get("warmCool")
        deep = body.get("lightDeep")
        lab_l = body.get("lab_l", 0)
        lab_a = body.get("lab_a", 0)
        lab_b = body.get("lab_b", 0)

        if warm is None or deep is None:
            return JsonResponse({"error": "Missing coordinates"}, status=400)

        coord = np.array([warm, deep, lab_l, lab_a, lab_b])
        logger.info(f"Received coordinates: warmCool={warm}, lightDeep={deep}, lab_l={lab_l}, lab_a={lab_a}, lab_b={lab_b}")

        with open("static/data/cluster_centers.json", "r") as f:
            centers = json.load(f)
        with open("static/data/products_clustered.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        # Step 1: Find closest cluster
        cluster_idx = np.argmin([np.linalg.norm(coord - np.array(c)) for c in centers])
        logger.info(f"Closest cluster index: {cluster_idx}")

        # Step 2: Gather products from the cluster
        cluster_products = [p for p in products if p.get("cluster") == cluster_idx]

        # Step 3: Feature vector comparison (WarmCool, LightDeep, lab_l, lab_a, lab_b)
        def get_feature_vec(p):
            return np.array([
                p.get("warmCool", 0),
                p.get("lightDeep", 0),
                p.get("lab_l", 0),
                p.get("lab_a", 0),
                p.get("lab_b", 0),
            ])

        if len(cluster_products) >= 5:
            candidates = cluster_products
            logger.info(f"Cluster size sufficient: {len(candidates)} candidates")
        else:
            candidates = products
            logger.warning(f"Cluster {cluster_idx} has only {len(cluster_products)} products — using full dataset")

        similarities = []
        for p in candidates:
            prod_vec = get_feature_vec(p).reshape(1, -1)
            user_vec_for_similarity = np.array([
                warm,
                deep,
                p.get("lab_l", 0),
                p.get("lab_a", 0),
                p.get("lab_b", 0),
            ]).reshape(1, -1)

            sim = cosine_similarity(user_vec_for_similarity, prod_vec)[0][0]
            similarities.append((p, sim))

        # Step 4: Sort by cosine similarity (higher is better)
        top_matches = sorted(similarities, key=lambda x: -x[1])[:5]

        # Step 5: Format response
        response = []
        for product, sim in top_matches:
            response.append({
                "name": product.get("name"),
                "color_name": product.get("color_name"),
                "hex": product.get("hex"),
                "image": product.get("image"),
                "price": product.get("price"),
                "url": product.get("url"),
                "brand": product.get("brand"),
                "category": product.get("category"),
                "warmCool": product.get("warmCool"),
                "lightDeep": product.get("lightDeep"),
                "distance": round(sim, 4),  # Cosine similarity score
            })

        return JsonResponse({"recommended": response}, json_dumps_params={"ensure_ascii": False})

    except Exception as e:
        logger.exception("Recommendation error")
        return JsonResponse({"error": str(e)}, status=500)


# DB 구현 이후 검색 로직 수정 필요 - 현재는 검색시마다 json 파일을 매번 불러오고 있음
## 현재는 단어 단위의 검색만 가능.. (제품 데이터를 밑에 표시함으로써 이 문제 완화 가능) 
## 만일 사용자가 "조선무화과"를 검색한다면 "조선 무화과" 검색어는 서치에 걸리지 않음("조선", "무화과"는 정상적으로 검색 가능)
def search_product(request):
    query = request.GET.get('q', '').lower().strip()
    query_words = query.split()

    product_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
    with open(product_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    def normalize(text):
        text = text.lower()
        return text
    
    filtered = []
    for p in products:
        search_for = normalize(p['brand'] + ' - ' + p['name'])
        if all(word in search_for for word in query_words):
            filtered.append(p)

    return JsonResponse({'results':filtered})


@csrf_exempt
@require_http_methods(["POST"])
def toggle_product_like(request):
    """제품 좋아요 토글 API"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_brand = data.get('product_brand')
        product_price = data.get('product_price')
        product_image = data.get('product_image', '')
        
        if not all([product_id, product_name, product_brand, product_price]):
            return JsonResponse({
                'success': False,
                'message': '필수 제품 정보가 누락되었습니다.'
            }, status=400)
        
        # 사용자 확인 (임시로 세션 기반)
        user = request.user if request.user.is_authenticated else None
        if not user:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            }, status=401)
        
        # 기존 좋아요 확인
        existing_like = ProductLike.objects.filter(
            user=user,
            product_id=product_id
        ).first()
        
        if existing_like:
            # 좋아요 취소
            existing_like.delete()
            is_liked = False
            message = '좋아요가 취소되었습니다.'
        else:
            # 좋아요 추가
            ProductLike.objects.create(
                user=user,
                product_id=product_id,
                product_name=product_name,
                product_brand=product_brand,
                product_price=product_price,
                product_image=product_image
            )
            is_liked = True
            message = '좋아요에 추가되었습니다! 💖'
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        logger.error(f"좋아요 토글 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


@require_http_methods(["GET"])
def get_user_likes(request):
    """사용자의 좋아요 목록 조회 API"""
    try:
        # 사용자 확인
        user = request.user if request.user.is_authenticated else None
        if not user:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            }, status=401)
        
        # 사용자의 좋아요 목록 조회
        likes = ProductLike.objects.filter(user=user).values(
            'product_id', 'product_name', 'product_brand', 
            'product_price', 'product_image', 'created_at'
        )
        
        return JsonResponse({
            'success': True,
            'likes': list(likes)
        })
        
    except Exception as e:
        logger.error(f"좋아요 목록 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


def liked_products_page(request):
    """찜한 아이템 페이지 뷰"""
    # 사용자 확인
    user = request.user if request.user.is_authenticated else None
    if not user:
        return redirect('login')
    
    # 사용자의 좋아요 목록 조회
    liked_products = ProductLike.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'liked_products.html', {
        'liked_products': liked_products
    })

@login_required
def profile(request):
    user_name = request.user.username if request.user.is_authenticated else request.session.get("nickname", "게스트")
    user_mood = "정보 없음"  # mood_result 저장 로직 구현 후 변경 예정
    liked_products = ProductLike.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'user_name': user_name,
        'user_mood': user_mood,
        'liked_products': liked_products,
    }

    return render(request, 'profile.html', context)

# upload.html에서 검색한 제품의 이미지를 가져옴
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse("URL not provided", status=400)
    
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', 'image/jpeg')
        return HttpResponse(response.content, content_type=content_type)
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching image: {e}", status=500)