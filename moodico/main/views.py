from django.shortcuts import render
from moodico.products.views import get_top_liked_products
from moodico.products.models import ProductLike
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import F
from .models import Vote, VotingSession, RankedProduct
from django.contrib.auth.decorators import login_required
from django.urls import reverse

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
    session_id = None
    session_vote_count = None
    voting_data = None

    if session:
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
    
    # 지난 세션 투표 결과 정보 받아오기
    previous_session = VotingSession.objects.filter(is_active=False).order_by('-end_time').first()
    
    previous_session_data = None
    if previous_session:
        total_votes = previous_session.product1_votes + previous_session.product2_votes
        if total_votes > 0:
            p1_percentage = round((previous_session.product1_votes / total_votes) * 100)
            p2_percentage = round((previous_session.product2_votes / total_votes) * 100)
        else:
            p1_percentage = p2_percentage = 0
        
        if previous_session.winner:
            previous_session_data = {
                'winner_name': previous_session.winner.name,
                'winner_brand': previous_session.winner.brand,
                'winner_url': reverse('crawled_product_detail', kwargs={'crawled_id': previous_session.winner.product_id}),
                'winner_image_url': previous_session.winner.image_url,
                'is_draw': False,
            }
        else:
            previous_session_data = {
                'winner_name': '무승부',
                'is_draw': True,
            }
        
        # 공통데이터
        previous_session_data.update({
            'product1_name': previous_session.product1.name,
            'product2_name': previous_session.product2.name,
            'product1_percentage': p1_percentage,
            'product2_percentage': p2_percentage,
            'product1_url': reverse('crawled_product_detail', kwargs={'crawled_id': previous_session.product1.product_id}),
            'product2_url': reverse('crawled_product_detail', kwargs={'crawled_id': previous_session.product2.product_id}),
        })

    
    return render(request, 'main/main.html', {
        'top_liked_products': top_liked_products,
        'recommended_product': recommended_product,
        'session_id': session_id,
        'session_vote_count': session_vote_count,
        'voting_data': voting_data,
        'previous_session_data': previous_session_data,
        'is_user_logged_in': request.user.is_authenticated,
    })

def personalcolor(request):
    """퍼스널 컬러 페이지 뷰"""
    return render(request, 'personalcolor/personalcolor.html')

# 사용자의 투표 정보를 받는 api
@login_required # 로그인한 사용자만 투표 가능
@require_POST
def voting_api(request):
    try:
        session_id = request.POST.get('session_id')
        product_id = request.POST.get('product_id')
        user = request.user

        session = VotingSession.objects.get(id=session_id, is_active=True)
        product_to_vote = RankedProduct.objects.get(product_id=product_id)

        # 사용자의 이 세션에 대한 투표 기록이 있다면 업데이트, 없다면 생성
        Vote.objects.update_or_create(
            user=user, 
            session=session,
            defaults={'voted_product': product_to_vote}
        )

        # 전체 득표수 계산
        session.product1_votes = Vote.objects.filter(session=session, voted_product=session.product1).count()
        session.product2_votes = Vote.objects.filter(session=session, voted_product=session.product2).count()
        session.save()

        return JsonResponse({
            'status': 'success',
            'product1_votes': session.product1_votes,
            'product2_votes': session.product2_votes,
            'user_voted_for': product_to_vote.product_id # 사용자가 최종 선택한 제품 ID
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)