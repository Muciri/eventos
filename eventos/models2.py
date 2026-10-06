from django.db import models
from datetime import datetime

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.nome}'

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100)
    carga_horaria = models.IntegerField(max=100)
    ativo = models.BooleanField()

    categoria_id = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="categoria"
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return f'{self.nome}'

class Aluno(models.Model):
    nome = models.CharField(max_length=100,)
    email = models.EmailField(help_text="insira seu email")
    data_cadastro = models.DateField(default=datetime.now())

    cursos = models.ManyToManyField(
        Curso,
        related_name="cursos",
        blank=True
    )

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome'],
                name="categoria_nome_unico"
            )
        ]

    def __str__(self):
        return f'{self.nome}'

class PerfilAluno():
    telefone = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    biografia = models.TextField()

    aluno_id = models.OneToOneField(
        Aluno,
        on_delete=models.CASCADE,
        related_name="aluno"
    )

    def __str__(self):
        return f'perfil de: {self.aluno_id}'
