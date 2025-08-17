from django.db import models
from django.utils import timezone

# Create your models here.
class RankedProduct(models.Model):
    product_id = models.CharField(max_length=100, unique=True, db_index=True) # 제품 id
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    image_url = models.CharField(max_length=500)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.brand}] {self.name}"

class VotingSession(models.Model):
    """
    하나의 투표 세션 - 24시간 간격으로 생성
    """
    #session_id = 
    product1 = models.ForeignKey(RankedProduct, on_delete=models.CASCADE, related_name='product1_sessions')
    product2 = models.ForeignKey(RankedProduct, on_delete=models.CASCADE, related_name='product2_sessions')
    product1_votes = models.PositiveIntegerField(default=0)
    product2_votes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    winner = models.ForeignKey(RankedProduct, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_sessions')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "Active" if self.is_active else "Finished"
        return f"Session {self.id}: {self.product1.name} vs {self.product2.name} ({status})"
    
    # session is_active false 변경 함수
    def close_session(self):
        self.end_time = timezone.now()
        self.is_active = False

        if self.product1_votes > self.product2_votes:
            self.winner = self.product1
        elif self.product2_votes > self.product1_votes:
            self.winner = self.product2
        
        self.save()