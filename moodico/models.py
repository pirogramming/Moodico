import uuid
# 몇몇 id를 charField보다 autoFeilf, uuidfield쓰면 좋을거 같은데 이미지 서버도 사용할 수 있을거 같아서 uuidfield 사용이 적합해보임


import uuid
from django.db import models
from django.contrib.auth.models import User


# ------------------------------
# 사용자 관련
# ------------------------------

# Django의 기본 User 모델을 사용할 거여서 지워됬습니다
# class User(models.Model):
#     user = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="유저 식별자")
#     username = models.CharField(max_length=225, verbose_name="유저 이름")
#     email = models.EmailField(max_length=225, verbose_name="이메일")
#     date_join = models.DateTimeField(verbose_name="가입날짜")

#     def __str__(self):
#         return self.username


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

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="유저 프로필 식별자")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles', verbose_name="유저")
    default_tone_tag = models.ForeignKey('ToneTag', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="기본 톤 태그")
    
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="프로필 생성 날짜")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="프로필 업데이트 날짜")
    
    notes = models.TextField(null=True, blank=True, verbose_name="노트")
    color_type = models.CharField(max_length=225, null=True, blank=True, verbose_name="컬러 타입")

    def __str__(self):
        return f"{self.user.username}의 프로필 ({self.id})"

# 현재 모델에는 "사용자가 어떤 방식으로 추천을 받았는지"에 대한 정보가 없음
# → 분석이나 개인화가 어려워져요. 지피티가 이렇다는데 추천 받는거 구체화 한다음에 더 생각해봐야 될거 같습니다.



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
    tone_tag = models.ForeignKey(ToneTag, on_delete=models.CASCADE, verbose_name="톤 태그")
    primary_hex = models.CharField(max_length=225, verbose_name="대표 HEX")
    palette_json = models.JSONField(verbose_name="팔레트 JSON")

    def __str__(self):
        return f"분석 결과 - {self.id}"


class PaletteColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="팔레트 컬러 식별자")
    analysis_result = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='palette_colors', verbose_name="분석 결과")
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
    tone_tag = models.ForeignKey(ToneTag, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="톤 태그")
    hex = models.CharField(max_length=7, null=True, blank=True, verbose_name="색상 HEX")#헥사 코드 숫자에 따라 max_length = 6~7
    lab_l = models.FloatField(null=True, blank=True, verbose_name="명도(L)")
    lab_a = models.FloatField(null=True, blank=True, verbose_name="채도(G/R)")
    lab_b = models.FloatField(null=True, blank=True, verbose_name="채도(B/Y)")
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="제품 셰이드 식별자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shades", verbose_name="제품")
    tone_tag = models.ForeignKey(ToneTag, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="톤 태그")
    hex = models.CharField(max_length=7, null=True, blank=True, verbose_name="색상 HEX")#헥사 코드 숫자에 따라 max_length = 6~7
    lab_l = models.FloatField(null=True, blank=True, verbose_name="명도(L)")
    lab_a = models.FloatField(null=True, blank=True, verbose_name="채도(G/R)")
    lab_b = models.FloatField(null=True, blank=True, verbose_name="채도(B/Y)")
    shade_name = models.CharField(max_length=255, verbose_name="셰이드 이름")

    def __str__(self):
        return f"{self.product.name} - {self.shade_name}"


# ------------------------------
# 추천 결과
# ------------------------------

class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="추천 식별자")
    product_shade = models.ForeignKey(ProductShade, on_delete=models.CASCADE, verbose_name="추천된 셰이드")
    analysis_result = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, verbose_name="분석 결과")
    score = models.IntegerField(verbose_name="점수")
    rank = models.IntegerField(verbose_name="순위")

    def __str__(self):
        return f"{self.analysis_result.id} → {self.product_shade.shade_name} (rank {self.rank})"

    class Meta:
        ordering = ['rank', '-score']


# ------------------------------
# 좋아요 기능
# ------------------------------

class ProductLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="좋아요 식별자")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
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