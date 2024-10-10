from openpyxl import load_workbook


arquivo = r'C:\Users\lizeac\Documents\excel_login\matricula_alunos.xlsx'



try:
    wb = load_workbook(arquivo)
    ws = wb['Alunos']

except FileNotFoundError:
    print(FileExistsError)

c = []
for r in ws:
    for w in r:
        c.append(w.value)



def check_mat(n_matricula):
    is_valid = False
    for item in c:
        if n_matricula in item:
            is_valid = True
            print('Encontrou a matricula')
            return is_valid
    return is_valid



# n_matricula = '224119294'

# print(check_mat("224119294"))
# is_valid = False
# for item in c:
#     print(item)
#     if n_matricula in item:
#         is_valid = True
#         print('Encontrou a matricula', item)





