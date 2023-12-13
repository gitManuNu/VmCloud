from django.urls import path
from Recursos import views

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('Resources/',views.Recursos.as_view(),name='resources'),
    path('Add_VM/',views.AddVirtualMachines.as_view(),name='add_vm'),
    path('Add_NAT/',views.AddNetwork.as_view(),name='add_nat')
]