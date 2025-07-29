from django.db import models

class Brand(models.Model):
    id = models.CharField(primary_key=True, max_length=225, verbose_name="브랜드 식별자")
    name = models.CharField(max_length=225, verbose_name="브랜드 명")

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=225, verbose_name="제품 식별자")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="브랜드", related_name="products")
    name = models.CharField(max_length=255, verbose_name="제품 이름")
    category = models.CharField(max_length=255, verbose_name="제품 카테고리")  # ex. 립, 블러셔, 섀도우
    url = models.TextField(null=True, blank=True, verbose_name="제품 링크")
    price = models.IntegerField(null=True, blank=True, verbose_name="제품 가격")
    external_code = models.CharField(max_length=255, null=True, blank=True, verbose_name="사이트별 제품코드")

    def __str__(self):
        return self.name


class ProductShade(models.Model):
    id = models.CharField(primary_key=True, max_length=225, verbose_name="제품 셰이드 식별자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="제품", related_name="shades")
    tone_tag_id = models.CharField(max_length=225, null=True, blank=True, verbose_name="톤 태그 ID")

    hex = models.CharField(max_length=225, null=True, blank=True, verbose_name="색상 HEX")
    lab_l = models.FloatField(null=True, blank=True, verbose_name="명도(L)")  # 0~100
    lab_a = models.FloatField(null=True, blank=True, verbose_name="채도(G/R)")  # 초록(−) ~ 빨강(+)
    lab_b = models.FloatField(null=True, blank=True, verbose_name="채도(B/Y)")  # 파랑(−) ~ 노랑(+)

    shade_name = models.CharField(max_length=255, verbose_name="셰이드 이름")

    def __str__(self):
        return f"{self.product.name} - {self.shade_name}"
