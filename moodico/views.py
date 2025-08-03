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
from .models import Upload
from PIL import Image
import numpy as np
from skimage import color
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from skimage.color import rgb2lab
import logging
logger = logging.getLogger(__name__)
from sklearn.metrics.pairwise import cosine_similarity


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
    # products.json에서 크롤링 데이터 읽기
    json_path = os.path.join('static', 'data', 'products.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # 제품명에서 브랜드 추출 및 데이터 가공
    processed_products = []
    for product in products:
        # 제품명에서 브랜드 추출 (첫 번째 공백까지)
        product_name = product['name']
        brand = product_name.split()[0] if product_name else "브랜드"
        
        processed_product = {
            'type': '립',  # 기본값
            'image': product['image'],
            'brand': brand,
            'product_name': product['name'],
            'price': product['price'],
            'rating': '4.0',  # 기본값 유지
            'review_count': '123'  # 기본값 유지
        }
        processed_products.append(processed_product)
    
    # 무드 테스트 결과 데이터
    mood_data = {
        'mood_name': '로맨틱',
        'mood_description': '부드럽고 여성스러운 사랑스러운 느낌',
        'colors': ['#FEEBEB', '#FFD2CC', '#FFB7B3'],
        'tags': ['#soft', '#feminine', '#pink', '#shimmer'],
        'recommended_products': processed_products
    }
    return render(request, 'mood_result.html', mood_data)


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
