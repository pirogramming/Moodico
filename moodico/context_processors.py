def kakao_user(request):
    return {
        'nickname': request.session.get('nickname'),
        'profile_image': request.session.get('profile_image'),
    }