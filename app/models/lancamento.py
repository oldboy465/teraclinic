# app/models/lancamento.py
from database import get_db

class Lancamento:
    """
    Classe Model para gerenciar os Lançamentos diários (Atividades e Intercorrências dos alunos).
    """

    @staticmethod
    def create_table():
        """Garante que a tabela de lançamentos exista no banco de dados."""
        conn = get_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                atividade_id INTEGER,
                nota_atividade INTEGER,
                intercorrencia_id INTEGER,
                nota_intercorrencia INTEGER,
                data_lancamento DATE NOT NULL,
                FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE,
                FOREIGN KEY (professor_id) REFERENCES professores (id) ON DELETE CASCADE,
                FOREIGN KEY (atividade_id) REFERENCES atividades (id) ON DELETE SET NULL,
                FOREIGN KEY (intercorrencia_id) REFERENCES intercorrencias (id) ON DELETE SET NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        """Busca os lançamentos unindo os nomes de alunos, professores, atividades e intercorrências."""
        conn = get_db()
        # Inicializa a tabela caso seja a primeira vez rodando o model
        Lancamento.create_table() 
        
        query = '''
            SELECT l.*, a.nome as aluno_nome, p.nome_completo as professor_nome,
                   act.sigla as atividade_sigla, intc.sigla as intercorrencia_sigla
            FROM lancamentos l
            JOIN alunos a ON l.aluno_id = a.id
            JOIN professores p ON l.professor_id = p.id
            LEFT JOIN atividades act ON l.atividade_id = act.id
            LEFT JOIN intercorrencias intc ON l.intercorrencia_id = intc.id
            ORDER BY l.data_lancamento DESC, l.id DESC
        '''
        lancamentos = conn.execute(query).fetchall()
        conn.close()
        return lancamentos

    @staticmethod
    def create(aluno_id, professor_id, data_lancamento, atividade_id=None, nota_atividade=None, intercorrencia_id=None, nota_intercorrencia=None):
        conn = get_db()
        Lancamento.create_table()
        conn.execute('''
            INSERT INTO lancamentos (aluno_id, professor_id, atividade_id, nota_atividade, intercorrencia_id, nota_intercorrencia, data_lancamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (aluno_id, professor_id, atividade_id, nota_atividade, intercorrencia_id, nota_intercorrencia, data_lancamento))
        conn.commit()
        conn.close()

    # NOVA MUDANÇA: Método para inserir múltiplos lançamentos de uma vez (Lote)
    @staticmethod
    def create_many(lancamentos_dados):
        """
        Insere uma lista de lançamentos no banco de dados de forma otimizada.
        lancamentos_dados deve ser uma lista de tuplas com a seguinte ordem:
        (aluno_id, professor_id, atividade_id, nota_atividade, intercorrencia_id, nota_intercorrencia, data_lancamento)
        """
        if not lancamentos_dados:
            return

        conn = get_db()
        Lancamento.create_table()
        conn.executemany('''
            INSERT INTO lancamentos (aluno_id, professor_id, atividade_id, nota_atividade, intercorrencia_id, nota_intercorrencia, data_lancamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', lancamentos_dados)
        conn.commit()
        conn.close()

    @staticmethod
    def get_relatorio_avancado(filtros):
        """
        Busca lançamentos aplicando múltiplos filtros dinâmicos.
        Retorna os dados brutos para processamento de gráficos e tabelas.
        """
        conn = get_db()
        Lancamento.create_table()
        
        # O WHERE 1=1 é um truque clássico para facilitar a concatenação dinâmica dos filtros com AND
        query = '''
            SELECT l.*, 
                   a.nome as aluno_nome, 
                   p.nome_completo as professor_nome,
                   act.sigla as atividade_sigla, 
                   intc.sigla as intercorrencia_sigla
            FROM lancamentos l
            JOIN alunos a ON l.aluno_id = a.id
            JOIN professores p ON l.professor_id = p.id
            LEFT JOIN atividades act ON l.atividade_id = act.id
            LEFT JOIN intercorrencias intc ON l.intercorrencia_id = intc.id
            WHERE 1=1
        '''
        params = []

        # Adiciona dinamicamente os parâmetros recebidos
        if filtros.get('data_inicio'):
            query += ' AND l.data_lancamento >= ?'
            params.append(filtros['data_inicio'])
            
        if filtros.get('data_fim'):
            query += ' AND l.data_lancamento <= ?'
            params.append(filtros['data_fim'])

        if filtros.get('aluno_id'):
            query += ' AND l.aluno_id = ?'
            params.append(filtros['aluno_id'])

        if filtros.get('professor_id'):
            query += ' AND l.professor_id = ?'
            params.append(filtros['professor_id'])

        if filtros.get('atividade_id'):
            query += ' AND l.atividade_id = ?'
            params.append(filtros['atividade_id'])

        if filtros.get('intercorrencia_id'):
            query += ' AND l.intercorrencia_id = ?'
            params.append(filtros['intercorrencia_id'])

        # Para os gráficos, é fundamental que a ordem seja cronológica (ASC)
        query += ' ORDER BY l.data_lancamento ASC, l.id ASC'
        
        lancamentos = conn.execute(query, params).fetchall()
        conn.close()
        return lancamentos