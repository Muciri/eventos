from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    path('', views.main, name='main'),
    path('programacao', views.programacao, name='programacao'),
    path('criar_evento', views.criar_evento, name='criar_evento'),
    path('evento/<int:id>', views.detalhe_evento, name='evento'),
    path('evento/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('evento/<int:evento_id>/excluir/', views.excluir_evento, name='excluir_evento'),
    path('evento/<int:evento_id>/criar-atividade/', views.criar_atividade, name='criar_atividade'),
    path('atividade/<int:atividade_id>/editar/', views.editar_atividade, name='editar_atividade'),
    path('atividade/<int:atividade_id>/excluir/', views.excluir_atividade, name='excluir_atividade'),
    path('minha_agenda', views.minha_agenda, name='minha_agenda'),
]