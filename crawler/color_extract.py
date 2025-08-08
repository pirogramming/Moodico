## 기존 크롤링한 데이터(all_products.json)를 불러와서 image 필드로부터 hex 값과 lab 값을 뽑는 로직을 시험적으로 구현
# 립 발색 부분이 이난 부분의 색상이 같이 섞이는 문제 때문에..

import json
import requests
import numpy as np
from PIL import Image
import cv2
from io import BytesIO
from sklearn.cluster import KMeans
from skimage.color import rgb2lab
import matplotlib.pyplot as plt

def get_product_color_w_kmeans(image_url):
    try:
        # 이미지 가져오기
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 이미지 열기 및 처리
        pil_img = Image.open(BytesIO(response.content)).convert("RGB")

        # [디버깅용 출력] 원본 이미지
        plt.imshow(pil_img)
        plt.title("1. Original Image")
        plt.axis('off')
        plt.show()
        
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        ## 배경 제거 - cv의 grabcut 매서드 사용
        # GrabCut에 필요한 마스크와 임시 배열 초기화
        mask = np.zeros(cv_img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        height, width = cv_img.shape[:2]
        roi_rect = (int(width * 0.1), int(height * 0.1), int(width * 0.8), int(height * 0.8))

        # [디버깅용 출력] roi_rect가 그려진 이미지
        img_with_rect = cv_img.copy()
        cv2.rectangle(img_with_rect, (roi_rect[0], roi_rect[1]), (roi_rect[0] + roi_rect[2], roi_rect[1] + roi_rect[3]), (0, 255, 0), 3) # 초록색 사각형
        plt.imshow(cv2.cvtColor(img_with_rect, cv2.COLOR_BGR2RGB))
        plt.title("3. Image with ROI Rectangle")
        plt.axis('off')
        plt.show()

        cv2.grabCut(cv_img, mask, roi_rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        final_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        img_fg_only = cv_img * final_mask[:, :, np.newaxis]

        # [디버깅용 출력] 배경이 제거된 이미지
        plt.imshow(cv2.cvtColor(img_fg_only, cv2.COLOR_BGR2RGB))
        plt.title("2. Background Removed Image")
        plt.axis('off')
        plt.show()
        
        # 이미지를 numpy 배열 형태로 변환
        pixels = cv2.cvtColor(img_fg_only, cv2.COLOR_BGR2RGB).reshape(-1, 3)
        foreground_pixels = pixels[pixels.any(axis=1)]

        # k-means 처리 부분
        # kmeans = KMeans(n_clusters=1)
        kmeans = KMeans(n_clusters=3)
        kmeans.fit(foreground_pixels)
        dominant_rgb = kmeans.cluster_centers_[0]
        hex_code = f"#{int(dominant_rgb[0]):02x}{int(dominant_rgb[1]):02x}{int(dominant_rgb[2]):02x}"
        lab_values = rgb2lab(np.uint8(dominant_rgb).reshape(1, 1, 3) / 255.0).flatten()

        second_dominant_rgb = kmeans.cluster_centers_[1]
        second_dominant_hex_code = f"#{int(second_dominant_rgb[0]):02x}{int(second_dominant_rgb[1]):02x}{int(second_dominant_rgb[2]):02x}"
        color_swatch2 = np.full((100, 100, 3), second_dominant_rgb, dtype=np.uint8)

        third_dominant_rgb = kmeans.cluster_centers_[2]
        third_dominant_hex_code = f"#{int(third_dominant_rgb[0]):02x}{int(third_dominant_rgb[1]):02x}{int(third_dominant_rgb[2]):02x}"
        color_swatch3 = np.full((100, 100, 3), third_dominant_rgb, dtype=np.uint8)

        fourth_dominant_rgb = kmeans.cluster_centers_[2]
        fourth_dominant_hex_code = f"#{int(fourth_dominant_rgb[0]):02x}{int(fourth_dominant_rgb[1]):02x}{int(fourth_dominant_rgb[2]):02x}"
        color_swatch4 = np.full((100, 100, 3), fourth_dominant_rgb, dtype=np.uint8)

        # [디버깅용 출력] k-means 결과 값에 해당하는 hex 색상 이미지
        color_swatch = np.full((100, 100, 3), dominant_rgb, dtype=np.uint8)

        combined_swatch = np.concatenate((color_swatch, color_swatch2, color_swatch3, color_swatch4), axis=1)
        plt.imshow(combined_swatch)
        plt.title(f"4. K-Means Result: {hex_code}, {second_dominant_hex_code}, {third_dominant_hex_code}, {fourth_dominant_hex_code}")
        plt.axis('off')
        plt.show()

        return hex_code, lab_values

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {image_url}, 오류: {e}")
        return None, None
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return None, None

if __name__ == "__main__":

    image_url = "https://romand.io/images/product/902/EJ1VyyBRxhumy6rRRC3oNLbiy8qkqiB6KKPOWG5h.jpg"
    new_hex, new_lab = get_product_color_w_kmeans(image_url)
    print(new_hex, new_lab)

    # with open('../static/data/all_products.json', 'r', encoding='utf-8') as f:
    #     products = json.load(f)

    # new_data = []
    # process_num = 0
    
    # for product in products:
    #     process_num+=1
    #     image_url = product.get("image")
        
    #     print(f"{process_num}. {product['name']} 처리 중 ..")
    #     new_hex, new_lab = get_product_color_w_kmeans(image_url)

    #     new_product_object = product.copy()
    #     new_product_object['hex'] = new_hex
    #     new_product_object['lab_l'] = round(new_lab[0], 2)
    #     new_product_object['lab_a'] = round(new_lab[1], 2)
    #     new_product_object['lab_b'] = round(new_lab[2], 2)

    #     new_data.append(new_product_object)
    
    # new_file = "all_products_hex_update_temp2.json"
    # with open(new_file, 'w', encoding='utf-8') as f:
    #     json.dump(new_data, f, indent = 2, ensure_ascii=False)
    # print("전 제품 재추출 완료")