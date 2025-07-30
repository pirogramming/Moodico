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
def compare_color(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            hex_color = body.get("hex")  # e.g. "#E3B49E"

            if not hex_color or not hex_color.startswith("#") or len(hex_color) != 7:
                return JsonResponse({"error": "Invalid HEX color format."}, status=400)

            # Convert HEX to RGB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            rgb = np.array([[[r, g, b]]]) / 255.0
            lab = rgb2lab(rgb)[0][0]  # [L, a, b]

            # Load product JSON
            json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'romand_products_enhanced.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                products = json.load(f)

            # Compute LAB distance
            def lab_distance(p):
                try:
                    return np.linalg.norm([
                        lab[0] - p["lab_l"],
                        lab[1] - p["lab_a"],
                        lab[2] - p["lab_b"]
                    ])
                except KeyError:
                    return float('inf')

            recommended = sorted(products, key=lab_distance)[:6]

            return JsonResponse({"recommended": recommended}, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


