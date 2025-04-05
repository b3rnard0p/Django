from django.contrib import admin
from .models import Banner,Product, Category, Marca, Color, Size, ProductAttribute

admin.site.register(Marca)
admin.site.register(Size)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'marca', 'color', 'size', 'status', 'if_feat_caracterico')
    list_editable = ('status', 'if_feat_caracterico' )
admin.site.register(Product, ProductAdmin)


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'size', 'price', 'image_tag_path')
    
admin.site.register(ProductAttribute, ProductAttributeAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_tag_path')
admin.site.register(Category, CategoryAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'color_tag_path')
admin.site.register(Color, ColorAdmin)

class BannerAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'image_tag_path')
admin.site.register(Banner, BannerAdmin)