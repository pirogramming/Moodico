from django.shortcuts import redirect
from functools import wraps

def login_or_kakao_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get("nickname"):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view