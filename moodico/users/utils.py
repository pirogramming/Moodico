from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import User

def login_or_kakao_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get("nickname"):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

def get_user_from_request(request):
    """요청에서 사용자 정보를 가져오는 함수"""
    if request.user.is_authenticated:
        return request.user
    elif request.session.get("nickname"):
        # 카카오 로그인 사용자의 경우 User 객체가 없을 수 있음
        return None
    return None