# moodico/users/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
# class UserProfile(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="유저 프로필 식별자")
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles', verbose_name="유저")
#     default_tone_tag = models.ForeignKey('recommendation.ToneTag', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="기본 톤 태그")
    
#     created_at = models.DateTimeField(auto_now_add=True,verbose_name="프로필 생성 날짜")
#     updated_at = models.DateTimeField(auto_now=True,verbose_name="프로필 업데이트 날짜")
    
#     notes = models.TextField(null=True, blank=True, verbose_name="노트")
#     color_type = models.CharField(max_length=225, null=True, blank=True, verbose_name="컬러 타입")

#     def __str__(self):
#         return f"{self.user.username}의 프로필 ({self.id})"

# # 현재 모델에는 "사용자가 어떤 방식으로 추천을 받았는지"에 대한 정보가 없음
# # → 분석이나 개인화가 어려워져요. 지피티가 이렇다는데 추천 받는거 구체화 한다음에 더 생각해봐야 될거 같습니다.


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="유저 프로필 식별자")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles', verbose_name="유저")    
    mood_result = models.CharField(max_length=50, null=True, blank=True, verbose_name="무드 테스트 결과")

    def __str__(self):
        return f"{self.user.username}의 프로필 ({self.id})"