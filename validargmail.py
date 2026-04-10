import re

def validar_email(email):
    padrao = r'^[\w\.-]+@gmail\.com$'
    return re.match(padrao, email) is not None

# Teste
print(validar_email("teste@gmail.com"))  # True
print(validar_email("teste@outlook.com"))  # False