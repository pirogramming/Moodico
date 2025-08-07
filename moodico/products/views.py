from django.shortcuts import render
import json
import os
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from moodico.products.models import ProductLike
import logging
logger = logging.getLogger(__name__)
from moodico.users.utils import login_or_kakao_required

# Create your views here.

def color_matrix_explore(request):
    """색상 매트릭스 페이지 뷰"""
    product_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
    with open(product_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    return render(request, 'recommendation/color_matrix.html', {'makeupProducts': products})

def product_detail(request, product_id):
    """제품 상세 페이지 뷰"""
    # 제품 상세 정보 (백엔드에서 받아올 예정)
    product = {
        'id': product_id,
        'name': f'제품 {product_id}',
        'description': '이 제품은 아주 좋은 제품입니다.',
        'price': '30,000원',
        'image': '/static/images/test.jpg', # 임시 이미지
    }
    return render(request, 'products/detail.html', {'product': product})

def product_list(request):
    json_path = os.path.join('static', 'data', 'products.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    return render(request, 'products/product_list.html', {'products': products})

# DB 구현 이후 검색 로직 수정 필요 - 현재는 검색시마다 json 파일을 매번 불러오고 있음
## 현재는 단어 단위의 검색만 가능.. (제품 데이터를 밑에 표시함으로써 이 문제 완화 가능) 
## 만일 사용자가 "조선무화과"를 검색한다면 "조선 무화과" 검색어는 서치에 걸리지 않음("조선", "무화과"는 정상적으로 검색 가능)
def search_product(request):
    query = request.GET.get('q', '').lower().strip()
    query_words = query.split()

    product_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
    with open(product_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    def normalize(text):
        text = text.lower()
        return text
    
    filtered = []
    for p in products:
        search_for = normalize(p['brand'] + ' - ' + p['name'])
        if all(word in search_for for word in query_words):
            filtered.append(p)

    return JsonResponse({'results':filtered})

@csrf_exempt
@require_http_methods(["POST"])
def toggle_product_like(request):
    """제품 좋아요 토글 API"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_brand = data.get('product_brand')
        product_price = data.get('product_price')
        product_image = data.get('product_image', '')
        
        if not all([product_id, product_name, product_brand, product_price]):
            return JsonResponse({
                'success': False,
                'message': '필수 제품 정보가 누락되었습니다.'
            }, status=400)
        
        # 사용자 확인 (임시로 세션 기반)
        user = request.user if request.user.is_authenticated else None
        session_nickname = request.session.get("nickname")
        if not user and not session_nickname:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            }, status=401)
        
        # 기존 좋아요 확인
        like_filter = ProductLike.objects.filter(product_id=product_id)
        if user:
            like_filter = like_filter.filter(user=user)
        else:
            like_filter = like_filter.filter(session_nickname=session_nickname)

        existing_like = like_filter.first()
        
        if existing_like:
            # 좋아요 취소
            existing_like.delete()
            is_liked = False
            message = '좋아요가 취소되었습니다.'
        else:
            # 좋아요 추가
            ProductLike.objects.create(
                user=user,
                session_nickname=session_nickname if not user else None,
                product_id=product_id,
                product_name=product_name,
                product_brand=product_brand,
                product_price=product_price,
                product_image=product_image
            )
            is_liked = True
            message = '좋아요에 추가되었습니다! 💖'
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        logger.error(f"좋아요 토글 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_user_likes(request):
    """사용자의 좋아요 목록 조회 API"""
    try:
        # 사용자 확인
        user = request.user if request.user.is_authenticated else None
        if not user:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.',
                'likes': []
            }, status=401)
        
        # 사용자의 좋아요 목록 조회
        likes = ProductLike.objects.filter(user=user).values(
            'product_id', 'product_name', 'product_brand', 
            'product_price', 'product_image', 'created_at'
        )
        
        return JsonResponse({
            'success': True,
            'likes': list(likes)
        })
        
    except Exception as e:
        logger.error(f"좋아요 목록 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


def liked_products_page(request):
    """찜한 아이템 페이지 뷰"""
    # 사용자 확인
    user = request.user if request.user.is_authenticated else None
    if not user:
        return redirect('login')
    
    # 사용자의 좋아요 목록 조회
    liked_products = ProductLike.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'products/liked_products.html', {
        'liked_products': liked_products
    })

from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

@require_POST
@login_or_kakao_required
def clear_likes(request):
    ProductLike.objects.all().delete()
    return JsonResponse({'success': True})