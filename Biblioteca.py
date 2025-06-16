from collections import deque
from livro import livro as Livro
from usuario import usuario as Usuario
from datetime import datetime

class Biblioteca:
    def __init__(self):
        self.livros = []  # Lista
        self.usuarios = []  # Lista
        self.historico_emprestimos = []  # Lista de tuplas
        self.livros_emprestados = set()  # Set
        self.reservas = {}  # Dicionário: isbn -> deque de usuários

    def cadastrar_livro(self, titulo, autor, isbn, valor_emprestimo, faixa_etaria, quantidade, data):
        print("\n--- Cadastro de Livro ---")
        try:
            quantidade = int(quantidade)
            valor_emprestimo = float(valor_emprestimo)
            if valor_emprestimo <= 0:
                raise ValueError("O valor do empréstimo deve ser positivo")
            livro = Livro(titulo, autor, isbn, valor_emprestimo, faixa_etaria, quantidade, data)
            self.livros.append(livro)
            self.reservas[isbn] = deque()
            print(f"Livro '{titulo}' cadastrado com sucesso!")
        except ValueError as e:
            print(f"Erro: {e}")

    def cadastrar_usuario(self, nome, idade, documento, telefone):
        print("\n--- Cadastro de Usuário ---")
        try:
            idade = int(idade)
            if idade <= 0:
                raise ValueError("Idade deve ser um número positivo")
            usuario = Usuario(nome, idade, documento, telefone)
            self.usuarios.append(usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso!")
        except ValueError as e:
            print(f"Erro: {e}")

    def emprestar_livro(self, nome_usuario, titulo_livro, data_emprestimo):
        # Aqui verifica se o livro está disponível
        print("\n--- Empréstimo de Livro ---")
        usuario = self.buscar_usuario_por_nome(nome_usuario)
        livro = self.buscar_livro_por_titulo(titulo_livro)

        if not usuario or not livro:
            print("Usuário ou livro não encontrado.")
            return

        if livro.isbn not in self.livros_emprestados:
            self.livros_emprestados.add(livro.isbn)
            self.historico_emprestimos.append(("empréstimo", titulo_livro, nome_usuario, data_emprestimo))
            print(f"Livro '{titulo_livro}' emprestado para {nome_usuario}!")
            print("Lembrando que a devolução deve ser realidade em 15 dias após o emprestimo!")
        else:
            self.reservas[livro.isbn].append(usuario.nome)
            print(f"Livro indisponível. {nome_usuario} entrou na fila de espera.")

    def calcular_multa(self, data_emprestimo_str, data_devolucao_str, valor_livro):
        try:
            data_emprestimo = datetime.strptime(data_emprestimo_str, "%d/%m/%Y")
            data_devolucao = datetime.strptime(data_devolucao_str, "%d/%m/%Y")
            
            dias_emprestimo = (data_devolucao - data_emprestimo).days
            
            if dias_emprestimo > 15:
                dias_atraso = dias_emprestimo - 15
                multa = dias_atraso * 1.00  # 1 real por dia de atraso
                return valor_livro + multa
            return valor_livro
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA")
            return valor_livro

    def mostrar_historico(self):
        print("\n--- Histórico de Empréstimos ---")
        for registro in self.historico_emprestimos:
            if len(registro) == 4:  # Agora quanto você busca o historico ele mostra a data, tanto entrada e tanto saida
                print(f"{registro[0].upper()}: {registro[1]} -> {registro[2]} em {registro[3]}")
            else:  # Registros antigos sem data tambem mostra
                print(f"{registro[0].upper()}: {registro[1]} -> {registro[2]}")

    def devolver_livro(self, titulo_livro, nome_usuario, data_devolucao):
        print("\n--- Devolução de Livro ---")
        
        livro = self.buscar_livro_por_titulo(titulo_livro)
        if not livro:
            print("Livro não encontrado na biblioteca.")
            return
        
        if livro.isbn in self.livros_emprestados:
            # Encontra a data de empréstimo no histórico
            data_emprestimo = None
            for registro in reversed(self.historico_emprestimos):
                if (registro[0] == "empréstimo" and 
                    registro[1].lower() == titulo_livro.lower() and 
                    registro[2].lower() == nome_usuario.lower()):
                    data_emprestimo = registro[3]
                    break
            
            if data_emprestimo:
                valor_a_pagar = self.calcular_multa(data_emprestimo, data_devolucao, livro.valor_emprestimo)
                print(f"Valor a pagar: R${valor_a_pagar:.2f}")
            
            self.livros_emprestados.remove(livro.isbn)
            self.historico_emprestimos.append(("devolução", titulo_livro, nome_usuario, data_devolucao))
            print(f"Livro '{titulo_livro}' devolvido por {nome_usuario} com sucesso!")
            
            self.atender_fila_reserva(livro.isbn)
        else:
            print("Este livro não está registrado como emprestado.")

    def _buscar_ultimo_usuario_do_livro(self, titulo):
        # Percorre o histórico de trás para frente para encontrar o último empréstimo
        for registro in reversed(self.historico_emprestimos):
            # registro é uma tupla: (acao, livro, usuario)
            if registro[0] == "empréstimo" and registro[1].lower() == titulo.lower():
                return registro[2]
        return None

    def buscar_livro_por_titulo(self, titulo):
        for livro in self.livros:
            if livro.titulo.lower().strip() == titulo.lower().strip():
                return livro
        return None

    def buscar_usuario_por_nome(self, nome):
        for usuario in self.usuarios:
            if usuario.nome.lower().strip() == nome.lower().strip():
                return usuario
        return None

    def editar_livro(self, titulo):
        livro = self.buscar_livro_por_titulo(titulo)
        if livro:
            print("Edite os dados do livro:")
            livro.titulo = input("Título: ")
            livro.autor = input("Autor: ")
            livro.isbn = input("ISBN: ")
            livro.valor_emprestimo = float(input("Valor do empréstimo: "))
            livro.faixa_etaria = input("Faixa Etária: ")
            livro.quantidade = int(input("Quantidade: "))
            print("Livro editado com sucesso!")
        else:
            print("Livro não encontrado.")

    def excluir_livro(self, titulo):
        livro = self.buscar_livro_por_titulo(titulo)
        if livro:
            self.livros.remove(livro)
            self.reservas.pop(livro.isbn, None)
            print("Livro excluído com sucesso!")
        else:
            print("Livro não encontrado.")

    def editar_usuario(self, nome):
        usuario = self.buscar_usuario_por_nome(nome)
        if usuario:
            print("Edite os dados do usuário:")
            usuario.nome = input("Nome: ")
            usuario.idade = int(input("Idade: "))
            usuario.documento = input("Documento: ")
            usuario.telefone = input("Telefone: ")
            print("Usuário editado com sucesso!")
        else:
            print("Usuário não encontrado.")

    def excluir_usuario(self, nome):
        usuario = self.buscar_usuario_por_nome(nome)
        if usuario:
            self.usuarios.remove(usuario)
            print("Usuário excluído com sucesso!")
        else:
            print("Usuário não encontrado.")

    def atender_fila_reserva(self, isbn):
        if isbn in self.reservas and self.reservas[isbn]:
            proximo_usuario = self.reservas[isbn].popleft()
            livro = next((livro for livro in self.livros if livro.isbn == isbn), None)
            if livro:
                print(f"Livro '{livro.titulo}' agora está disponível. Emprestando automaticamente para {proximo_usuario}.")
                self.emprestar_livro(proximo_usuario, livro.titulo, "Data automática")

def main():
    biblioteca = Biblioteca()

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Cadastrar Livro")
        print("2. Cadastrar Usuário")
        print("3. Emprestar Livro")
        print("4. Ver Histórico")
        print("5. Devolver Livro")
        print("6. Buscar Livro")
        print("7. Buscar Usuário")
        print("8. Editar Livro")
        print("9. Excluir Livro")
        print("10. Editar Usuário")
        print("11. Excluir Usuário")
        print("12. Sair")

        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            titulo = input("Digite o título do Livro: ")
            autor = input("Digite o nome do autor: ")
            isbn = input("Digite o ISBN (13 dígitos): ")
            valor_emprestimo = input("Digite o valor do empréstimo do Livro: ")
            faixa_etaria = input("Digite a faixa etária: ")
            quantidade = input("Digite a quantidade: ")
            data = input("Digite a data (DD/MM/AAAA): ")
            biblioteca.cadastrar_livro(titulo, autor, isbn, valor_emprestimo, faixa_etaria, quantidade, data)
        elif opcao == "2":
            nome = input("Digite o nome: ")
            idade = (input("Digite a idade: "))
            documento = input("Digite o CPF: ")
            telefone = input("Digite o telefone: ")
            biblioteca.cadastrar_usuario(nome, idade, documento, telefone)
        elif opcao == "3":
            nome_usuario = input("Nome do usuário: ")
            titulo_livro = input("Título do livro: ")
            data_emprestimo = input("Digite a data que o livro foi emprestado: ")
            biblioteca.emprestar_livro(nome_usuario, titulo_livro, data_emprestimo)
        elif opcao == "4":
            biblioteca.mostrar_historico()
        elif opcao == "5":
            titulo_livro = input("Título do livro para devolução: ")
            nome_usuario = input("Nome do usuário que está realizando a devolução: ")
            data_devolucao = input("Data que o livro está sendo devolvido (DD/MM/AAAA): ")
            biblioteca.devolver_livro(titulo_livro, nome_usuario, data_devolucao)
        elif opcao == "6":
            titulo = input("Título do livro a buscar: ")
            livro = biblioteca.buscar_livro_por_titulo(titulo)
            if livro:
                print("\n--- Livro Encontrado ---")
                print(f"Título: {livro.titulo}\nAutor: {livro.autor}\nISBN: {livro.isbn}")
                print(f"Valor do empréstimo: R${livro.valor_emprestimo:.2f}")
                print(f"Faixa Etária: {livro.faixa_etaria}\nQuantidade: {livro.quantidade}")
            else:
                print("Livro não encontrado.")
        elif opcao == "7":
            nome = input("Nome do usuário a buscar: ")
            usuario = biblioteca.buscar_usuario_por_nome(nome)
            if usuario:
                print("\n--- Usuário Encontrado ---")
                print(f"Nome: {usuario.nome}\nIdade: {usuario.idade}")
                print(f"Documento: {usuario.documento}\nTelefone: {usuario.telefone}")
            else:
                print("Usuário não encontrado.")
        elif opcao == "8":
            titulo = input("Título do livro a editar: ")
            biblioteca.editar_livro(titulo)
        elif opcao == "9":
            titulo = input("Título do livro a excluir: ")
            biblioteca.excluir_livro(titulo)
        elif opcao == "10":
            nome = input("Nome do usuário a editar: ")
            biblioteca.editar_usuario(nome)
        elif opcao == "11":
            nome = input("Nome do usuário a excluir: ")
            biblioteca.excluir_usuario(nome)
        elif opcao == "12":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()