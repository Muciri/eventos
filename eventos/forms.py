from django import forms
from .models import Evento, Atividade

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome', 'descricao', 'inicio', 'fim', 'inscricoes_abertas']
        widgets = {
            'inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'fim': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }

# class AtividadeForm(forms.ModelForm):
#     class Meta:
#         model = Atividade
#         fields = ['evento', 'titulo', 'tipo', 'descricao', 'responsavel', 'sala', 'inicio', 'fim',]
#         widgets = {
#             'inicio': forms.DateTimeInput(
#                 attrs={'type': 'datetime-local'}
#             ),
#             'fim': forms.DateTimeInput(
#                 attrs={'type': 'datetime-local'}
#             ),
#         }

class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['titulo', 'tipo', 'descricao', 'responsavel', 'sala', 'inicio', 'fim',]
        widgets = {
            'inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'fim': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ), 
        }