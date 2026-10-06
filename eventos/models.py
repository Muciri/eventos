from django.conf import settings
from django.db import models

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    bloco = models.CharField(max_length=50)
    capacidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nome} - Bloco {self.bloco}"

class Evento(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    inscricoes_abertas = models.BooleanField(default=True)

    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eventos_organizados"
    )

    def __str__(self):
        return self.nome

class Atividade(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="atividades"
    )
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="atividades_responsaveis"
    )

    sala = models.ForeignKey(
        Sala,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades"
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField()

    def __str__(self):
        return self.titulo

class InscricaoEvento(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="inscricoes"
    )

    participante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inscricoes_eventos"
    )

    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evento", "participante"],
                name="inscricao_unica_evento"
            )
        ]

    def __str__(self):
        return f"{self.participante} - {self.evento}"

class InscricaoAtividade(models.Model):
    inscricao_evento = models.ForeignKey(
        InscricaoEvento,
        on_delete=models.CASCADE,
        related_name="inscricoes_atividades"
    )
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        related_name="inscricoes"
    )
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["inscricao_evento", "atividade"],
                name="inscricao_unica_atividade"
            )
        ]

    def __str__(self):
        return f"{self.inscricao_evento.participante} - {self.atividade.titulo}"