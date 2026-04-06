[14:05, 06/04/2026] Michele 🦋: def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos ou se todos são iguais
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10

    # Verifica se os dígitos calculados batem com os informados
    return dig1 == int(cpf[9]) and dig2 == int(cpf[10])
[14:06, 06/04/2026] Michele 🦋: cpf = "123.456.789-09"
if validar_cpf(cpf):
    print("CPF válido")
else:
    print("CPF inválido")