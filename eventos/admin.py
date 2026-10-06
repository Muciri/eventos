from django.contrib import admin

from .models import (
    Sala,
    Evento,
    Atividade,
    InscricaoEvento,
    InscricaoAtividade,
)


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("nome", "bloco", "capacidade")
    list_filter = ("bloco",)
    search_fields = ("nome", "bloco")
    ordering = ("bloco", "nome")


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "organizador",
        "inicio",
        "fim",
        "inscricoes_abertas",
    )
    list_filter = (
        "inscricoes_abertas",
        "inicio",
    )
    search_fields = (
        "nome",
        "descricao",
        "organizador",
    )
    ordering = ("-inicio",)
    date_hierarchy = "inicio"


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "evento",
        "tipo",
        "responsavel",
        "sala",
        "inicio",
        "fim",
    )
    list_filter = (
        "tipo",
        "evento",
        "sala",
    )
    search_fields = (
        "titulo",
        "descricao",
        "responsavel",
        "evento__nome",
    )
    ordering = ("inicio",)
    date_hierarchy = "inicio"


@admin.register(InscricaoEvento)
class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = (
        "participante",
        "evento",
        "data",
    )
    list_filter = (
        "evento",
        "data",
    )
    search_fields = (
        "participante",
        "evento__nome",
    )
    ordering = ("-data",)
    date_hierarchy = "data"
    readonly_fields = ("data",)


@admin.register(InscricaoAtividade)
class InscricaoAtividadeAdmin(admin.ModelAdmin):
    list_display = (
        "participante",
        "atividade",
        "evento",
        "data",
    )
    list_filter = (
        "atividade",
        "data",
    )
    search_fields = (
        "inscricao_evento__participante",
        "atividade__titulo",
    )
    ordering = ("-data",)
    date_hierarchy = "data"
    readonly_fields = ("data",)

    @admin.display(description="Participante")
    def participante(self, obj):
        return obj.inscricao_evento.participante

    @admin.display(description="Evento")
    def evento(self, obj):
        return obj.atividade.evento.nome
