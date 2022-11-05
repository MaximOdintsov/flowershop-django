from django.urls import path

from . import views

# for reading static files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.ListFlower.as_view()),
    path('', views.index, name='index'),
    path('flowers', views.flower, name='flowers'),
    path('bouquets', views.bouquet, name='bouquets'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# узнать, что такое as_view()