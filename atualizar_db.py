# atualizar_db.py
import sqlite3
import os

# Pega o caminho absoluto da pasta raiz e entra na pasta 'app'
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
DB_PATH = os.path.join(BASE_DIR, 'tera_database.db')

def atualizar_banco():
    print("Iniciando verificação e atualização do Banco de Dados...")
    
    # Se o banco não existir, criamos a conexão mesmo assim (ele será criado vazio)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Criar a Tabela de Usuários (se não existir)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        print("✅ Tabela 'usuarios' verificada/criada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar tabela de usuários: {e}")

    # 2. Exemplo prático de como adicionar uma coluna no futuro sem perder dados
    try:
        # Pega as informações da tabela professores
        cursor.execute("PRAGMA table_info(professores)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        if 'status_ativo' not in colunas:
            cursor.execute("ALTER TABLE professores ADD COLUMN status_ativo INTEGER DEFAULT 1")
            print("✅ Coluna 'status_ativo' adicionada à tabela 'professores'.")
        else:
            print("✔️ A coluna 'status_ativo' já existe na tabela 'professores'.")
            
        # NOVA MUDANÇA (CORRIGIDA): Adicionando dados de login para professores
        if 'username' not in colunas:
            # SQLite não aceita ADD COLUMN com UNIQUE. 
            # A solução é criar a coluna normal e depois adicionar um UNIQUE INDEX.
            cursor.execute("ALTER TABLE professores ADD COLUMN username TEXT")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_prof_username ON professores(username)")
            print("✅ Coluna 'username' adicionada à tabela 'professores' com índice único.")
            
        if 'password_hash' not in colunas:
            cursor.execute("ALTER TABLE professores ADD COLUMN password_hash TEXT")
            print("✅ Coluna 'password_hash' adicionada à tabela 'professores'.")

    except Exception as e:
        print(f"❌ Erro ao atualizar tabela de professores: {e}")
        
    # NOVA MUDANÇA: Adicionando vínculo de professor na tabela de atividades
    try:
        cursor.execute("PRAGMA table_info(atividades)")
        colunas_atv = [info[1] for info in cursor.fetchall()]
        if 'professor_id' not in colunas_atv:
            cursor.execute("ALTER TABLE atividades ADD COLUMN professor_id INTEGER REFERENCES professores(id) ON DELETE CASCADE")
            print("✅ Coluna 'professor_id' adicionada à tabela 'atividades'.")
    except Exception as e:
        print(f"❌ Erro ao atualizar tabela de atividades: {e}")

    # 3. CRIAR A TABELA DE NOTAS SEMÂNTICAS (NOVIDADE)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                valor INTEGER NOT NULL,
                descricao TEXT NOT NULL
            )
        ''')
        print("✅ Tabela 'notas' verificada/criada com sucesso.")
        
        # Popula a tabela com os valores padrão se ela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM notas")
        if cursor.fetchone()[0] == 0:
            print("Populando tabela 'notas' com os valores iniciais...")
            notas_padrao = [
                ('atividade', 0, "Não realizou a atividade"),
                ('atividade', 1, "Realizou com total suporte físico e verbal"),
                ('atividade', 2, "Realizou com muito suporte físico"),
                ('atividade', 3, "Realizou com suporte físico moderado"),
                ('atividade', 4, "Realizou com suporte físico leve"),
                ('atividade', 5, "Realizou com muito suporte verbal"),
                ('atividade', 6, "Realizou com suporte verbal moderado"),
                ('atividade', 7, "Realizou com suporte verbal leve"),
                ('atividade', 8, "Realizou com dicas visuais/gestuais"),
                ('atividade', 9, "Realizou quase de forma independente (hesitou)"),
                ('atividade', 10, "Realizou de forma totalmente independente"),
                ('intercorrencia', 0, "Nenhuma ocorrência"),
                ('intercorrencia', 1, "Mínima: Resolvida instantaneamente"),
                ('intercorrencia', 2, "Muito Leve: Rápida distração"),
                ('intercorrencia', 3, "Leve: Necessitou de redirecionamento simples"),
                ('intercorrencia', 4, "Leve/Moderada: Resistência breve"),
                ('intercorrencia', 5, "Moderada: Necessitou de pausa na terapia"),
                ('intercorrencia', 6, "Moderada/Alta: Resistência prolongada"),
                ('intercorrencia', 7, "Alta: Desregulação emocional evidente"),
                ('intercorrencia', 8, "Muito Alta: Crise moderada, difícil de acalmar"),
                ('intercorrencia', 9, "Severa: Risco leve a si ou terceiros, crise longa"),
                ('intercorrencia', 10, "Extrema: Crise severa, necessidade de contenção/interrupção total")
            ]
            cursor.executemany("INSERT INTO notas (tipo, valor, descricao) VALUES (?, ?, ?)", notas_padrao)
            print("✅ Valores padrão de notas inseridos com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar/popular tabela de notas: {e}")

    conn.commit()
    conn.close()
    print("🚀 Atualização do banco de dados concluída!")

if __name__ == '__main__':
    atualizar_banco()