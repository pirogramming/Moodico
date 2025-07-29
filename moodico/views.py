from django.shortcuts import render
from django.http import HttpResponse
import json
import os

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