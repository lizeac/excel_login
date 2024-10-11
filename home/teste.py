from models import LoginRecord

# Obter todos os registros
todos_os_registros = LoginRecord.objects.all()

# Obter um registro específico (por ID)
registro = LoginRecord.objects.get(id=1)

# Filtrar registros
registros_filtrados = LoginRecord.objects.filter(matricula='123456')

# Contar registros
total_registros = LoginRecord.objects.count()

print(todos_os_registros)