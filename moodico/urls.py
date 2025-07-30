from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.main, name='main'), #메인 페이지
    path('signup/', views.signup_view, name='signup'), #회원가입
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path("authorize/", views.kakao_authorize, name="kakao_authorize"), # 카카오 로그인 인증
    path("kakao/callback/", views.kakao_callback, name="kakao_callback"),  # 카카오 로그인 콜백
    path("profile/", views.kakao_profile, name="kakao_profile"), # 카카오 프로필 정보 가져오기
    path("kakao_logout/", views.kakao_logout, name="kakao_logout"), # 카카오 로그아웃

    path('my_item_recommendation/', views.my_item_recommendation, name='my_item_recommendation'), #내 아이템 기반 추천 페이지
    path('mood_test/', views.mood_test, name='mood_test'), #무드 테스트 페이지
    path('mood_result/', views.mood_result, name='mood_result'), #무드 테스트 결과 페이지
    path('color_matrix_explore/', views.color_matrix_explore, name='color_matrix_explore'), #색상 매트릭스
    path('product/<int:product_id>/', views.product_detail, name='product_detail'), #제품 상세 페이지
    path('products/', views.product_list, name='product_list'),
    path('products_list/', views.product_list, name='products_list'),
]