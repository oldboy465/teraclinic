# app/models/atividade.py
from database import get_db

class Atividade:
    """
    Classe Model para gerenciar o catálogo de Atividades.
    """

    @staticmethod
    def get_all():
        """Busca todas as atividades (visão geral/admin)."""
        conn = get_db()
        atividades = conn.execute('SELECT * FROM atividades ORDER BY sigla ASC').fetchall()
        conn.close()
        return atividades

    # NOVA MUDANÇA: Adicionado método para buscar atividades de um professor específico
    @staticmethod
    def get_by_professor(professor_id):
        """Busca as atividades vinculadas exclusivamente a um professor."""
        conn = get_db()
        atividades = conn.execute('SELECT * FROM atividades WHERE professor_id = ? ORDER BY sigla ASC', (professor_id,)).fetchall()
        conn.close()
        return atividades

    @staticmethod
    def get_by_id(atividade_id):
        conn = get_db()
        atividade = conn.execute('SELECT * FROM atividades WHERE id = ?', (atividade_id,)).fetchone()
        conn.close()
        return atividade

    # NOVA MUDANÇA: Modificado para aceitar o professor_id ao criar
    @staticmethod
    def create(sigla, descricao, informacoes_adicionais, professor_id=None):
        conn = get_db()
        conn.execute('''
            INSERT INTO atividades (sigla, descricao, informacoes_adicionais, professor_id)
            VALUES (?, ?, ?, ?)
        ''', (sigla, descricao, informacoes_adicionais, professor_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update(atividade_id, sigla, descricao, informacoes_adicionais):
        conn = get_db()
        conn.execute('''
            UPDATE atividades SET sigla = ?, descricao = ?, informacoes_adicionais = ?
            WHERE id = ?
        ''', (sigla, descricao, informacoes_adicionais, atividade_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(atividade_id):
        conn = get_db()
        conn.execute('DELETE FROM atividades WHERE id = ?', (atividade_id,))
        conn.commit()
        conn.close()