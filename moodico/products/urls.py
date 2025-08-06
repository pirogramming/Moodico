# moodico/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('color_matrix_explore/', views.color_matrix_explore, name='color_matrix_explore'), #색상 매트릭스
    path('<int:product_id>/', views.product_detail, name='product_detail'), #제품 상세 페이지
    path('', views.product_list, name='product_list'),
    path('products_list/', views.product_list, name='products_list'),
    path('search_product/', views.search_product, name='search_product'), # 제품 검색
    path('liked_products/', views.liked_products_page, name='liked_products'),
    path('toggle_product_like/', views.toggle_product_like, name='toggle_product_like'),
    path('get_user_likes/', views.get_user_likes, name='get_user_likes'),
]