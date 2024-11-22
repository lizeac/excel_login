from django.db import models

class LoginRecord(models.Model):
    matricula = models.CharField(max_length=15)
    nome_completo = models.CharField(max_length=100)
    servico = models.CharField(max_length=100)
    data_acesso = models.DateField()
    hora_acesso = models.TimeField()
    visitante = models.CharField(max_length=50)
    curso = models.CharField(max_length=20)


    def __str__(self):
        return self.nome_completo