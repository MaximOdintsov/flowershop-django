from django.urls import path

from . import views

# for reading static files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.ListProduct.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# узнать, что такое as_view()