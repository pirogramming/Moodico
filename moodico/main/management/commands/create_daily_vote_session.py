from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from moodico.main.models import RankedProduct, VotingSession
from moodico.products.utils import get_top_liked_products

# 매일 자정, 현재의 랭킹 최상위 두 개 제품으로 투표 세션을 생성하는 함수
class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(f"[{timezone.now()}] 투표 세션 생성 시작")

        active_sessions = VotingSession.objects.filter(is_active=True)
        if active_sessions.exists():
            updated_count = active_sessions.update(is_active=False, end_time=timezone.now())
            self.stdout.write(self.style.WARNING(f"{updated_count}개의 기존 활성 세션을 종료했습니다."))
        
        try:
            ranked1_data, ranked2_data = get_top_liked_products(2)
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR("상위 2개 제품을 가져오는 데 실패했습니다. 작업을 중단합니다."))
            return

        # 가져온 데이터로 Product 객체 생성 및 업데이트
        product1, created1 = RankedProduct.objects.update_or_create(
            product_id=ranked1_data["product_id"],
            defaults={
                'name': ranked1_data["product_name"],
                'brand': ranked1_data["product_brand"],
                'price': ranked1_data["product_price"],
                'image_url': ranked1_data["product_image"],
                'like_count': ranked1_data["like_count"]
            }
        )
        if created1:
            self.stdout.write(f"새로운 제품 '{product1.name}'이 랭킹 1위로 투표 대상 객체가 생성")
        
        product2, created2 = RankedProduct.objects.update_or_create(
            product_id=ranked2_data["product_id"],
            defaults={
                'name': ranked2_data["product_name"],
                'brand': ranked2_data["product_brand"],
                'price': ranked2_data["product_price"],
                'image_url': ranked2_data["product_image"],
                'like_count': ranked2_data["like_count"]
            }
        )
        if created2:
            self.stdout.write(f"새로운 제품 '{product2.name}'이 랭킹 2위로 투표 대상 객체가 생성")

        # 투표 세션 생성
        new_session = VotingSession.objects.create(
            product1=product1,
            product2=product2
        )

        self.stdout.write(self.style.SUCCESS(
            f"새로운 투표 세션(ID: {new_session.id})을 생성했습니다: '{product1.name}' vs '{product2.name}'"
        ))