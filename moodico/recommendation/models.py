from django.db import models

# Create your models here.
import uuid

class ToneTag(models.Model):
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]
    SUBTYPE_CHOICES = [
        ('bright', 'Bright'),
        ('light', 'Light'),
        ('deep', 'Deep'),
        ('soft', 'Soft'),
    ]
    id = models.CharField(max_length=225, primary_key=True, verbose_name="톤 태그 식별자")
    code = models.CharField(max_length=225, verbose_name="색상코드")  # 예: spring_bright
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, verbose_name="계절")
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES, verbose_name="색상 명도 유형")   

    def __str__(self):
        return self.code


# ------------------------------
# 추천 결과
# ------------------------------

class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="추천 식별자")
    product_shade = models.ForeignKey("products.ProductShade", on_delete=models.CASCADE, verbose_name="추천된 셰이드")
    analysis_result = models.ForeignKey("upload.AnalysisResult", on_delete=models.CASCADE, verbose_name="분석 결과")
    score = models.IntegerField(verbose_name="점수")
    rank = models.IntegerField(verbose_name="순위")

    def __str__(self):
        return f"{self.analysis_result.id} → {self.product_shade.shade_name} (rank {self.rank})"

    class Meta:
        ordering = ['rank', '-score']
