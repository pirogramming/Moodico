from django.shortcuts import render
import requests
from django.http import HttpResponse
from moodico.upload.forms import UploadForm
from moodico.recommendation.views import get_recommendation_list

# Create your views here.
# 이미지 업로드
def upload_color_image(request):
    search_results = get_recommendation_list()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)

            if request.user.is_authenticated:
                upload.user = request.user
            else:
                upload.user = None 

            upload.save()
            return render(request, 'upload/upload.html', {
                'form': UploadForm(),
                'uploaded_image_url': upload.image_path.url,
                'search_results':search_results,
            })
    else:
        form = UploadForm()
    return render(request, 'upload/upload.html', {'form': form, 'search_results': search_results})

# upload.html에서 검색한 제품의 이미지를 가져옴
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse("URL not provided", status=400)
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', 'image/jpeg')
        return HttpResponse(response.content, content_type=content_type)
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching image: {e}", status=500)