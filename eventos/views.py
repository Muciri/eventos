from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Evento, Atividade, InscricaoEvento
from .forms import EventoForm, AtividadeForm

from django.db.models import Count, F, Case, When, Value, IntegerField

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
            #evento.organizador = request.user
            evento.save()
            
            messages.success(request, 'Criação do Evento deu certo!')
            return redirect('eventos:programacao')
    else:
        form = EventoForm()

    return render(request, 'eventos/criar_evento.html', {'form':form})

@login_required
def editar_evento(request, evento_id):
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    evento = get_object_or_404(Evento, id=evento_id)

    if evento.organizador != request.user.username:
        return redirect('eventos:main')

    # if evento.organizador != request.user:
    #     return redirect('eventos:main')

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)

        if form.is_valid():
            evento_editado = form.save(commit=False)
            evento_editado.organizador = evento.organizador
            evento_editado.save()
            messages.success(request,'Evento editado com sucesso!')

            return redirect('eventos:programacao')

    else:
        form = EventoForm(instance=evento)

    return render(request,'eventos/editar_evento.html',{'form': form, 'evento': evento})


@login_required
def excluir_evento(request, evento_id):

    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    evento = get_object_or_404(Evento, id=evento_id)

    if evento.organizador != request.user.username:
        return redirect('eventos:main')

    # if evento.organizador != request.user:
    #     return redirect('eventos:main')

    if request.method == 'POST':
        evento.delete()

        messages.success(
            request,
            'Evento excluído com sucesso!'
        )

        return redirect('eventos:programacao')

    return render(
        request,
        'eventos/excluir_evento.html',
        {
            'evento': evento
        }
    )


@login_required
def criar_atividade(request, evento_id):
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    evento = get_object_or_404(Evento, id=evento_id)

    if evento.organizador != request.user.username:
        return redirect('eventos:main')

    # if evento.organizador != request.user:
    #     return redirect('eventos:main')

    if request.method == 'POST':
        form = AtividadeForm(request.POST)

        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.evento = evento

            if atividade.inicio >= atividade.fim:
                messages.error(
                    request,
                    'O início da atividade deve ser anterior ao fim.'
                )

            elif atividade.inicio < evento.inicio or atividade.fim > evento.fim:
                messages.error(
                    request,
                    'A atividade deve estar dentro do horário do evento.'
                )

            else:
                conflito = False

                if atividade.sala:
                    conflito = Atividade.objects.filter(
                        sala=atividade.sala,
                        inicio__lt=atividade.fim,
                        fim__gt=atividade.inicio
                    ).exists()

                if conflito:
                    messages.error(
                        request,
                        'Não é possível criar a atividade: '
                        'já existe outra atividade nessa sala nesse horário.'
                    )
                else:
                    atividade.save()
                    messages.success(
                        request,
                        'Atividade criada com sucesso!'
                    )
                    return redirect('eventos:programacao')

    else:
        form = AtividadeForm()

    return render(
        request,
        'eventos/criar_atividade.html',
        {'form': form, 'evento': evento}
    )

@login_required
def editar_atividade(request, atividade_id):
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    atividade = get_object_or_404(Atividade, id=atividade_id)

    evento = atividade.evento

    if evento.organizador != request.user.username:
        return redirect('eventos:main')

    # if evento.organizador != request.user:
    #     return redirect('eventos:main')

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade)

        if form.is_valid():
            atividade_editada = form.save(commit=False)

            if atividade_editada.inicio >= atividade_editada.fim:
                messages.error(request, 'O início da atividade deve ser anterior ao fim.')

            elif (atividade_editada.inicio < evento.inicio or atividade_editada.fim > evento.fim):
                messages.error(request, 'A atividade deve estar dentro do horário do evento.')

            else:
                conflito = False

                if atividade_editada.sala:
                    conflito = Atividade.objects.filter(
                        sala=atividade_editada.sala,
                        inicio__lt=atividade_editada.fim,
                        fim__gt=atividade_editada.inicio
                    ).exclude(
                        id=atividade.id
                    ).exists()

                if conflito:
                    messages.error(
                        request, 'Não é possível editar a atividade: ' 'já existe outra atividade nessa sala nesse horário.')
                else:
                    atividade_editada.evento = evento
                    atividade_editada.save()

                    messages.success(request, 'Atividade editada com sucesso!')

                    return redirect('eventos:programacao')

    else:
        form = AtividadeForm(instance=atividade)

    return render(request, 'eventos/editar_atividade.html', {'form': form, 'atividade': atividade, 'evento': evento})

@login_required
def excluir_atividade(request, atividade_id):
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    atividade = get_object_or_404(Atividade,id=atividade_id)

    evento = atividade.evento

    if evento.organizador != request.user.username:
        return redirect('eventos:main')

    # if evento.organizador != request.user:
    #     return redirect('eventos:main')

    if request.method == 'POST':
        atividade.delete()
        messages.success(request,'Atividade excluída com sucesso!')

        return redirect('eventos:programacao')

    return render(request,'eventos/excluir_atividade.html', {'atividade': atividade,'evento': evento})

@login_required
def painel_organizador(request):
    atividades = Atividade.objects.filter(responsavel = request.user.username).annotate(
        quantidade_inscritos = Count("inscricoes")
    ).annotate(
    vagas_restantes=Case(
        When(
            sala__isnull=False,
            then=F("sala__capacidade") - F("quantidade_inscritos")
        ),
        default=Value(None),
        output_field=IntegerField()
    ))

    # atividades = Atividade.objects.filter(responsavel = request.user).annotate(
    #     quantidade_inscritos = Count("inscricoes")
    # ).annotate(
    # vagas_restantes=Case(
    #     When(
    #         sala__isnull=False,
    #         then=F("sala__capacidade") - F("quantidade_inscritos")
    #     ),
    #     default=Value(None),
    #     output_field=IntegerField()
    # ))

    return render(request, 'eventos/painel_organizador.html', {'atividades': atividades})