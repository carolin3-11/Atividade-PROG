import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="biblioteca.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
         
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS autores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    nacionalidade TEXT
                )
            """)
            
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS livros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    ano_publicacao INTEGER,
                    autor_id INTEGER NOT NULL,
                    FOREIGN KEY (autor_id) REFERENCES autores(id) ON DELETE CASCADE
                )
            """)
            
    
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emprestimos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    livro_id INTEGER NOT NULL,
                    usuario TEXT NOT NULL,
                    data_emprestimo TEXT NOT NULL,
                    data_devolucao TEXT,
                    FOREIGN KEY (livro_id) REFERENCES livros(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

class AutorRepo:
    def __init__(self, db):
        self.db = db

    def criar(self, nome, nacionalidade):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO autores (nome, nacionalidade) VALUES (?, ?)", (nome, nacionalidade))

    def listar(self):
        with self.db.get_connection() as conn:
            return conn.execute("SELECT * FROM autores").fetchall()

    def atualizar(self, id_autor, nome, nacionalidade):
        with self.db.get_connection() as conn:
            conn.execute("UPDATE autores SET nome = ?, nacionalidade = ? WHERE id = ?", (nome, nacionalidade, id_autor))

    def deletar(self, id_autor):
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM autores WHERE id = ?", (id_autor,))


class LivroRepo:
    def __init__(self, db):
        self.db = db

    def criar(self, titulo, ano, autor_id):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO livros (titulo, ano_publicacao, autor_id) VALUES (?, ?, ?)", (titulo, ano, autor_id))

    def listar(self):
        with self.db.get_connection() as conn:
            # INNER JOIN para trazer o nome do autor
            return conn.execute("""
                SELECT l.id, l.titulo, l.ano_publicacao, a.nome 
                FROM livros l 
                INNER JOIN autores a ON l.autor_id = a.id
            """).fetchall()

    def atualizar(self, id_livro, titulo, ano, autor_id):
        with self.db.get_connection() as conn:
            conn.execute("UPDATE livros SET titulo = ?, ano_publicacao = ?, autor_id = ? WHERE id = ?", (titulo, ano, autor_id, id_livro))

    def deletar(self, id_livro):
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM livros WHERE id = ?", (id_livro,))


class EmprestimoRepo:
    def __init__(self, db):
        self.db = db

    def criar(self, livro_id, usuario):
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO emprestimos (livro_id, usuario, data_emprestimo) VALUES (?, ?, ?)", (livro_id, usuario, data_atual))

    def listar(self):
        with self.db.get_connection() as conn:
            return conn.execute("""
                SELECT e.id, l.titulo, e.usuario, e.data_emprestimo, e.data_devolucao 
                FROM emprestimos e
                INNER JOIN livros l ON e.livro_id = l.id
            """).fetchall()

    def devolver(self, id_emprestimo):
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        with self.db.get_connection() as conn:
            conn.execute("UPDATE emprestimos SET data_devolucao = ? WHERE id = ?", (data_atual, id_emprestimo))

    def deletar(self, id_emprestimo):
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM emprestimos WHERE id = ?", (id_emprestimo,))

class BibliotecaApp:
    def __init__(self):
        self.db = Database()
        self.autor_repo = AutorRepo(self.db)
        self.livro_repo = LivroRepo(self.db)
        self.emprestimo_repo = EmprestimoRepo(self.db)

    def obter_opcao(self, mensagem, max_opcao):
        while True:
            try:
                opcao = int(input(mensagem))
                if 1 <= opcao <= max_opcao:
                    return opcao
                print(f"Erro: Escolha uma opção entre 1 e {max_opcao}.")
            except ValueError:
                print("Erro: Digite apenas números inteiros.")

    def obter_inteiro(self, mensagem):
        while True:
            try:
                return int(input(mensagem))
            except ValueError:
                print("Erro: Digite um número inteiro válido.")

    def menu_principal(self):
        while True:
            print("\n" + "="*30)
            print("  SISTEMA BIBLIOTECA(MENU)")
            print("="*30)
            print("1. Gerenciar Autores")
            print("2. Gerenciar Livros")
            print("3. Gerenciar Empréstimos")
            print("4. Sair")
            print(""*30)
            
            opcao = self.obter_opcao("Escolha uma opção: ", 4)
            
            if opcao == 1:
                self.menu_autores()
            elif opcao == 2:
                self.menu_livros()
            elif opcao == 3:
                self.menu_emprestimos()
            elif opcao == 4:
                print("\nEncerrando o sistema com segurança. Até logo!")
                break

    
    def menu_autores(self):
        while True:
            print("\n--- GERENCIAR AUTORES ---")
            print("1. Cadastrar Autor")
            print("2. Listar Autores")
            print("3. Atualizar Autor")
            print("4. Excluir Autor")
            print("5. Voltar")
            
            op = self.obter_opcao("Opção: ", 5)
            try:
                if op == 1:
                    nome = input("Nome do Autor: ").strip()
                    nac = input("Nacionalidade: ").strip()
                    if nome:
                        self.autor_repo.criar(nome, nac)
                        print("Autor cadastrado com sucesso!")
                    else:
                        print("Nome não pode ser vazio.")
                elif op == 2:
                    autores = self.autor_repo.listar()
                    print("\nID | Nome | Nacionalidade")
                    for a in autores:
                        print(f"{a[0]} | {a[1]} | {a[2]}")
                elif op == 3:
                    id_a = self.obter_inteiro("ID do Autor a atualizar: ")
                    nome = input("Novo Nome: ").strip()
                    nac = input("Nova Nacionalidade: ").strip()
                    self.autor_repo.atualizar(id_a, nome, nac)
                    print("Autor atualizado com sucesso!")
                elif op == 4:
                    id_a = self.obter_inteiro("ID do Autor a excluir: ")
                    self.autor_repo.deletar(id_a)
                    print("Autor excluído com sucesso (e seus livros correspondentes)!")
                elif op == 5:
                    break
            except sqlite3.Error as e:
                print(f"Erro no Banco de Dados: {e}")

    def menu_livros(self):
        while True:
            print("\n--- GERENCIAR LIVROS ---")
            print("1. Cadastrar Livro")
            print("2. Listar Livros")
            print("3. Atualizar Livro")
            print("4. Excluir Livro")
            print("5. Voltar")
            
            op = self.obter_opcao("Opção: ", 5)
            try:
                if op == 1:
                    titulo = input("Título do Livro: ").strip()
                    ano = self.obter_inteiro("Ano de Publicação: ")
                    autor_id = self.obter_inteiro("ID do Autor: ")
                    if titulo:
                        self.livro_repo.criar(titulo, ano, autor_id)
                        print("Livro cadastrado com sucesso!")
                    else:
                        print("Título não pode ser vazio.")
                elif op == 2:
                    livros = self.livro_repo.listar()
                    print("\nID | Título | Ano | Autor")
                    for l in livros:
                        print(f"{l[0]} | {l[1]} | {l[2]} | {l[3]}")
                elif op == 3:
                    id_l = self.obter_inteiro("ID do Livro a atualizar: ")
                    titulo = input("Novo Título: ").strip()
                    ano = self.obter_inteiro("Novo Ano: ")
                    autor_id = self.obter_inteiro("Novo ID do Autor: ")
                    self.livro_repo.atualizar(id_l, titulo, ano, autor_id)
                    print("Livro atualizado com sucesso!")
                elif op == 4:
                    id_l = self.obter_inteiro("ID do Livro a excluir: ")
                    self.livro_repo.deletar(id_l)
                    print("Livro excluído com sucesso!")
                elif op == 5:
                    break
            except sqlite3.IntegrityError:
                print("Erro: O ID do autor fornecido não existe.")
            except sqlite3.Error as e:
                print(f"Erro no Banco de Dados: {e}")

    def menu_emprestimos(self):
        while True:
            print("\n--- GERENCIAR EMPRÉSTIMOS ---")
            print("1. Registrar Empréstimo")
            print("2. Listar Empréstimos")
            print("3. Registrar Devolução")
            print("4. Excluir Registro de Empréstimo")
            print("5. Voltar")
            
            op = self.obter_opcao("Opção: ", 5)
            try:
                if op == 1:
                    livro_id = self.obter_inteiro("ID do Livro: ")
                    usuario = input("Nome do Usuário: ").strip()
                    if usuario:
                        self.emprestimo_repo.criar(livro_id, usuario)
                        print("Empréstimo registrado com sucesso!")
                    else:
                        print("Nome do usuário não pode ser vazio.")
                elif op == 2:
                    emprestimos = self.emprestimo_repo.listar()
                    print("\nID | Livro | Usuário | Data Empréstimo | Data Devolução")
                    for e in emprestimos:
                        dev = e[4] if e[4] else "Aberto"
                        print(f"{e[0]} | {e[1]} | {e[2]} | {e[3]} | {dev}")
                elif op == 3:
                    id_e = self.obter_inteiro("ID do Empréstimo a devolver: ")
                    self.emprestimo_repo.devolver(id_e)
                    print("Devolução registrada com sucesso!")
                elif op == 4:
                    id_e = self.obter_inteiro("ID do Empréstimo a excluir: ")
                    self.emprestimo_repo.deletar(id_e)
                    print("Registro excluído com sucesso!")
                elif op == 5:
                    break
            except sqlite3.IntegrityError:
                print("Erro: O ID do livro fornecido não existe.")
            except sqlite3.Error as e:
                print(f"Erro no Banco de Dados: {e}")


if __name__ == "__main__":
    app = BibliotecaApp()
    app.menu_principal()