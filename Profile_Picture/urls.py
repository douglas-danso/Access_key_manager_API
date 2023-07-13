from django.urls import path
from Profile_Picture.views import ProfileImageView

urlpatterns = [
    path('image/', ProfileImageView.as_view(), name='profile-image'),
]
