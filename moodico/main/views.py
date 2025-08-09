from django.shortcuts import render
from moodico.products.views import get_top_liked_products

# Create your views here.

def main(request):
    """메인 페이지 뷰"""
    # 상위 3개의 인기 제품만 메인페이지에 표시
    top_liked_products = get_top_liked_products(3)
    
    return render(request, 'main/main.html', {
        'top_liked_products': top_liked_products
    })


