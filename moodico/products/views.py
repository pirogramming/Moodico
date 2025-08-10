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
from django.db import models
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
    
    # 찜한 제품들의 색상 정보 가져오기
    liked_products_with_colors = get_liked_products_color_info(liked_products)
    
    return render(request, 'products/liked_products.html', {
        'liked_products': liked_products,
        'liked_products_colors': json.dumps(liked_products_with_colors, ensure_ascii=False)
    })


def get_liked_products_color_info(liked_products):
    """찜한 제품들의 색상 정보를 가져오는 함수"""
    import json
    import os
    
    # 좌표 정보가 포함된 제품 데이터 로드
    json_path = os.path.join('static', 'data', 'products_clustered.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except FileNotFoundError:
        logger.error("products_clustered.json 파일을 찾을 수 없습니다.")
        return []
    
    # 제품명으로 매칭하여 색상 정보 추가
    products_with_colors = []
    
    for liked_product in liked_products:
        logger.info(f"찜한 제품 처리 중: {liked_product.product_name} (브랜드: {liked_product.product_brand})")
        # all_products.json에서 매칭되는 제품 찾기
        matching_product = None
        for product in all_products:
            # 제품명으로 매칭 (부분 일치도 허용)
            if (liked_product.product_name in product.get('name', '') or 
                product.get('name', '') in liked_product.product_name):
                matching_product = product
                break
        
        # 제품명으로 매칭이 안 되면 브랜드명으로도 시도
        if not matching_product:
            for product in all_products:
                if (liked_product.product_brand.lower() in product.get('brand', '').lower() or 
                    product.get('brand', '').lower() in liked_product.product_brand.lower()):
                    # 브랜드가 일치하면 제품명도 부분적으로 일치하는지 확인
                    if (liked_product.product_name.lower() in product.get('name', '').lower() or 
                        product.get('name', '').lower() in liked_product.product_name.lower()):
                        matching_product = product
                        break
        
        if matching_product:
            logger.info(f"제품 매칭 성공: {matching_product.get('name')} -> URL: {matching_product.get('url')}")
            products_with_colors.append({
                'id': liked_product.product_id,  # ProductLike의 product_id 사용
                'name': liked_product.product_name,
                'brand': liked_product.product_brand,
                'price': liked_product.product_price,
                'image': liked_product.product_image or matching_product.get('image', ''),
                'hex': matching_product.get('hex', '#cccccc'),
                'warmCool': matching_product.get('warmCool', 50),
                'lightDeep': matching_product.get('lightDeep', 50),
                'category': matching_product.get('category', 'Unknown'),
                'url': matching_product.get('url', '#')
            })
        else:
            logger.warning(f"제품 매칭 실패: {liked_product.product_name} (브랜드: {liked_product.product_brand})")
            # 매칭되지 않는 경우 기본값 사용
            products_with_colors.append({
                'id': liked_product.product_id,
                'name': liked_product.product_name,
                'brand': liked_product.product_brand,
                'price': liked_product.product_price,
                'image': liked_product.product_image,
                'hex': '#cccccc',  # 기본 회색
                'warmCool': 50,
                'lightDeep': 50,
                'category': 'Unknown',
                'url': '#'
            })
    
    return products_with_colors

from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

@require_POST
@login_or_kakao_required
def clear_likes(request):
    ProductLike.objects.all().delete()
    return JsonResponse({'success': True})


@require_http_methods(["GET"])
def get_product_like_count(request):
    """제품별 찜 개수 조회 API"""
    try:
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': '제품 ID가 필요합니다.'
            }, status=400)
        
        # 해당 제품의 총 찜 개수
        like_count = ProductLike.objects.filter(product_id=product_id).count()
        
        # 현재 사용자가 찜했는지 확인
        user = request.user if request.user.is_authenticated else None
        session_nickname = request.session.get("nickname")
        
        is_liked = False
        if user:
            is_liked = ProductLike.objects.filter(user=user, product_id=product_id).exists()
        elif session_nickname:
            is_liked = ProductLike.objects.filter(session_nickname=session_nickname, product_id=product_id).exists()
        
        return JsonResponse({
            'success': True,
            'like_count': like_count,
            'is_liked': is_liked
        })
        
    except Exception as e:
        logger.error(f"찜 개수 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


@require_http_methods(["GET"])
def get_multiple_products_like_info(request):
    """여러 제품의 찜 정보를 한 번에 조회하는 API"""
    try:
        product_ids = request.GET.getlist('product_ids[]')
        if not product_ids:
            return JsonResponse({
                'success': False,
                'message': '제품 ID 목록이 필요합니다.'
            }, status=400)
        
        # 현재 사용자 정보
        user = request.user if request.user.is_authenticated else None
        session_nickname = request.session.get("nickname")
        
        result = {}
        for product_id in product_ids:
            # 각 제품의 찜 개수
            like_count = ProductLike.objects.filter(product_id=product_id).count()
            
            # 현재 사용자가 찜했는지 확인
            is_liked = False
            if user:
                is_liked = ProductLike.objects.filter(user=user, product_id=product_id).exists()
            elif session_nickname:
                is_liked = ProductLike.objects.filter(session_nickname=session_nickname, product_id=product_id).exists()
            
            result[product_id] = {
                'like_count': like_count,
                'is_liked': is_liked
            }
        
        return JsonResponse({
            'success': True,
            'products': result
        })
        
    except Exception as e:
        logger.error(f"여러 제품 찜 정보 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


def get_top_liked_products(limit=10):
    """상위 찜 제품 조회 함수 - 전체 제품 데이터 기반"""
    import json
    import os
    from django.db.models import Count
    from collections import defaultdict
    
    # 전체 제품 데이터 로드
    json_path = os.path.join('static', 'data', 'all_products.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except FileNotFoundError:
        logger.error("all_products.json 파일을 찾을 수 없습니다.")
        return []
    
    # 제품명+브랜드별로 찜 개수 집계 (중복 제거)
    product_likes_summary = {}
    for item in ProductLike.objects.all():
        key = f"{item.product_brand}_{item.product_name}"
        if key not in product_likes_summary:
            product_likes_summary[key] = {
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_brand': item.product_brand,
                'product_price': item.product_price,
                'product_image': item.product_image,
                'like_count': 0
            }
        product_likes_summary[key]['like_count'] += 1
    
    # 전체 제품 리스트 생성
    products_with_likes = []
    
    # 1. 먼저 찜된 제품들 추가 (찜 개수 > 0)
    for product_data in product_likes_summary.values():
        products_with_likes.append(product_data)
    
    # 2. 찜되지 않은 제품들도 추가 (찜 개수 = 0)
    # JSON 파일의 제품들 중 찜되지 않은 것들 찾기
    existing_product_keys = set(f"{item['product_brand']}_{item['product_name']}" 
                               for item in product_likes_summary.values())
    
    for product in all_products:
        product_name = product.get('name', '')
        product_brand = product.get('brand', '')
        product_key = f"{product_brand}_{product_name}"
        
        if product_name and product_key not in existing_product_keys:
            products_with_likes.append({
                'product_id': product.get('id', product_name),
                'product_name': product_name,
                'product_brand': product_brand,
                'product_price': product.get('price', ''),
                'product_image': product.get('image', ''),
                'like_count': 0
            })
    
    # 찜 개수로 정렬 (찜 개수가 같으면 이름순)
    products_with_likes.sort(key=lambda x: (-x['like_count'], x['product_name']))
    
    return products_with_likes[:limit]


@require_http_methods(["GET"])
def product_ranking_api(request):
    """제품 랭킹 API"""
    try:
        limit = int(request.GET.get('limit', 10))
        top_products = get_top_liked_products(limit)
        
        return JsonResponse({
            'success': True,
            'products': top_products
        })
        
    except Exception as e:
        logger.error(f"제품 랭킹 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }, status=500)


def product_ranking_page(request):
    """제품 랭킹 페이지 뷰"""
    try:
        top_products = get_top_liked_products(10)
        
        return render(request, 'products/product_ranking.html', {
            'top_products': top_products
        })
        
    except Exception as e:
        logger.error(f"제품 랭킹 페이지 오류: {str(e)}")
        return render(request, 'products/product_ranking.html', {
            'top_products': [],
            'error_message': '랭킹 정보를 불러오는데 실패했습니다.'
        })