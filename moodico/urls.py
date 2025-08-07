# moodico/urls.py
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('', include('moodico.main.urls')), # 메인
    path('upload/', include('moodico.upload.urls')),  # 이미지 업로드
    path('recommend/', include('moodico.recommendation.urls')), # 추천 관련 URL
    path('products/', include('moodico.products.urls')), # 제품 관련 URL
    path('moodtest/', include('moodico.moodtest.urls')), # 무드 테스트
    path('users/', include('moodico.users.urls')), # 유저 관련 URL
]

# Enable media file serving (during development only)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)