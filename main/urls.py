from django.urls import path
from .views import HomeView, SubirTextoView, ListaTextosView, BorrarTextoView, TextoDetailView, \
    TablaCorrespondenciasCreateView, TablaCorrespondenciasUpdateView, TablaCorrespondenciasDeleteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('lista-textos', ListaTextosView.as_view(), name='lista.textos'),
    path('detalle-texto/<int:pk>', TextoDetailView.as_view(), name='detalle.texto'),
    path('borrar-texto/<int:pk>', BorrarTextoView.as_view(), name='borrar.texto'),
    path('subir-texto', SubirTextoView.as_view(), name='subir.texto'),
    path('agregar-correspondencia', TablaCorrespondenciasCreateView.as_view(), name='agregar.correspondencia'),
    path('editar-correspondencia/<int:pk>', TablaCorrespondenciasUpdateView.as_view(), name='editar.correspondencia'),
    path('eliminar-correspondencia/<int:pk>', TablaCorrespondenciasDeleteView.as_view(), name='eliminar.correspondencia'),
]
