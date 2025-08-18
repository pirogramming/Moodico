from django.shortcuts import render,redirect
from moodico.users.forms import CustomSignupForm
from django.contrib.auth import login
import requests
from django.http import HttpRequest
from django.conf import settings
from django.views.decorators.http import require_http_methods
from moodico.products.models import ProductLike, ProductRating
from .utils import login_or_kakao_required
from moodico.users.models import UserProfile
from moodico.products.views import get_liked_products_color_info
from django.contrib.auth.models import User
import secrets

# Create your views here.
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
    return render(request, 'users/signup.html', {'form': form})

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
        return redirect("/?logout=fail")

    # 사용자 정보 요청
    profile_url = f"{settings.KAKAO_API_HOST}/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()

    # 닉네임, 프로필 이미지 가져오기
    nickname = profile_data.get("properties", {}).get("nickname")
    profile_image = profile_data.get("properties", {}).get("profile_image")

    kakao_id = profile_data.get("id")
    email = profile_data.get("kakao_account", {}).get("email")  # optional email field

    # Django User username must be unique, so prepend something like 'kakao_'
    username = f'kakao_{kakao_id}'

    # Get or create Django User
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email or '',
            'first_name': nickname or '',
            'password': secrets.token_urlsafe(12)
        }
    )

    # create or update UserProfile for kakao users
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Log the user in
    login(request, user)

    request.session["access_token"] = access_token
    request.session["nickname"] = nickname
    request.session["profile_image"] = profile_image

    return redirect("main")



def kakao_profile(request):
    access_token = request.session.get("access_token")

    if not access_token:
        return redirect("/?logout=fail")

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

    return render(request, "main/main.html", context)

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

@login_or_kakao_required
def profile(request):
    if request.user.is_authenticated:
        display_name = request.user.first_name or request.user.username
    else:
        display_name = request.session.get("nickname", "게스트")
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_mood = user_profile.mood_result if user_profile.mood_result else "정보 없음"
    except UserProfile.DoesNotExist:
        user_mood = "정보 없음"
    
    liked_products = ProductLike.objects.filter(user=request.user).order_by('-created_at')
    
    # 사용자가 작성한 리뷰들 가져오기
    user_reviews = ProductRating.objects.filter(user=request.user).order_by('-created_at')

    # 찜한 제품들의 색상 및 URL 정보 가져오기
    liked_products_colors = get_liked_products_color_info(liked_products)

    context = {
        'user_name': display_name,
        'user_mood': user_mood,
        'liked_products': liked_products,
        'liked_products_colors': liked_products_colors,
        'user_reviews': user_reviews,
    }

    return render(request, 'users/profile.html', context)