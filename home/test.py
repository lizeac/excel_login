from datetime import datetime
months_name = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

data_month = datetime.now().strftime('%m')
data_month = int(data_month)
month_name = months_name[data_month-1]

print(month_name)

