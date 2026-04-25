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
        # A tabela Lançamentos agora usa as tentativas em lote
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                atividade_id INTEGER,
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
                FOREIGN KEY (intercorrencia1_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
                FOREIGN KEY (intercorrencia2_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
                FOREIGN KEY (intercorrencia3_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
                FOREIGN KEY (intercorrencia4_id) REFERENCES intercorrencias (id) ON DELETE SET NULL,
                FOREIGN KEY (intercorrencia5_id) REFERENCES intercorrencias (id) ON DELETE SET NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        """Busca os lançamentos unindo os nomes de alunos, professores e atividades."""
        conn = get_db()
        Lancamento.create_table()

        query = '''
            SELECT l.*, a.nome as aluno_nome, p.nome_completo as professor_nome,
                   act.sigla as atividade_sigla
            FROM lancamentos l
            JOIN alunos a ON l.aluno_id = a.id
            JOIN professores p ON l.professor_id = p.id
            LEFT JOIN atividades act ON l.atividade_id = act.id
            ORDER BY l.data_lancamento DESC, l.id DESC
        '''
        lancamentos = conn.execute(query).fetchall()
        conn.close()
        return lancamentos

    @staticmethod
    def create(aluno_id, professor_id, atividade_id, data_lancamento, t1, t2, t3, t4, t5, i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs):
        conn = get_db()
        Lancamento.create_table()
        conn.execute('''
            INSERT INTO lancamentos (
                aluno_id, professor_id, atividade_id, data_lancamento,
                tentativa1, tentativa2, tentativa3, tentativa4, tentativa5,
                intercorrencia1_id, int_nota1, intercorrencia2_id, int_nota2,
                intercorrencia3_id, int_nota3, intercorrencia4_id, int_nota4,
                intercorrencia5_id, int_nota5, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (aluno_id, professor_id, atividade_id, data_lancamento, t1, t2, t3, t4, t5, i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs))
        conn.commit()
        conn.close()

    @staticmethod
    def create_many(lancamentos_dados):
        """
        Insere uma lista de lançamentos no banco de dados de forma otimizada.
        lancamentos_dados deve ser uma lista de dicionarios ou tuplas com os campos certos.
        """
        if not lancamentos_dados:
            return

        conn = get_db()
        Lancamento.create_table()
        conn.executemany('''
            INSERT INTO lancamentos (
                aluno_id, professor_id, atividade_id, data_lancamento,
                tentativa1, tentativa2, tentativa3, tentativa4, tentativa5,
                intercorrencia1_id, int_nota1, intercorrencia2_id, int_nota2,
                intercorrencia3_id, int_nota3, intercorrencia4_id, int_nota4,
                intercorrencia5_id, int_nota5, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        query = '''
            SELECT l.*,
                   a.nome as aluno_nome,
                   p.nome_completo as professor_nome,
                   act.sigla as atividade_sigla,
                   COALESCE(l.tentativa1, 0) + COALESCE(l.tentativa2, 0) + COALESCE(l.tentativa3, 0) + COALESCE(l.tentativa4, 0) + COALESCE(l.tentativa5, 0) as soma_atividades,
                   COALESCE(l.int_nota1, 0) + COALESCE(l.int_nota2, 0) + COALESCE(l.int_nota3, 0) + COALESCE(l.int_nota4, 0) + COALESCE(l.int_nota5, 0) as soma_intercorrencias
            FROM lancamentos l
            JOIN alunos a ON l.aluno_id = a.id
            JOIN professores p ON l.professor_id = p.id
            LEFT JOIN atividades act ON l.atividade_id = act.id
            WHERE 1=1
        '''
        params = []

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

        if filtros.get('atividades_ids'):
            # Permite filtrar por múltiplas atividades (IN clause)
            placeholders = ','.join('?' for _ in filtros['atividades_ids'])
            query += f' AND l.atividade_id IN ({placeholders})'
            params.extend(filtros['atividades_ids'])

        query += ' ORDER BY l.data_lancamento ASC, l.id ASC'

        lancamentos = conn.execute(query, params).fetchall()
        conn.close()
        return lancamentos
        
    @staticmethod
    def delete(lancamento_id):
        conn = get_db()
        conn.execute('DELETE FROM lancamentos WHERE id = ?', (lancamento_id,))
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_by_id(lancamento_id):
        conn = get_db()
        lancamento = conn.execute('SELECT * FROM lancamentos WHERE id = ?', (lancamento_id,)).fetchone()
        conn.close()
        return lancamento
        
    @staticmethod
    def update(lanc_id, t1, t2, t3, t4, t5, i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs):
        conn = get_db()
        conn.execute('''
            UPDATE lancamentos 
            SET tentativa1=?, tentativa2=?, tentativa3=?, tentativa4=?, tentativa5=?,
                intercorrencia1_id=?, int_nota1=?, intercorrencia2_id=?, int_nota2=?,
                intercorrencia3_id=?, int_nota3=?, intercorrencia4_id=?, int_nota4=?,
                intercorrencia5_id=?, int_nota5=?, observacoes=?
            WHERE id=?
        ''', (t1, t2, t3, t4, t5, i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs, lanc_id))
        conn.commit()
        conn.close()