from django import forms
from .models import Evento

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