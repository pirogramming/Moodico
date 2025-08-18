from django.shortcuts import render
import json
import os
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Product

from moodico.products.models import ProductLike, ProductRating, ProductRatingImage
from django.db import models
import logging
logger = logging.getLogger(__name__)
from moodico.users.utils import login_or_kakao_required
from moodico.products.utils.common_utils import get_top_liked_products

# Create your views here.
def color_matrix_explore(request):
    """색상 매트릭스 페이지 뷰"""
    # 로그인이 되어있다면, 찜한 제품 정보 불러오기
    liked_product_ids = set()
    if request.user.is_authenticated:
        liked_product_ids = set(ProductLike.objects.filter(user=request.user).values_list('product_id', flat=True))

    static_cluster = os.path.join(settings.BASE_DIR, 'static','data', 'products_clustered.json')
    static_all = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')

    product_path = None
    if os.path.exists(static_cluster):
        product_path = static_cluster
    else:
        product_path = static_all  

    with open(product_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    # 찜 여부 추가
    for product in products:
        product['is_liked'] = product.get('id') in liked_product_ids

    return render(request, 'recommendation/color_matrix.html', {'makeupProducts': products})
from django.templatetags.static import static
def product_detail(request, product_id):
    """제품 상세 페이지 뷰"""
    # 제품 상세 정보 (백엔드에서 받아올 예정)
    product = {
        'id': product_id,
        'name': f'제품 {product_id}',
        'description': '이 제품은 아주 좋은 제품입니다.',
        'price': '30,000원',
        'image': static('images/test.jpg')
    }
    return render(request, 'products/detail.html', {'product': product})

def crawled_product_detail(request, crawled_id):
    """크롤링된 제품 상세 페이지 뷰"""
    try:
        logger.info(f"크롤링된 제품 상세 페이지 요청: crawled_id = {crawled_id}")
        
        # products_clustered.json에서 제품 정보 찾기
        product_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')
        
        with open(product_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
                
        # crawled_id로 제품 찾기
        product = None
        
        for p in products:
            if p.get('id') == crawled_id:
                product = p
                break
        print('...',crawled_id)
        product_id = product['id']
        # 모든 리뷰
        all_reviews = ProductRating.objects.filter(product_id=crawled_id).order_by('-created_at')
        # 유저 리뷰
        from moodico.users.utils import get_user_from_request
        user = get_user_from_request(request)
        if user:
            user_review = all_reviews.filter(user=user).first()
        else:
            user_review = None
        # ratings 총수
        total_ratings = all_reviews.count()
        # average ratings 총수 
        from django.db.models import Avg
        average_rating = all_reviews.aggregate(avg=Avg('rating')).get('avg') or 0
        average_rating = round(average_rating, 2)

        context = {
            'product': product,
            'user_review': user_review,
            'all_reviews': all_reviews,
            'user': user,
            'total_ratings': total_ratings,
            'average_rating': average_rating,
        }
        
        return render(request, 'products/crawled_detail.html', context)
        
    except Exception as e:
        logger.error(f"크롤링된 제품 상세 정보 로드 실패: {e}")
        return render(request, 'products/detail.html', {
            'error': '제품 정보를 불러오는 중 오류가 발생했습니다.',
            'product': None
        })

def product_list(request):
    media_path  = os.path.join(settings.MEDIA_ROOT, 'data', 'products.json')
    static_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'products.json')
    json_path   = media_path if os.path.exists(media_path) else static_path

    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    return render(request, 'products/product_list.html', {'products': products})

# DB 구현 이후 검색 로직 수정 필요 - 현재는 검색시마다 json 파일을 매번 불러오고 있음
## 현재는 단어 단위의 검색만 가능.. (제품 데이터를 밑에 표시함으로써 이 문제 완화 가능) 
## 만일 사용자가 "조선무화과"를 검색한다면 "조선 무화과" 검색어는 서치에 걸리지 않음("조선", "무화과"는 정상적으로 검색 가능)
def search_product(request):
    query = request.GET.get('q', '').lower().strip()
    query_words = query.split()

    static_cluster = os.path.join(settings.BASE_DIR, 'static','data', 'products_clustered.json')
    static_all = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')

    product_path = static_cluster if os.path.exists(static_cluster) else static_all

    with open(product_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    def normalize(text): return text.lower()

    filtered = []
    for p in products:
        search_for = normalize(p.get('brand','') + ' - ' + p.get('name',''))
        if all(word in search_for for word in query_words):
            filtered.append(p)

    return JsonResponse({'results': filtered})

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
    static_cluster = os.path.join(settings.BASE_DIR, 'static', 'data', 'products_clustered.json')
    static_all = os.path.join(settings.BASE_DIR, 'static', 'data', 'all_products.json')

    json_path = None
    if os.path.exists(static_cluster):
        json_path = static_cluster
    else:
        json_path = static_all  
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except FileNotFoundError:
        logger.error("products JSON 파일을 찾을 수 없습니다: %s", json_path)
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
            logger.info("제품 매칭 성공: %s -> URL: %s", matching_product.get('name'), matching_product.get('url'))
            products_with_colors.append({
                'id': liked_product.product_id,  # 기존과 동일: Like의 product_id 유지
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
    """제품별 좋아요 수 조회 API"""
    try:
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'error': '제품 ID가 필요합니다.'}, status=400)
        
        like_count = ProductLike.objects.filter(product_id=product_id).count()
        
        return JsonResponse({
            'product_id': product_id,
            'like_count': like_count
        })
        
    except Exception as e:
        logger.error(f"제품 좋아요 수 조회 실패: {e}")
        return JsonResponse({'error': '좋아요 수를 가져오는 중 오류가 발생했습니다.'}, status=500)

# ------------------------------
# 별점 기능
# ------------------------------

@csrf_exempt
@require_http_methods(["POST"])
def submit_product_rating(request):
    """제품 별점 제출 및 수정 API"""
    try:
        #data = json.loads(request.body)
        product_id = request.POST.get('product_id')
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        
        if not product_id or not rating:
            return JsonResponse({'error': '제품 ID와 별점이 필요합니다.'}, status=400)
        
        if rating not in [1, 2, 3, 4, 5]:
            return JsonResponse({'error': '별점은 1~5점 사이여야 합니다.'}, status=400)
        
        # 사용자 정보 가져오기
        user = request.user if request.user.is_authenticated else None
        session_nickname = None
        
        if not user:
            # 세션 사용자 처리
            session_nickname = request.session.get('nickname')
            if not session_nickname:
                return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        
        # 제품 정보 가져오기 (실제로는 데이터베이스에서 조회해야 함)
        product_name = request.POST.get('product_name', f'제품 {product_id}')
        product_brand = request.POST.get('product_brand', '브랜드')
        
        # # 기존 별점이 있는지 확인
        # existing_rating = None
        # if user:
        #     existing_rating = ProductRating.objects.filter(user=user, product_id=product_id).first()
        # else:
        #     existing_rating = ProductRating.objects.filter(session_nickname=session_nickname, product_id=product_id).first()
        
        # if existing_rating:
        #     # 기존 별점 업데이트
        #     existing_rating.rating = rating
        #     existing_rating.comment = comment
        #     existing_rating.save()
        #     message = '별점이 수정되었습니다.'
        # else:
        #     # 새 별점 생성
        #     existing_rating = ProductRating.objects.create(
        #         user=user,
        #         session_nickname=session_nickname,
        #         product_id=product_id,
        #         product_name=product_name,
        #         product_brand=product_brand,
        #         rating=rating,
        #         comment=comment
        #     )
        #     message = '별점이 등록되었습니다.'

        # -> update_or_create 함수 사용 - 사용자가 작성한 리뷰를 찾고, 없으면 새로 생성
        if user:
            rating_product, created = ProductRating.objects.update_or_create(
                user=user, product_id = product_id,
                defaults={
                    'rating':rating, 'comment':comment,
                    'product_name': product_name, 'product_brand': product_brand
                }
            )
        else:
            rating_product, created = ProductRating.objects.update_or_create(
                session_nickname=session_nickname, product_id=product_id,
                defaults={
                    'rating': rating, 'comment': comment,
                    'product_name': product_name, 'product_brand': product_brand
                }
            )
        
        message = '별점이 등록되었습니다.' if created else '별점이 수정되었습니다.'

        # 이미지 생성/수정/삭제 부분
        files = request.FILES.getlist('images')
        if files:
            current_image_count = rating_product.images.count()

            if current_image_count + len(files) > 4:
                return JsonResponse({'error': '이미지는 최대 4개까지 등록 가능합니다.'}, status=400)
            for file in files:
                ProductRatingImage.objects.create(review=rating_product, image=file)
          
        return JsonResponse({
            'success': True,
            'message': message,
            'rating': rating
        })

    except Exception as e:
        logger.error(f"제품 별점 제출 실패: {e}")
        return JsonResponse({'error': '별점을 저장하는 중 오류가 발생했습니다.'}, status=500)

@require_http_methods(["GET"])
def get_product_rating(request):
    """제품 별점 조회 API"""
    try:
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'error': '제품 ID가 필요합니다.'}, status=400)
        
        # 제품의 모든 별점 조회
        ratings = ProductRating.objects.filter(product_id=product_id)
        
        # 평균 별점 계산
        if ratings.exists():
            avg_rating = sum(r.rating for r in ratings) / ratings.count()
            total_ratings = ratings.count()
        else:
            avg_rating = 0
            total_ratings = 0
        
        # 사용자의 별점 조회
        user_rating = None
        user_images = []
        if request.user.is_authenticated:
            user_rating = ratings.filter(user=request.user).first()
        else:
            session_nickname = request.session.get('nickname')
            if session_nickname:
                user_rating = ratings.filter(session_nickname=session_nickname).first()

        # 별점 분포 계산
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = ratings.filter(rating=i).count()
        
        # 사용자가 업로드한 기존 리뷰 이미지 불러오기
        if user_rating:
            for img in user_rating.images.all():
                user_images.append({'id': img.id, 'url': request.build_absolute_uri(img.image.url)})
        
        return JsonResponse({
            'product_id': product_id,
            'average_rating': round(avg_rating, 1),
            'total_ratings': total_ratings,
            'rating_distribution': rating_distribution,
            'user_rating': user_rating.rating if user_rating else None,
            'user_comment': user_rating.comment if user_rating else None,
            'user_images': user_images,
        })
        
    except Exception as e:
        logger.error(f"제품 별점 조회 실패: {e}")
        return JsonResponse({'error': '별점을 가져오는 중 오류가 발생했습니다.'}, status=500)

