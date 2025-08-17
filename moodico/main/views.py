from django.shortcuts import render
from moodico.products.views import get_top_liked_products
from moodico.products.models import ProductLike
import random
from .models import RankedProduct, VotingSession

# Create your views here.

def main(request):
    """메인 페이지 뷰"""
    # 상위 3개의 인기 제품만 메인페이지에 표시
    top_liked_products = get_top_liked_products(3)
    
    # 오늘의 추천 제품 선택
    recommended_product = None
    
    if request.user.is_authenticated:
        # 로그인한 사용자의 경우: 찜한 제품 중 랜덤 선택
        user_liked_products = ProductLike.objects.filter(user=request.user)
        if user_liked_products.exists():
            # 찜한 제품이 있으면 랜덤으로 하나 선택
            random_like = random.choice(user_liked_products)
            recommended_product = {
                'product_name': random_like.product_name,
                'product_brand': random_like.product_brand,
                'product_image': random_like.product_image,
                'like_count': 1,  # 사용자가 찜한 제품이므로 1
                'is_user_liked': True
            }
    
    if not recommended_product:
        # 사용자가 찜한 제품이 없거나 비로그인인 경우: 인기 제품 중 랜덤 선택
        if top_liked_products:
            random_product = random.choice(top_liked_products)
            recommended_product = {
                'product_name': random_product['product_name'],
                'product_brand': random_product['product_brand'],
                'product_image': random_product['product_image'],
                'like_count': random_product['like_count'],
                'is_user_liked': False
            }
        else:
            # 아무 제품도 없는 경우 기본값
            recommended_product = {
                'product_name': '추천 제품 준비 중',
                'product_brand': '',
                'product_image': '/static/images/test.jpg',
                'like_count': 0,
                'is_user_liked': False
            }
    
    # 오늘의 투표 데이터베이스 전달
    session = VotingSession.objects.filter(is_active=True).first()

    session_id = session.id
    session_vote_count = session.product1_votes + session.product2_votes
    voting_data = {
        'product1': {
            #'id': session.product1.id,
            'product_id': session.product1.product_id,
            'product_name': session.product1.name,
            'product_brand': session.product1.brand,
            'image_url': session.product1.image_url,
            'like_count': session.product1.like_count,
            'votes': session.product1_votes
        },
        'product2': {
            #'id': session.product2.id,
            'product_id': session.product2.product_id,
            'product_name': session.product2.name,
            'product_brand': session.product2.brand,
            'image_url': session.product2.image_url,
            'like_count': session.product2.like_count,
            'votes': session.product2_votes
        }
    }

    
    return render(request, 'main/main.html', {
        'top_liked_products': top_liked_products,
        'recommended_product': recommended_product,
        'session_id': session_id,
        'session_vote_count': session_vote_count,
        'voting_data': voting_data,
    })