from django.shortcuts import render,redirect
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
    # 무드 테스트 결과 데이터 (백엔드에서 받아올 예정)
    """무드 테스트 결과 페이지 뷰"""
    mood_data = {
        'mood_name': '로맨틱',
        'mood_description': '부드럽고 여성스러운 사랑스러운 느낌',
        'colors': ['#FEEBEB', '#FFD2CC', '#FFB7B3'],
        'tags': ['#soft', '#feminine', '#pink', '#shimmer'],
        'recommended_products': [
            {'type': '립스틱', 'image': '/static/images/test.jpg', 'brand': 'ETUDE HOUSE', 'product_name': '코랄 틴트 립', 'price': '12,000원', 'rating': '4.0', 'review_count': '123'},
            {'type': '블러셔', 'image': '/static/images/test.jpg', 'brand': 'PERIPERA', 'product_name': '글로우 체크 블러셔', 'price': '18,000원', 'rating': '4.0', 'review_count': '456'},
            {'type': '아이쉐도우', 'image': '/static/images/test.jpg', 'brand': 'INNISFREE', 'product_name': '내추럴 아이쉐도우', 'price': '22,000원', 'rating': '4.0', 'review_count': '789'},
        ]
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