@require_http_methods(["GET"])
def get_product_ratings_list(request):
    """제품 별점 목록 조회 API"""
    try:
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'error': '제품 ID가 필요합니다.'}, status=400)
        
        # 제품의 모든 별점 조회 (최신순)
        ratings = ProductRating.objects.filter(product_id=product_id).order_by('-created_at')
        
        ratings_data = []
        for rating in ratings:
            images = [request.build_absolute_uri(img.image.url) for img in rating.images.all()]
            ratings_data.append({
                'id': str(rating.id),
                'rating': rating.rating,
                'comment': rating.comment,
                'created_at': rating.created_at.strftime('%Y-%m-%d'),
                'user_name': rating.user.username if rating.user else rating.session_nickname,
                'images': images
            })
        
        return JsonResponse({
            'product_id': product_id,
            'ratings': ratings_data
        })
        
    except Exception as e:
        logger.error(f"제품 별점 목록 조회 실패: {e}")
        return JsonResponse({'error': '별점 목록을 가져오는 중 오류가 발생했습니다.'}, status=500)

# 리뷰 이미지 삭제 부분
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_review_image(request, image_id):
    try:
        image = get_object_or_404(ProductRatingImage, id=image_id)

        image.delete()
        return JsonResponse({'success': True, 'message': '이미지가 삭제되었습니다.'})
    
    except Exception as e:
        return JsonResponse({'error': f'이미지 삭제 중 오류가 발생했습니다: {e}'}, status=500)


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

