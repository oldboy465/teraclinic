# app/models/professor.py
from database import get_db

class Professor:
    """
    Classe Model responsável por gerenciar os dados dos Professores/Terapeutas.
    """

    @staticmethod
    def get_all():
        """Busca todos os professores cadastrados, ordenados por nome."""
        conn = get_db()
        professores = conn.execute('SELECT * FROM professores ORDER BY nome_completo ASC').fetchall()
        conn.close()
        return professores

    @staticmethod
    def get_by_id(professor_id):
        """Busca um professor específico pelo seu ID."""
        conn = get_db()
        professor = conn.execute('SELECT * FROM professores WHERE id = ?', (professor_id,)).fetchone()
        conn.close()
        return professor

    @staticmethod
    def create(nome_completo, telefone, email, foto=None):
        """Insere um novo professor no banco de dados."""
        conn = get_db()
        conn.execute('''
            INSERT INTO professores (nome_completo, telefone, email, foto)
            VALUES (?, ?, ?, ?)
        ''', (nome_completo, telefone, email, foto))
        conn.commit()
        conn.close()

    @staticmethod
    def update(professor_id, nome_completo, telefone, email, foto=None):
        """Atualiza os dados de um professor."""
        conn = get_db()
        if foto:
            conn.execute('''
                UPDATE professores SET nome_completo = ?, telefone = ?, email = ?, foto = ?
                WHERE id = ?
            ''', (nome_completo, telefone, email, foto, professor_id))
        else:
            conn.execute('''
                UPDATE professores SET nome_completo = ?, telefone = ?, email = ?
                WHERE id = ?
            ''', (nome_completo, telefone, email, professor_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(professor_id):
        """Remove um professor do sistema."""
        conn = get_db()
        conn.execute('DELETE FROM professores WHERE id = ?', (professor_id,))
        conn.commit()
        conn.close()