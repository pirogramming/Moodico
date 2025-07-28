from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'), #메인 페이지
    path('login/', views.login_view, name='login'), #로그인 페이지
    path('signup/', views.signup_view, name='signup'), #회원가입
    path('my_item_recommendation/', views.my_item_recommendation, name='my_item_recommendation'), #내 아이템 기반 추천 페이지
    path('mood_test/', views.mood_test, name='mood_test'), #무드 테스트 페이지
    path('mood_result/', views.mood_result, name='mood_result'), #무드 테스트 결과 페이지
    path('color_matrix_explore/', views.color_matrix_explore, name='color_matrix_explore'), #색상 매트릭스
    path('product/<int:product_id>/', views.product_detail, name='product_detail'), #제품 상세 페이지
]