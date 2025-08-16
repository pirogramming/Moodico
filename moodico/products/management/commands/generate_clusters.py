# python manage.py generate_clusters
import os
import json
import numpy as np

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def hex_to_rgb(hex_code):
    h = hex_code.lstrip('#')
    if len(h) == 3:
        h = ''.join([c * 2 for c in h])
    r = int(h[:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:], 16)
    return r, g, b

def rgb_to_hsl(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
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
        warm_cool_score *= s ** 0.8

    if l < 0.1 or l > 0.9:
        warm_cool_score *= (1 - ((abs(0.5 - l) * 2) ** 2))

    final_warm = (warm_cool_score + 1) * 50
    final_warm = max(0, min(100, final_warm))
    final_deep = (1 - l) * 100
    return round(final_warm, 2), round(final_deep, 2)


class Command(BaseCommand):
    help = "Cluster products from STATIC_ROOT/data/all_products.json and write clustered results."

    def handle(self, *args, **options):
        # paths (match your scraper’s MEDIA_ROOT usage)
        in_path = os.path.join(settings.BASE_DIR, "static", "data", "all_products.json")
        out_dir = os.path.join(settings.BASE_DIR, "static", "data")
        products_out = os.path.join(out_dir, "products_clustered.json")
        centers_out = os.path.join(out_dir, "cluster_centers.json")

        if not os.path.exists(in_path):
            raise CommandError(f"Input not found: {in_path}")

        with open(in_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        coordinates = []
        valid_products = []

        for p in products:
            hex_color = p.get("hex")
            if not hex_color:
                continue
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
            except Exception:
                continue

        if not coordinates:
            raise CommandError("No valid products with color data.")

        # scale once (remove repeated/overwritten arrays)
        coords_np = np.array(coordinates, dtype=float)
        coords_std = StandardScaler().fit_transform(coords_np)

        # fixed k=4 as in your script
        kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(coords_std)

        for i, label in enumerate(labels):
            valid_products[i]["cluster"] = int(label)

        os.makedirs(out_dir, exist_ok=True)
        with open(products_out, "w", encoding="utf-8") as f:
            json.dump(valid_products, f, ensure_ascii=False, indent=2)
        with open(centers_out, "w", encoding="utf-8") as f:
            json.dump(kmeans.cluster_centers_.tolist(), f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS("Clustering complete. Files saved."))
        self.stdout.write(f"  → {products_out}")
        self.stdout.write(f"  → {centers_out}")

        # silhouette sweep (same behavior, now using the standardized features)
        max_k = min(len(coords_std) - 1, 10)
        for k in range(2, max_k + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels_k = model.fit_predict(coords_std)
            score = silhouette_score(coords_std, labels_k)
            self.stdout.write(f"k={k}, Silhouette Score={score:.4f}")
