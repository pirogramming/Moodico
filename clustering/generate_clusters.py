import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 클러스터링을 위한 함수들
def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    if len(hex) == 3:
        hex = ''.join([c*2 for c in hex])
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:], 16)
    return r, g, b

def rgb_to_hsl(r, g, b):
    r, g, b = r/255, g/255, b/255
    maxc, minc = max(r, g, b), min(r, g, b)
    l = (maxc + minc) / 2
    if maxc == minc:
        h = s = 0
    else:
        d = maxc - minc
        s = d / (2 - maxc - minc) if l > 0.5 else d / (maxc + minc)
        if maxc == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif maxc == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return h * 360, s, l

def calculate_coordinates(h, s, l):
    if h >= 330 or h < 60:
        if h >= 330:
            h -= 360
        warm_cool_score = (h + 30) / 90
    elif 60 <= h < 180:
        warm_cool_score = 1 - ((h - 60) / 120)
    elif 180 <= h < 300:
        warm_cool_score = -((h - 180) / 120)
    else:
        warm_cool_score = -1 + ((h - 300) / 30)

    if s < 0.05:
        warm_cool_score = 0
    else:
        warm_cool_score *= s**0.8

    if l < 0.1 or l > 0.9:
        warm_cool_score *= (1 - ((abs(0.5 - l) * 2)**2))

    final_warm = (warm_cool_score + 1) * 50
    final_warm = max(0, min(100, final_warm))
    final_deep = (1 - l) * 100

    return round(final_warm, 2), round(final_deep, 2)

from django.conf import settings
import os, json
# 데이터 로드
file_path = os.path.join(settings.STATIC_ROOT, "data", "test_products.json")
with open(file_path, "r", encoding="utf-8") as f:
    products = json.load(f)

coordinates = []
valid_products = []

for p in products:
    hex_color = p.get("hex")
    if hex_color:
        try:
            r, g, b = hex_to_rgb(hex_color)
            h, s, l = rgb_to_hsl(r, g, b)
            warm, deep = calculate_coordinates(h, s, l)
            lab_l = p.get("lab_l", 0)
            lab_a = p.get("lab_a", 0)
            lab_b = p.get("lab_b", 0)

            p["warmCool"] = warm
            p["lightDeep"] = deep
            coordinates.append([warm, deep, lab_l, lab_a, lab_b])
            valid_products.append(p)
        except:
            continue

# 클러스터링을 위한 데이터 정규화
from sklearn.preprocessing import StandardScaler
coords_np = StandardScaler().fit_transform(np.array(coordinates))

# KMeans 클러스터링
coords_np = np.array(coordinates)
kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
labels = kmeans.fit_predict(coords_np)

# 클러스터 레이블을 제품에 추가
for i, label in enumerate(labels):
    valid_products[i]["cluster"] = int(label)

# 클러스터링 결과를 JSON 파일로 저장
# with open("static/data/products_clustered.json", "w", encoding="utf-8") as f:
#     json.dump(valid_products, f, ensure_ascii=False, indent=2)

# Create a data directory in MEDIA_ROOT
data_dir = os.path.join(settings.MEDIA_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "products_clustered.json")
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(valid_products, f, ensure_ascii=False, indent=2)

# 클러스터 중심 좌표 저장
# with open("static/data/cluster_centers.json", "w", encoding="utf-8") as f:
#     json.dump(kmeans.cluster_centers_.tolist(), f, ensure_ascii=False, indent=2)
data_dir = os.path.join(settings.MEDIA_ROOT, "data")
os.makedirs(data_dir, exist_ok=True)

file_path = os.path.join(data_dir, "cluster_centers.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(kmeans.cluster_centers_.tolist(), f, ensure_ascii=False, indent=2)

print(" Clustering complete. Files saved.")

# 실루엣 점수 계산
max_k = min(len(coords_np) - 1, 10)  # Prevents ValueError when sample count is low
for k in range(2, max_k+1):
    model = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels = model.fit_predict(coords_np)
    score = silhouette_score(coords_np, labels)
    print(f"k={k}, Silhouette Score={score}")