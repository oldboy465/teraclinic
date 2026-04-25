# app/controllers/dashboard_controller.py
from flask import Blueprint, render_template, request, jsonify, session
from database import get_db
from controllers.auth_controller import login_required

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    conn = get_db()
    ranking_professores = []

    if session.get('username') == 'admin':
        query_alunos = 'SELECT COUNT(*) FROM alunos'
        query_atividades = 'SELECT COUNT(*) FROM atividades'
        query_intercorrencias = 'SELECT COUNT(*) FROM intercorrencias'
        query_avg_atv = '''
            SELECT AVG(COALESCE(tentativa1,0) + COALESCE(tentativa2,0) + COALESCE(tentativa3,0) + COALESCE(tentativa4,0) + COALESCE(tentativa5,0)) 
            FROM lancamentos
        '''
        query_avg_intc = '''
            SELECT AVG(COALESCE(int_nota1,0) + COALESCE(int_nota2,0) + COALESCE(int_nota3,0) + COALESCE(int_nota4,0) + COALESCE(int_nota5,0)) 
            FROM lancamentos
        '''
        params = ()
        
        ranking_professores = conn.execute('''
            SELECT p.nome_completo, 
                   AVG(COALESCE(l.tentativa1,0) + COALESCE(l.tentativa2,0) + COALESCE(l.tentativa3,0) + COALESCE(l.tentativa4,0) + COALESCE(l.tentativa5,0)) as media_atv,
                   COUNT(DISTINCT a.id) as total_alunos
            FROM professores p
            LEFT JOIN lancamentos l ON p.id = l.professor_id
            LEFT JOIN alunos a ON p.id = a.terapeuta_id
            GROUP BY p.id
            ORDER BY media_atv DESC
        ''').fetchall()
    else:
        prof_id = session.get('user_id')
        query_alunos = 'SELECT COUNT(*) FROM alunos WHERE terapeuta_id = ?'
        query_atividades = 'SELECT COUNT(*) FROM atividades WHERE professor_id = ?'
        query_intercorrencias = 'SELECT COUNT(*) FROM lancamentos WHERE professor_id = ? AND (intercorrencia1_id IS NOT NULL OR intercorrencia2_id IS NOT NULL)'
        query_avg_atv = '''
            SELECT AVG(COALESCE(tentativa1,0) + COALESCE(tentativa2,0) + COALESCE(tentativa3,0) + COALESCE(tentativa4,0) + COALESCE(tentativa5,0)) 
            FROM lancamentos WHERE professor_id = ?
        '''
        query_avg_intc = '''
            SELECT AVG(COALESCE(int_nota1,0) + COALESCE(int_nota2,0) + COALESCE(int_nota3,0) + COALESCE(int_nota4,0) + COALESCE(int_nota5,0)) 
            FROM lancamentos WHERE professor_id = ?
        '''
        params = (prof_id,)

    total_alunos = conn.execute(query_alunos, params if session.get('username') != 'admin' else ()).fetchone()[0]
    total_atividades = conn.execute(query_atividades, params if session.get('username') != 'admin' else ()).fetchone()[0]
    total_intercorrencias = conn.execute(query_intercorrencias, params if session.get('username') != 'admin' else ()).fetchone()[0]

    media_atv_query = conn.execute(query_avg_atv, params if session.get('username') != 'admin' else ()).fetchone()[0]
    media_int_query = conn.execute(query_avg_intc, params if session.get('username') != 'admin' else ()).fetchone()[0]

    media_notas_atividades = round(media_atv_query, 2) if media_atv_query else 0.0
    media_notas_intercorrencias = round(media_int_query, 2) if media_int_query else 0.0

    conn.close()

    return render_template(
        'dashboard.html',
        total_alunos=total_alunos,
        total_atividades=total_atividades,
        total_intercorrencias=total_intercorrencias,
        media_notas_atividades=media_notas_atividades,
        media_notas_intercorrencias=media_notas_intercorrencias,
        ranking_professores=ranking_professores
    )

@dashboard_bp.route('/api/dados_graficos')
@login_required
def api_dados_graficos():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    aluno_id = request.args.get('aluno_id')
    atividade_id = request.args.get('atividade_id')

    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if session.get('username') != 'admin':
        where_clauses.append("professor_id = ?")
        params.append(session.get('user_id'))

    if data_inicio and data_fim:
        where_clauses.append("data_lancamento BETWEEN ? AND ?")
        params.extend([data_inicio, data_fim])
        
    if aluno_id:
        where_clauses.append("aluno_id = ?")
        params.append(aluno_id)
        
    if atividade_id:
        where_clauses.append("atividade_id = ?")
        params.append(atividade_id)

    query_filtro = " WHERE " + " AND ".join(where_clauses)

    query = f'''
        SELECT data_lancamento, atividade_id,
               COALESCE(tentativa1,0) + COALESCE(tentativa2,0) + COALESCE(tentativa3,0) + COALESCE(tentativa4,0) + COALESCE(tentativa5,0) as soma_atividades,
               COALESCE(int_nota1,0) + COALESCE(int_nota2,0) + COALESCE(int_nota3,0) + COALESCE(int_nota4,0) + COALESCE(int_nota5,0) as soma_intercorrencias
        FROM lancamentos
        {query_filtro}
        ORDER BY data_lancamento ASC
    '''

    resultados = conn.execute(query, params).fetchall()
    conn.close()

    dados = [dict(row) for row in resultados]
    return jsonify(dados)