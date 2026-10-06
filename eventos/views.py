from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Evento, Atividade, InscricaoEvento
from .forms import EventoForm

def main(request):
    return render(request, "eventos/main.html")

def programacao(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/programacao.html', {'eventos': eventos})

def detalhe_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    atividades = Atividade.objects.filter(evento=evento)
    return render(request, 'eventos/detalhe_evento.html', {'evento': evento, 'atividades': atividades})

@login_required
def minha_agenda(request):
    #TODO: atualmente, o model InscricaoEvento só tem o campo 'participante', não uma ForeignKey para um usuario, depois tem que mudar isso.
    #TODO: também mudar aqui pra filtrar inscricoes de eventos do usuario logado, não pegar pelo Username igual
    inscricoes_eventos = InscricaoEvento.objects.filter(participante = request.user.username)

    return render(request, 'eventos/minha_agenda.html', {'inscricoes_eventos': inscricoes_eventos})

@login_required
def criar_evento(request):
    #TODO: atualmente, o model Evento também só tem um campo 'organizador' sem um usuario, só o nome do cara, depois tem que mudar isso e mudar a logica aqui tbm
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    if request.method == 'POST':
        form = EventoForm(request.POST)

        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user.username
            evento.save()
            
            messages.success(request, 'Criação do Evento deu certo!')
            return redirect('eventos:programacao')
    else:
        form = EventoForm()

    return render(request, 'eventos/criar_evento.html', {'form':form})