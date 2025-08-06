from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
# ------------------------------
# 제품 관련
# ------------------------------

class Brand(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="브랜드 식별자")
    name = models.CharField(max_length=100,unique=True, verbose_name="브랜드 명")
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="브랜드 식별자")
    name = models.CharField(max_length=100,unique=True, verbose_name="브랜드 명")

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="제품 식별자")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="브랜드")
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="제품 식별자")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="브랜드")
    name = models.CharField(max_length=255, verbose_name="제품 이름")
    category = models.CharField(max_length=255, verbose_name="제품 카테고리")
    url = models.URLField(null=True, blank=True, verbose_name="제품 링크") #urlfeild 사용
    price = models.PositiveIntegerField(null=True, blank=True, verbose_name="제품 가격") #음수 가격 예외
    category = models.CharField(max_length=255, verbose_name="제품 카테고리")
    url = models.URLField(null=True, blank=True, verbose_name="제품 링크") #urlfeild 사용
    price = models.PositiveIntegerField(null=True, blank=True, verbose_name="제품 가격") #음수 가격 예외
    external_code = models.CharField(max_length=255, null=True, blank=True, verbose_name="사이트별 제품코드")

    def __str__(self):
        return self.name


class ProductShade(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="제품 셰이드 식별자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shades", verbose_name="제품")
    tone_tag = models.ForeignKey("recommendation.ToneTag", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="톤 태그")
    hex = models.CharField(max_length=7, null=True, blank=True, verbose_name="색상 HEX")#헥사 코드 숫자에 따라 max_length = 6~7
    lab_l = models.FloatField(null=True, blank=True, verbose_name="명도(L)")
    lab_a = models.FloatField(null=True, blank=True, verbose_name="채도(G/R)")
    lab_b = models.FloatField(null=True, blank=True, verbose_name="채도(B/Y)")
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="제품 셰이드 식별자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shades", verbose_name="제품")
    tone_tag = models.ForeignKey("recommendation.ToneTag", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="톤 태그")
    hex = models.CharField(max_length=7, null=True, blank=True, verbose_name="색상 HEX")#헥사 코드 숫자에 따라 max_length = 6~7
    lab_l = models.FloatField(null=True, blank=True, verbose_name="명도(L)")
    lab_a = models.FloatField(null=True, blank=True, verbose_name="채도(G/R)")
    lab_b = models.FloatField(null=True, blank=True, verbose_name="채도(B/Y)")
    shade_name = models.CharField(max_length=255, verbose_name="셰이드 이름")

    def __str__(self):
        return f"{self.product.name} - {self.shade_name}"
    
# ------------------------------
# 좋아요 기능
# ------------------------------

class ProductLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="좋아요 식별자")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="사용자")  
    session_nickname = models.CharField(max_length=100, null=True, blank=True)
    product_id = models.CharField(max_length=255, verbose_name="제품 ID")
    product_name = models.CharField(max_length=255, verbose_name="제품명")
    product_brand = models.CharField(max_length=255, verbose_name="브랜드")
    product_price = models.CharField(max_length=100, verbose_name="가격")
    product_image = models.URLField(null=True, blank=True, verbose_name="제품 이미지")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 날짜")

    class Meta:
        unique_together = ['user', 'product_id']  # 같은 사용자가 같은 제품을 중복 좋아요 방지
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product_name}"