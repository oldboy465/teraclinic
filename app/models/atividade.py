# app/models/atividade.py
from database import get_db

class Atividade:
    """
    Classe Model para gerenciar o catálogo de Atividades.
    """

    @staticmethod
    def get_all():
        conn = get_db()
        atividades = conn.execute('SELECT * FROM atividades ORDER BY sigla ASC').fetchall()
        conn.close()
        return atividades

    @staticmethod
    def get_by_id(atividade_id):
        conn = get_db()
        atividade = conn.execute('SELECT * FROM atividades WHERE id = ?', (atividade_id,)).fetchone()
        conn.close()
        return atividade

    @staticmethod
    def create(sigla, descricao, informacoes_adicionais):
        conn = get_db()
        conn.execute('''
            INSERT INTO atividades (sigla, descricao, informacoes_adicionais)
            VALUES (?, ?, ?)
        ''', (sigla, descricao, informacoes_adicionais))
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