from django.contrib import admin
from .models import Brand, Product, ProductShade, ProductRating

# Register your models here.

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'category', 'price']
    list_filter = ['brand', 'category']
    search_fields = ['name', 'brand__name']
    list_select_related = ['brand']

@admin.register(ProductShade)
class ProductShadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'shade_name', 'product', 'hex', 'lab_l', 'lab_a', 'lab_b']
    list_filter = ['product__brand', 'product__category']
    search_fields = ['shade_name', 'product__name']
    list_select_related = ['product', 'product__brand']

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'product_brand', 'rating', 'user', 'session_nickname', 'created_at']
    list_filter = ['rating', 'created_at', 'product_brand']
    search_fields = ['product_name', 'product_brand', 'user__username', 'session_nickname']
    list_select_related = ['user']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
