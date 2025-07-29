from django.shortcuts import render
from django.http import HttpResponse
import json
import os


def main(request):
    return render(request, 'main.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def my_item_recommendation(request):
    # 백엔드 연동을 위해 임시로 빈 리스트 전달
    recommended_items = []
    search_results = []
    return render(request, 'upload.html', {'search_results': search_results, 'recommended_items': recommended_items})

def mood_test(request):
    return render(request, 'mood_test.html')

def mood_result(request):
    # 무드 테스트 결과 데이터 (백엔드에서 받아올 예정)
    mood_data = {
        'mood_name': '로맨틱',
        'mood_description': '부드럽고 여성스러운 사랑스러운 느낌',
        'colors': ['#FEEBEB', '#FFD2CC', '#FFB7B3'],
        'tags': ['#soft', '#feminine', '#pink', '#shimmer'],
        'recommended_products': [
            {'type': '립스틱', 'image': '/static/images/test.jpg', 'brand': 'ETUDE HOUSE', 'product_name': '코랄 틴트 립', 'price': '12,000원', 'rating': '4.0', 'review_count': '123'},
            {'type': '블러셔', 'image': '/static/images/test.jpg', 'brand': 'PERIPERA', 'product_name': '글로우 체크 블러셔', 'price': '18,000원', 'rating': '4.0', 'review_count': '456'},
            {'type': '아이쉐도우', 'image': '/static/images/test.jpg', 'brand': 'INNISFREE', 'product_name': '내추럴 아이쉐도우', 'price': '22,000원', 'rating': '4.0', 'review_count': '789'},
        ]
    }
    return render(request, 'mood_result.html', mood_data)

def color_matrix_explore(request):
    return render(request, 'color_matrix.html')

def product_detail(request, product_id):
    # 제품 상세 정보 (백엔드에서 받아올 예정)
    product = {
        'id': product_id,
        'name': f'제품 {product_id}',
        'description': '이 제품은 아주 좋은 제품입니다.',
        'price': '30,000원',
        'image': '/static/images/test.jpg', # 임시 이미지
    }
    return render(request, 'detail.html', {'product': product})

# Create your views here.

def main(request):
    """메인 페이지 뷰"""
    return render(request, 'base.html')

def login_view(request):
    """로그인 페이지 뷰"""
    return render(request, 'login.html')

def signup_view(request):
    """회원가입 페이지 뷰"""
    return render(request, 'signup.html')

def my_item_recommendation(request):
    """내 아이템 기반 추천 페이지 뷰"""
    return render(request, 'base.html')

def mood_test(request):
    """무드 테스트 페이지 뷰"""
    return render(request, 'mood_test.html')

def mood_result(request):
    """무드 테스트 결과 페이지 뷰"""
    return render(request, 'mood_result.html')

def color_matrix_explore(request):
    """색상 매트릭스 페이지 뷰"""
    return render(request, 'color_matrix.html')

def product_detail(request, product_id):
    """제품 상세 페이지 뷰"""
    return render(request, 'detail.html', {'product_id': product_id})

def product_list(request):
    json_path = os.path.join('static', 'data', 'products.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    return render(request, 'product_list.html', {'products': products})
