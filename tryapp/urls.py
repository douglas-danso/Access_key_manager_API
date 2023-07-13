from django.urls import path
from tryapp import views
from tryapp.views import (UserSignupView,UserLoginView,UserLists,PasswordResetView,PasswordResetConfirm,
                          PasswordChange,DeleteAccount,Activate,ResendActivationLink,LogoutView)
 
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userlists/', UserLists.as_view(), name= 'lists'),
    path('passwordreset/', PasswordResetView.as_view(), name= 'passwordreset'),
    path('passwordresetconfirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name= 'passwordresetconfirm'),
    path('passwordchange/', PasswordChange.as_view(), name= 'passwordchange'),
    path('delete/', DeleteAccount.as_view(), name= 'delete'),
    path('activate/<token>/', Activate.as_view(), name= 'activate'),
    path('resend/', ResendActivationLink.as_view(), name= 'resend'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
