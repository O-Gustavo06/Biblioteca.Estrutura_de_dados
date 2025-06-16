class usuario:
    def __init__(self, nome, idade, documento, telefone):
        # Validação do CPF (11 dígitos)
        if len(str(documento)) != 11:
            raise ValueError("CPF deve ter 11 digitos")
        # Validação do telefone (11 dígitos)
        if len(str(telefone)) != 11:
            raise ValueError(("Telefone não esta completo"))
        # Validação da idade (número positivo e razoável)
        if idade > 120:
            raise ValueError()

        self.nome = nome
        self.idade = idade
        self.documento = documento
        self.telefone = telefone
        self.aprovado = idade >= 18