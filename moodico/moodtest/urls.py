# moodico/moodtest/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mood_test, name='mood_test'), #무드 테스트 페이지
    path('mood_result/', views.mood_result, name='mood_result'), #무드 테스트 결과 페이지
]
