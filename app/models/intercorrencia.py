# app/models/intercorrencia.py
from database import get_db

class Intercorrencia:
    """
    Classe Model para gerenciar o catálogo de Intercorrências.
    """

    @staticmethod
    def get_all():
        conn = get_db()
        intercorrencias = conn.execute('SELECT * FROM intercorrencias ORDER BY sigla ASC').fetchall()
        conn.close()
        return intercorrencias

    @staticmethod
    def get_by_id(intercorrencia_id):
        conn = get_db()
        intercorrencia = conn.execute('SELECT * FROM intercorrencias WHERE id = ?', (intercorrencia_id,)).fetchone()
        conn.close()
        return intercorrencia

    @staticmethod
    def create(sigla, descricao, informacoes_adicionais):
        conn = get_db()
        conn.execute('''
            INSERT INTO intercorrencias (sigla, descricao, informacoes_adicionais)
            VALUES (?, ?, ?)
        ''', (sigla, descricao, informacoes_adicionais))
        conn.commit()
        conn.close()

    @staticmethod
    def update(intercorrencia_id, sigla, descricao, informacoes_adicionais):
        conn = get_db()
        conn.execute('''
            UPDATE intercorrencias SET sigla = ?, descricao = ?, informacoes_adicionais = ?
            WHERE id = ?
        ''', (sigla, descricao, informacoes_adicionais, intercorrencia_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(intercorrencia_id):
        conn = get_db()
        conn.execute('DELETE FROM intercorrencias WHERE id = ?', (intercorrencia_id,))
        conn.commit()
        conn.close()