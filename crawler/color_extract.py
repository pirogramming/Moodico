## 기존 크롤링한 데이터(all_products.json)를 불러와서 image 필드로부터 hex 값과 lab 값을 뽑는 로직을 시험적으로 구현
# 립 발색 부분이 아닌 부분의 색상이 같이 섞이는 문제 때문에..

import json
import requests
import numpy as np
from PIL import Image
import cv2
from io import BytesIO
from sklearn.cluster import KMeans
from skimage.color import rgb2lab
import matplotlib.pyplot as plt
from collections import Counter

## 디버깅을 위한 코드
# k-means -> hex, hsl, swatch 추출
def hex_hsl_swatch(rgb_colors, i,  ):
    rgb = rgb_colors[i]
    hex_code = f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
    lab_values = rgb2lab(np.uint8(rgb).reshape(1, 1, 3) / 255.0).flatten()
    color_swatch = np.full((100, 100, 3), rgb, dtype=np.uint8)

    return rgb, hex_code, lab_values, color_swatch

# 실제 출력 함수
def pltshow(img, title):
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.show()

def get_product_color_w_kmeans(image_url):
    try:
        # 이미지 가져오기
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 이미지 열기 및 처리
        pil_img = Image.open(BytesIO(response.content)).convert("RGB")

        # [디버깅용 출력] 원본 이미지
        # pltshow(pil_img, "1. Original Image")
        
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        ## 배경 제거 - cv의 grabcut 매서드 사용
        # GrabCut에 필요한 마스크와 임시 배열 초기화
        mask = np.zeros(cv_img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        height, width = cv_img.shape[:2]
        roi_rect = (int(width * 0.1), int(height * 0.1), int(width * 0.8), int(height * 0.8))

        # [디버깅용 출력] roi_rect가 그려진 이미지
        # img_with_rect = cv_img.copy()
        # cv2.rectangle(img_with_rect, (roi_rect[0], roi_rect[1]), (roi_rect[0] + roi_rect[2], roi_rect[1] + roi_rect[3]), (0, 255, 0), 3) # 초록색 사각형
        # pltshow(cv2.cvtColor(img_with_rect, cv2.COLOR_BGR2RGB), "2. Image with ROI Rectangle")

        cv2.grabCut(cv_img, mask, roi_rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        final_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        img_fg_only = cv_img * final_mask[:, :, np.newaxis]

        # [디버깅용 출력] 배경이 제거된 이미지
        # pltshow(cv2.cvtColor(img_fg_only, cv2.COLOR_BGR2RGB), "3. Background Removed Image")
        
        # 이미지를 numpy 배열 형태로 변환
        pixels = cv2.cvtColor(img_fg_only, cv2.COLOR_BGR2RGB).reshape(-1, 3)
        foreground_pixels = pixels[pixels.any(axis=1)]

        # k-means 처리 부분
        k=4
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(foreground_pixels)

        rgb_colors = kmeans.cluster_centers_.astype('uint8')
        labels = kmeans.labels_
        hsv_colors = cv2.cvtColor(rgb_colors.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV)

        pixel_counts = Counter(labels)
        clusters = []
        for i in range(len(rgb_colors)):
            clusters.append({
                'index': i,
                'rgb': rgb_colors[i],
                'hsv': hsv_colors[i][0], # [H, S, V]
                'count': pixel_counts.get(i, 0) # 해당 클러스터의 픽셀 수
            })
        clusters_sorted_by_value = sorted(clusters, key=lambda x: x['hsv'][2])
        candidate_clusters = clusters_sorted_by_value[1:-1]  # 명도가 가장 높은 클러스터 제외(글씨 혹은 배경일 가능성), 명도가 가장 낮은 클러스터 제외(어두운 색상의 용기 혹은 그림자진 부분일 가능성)
        #final_cluster = max(candidate_clusters, key=lambda x: x['count']) # 남은 클러스터들 중 픽셀 수가 더 많은 클러스터 선택
        final_cluster = max(candidate_clusters, key=lambda x: x['hsv'][1]) # 남은 클러스터들 중 채도가 더 높은 클러스터 선택 - 이걸로 함

        best_color_rgb = final_cluster['rgb']
        
        final_hex_code = f"#{int(best_color_rgb[0]):02x}{int(best_color_rgb[1]):02x}{int(best_color_rgb[2]):02x}"
        lab_values = rgb2lab(np.uint8(best_color_rgb).reshape(1, 1, 3) / 255.0).flatten()
        print(f"{lab_values}, {final_hex_code}")

        # [디버깅용 출력] k-means 결과 값에 해당하는 hex 색상 이미지
        # swatches_list = []
        # hex_list = []

        # resized_pil_img = pil_img.resize((100, 100))
        # swatches_list.append(np.array(resized_pil_img))

        # for i in range(k):
        #     rgb, hex_code, lab_values, color_swatch = hex_hsl_swatch(rgb_colors, i)
        #     swatches_list.append(color_swatch)
        #     hex_list.append(hex_code)

        # combined_swatch = np.concatenate(swatches_list, axis=1)
        # pltshow(combined_swatch, f"4. K-Means Result: {hex_list} - {final_hex_code}")

        return final_hex_code, lab_values

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {image_url}, 오류: {e}")
        return None, None
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return None, None

if __name__ == "__main__":

    #image_url = "https://romand.io/images/product/902/EJ1VyyBRxhumy6rRRC3oNLbiy8qkqiB6KKPOWG5h.jpg"
    # image_url = "https://romand.io/images/product/994/2hVgwjntZmhpGANTN6g0dJii6FWJRdKWcoJIDJVM.jpg"
    # new_hex, new_lab = get_product_color_w_kmeans(image_url)
    # print(new_hex, new_lab)

    with open('../static/data/all_products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    new_data = []
    process_num = 0
    
    for product in products:
        process_num+=1
        image_url = product.get("image")
        
        print(f"{process_num}. {product['name']} 처리 중 ..")
        new_hex, new_lab = get_product_color_w_kmeans(image_url)

        new_product_object = product.copy()
        new_product_object['hex'] = new_hex
        new_product_object['lab_l'] = round(new_lab[0], 2)
        new_product_object['lab_a'] = round(new_lab[1], 2)
        new_product_object['lab_b'] = round(new_lab[2], 2)

        new_data.append(new_product_object)
    
    new_file = "all_products_hex_update_tempk=3_1_1.json"
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent = 2, ensure_ascii=False)
    print("전 제품 재추출 완료")