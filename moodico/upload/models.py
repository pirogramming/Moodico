from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
# ------------------------------
# 업로드 및 분석 결과
# ------------------------------

class Upload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="업로드 식별자")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="유저")
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('done', '완료'),
        ('fail', '실패'),
    ]
    status = models.CharField(max_length=225, default='pending', verbose_name="상태")  # pending, done, fail 등
    
    image_path = models.ImageField(
    upload_to='uploads/',  # 업로드 된 이미지가 저장될 폴더 경로 지정
    verbose_name="이미지 경로"  # 관리자 페이지 등에서 표시할 필드 이름 지정
    )

    def __str__(self):
        return f"{self.user.username} 업로드 - {self.id}"

class AnalysisResult(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="분석 결과 식별자")
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, verbose_name="업로드")
    tone_tag = models.ForeignKey("recommendation.ToneTag", on_delete=models.CASCADE, verbose_name="톤 태그")
    primary_hex = models.CharField(max_length=225, verbose_name="대표 HEX")
    palette_json = models.JSONField(verbose_name="팔레트 JSON")

    def __str__(self):
        return f"분석 결과 - {self.id}"


class PaletteColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="팔레트 컬러 식별자")
    analysis_result = models.ForeignKey("upload.AnalysisResult", on_delete=models.CASCADE, related_name='palette_colors', verbose_name="분석 결과")
    hex = models.CharField(max_length=7, verbose_name="HEX") #헥사 코드 숫자에 따라 max_length = 6~7
    lab_l = models.FloatField(verbose_name="명도(L)")
    lab_a = models.FloatField(verbose_name="채도(G/R)")
    lab_b = models.FloatField(verbose_name="채도(B/Y)")
    sort_order = models.IntegerField(verbose_name="정렬 순서")

    def __str__(self):
        return self.hex

    class Meta:
        ordering = ['sort_order'] #쿼리할 때, 자동으로 ORDER BY sort_order ASC가 적용된 것처럼 결과가 정렬 -> .filter(...)만 해도 sort_order 기준으로 오름차순 정렬된 결과

        # 헥사 값의 색깔이나 순서의 중복을 조정하고 싶으면 아래 코드 사용
        # unique_together = [
        # ['analysis_result', 'hex'],
        # ['analysis_result', 'sort_order']
        # ]