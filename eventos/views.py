from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Evento, Atividade, InscricaoEvento, InscricaoAtividade
from .forms import EventoForm, AtividadeForm

from django.db.models import Count, F, Case, When, Value, IntegerField, Exists, OuterRef

def main(request):
    return render(request, "eventos/main.html")

def programacao(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/programacao.html', {'eventos': eventos})

def detalhe_evento(request, id):
    evento = get_object_or_404(Evento, id=id)

    inscrito_no_evento = False
    atividades = Atividade.objects.filter(evento=evento)

    if request.user.is_authenticated:
        inscrito_no_evento = InscricaoEvento.objects.filter(
            evento=evento,
            participante=request.user
        ).exists()

        atividades = atividades.annotate(
            ja_inscrito=Exists(
                InscricaoAtividade.objects.filter(
                    atividade=OuterRef('pk'),
                    inscricao_evento__evento=evento,
                    inscricao_evento__participante=request.user
                )
            )
        )

    return render(request, 'eventos/detalhe_evento.html', {
        'evento': evento,
        'atividades': atividades,
        'inscrito_no_evento': inscrito_no_evento,
    })

@login_required
def minha_agenda(request):
    inscricoes_eventos = InscricaoEvento.objects.filter(participante = request.user)

    return render(request, 'eventos/minha_agenda.html', {'inscricoes_eventos': inscricoes_eventos})

@login_required
def criar_evento(request):
    if not request.user.groups.filter(name="Organizadores").exists():
        return redirect('eventos:main')

    if request.method == 'POST':
        form = EventoForm(request.POST)

        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
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

    if evento.organizador != request.user:
        return redirect('eventos:main')

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

    if evento.organizador != request.user:
        return redirect('eventos:main')

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

    if evento.organizador != request.user:
        return redirect('eventos:main')

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

    if evento.organizador != request.user:
        return redirect('eventos:main')

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

    if evento.organizador != request.user:
        return redirect('eventos:main')

    if request.method == 'POST':
        atividade.delete()
        messages.success(request,'Atividade excluída com sucesso!')

        return redirect('eventos:programacao')

    return render(request,'eventos/excluir_atividade.html', {'atividade': atividade,'evento': evento})

@login_required
def inscrever_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        inscricao_existente = InscricaoEvento.objects.filter(
            evento=evento,
            participante=request.user
        )

        if inscricao_existente.exists():
            messages.error(request, 'Você já está inscrito neste evento.')
            return redirect("eventos:programacao")

        if not evento.inscricoes_abertas:
            messages.error(request, 'As inscrições deste evento estão fechadas.')
            return redirect("eventos:programacao")

        InscricaoEvento.objects.create(
            evento=evento,
            participante=request.user
        )

        return redirect("eventos:programacao")

    return render(request, 'eventos/inscrever-se_evento.html')

@login_required
def inscrever_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)

    inscricao_evento = InscricaoEvento.objects.filter(
        evento=atividade.evento,
        participante=request.user
    ).first()

    if not inscricao_evento:
        messages.error(request, 'Você não está inscrito neste evento.')
        return redirect("eventos:programacao")

    if request.method == "POST":
        inscricao_existente = InscricaoAtividade.objects.filter(
            inscricao_evento=inscricao_evento,
            atividade=atividade
        ).exists()

        if inscricao_existente:
            messages.error(request, 'Você já está inscrito nesta atividade.')
            return redirect("eventos:programacao")

        quantidade_inscritos = InscricaoAtividade.objects.filter(
            atividade=atividade
        ).count()

        capacidade_sala = atividade.sala.capacidade

        if quantidade_inscritos >= capacidade_sala:
            messages.error(request, 'A sala está lotada.')
            return redirect("eventos:programacao")

        InscricaoAtividade.objects.create(
            inscricao_evento=inscricao_evento,
            atividade=atividade
        )

        return redirect("eventos:programacao")

    return render(request, 'eventos/inscrever-se_atividade.html')

@login_required
def desinscrever_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    inscricao_evento = InscricaoEvento.objects.filter(evento=evento, participante=request.user).first()

    if not inscricao_evento:
        messages.error(request, 'Você não está inscrito neste evento.')
        return redirect("eventos:programacao")

    if request.method == "POST":
        InscricaoAtividade.objects.filter(inscricao_evento=inscricao_evento).delete()
        inscricao_evento.delete()
        messages.success(request, 'Você saiu do evento e de todas as suas atividades.')

        return redirect("eventos:programacao")

    return render(request, 'eventos/desinscrever-se_evento.html', {'evento': evento})

@login_required
def desinscrever_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    inscricao_evento = InscricaoEvento.objects.filter(evento=atividade.evento, participante=request.user).first()

    if not inscricao_evento:
        messages.error(request, 'Você não está inscrito neste evento.')
        return redirect("eventos:programacao")

    inscricao = InscricaoAtividade.objects.filter(inscricao_evento=inscricao_evento, atividade=atividade).first()

    if not inscricao:
        messages.error(request, 'Você não está inscrito nesta atividade.')
        return redirect("eventos:programacao")

    if request.method == "POST":
        inscricao.delete()
        messages.success(request,'Você saiu da atividade com sucesso.')
        return redirect("eventos:programacao")

    return render(request, 'eventos/desinscrever-se_atividade.html', {'atividade': atividade})

@login_required
def painel_organizador(request):
    atividades = Atividade.objects.filter(responsavel = request.user).annotate(
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

    return render(request, 'eventos/painel_organizador.html', {'atividades': atividades})