

from django.urls import path
from .views import (AdvertisementCreateView, AdvertisementListView,
                    AdvertisementDetailView, upload_media, AdvertisementDeleteView,
                    AdvertisementUpdateView, RespondToAdView, MyResponsesView,
                    accept_response, delete_response, IndexView, usual_login_view,
                    login_with_code_view, MailingCreateView, MailingListView)
from django.contrib.auth.views import LogoutView, LoginView


urlpatterns = [
    path('advertisement/', AdvertisementListView.as_view(), name='advertisement_list'),
    path('advertisement/<int:pk>/', AdvertisementDetailView.as_view(),
         name='advertisement_detail'),
    path('create/', AdvertisementCreateView.as_view(), name='advertisement_create'),
    path('delete/<int:pk>/', AdvertisementDeleteView.as_view(), name='advertisement_delete'),
    path('update/<int:pk>/', AdvertisementUpdateView.as_view(), name='advertisement_update'),
    path('tinymce/upload/', upload_media, name='tinymce_upload'),
    path('profile/', IndexView.as_view(), name='my_profile'),
    path('advertisement/<int:pk>/respond/', RespondToAdView.as_view(), name='respond_to_ad'),
    path('my-responses/', MyResponsesView.as_view(), name='my_responses'),
    path('response/<int:pk>/accept/', accept_response, name='accept_response'),
    path('response/<int:pk>/delete/', delete_response, name='delete_response'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/Advert/login/'), name='logout'),
    path('signup/', usual_login_view, name='signup'),
    path('confirm/', login_with_code_view, name='confirm_code'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
]