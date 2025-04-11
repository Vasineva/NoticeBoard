

from django.urls import path
from .views import AdvertisementCreateView, AdvertisementListView, AdvertisementDetailView, upload_media, AdvertisementDeleteView, AdvertisementUpdateView


urlpatterns = [
    path('advertisement/', AdvertisementListView.as_view(), name='advertisement_list'),
    path('create/', AdvertisementCreateView.as_view(), name='advertisement_create'),
    path('advertisement/<int:pk>/', AdvertisementDetailView.as_view(),
         name='advertisement_detail'),
    path('tinymce/upload/', upload_media, name='tinymce_upload'),
    path('delete/<int:pk>/', AdvertisementDeleteView.as_view(), name='advertisement_delete'),
    path('update/<int:pk>/', AdvertisementUpdateView.as_view(), name='advertisement_edit'),
]