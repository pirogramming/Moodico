## 기존 크롤링한 데이터(all_products.json)를 불러와서 image 필드로부터 hex 값과 lab 값을 뽑는 로직을 시험적으로 구현
# 립 발색 부분이 이난 부분의 색상이 같이 섞이는 문제 때문에..

import json
import requests
import numpy as np
from PIL import image

def get_product_mood_color(image_url):
    try:
        # 이미지 가져오기
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {image_url}, 오류: {e}")
        return None, None
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return None, None