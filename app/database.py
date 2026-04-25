# app/database.py
import sqlite3
import os

# Pega o caminho absoluto da pasta onde ESTE arquivo (database.py) está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'tera_database.db')

def get_db():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Adicionado timeout para evitar o erro "database is locked".
    """
    conn = sqlite3.connect(DB_NAME, timeout=20, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def init_db():
    """
    Cria as tabelas do sistema caso elas ainda não existam.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Tabela 0: Usuários (Mantida por compatibilidade, mas o login agora foca em professores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Tabela 1: Professores/Terapeutas (Adicionado credenciais de login próprio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            foto TEXT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')

    # Tabela 2: Alunos (Atualizada com campo de Email para o destinatário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento DATE,
            terapeuta_id INTEGER,
            sexo TEXT,
            preferencias TEXT,
            evitaveis TEXT,
            informacoes_adicionais TEXT,
            foto TEXT,
            email TEXT,
            FOREIGN KEY (terapeuta_id) REFERENCES professores (id) ON DELETE SET NULL
        )
    ''')

    # Tabela 3: Atividades (Adicionado vínculo com o professor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT NOT NULL,
            descricao TEXT NOT NULL,
            informacoes_adicionais TEXT,
            professor_id INTEGER,
            FOREIGN KEY (professor_id) REFERENCES professores (id) ON DELETE CASCADE
        )
    ''')

    # Tabela 4: Intercorrências
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intercorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla TEXT NOT NULL,
            descricao TEXT NOT NULL,
            informacoes_adicionais TEXT
        )
    ''')

    # Tabela 5: Lançamentos (Atualizada para suportar as 5 tentativas de notas e intercorrências)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            professor_id INTEGER NOT NULL,
            atividade_id INTEGER,
            nota_atividade INTEGER,
            intercorrencia_id INTEGER,
            nota_intercorrencia INTEGER,
            data_lancamento DATE NOT NULL,
            tentativa1 INTEGER,
            tentativa2 INTEGER,
            tentativa3 INTEGER,
            tentativa4 INTEGER,
            tentativa5 INTEGER,
            intercorrencia1_id INTEGER,
            int_nota1 INTEGER,
            intercorrencia2_id INTEGER,
            int_nota2 INTEGER,
            intercorrencia3_id INTEGER,
            int_nota3 INTEGER,
            intercorrencia4_id INTEGER,
            int_nota4 INTEGER,
            intercorrencia5_id INTEGER,
            int_nota5 INTEGER,
            observacoes TEXT,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE,
            FOREIGN KEY (professor_id) REFERENCES professores (id) ON DELETE CASCADE,
            FOREIGN KEY (atividade_id) REFERENCES atividades (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia1_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia2_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia3_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia4_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
            FOREIGN KEY (intercorrencia5_id) REFERENCES intercorrencias (id) ON DELETE SET NULL
        )
    ''')

    # Tabela 6: Notas Semânticas Dinâmicas (Módulo 5 Editável)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor INTEGER NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')
    
    # Tabela 7: Vínculo N:N entre Aluno e Atividades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aluno_atividades (
            aluno_id INTEGER NOT NULL,
            atividade_id INTEGER NOT NULL,
            PRIMARY KEY (aluno_id, atividade_id),
            FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE,
            FOREIGN KEY (atividade_id) REFERENCES atividades (id) ON DELETE CASCADE
        )
    ''')

    # Preencher notas padrão apenas se a tabela estiver completamente vazia
    cursor.execute("SELECT COUNT(*) FROM notas")
    if cursor.fetchone()[0] == 0:
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

    conn.commit()
    conn.close()