import json, os
from django.shortcuts import render
from django.conf import settings
from .models import ProductLike

# 랭킹 페이지 뷰
def product_ranking_page(request):
    category = request.GET.get('category', '')  # GET 파라미터로 카테고리 받기
    if category == '':
        category = None

    top_products = get_top_liked_products(limit=10, category=category)

    return render(request, 'products/product_ranking.html', {
        'top_products': top_products,
        'selected_category': category or '',
    })



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



# 별점 리뷰 삭제 부분
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product_rating(request, product_id):
    try:
        # 사용자 - 작성자 본인 여부 확인
        if request.user.is_authenticated:
            user = request.user
            review_to_delete = get_object_or_404(ProductRating, user=user, product_id=product_id)
        else:
            session_nickname = request.session.get('nickname')
            if not session_nickname:
                return JsonResponse({'error': '인증 정보가 없습니다.'}, status=401)
            review_to_delete = get_object_or_404(ProductRating, session_nickname=session_nickname, product_id=product_id)

        review_to_delete.delete()
        
        return JsonResponse({'success': True, 'message': '리뷰가 성공적으로 삭제되었습니다.'})

    except ProductRating.DoesNotExist:
        return JsonResponse({'error': '삭제할 리뷰를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'리뷰 삭제 중 오류가 발생했습니다: {e}'}, status=500)

        # views.py


def product_ranking(request):
    """제품 랭킹 페이지 뷰 - 카테고리 필터링 가능"""
    
    try:
        category = request.GET.get('category')  # URL에서 category 파라미터
        top_products = get_top_liked_products(1000)  # 충분히 많은 제품을 가져옴
        
        # 카테고리 필터링
        if category:
            top_products = [p for p in top_products if p.get('product_category') == category]
        
        # 최대 10개만 표시
        top_products = top_products[:10]
        
        return render(request, 'products/product_ranking.html', {
            'top_products': top_products,
            'selected_category': category,  # 선택된 카테고리 표시용
        })
    except Exception as e:
        logger.error(f"제품 랭킹 페이지 오류: {str(e)}")
        return render(request, 'products/product_ranking.html', {
            'top_products': [],
            'error_message': '랭킹 정보를 불러오는데 실패했습니다.'
        })

    