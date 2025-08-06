from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'), #회원가입
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path("authorize/", views.kakao_authorize, name="kakao_authorize"), # 카카오 로그인 인증
    path("kakao/callback/", views.kakao_callback, name="kakao_callback"),  # 카카오 로그인 콜백
    path("kakao_logout/", views.kakao_logout, name="kakao_logout"), # 카카오 로그아웃

    path('profile/', views.profile, name='profile') #유저 프로필 페이지 
]
