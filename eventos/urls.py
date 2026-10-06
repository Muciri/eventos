from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    path('', views.main, name='main'),
    path('programacao', views.programacao, name='programacao'),
    path('evento/<int:id>', views.detalhe_evento, name='evento'),
    path('criar_evento', views.criar_evento, name='criar_evento'),
    path('minha_agenda', views.minha_agenda, name='minha_agenda'),
]