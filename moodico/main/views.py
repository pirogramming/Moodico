from django.shortcuts import render

# Create your views here.

def main(request):
    """메인 페이지 뷰"""
    return render(request, 'main.html')


