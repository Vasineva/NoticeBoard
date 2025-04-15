

from django.urls import path
from .views import (AdvertisementCreateView, AdvertisementListView,
                    AdvertisementDetailView, upload_media, AdvertisementDeleteView,
                    AdvertisementUpdateView, respond_to_ad, MyResponsesView,
                    accept_response, delete_response, IndexView, register_view,
                    confirm_code_view)


urlpatterns = [
    path('advertisement/', AdvertisementListView.as_view(), name='advertisement_list'),
    path('create/', AdvertisementCreateView.as_view(), name='advertisement_create'),
    path('advertisement/<int:pk>/', AdvertisementDetailView.as_view(),
         name='advertisement_detail'),
    path('tinymce/upload/', upload_media, name='tinymce_upload'),
    path('delete/<int:pk>/', AdvertisementDeleteView.as_view(), name='advertisement_delete'),
    path('update/<int:pk>/', AdvertisementUpdateView.as_view(), name='advertisement_edit'),
    path('advertisement/<int:pk>/respond/', respond_to_ad, name='respond_to_ad'),
    path('my-responses/', MyResponsesView.as_view(), name='my_responses'),
    path('response/<int:pk>/accept/', accept_response, name='accept_response'),
    path('response/<int:pk>/delete/', delete_response, name='delete_response'),
    path('profile', IndexView.as_view(), name='my_profile'),
    path('register/', register_view, name='register'),
    path('confirm/', confirm_code_view, name='confirm'),
]