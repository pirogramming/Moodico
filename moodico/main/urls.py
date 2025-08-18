from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'), #메인 페이지
    path('personalcolor/', views.personalcolor, name='personalcolor'), #퍼스널 컬러 페이지
    path('voting_api', views.voting_api, name='voting_api'), # 투표 기능 api
]
