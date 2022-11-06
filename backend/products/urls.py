from django.urls import path

from . import views

# for reading static files
from django.conf import settings
from django.urls import include
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.ListFlower.as_view()),
    # path('', views.index, name='index'),
    # path('flowers', views.flower, name='flowers'),
    # path('bouquets', views.bouquet, name='bouquets'),

    # for api
    path('flower-list/', views.FlowerListView.as_view()),
    path('gallery-list/', views.FlowerGalleryView.as_view()),
    path('flower-list/<int:pk>/', views.FlowerDetailView.as_view()),

]

# узнать, что такое as_view()