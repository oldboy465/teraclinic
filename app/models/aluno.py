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

    @staticmethod
    def create(nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto=None):
        """Insere um novo aluno no banco de dados."""
        conn = get_db()
        conn.execute('''
            INSERT INTO alunos (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto))
        conn.commit()
        conn.close()

    @staticmethod
    def update(aluno_id, nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto=None):
        """Atualiza os dados de um aluno existente."""
        conn = get_db()
        
        # Se uma nova foto foi enviada, atualiza a foto também. Senão, mantém a antiga.
        if foto:
            conn.execute('''
                UPDATE alunos SET nome = ?, data_nascimento = ?, terapeuta_id = ?, 
                sexo = ?, preferencias = ?, evitaveis = ?, informacoes_adicionais = ?, foto = ?
                WHERE id = ?
            ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto, aluno_id))
        else:
            conn.execute('''
                UPDATE alunos SET nome = ?, data_nascimento = ?, terapeuta_id = ?, 
                sexo = ?, preferencias = ?, evitaveis = ?, informacoes_adicionais = ?
                WHERE id = ?
            ''', (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, aluno_id))
            
        conn.commit()
        conn.close()

    @staticmethod
    def delete(aluno_id):
        """Remove um aluno do sistema."""
        conn = get_db()
        conn.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
        conn.commit()
        conn.close()