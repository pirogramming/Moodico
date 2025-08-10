# moodico/products/management/commands/generate_clusters.py

#실행방법
'''
python manage.py generate_clusters --input data/all_products.json
'''
import os
import json
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.staticfiles import finders
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# --- helpers from your script ---
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

class Command(BaseCommand):
    help = "Generate color clusters from product JSON and save to MEDIA_ROOT/data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="data/test_products.json",
            help="Input JSON path relative to a static dir (e.g., data/test_products.json).",
        )
        parser.add_argument(
            "--clusters",
            type=int,
            default=4,
            help="Number of KMeans clusters (default: 4).",
        )
        parser.add_argument(
            "--no-silhouette",
            action="store_true",
            help="Skip silhouette score sweep.",
        )

    def handle(self, *args, **opts):
        input_rel = opts["input"]
        n_clusters = opts["clusters"]
        skip_sil = opts["no_silhouette"]

        # 1) Find input JSON via staticfiles finder; fallback to BASE_DIR/static
        src = finders.find(input_rel)
        if not src:
            fallback = os.path.join(settings.BASE_DIR, "static", input_rel)
            if os.path.exists(fallback):
                src = fallback
        if not src:
            raise CommandError(f"Input not found: {input_rel}")

        with open(src, "r", encoding="utf-8") as f:
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
            raise CommandError("No valid products with color data found.")

        # 2) Cluster — standardize first, then fit
        coords_np = np.array(coordinates, dtype=float)
        coords_std = StandardScaler().fit_transform(coords_np)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(coords_std)

        for i, label in enumerate(labels):
            valid_products[i]["cluster"] = int(label)

        # 3) Save outputs under MEDIA_ROOT/data (writable in prod)
        out_dir = os.path.join(settings.MEDIA_ROOT, "data")
        os.makedirs(out_dir, exist_ok=True)

        products_out = os.path.join(out_dir, "products_clustered.json")
        with open(products_out, "w", encoding="utf-8") as f:
            json.dump(valid_products, f, ensure_ascii=False, indent=2)

        centers_out = os.path.join(out_dir, "cluster_centers.json")
        with open(centers_out, "w", encoding="utf-8") as f:
            json.dump(kmeans.cluster_centers_.tolist(), f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Wrote:\n  {products_out}\n  {centers_out}"))

        # 4) Optional: silhouette sweep (k=2..10 or up to len-1)
        if not skip_sil:
            max_k = min(len(coords_std) - 1, 10)
            for k in range(2, max_k + 1):
                mdl = KMeans(n_clusters=k, random_state=42, n_init='auto')
                lab = mdl.fit_predict(coords_std)
                sc = silhouette_score(coords_std, lab)
                self.stdout.write(f"k={k}  Silhouette={sc:.4f}")
