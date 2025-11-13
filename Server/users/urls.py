from django.urls import path
from .views import signup_view,login_view,forgot_password,reset_password,logout_view,profile_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/',reset_password, name='reset-password'),
    path('logout/', logout_view, name='logout_view'),
    path('profile/', profile_view, name='profile'), 
]