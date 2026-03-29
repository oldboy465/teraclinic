# app/models/nota.py
from database import get_db

class NotaSemantica:
    """
    Classe Model responsável pelo CRUD das Notas Semânticas do sistema.
    As notas deixaram de ser fixas e agora são editáveis pelo banco de dados.
    """

    @staticmethod
    def get_all(tipo=None):
        """Busca todas as notas. Se o tipo for passado ('atividade' ou 'intercorrencia'), filtra por ele."""
        conn = get_db()
        if tipo:
            notas = conn.execute('SELECT * FROM notas WHERE tipo = ? ORDER BY valor ASC', (tipo,)).fetchall()
        else:
            notas = conn.execute('SELECT * FROM notas ORDER BY tipo DESC, valor ASC').fetchall()
        conn.close()
        return notas

    @staticmethod
    def get_by_id(nota_id):
        """Busca uma nota específica para edição."""
        conn = get_db()
        nota = conn.execute('SELECT * FROM notas WHERE id = ?', (nota_id,)).fetchone()
        conn.close()
        return nota

    @staticmethod
    def create(tipo, valor, descricao):
        """Cadastra uma nova nota no dicionário."""
        conn = get_db()
        conn.execute('''
            INSERT INTO notas (tipo, valor, descricao)
            VALUES (?, ?, ?)
        ''', (tipo, valor, descricao))
        conn.commit()
        conn.close()

    @staticmethod
    def update(nota_id, tipo, valor, descricao):
        """Atualiza o valor ou significado de uma nota existente."""
        conn = get_db()
        conn.execute('''
            UPDATE notas SET tipo = ?, valor = ?, descricao = ?
            WHERE id = ?
        ''', (tipo, valor, descricao, nota_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(nota_id):
        """Remove uma nota do dicionário."""
        conn = get_db()
        conn.execute('DELETE FROM notas WHERE id = ?', (nota_id,))
        conn.commit()
        conn.close()

    # =========================================================================
    # MÉTODOS MANTIDOS PARA COMPATIBILIDADE COM A TELA DE LANÇAMENTOS 
    # =========================================================================
    @staticmethod
    def get_notas_atividade():
        """Retorna o dicionário {valor: descricao} de atividades direto do banco."""
        conn = get_db()
        notas = conn.execute("SELECT valor, descricao FROM notas WHERE tipo = 'atividade' ORDER BY valor ASC").fetchall()
        conn.close()
        return {n['valor']: n['descricao'] for n in notas}

    @staticmethod
    def get_notas_intercorrencia():
        """Retorna o dicionário {valor: descricao} de intercorrências direto do banco."""
        conn = get_db()
        notas = conn.execute("SELECT valor, descricao FROM notas WHERE tipo = 'intercorrencia' ORDER BY valor ASC").fetchall()
        conn.close()
        return {n['valor']: n['descricao'] for n in notas}