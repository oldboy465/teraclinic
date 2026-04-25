# app/models/aluno.py
from database import get_db

class Aluno:
    """
    Classe Model responsável por gerenciar a lógica de dados dos Alunos.
    """

    @staticmethod
    def get_all():
        """Busca todos os alunos cadastrados no banco."""
        conn = get_db()
        # Faz um JOIN (junção) para já trazer o nome do terapeuta responsável
        alunos = conn.execute('''
            SELECT a.*, p.nome_completo as terapeuta_nome
            FROM alunos a
            LEFT JOIN professores p ON a.terapeuta_id = p.id
            ORDER BY a.nome ASC
        ''').fetchall()
        conn.close()
        return alunos

    @staticmethod
    def get_by_id(aluno_id):
        """Busca um aluno específico pelo seu ID."""
        conn = get_db()
        aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()
        conn.close()
        return aluno

    # NOVA MUDANÇA: Adicionado filtro para buscar alunos vinculados a um terapeuta específico
    @staticmethod
    def get_by_terapeuta(terapeuta_id):
        """Busca todos os alunos vinculados a um professor/terapeuta específico."""
        conn = get_db()
        alunos = conn.execute('''
            SELECT a.*, p.nome_completo as terapeuta_nome
            FROM alunos a
            LEFT JOIN professores p ON a.terapeuta_id = p.id
            WHERE a.terapeuta_id = ?
            ORDER BY a.nome ASC
        ''', (terapeuta_id,)).fetchall()
        conn.close()
        return alunos

    @staticmethod
    def create(nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto=None, email=None, atividades_ids=[]):
        """Insere um novo aluno no banco de dados e vincula suas atividades."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alunos (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto, email))
        
        aluno_id = cursor.lastrowid
        
        if atividades_ids:
            vinculos = [(aluno_id, int(atv_id)) for atv_id in atividades_ids]
            cursor.executemany('INSERT INTO aluno_atividades (aluno_id, atividade_id) VALUES (?, ?)', vinculos)
            
        conn.commit()
        conn.close()
        return aluno_id

    @staticmethod
    def update(aluno_id, nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto=None, email=None, atividades_ids=[]):
        """Atualiza os dados de um aluno existente e recria seus vínculos de atividades."""
        conn = get_db()
        cursor = conn.cursor()

        # Se uma nova foto foi enviada, atualiza a foto também. Senão, mantém a antiga.
        if foto:
            cursor.execute('''
                UPDATE alunos SET nome = ?, data_nascimento = ?, terapeuta_id = ?,
                sexo = ?, preferencias = ?, evitaveis = ?, informacoes_adicionais = ?, foto = ?, email = ?
                WHERE id = ?
            ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto, email, aluno_id))
        else:
            cursor.execute('''
                UPDATE alunos SET nome = ?, data_nascimento = ?, terapeuta_id = ?,
                sexo = ?, preferencias = ?, evitaveis = ?, informacoes_adicionais = ?, email = ?
                WHERE id = ?
            ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, email, aluno_id))

        # Atualiza vínculos: deleta os antigos e insere os novos
        cursor.execute('DELETE FROM aluno_atividades WHERE aluno_id = ?', (aluno_id,))
        if atividades_ids:
            vinculos = [(aluno_id, int(atv_id)) for atv_id in atividades_ids]
            cursor.executemany('INSERT INTO aluno_atividades (aluno_id, atividade_id) VALUES (?, ?)', vinculos)

        conn.commit()
        conn.close()

    @staticmethod
    def delete(aluno_id):
        """Remove um aluno do sistema."""
        conn = get_db()
        conn.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_atividades_vinculadas(aluno_id):
        """Busca apenas as atividades que o aluno foi selecionado para fazer."""
        conn = get_db()
        atividades = conn.execute('''
            SELECT atv.* FROM atividades atv
            JOIN aluno_atividades aa ON atv.id = aa.atividade_id
            WHERE aa.aluno_id = ?
            ORDER BY atv.sigla ASC
        ''', (aluno_id,)).fetchall()
        conn.close()
        return atividades