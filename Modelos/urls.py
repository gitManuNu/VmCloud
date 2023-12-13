from django.urls import path
from Modelos import views

urlpatterns = [
    path('', views.PlanillaUsuarios.as_view(), name='planilla_usuarios'),
    path('add_data/', views.AddData.as_view(), name='add_data'),
    path('geoip/', views.GeoIp.as_view(), name='geoip'),
    path('del_data/', views.DeleteData.as_view(), name='del_data'),
]
