from django.urls import path
from Mails import views

urlpatterns = [
    path('', views.AdminEnvios.as_view(), name='admin_envios'),
    path('datos_envio/', views.DatosEnvio.as_view(), name='datos_envio'),
    path('envio_registrado/', views.WelcomeMail.as_view(), name='envio_registrado'),
    path('reboot_psw_email/', views.RebootEmail.as_view(), name='reboot_psw_email'),
    path('reboot_psw_envio/', views.RebootSend.as_view(), name='reboot_psw_envio'),
]
