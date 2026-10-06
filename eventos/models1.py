from django.db import models

class Evento(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100)
    inicio = models.DateField()
    fim = models.DateField()
    inscricoes_abertas = models.BooleanField()
    organizador = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome}"

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    bloco = models.CharField(max_length=100)
    capacidade = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.nome} - {self.bloco}"

class Atividade(models.Model):
    titulo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    inicio = models.DateField()
    fim = models.DateField()

    evento_id = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="evento"
    )

    sala_id = models.ForeignKey(
        Sala,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades" )

    def __str__(self):
        return f"{self.titulo}"

class InscricaoEvento(models.Model):
    evento_id = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="evento"
    )
    participante = models.CharField(max_length=150)
    data = models.DateField()

    def __str__(self):
        return f"{self.evento} - {self.participante}"

class InscricaoAtividade(models.Model):
    inscricao_evento_id = models.ForeignKey(
        InscricaoEvento,
        on_delete=models.CASCADE,
        related_name="inscricao_atividade"
    )
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        related_name="atividade"
    )
    data = models.DateField()