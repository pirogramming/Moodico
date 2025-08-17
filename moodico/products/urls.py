# moodico/products/urls.py
from django.urls import path
from . import views
from .views import product_ranking_page

urlpatterns = [
    path('color_matrix_explore/', views.color_matrix_explore, name='color_matrix_explore'), #색상 매트릭스
    path('<int:product_id>/', views.product_detail, name='product_detail'), #제품 상세 페이지
    path('detail/<str:crawled_id>/', views.crawled_product_detail, name='crawled_product_detail'), #크롤링된 제품 상세 페이지
    path('', views.product_list, name='product_list'),
    path('products_list/', views.product_list, name='products_list'),
    path('search_product/', views.search_product, name='search_product'), # 제품 검색
    path('liked_products/', views.liked_products_page, name='liked_products'),
    path('toggle_product_like/', views.toggle_product_like, name='toggle_product_like'),
    path('get_user_likes/', views.get_user_likes, name='get_user_likes'),
    path('like_count/', views.get_product_like_count, name='get_product_like_count'),
    path('multiple_like_info/', views.get_multiple_products_like_info, name='get_multiple_products_like_info'),
    path('ranking/', views.product_ranking_page, name='product_ranking'),
    path('ranking/api/', views.product_ranking_api, name='product_ranking_api'),
    
    # 별점 관련 URL
    path('submit_rating/', views.submit_product_rating, name='submit_product_rating'),
    path('get_rating/', views.get_product_rating, name='get_product_rating'),
    path('get_ratings_list/', views.get_product_ratings_list, name='get_product_ratings_list'),
    path('delete_review_image/<uuid:image_id>/', views.delete_review_image, name='delete_review_image'), # 리뷰 이미지 삭제
    path('delete_rating/<str:product_id>/', views.delete_product_rating, name='delete_product_rating'), # 리뷰 별점 글 삭제
]