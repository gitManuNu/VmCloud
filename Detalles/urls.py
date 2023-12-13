from django.urls import path
from Detalles import views

urlpatterns = [
    path('DetalleVM/',views.DetallesVirtualMachines.as_view(),name='detallevm'),
    path('DetalleDK/',views.DetallesDiscos.as_view(),name='detalledk'),
    path('DetalleNW/',views.DetallesRedes.as_view(),name='detallenw'),
    path('DelData/',views.Borrado.as_view(),name='deldata'),
    path('Estado/',views.EncendidoApagado.as_view(),name='estado')
]