from django.urls import path
from Login import views

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('reboot_psw/', views.RebootPass.as_view(), name='reboot_psw'),
    path('logout/', views.Logout.as_view(), name='logout')
]
