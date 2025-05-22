from django.db import models

class LoginRecord(models.Model):
    matricula = models.CharField(max_length=15)
    nome_completo = models.CharField(max_length=100)
    servico = models.CharField(max_length=100)
    data_acesso = models.DateField()
    hora_acesso = models.TimeField()
    visitante = models.CharField(max_length=50)
    curso = models.CharField(max_length=20)
    dia_da_semana = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if self.data_acesso:
            # Extrai o nome do dia em inglês
            dia_em_ingles = self.data_acesso.strftime('%A')  # Monday, Tuesday...

            # Traduz para português (completo)
            tradutor = {
                'Monday': 'Segunda-feira',
                'Tuesday': 'Terça-feira',
                'Wednesday': 'Quarta-feira',
                'Thursday': 'Quinta-feira',
                'Friday': 'Sexta-feira',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo',
            }

            self.dia_da_semana = tradutor.get(dia_em_ingles, 'Desconhecido')
        super().save(*args, **kwargs)



    def __str__(self):
        return self.nome_completo
    
