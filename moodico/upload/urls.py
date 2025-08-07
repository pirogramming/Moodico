#moodico/upload/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload_color_image/', views.upload_color_image, name='upload_color_image'), #색상 이미지 업로드
    path('proxy_image/', views.proxy_image, name='proxy_image'), # 검색한 제품 이미지 불러오기
]
