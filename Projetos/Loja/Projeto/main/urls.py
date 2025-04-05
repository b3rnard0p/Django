from django.urls import path
from . import views
from django.conf  import settings
from django.conf.urls.static  import static

urlpatterns = [
    path('', views.home, name='Home'),
    path('category_list/', views.category_list, name='category_list'),
    path('marca_list/', views.marca_list, name='marca_list'), 
    path('product_list/', views.product_list, name='product_list'),
    path('category_product_list/<int:cat_id>', views.category_product_list, name='category_product_list'),
    path('marca_product_list/<int:marca_id>', views.marca_product_list, name='marca_product_list'),
    path('product/<str:slug>/<int:id>', views.product_details, name='product_details'),
    
]

if settings.DEBUG:
    urlpatterns  += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)