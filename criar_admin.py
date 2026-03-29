# criar_admin.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Pega o caminho absoluto da pasta raiz e entra na pasta 'app'
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
DB_PATH = os.path.join(BASE_DIR, 'tera_database.db')

def criar_usuario_admin():
    print("Iniciando a criação do usuário Administrador...")
    
    # Verifica se o banco existe
    if not os.path.exists(DB_PATH):
        print(f"Erro: O banco de dados não foi encontrado em {DB_PATH}.")
        print("Certifique-se de rodar o app.py pelo menos uma vez antes de criar o admin.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    username = 'admin'
    password_plana = 'allspark'
    
    # Por segurança, NUNCA salvamos a senha em texto puro. Usamos um "Hash".
    password_hash = generate_password_hash(password_plana)

    try:
        # Verifica se o usuário admin já existe
        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            print(f"O usuário '{username}' já existe. Atualizando a senha para o padrão...")
            cursor.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (password_hash, username))
        else:
            print(f"Criando novo usuário '{username}'...")
            cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, password_hash))
            
        conn.commit()
        print("✅ Sucesso! O usuário 'admin' foi configurado com a senha 'allspark'.")
    except sqlite3.OperationalError as e:
        print(f"❌ Erro operacional: {e}")
        print("Dica: Você já rodou o script 'atualizar_db.py' para criar a tabela de usuários?")
    finally:
        conn.close()

if __name__ == '__main__':
    criar_usuario_admin()