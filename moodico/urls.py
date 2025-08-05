from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static 

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

    path('upload_color_image/', views.upload_color_image, name='upload_color_image'), #색상 이미지 업로드
    path('recommend_by_color/', views.recommend_by_color, name='recommend_by_color'),  # 색상 추천
    path('search_product/', views.search_product, name='search_product'), # 제품 검색
    
    # 좋아요 API
    path('api/toggle_like/', views.toggle_product_like, name='toggle_product_like'),
    path('api/get_likes/', views.get_user_likes, name='get_user_likes'),
    path('liked_products/', views.liked_products_page, name='liked_products'),
]

# Enable media file serving (during development only)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
