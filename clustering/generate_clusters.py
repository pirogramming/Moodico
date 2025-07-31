import json
import numpy as np
from sklearn.cluster import KMeans

# --- Color conversion utilities ---
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

# Step 1: Load raw data
with open("static/data/romand_products_enhanced.json", "r", encoding="utf-8") as f:
    products = json.load(f)

coordinates = []
valid_products = []

# Step 2: Calculate warm_cool and light_deep
for p in products:
    hex_color = p.get("hex")
    if hex_color:
        try:
            r, g, b = hex_to_rgb(hex_color)
            h, s, l = rgb_to_hsl(r, g, b)
            warm, deep = calculate_coordinates(h, s, l)
            p["warmCool"] = warm
            p["lightDeep"] = deep
            coordinates.append([warm, deep])
            valid_products.append(p)
        except:
            continue

# Step 3: Cluster coordinates
coords_np = np.array(coordinates)
kmeans = KMeans(n_clusters=6, random_state=42, n_init='auto')
labels = kmeans.fit_predict(coords_np)

# Step 4: Assign cluster labels
for i, label in enumerate(labels):
    valid_products[i]["cluster"] = int(label)

# Step 5: Save clustered data
with open("static/data/romand_products_clustered.json", "w", encoding="utf-8") as f:
    json.dump(valid_products, f, ensure_ascii=False, indent=2)

# Step 6: Save cluster centers
with open("static/data/cluster_centers.json", "w", encoding="utf-8") as f:
    json.dump(kmeans.cluster_centers_.tolist(), f, ensure_ascii=False, indent=2)

print(" Clustering complete. Files saved.")
