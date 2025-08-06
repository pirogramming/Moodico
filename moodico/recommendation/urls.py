# moodico/recommendation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('my_item_recommendation/', views.my_item_recommendation, name='my_item_recommendation'), #내 아이템 기반 추천 페이지
    path('recommend_by_color/', views.recommend_by_color, name='recommend_by_color'),  # 색상 추천
]
