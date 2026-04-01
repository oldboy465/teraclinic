# app/controllers/dashboard_controller.py
from flask import Blueprint, render_template, request, jsonify, session
from database import get_db
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Renderiza a página inicial do Dashboard com as métricas gerais ou exclusivas do professor."""
    conn = get_db()
    
    # NOVA MUDANÇA: Restringe a contagem e visualização pelo ID do professor logado
    if session.get('username') == 'admin':
        query_alunos = 'SELECT COUNT(*) FROM alunos'
        query_atividades = 'SELECT COUNT(*) FROM atividades'
        query_intercorrencias = 'SELECT COUNT(*) FROM intercorrencias'
        query_avg_atv = 'SELECT AVG(nota_atividade) FROM lancamentos WHERE nota_atividade IS NOT NULL'
        query_avg_intc = 'SELECT AVG(nota_intercorrencia) FROM lancamentos WHERE nota_intercorrencia IS NOT NULL'
        params = ()
    else:
        prof_id = session.get('user_id')
        query_alunos = 'SELECT COUNT(*) FROM alunos WHERE terapeuta_id = ?'
        query_atividades = 'SELECT COUNT(*) FROM atividades WHERE professor_id = ?'
        # Intercorrências cadastradas no sistema são globais, mas contaremos quantas vezes ELE lançou intercorrências
        query_intercorrencias = 'SELECT COUNT(*) FROM lancamentos WHERE professor_id = ? AND intercorrencia_id IS NOT NULL'
        query_avg_atv = 'SELECT AVG(nota_atividade) FROM lancamentos WHERE professor_id = ? AND nota_atividade IS NOT NULL'
        query_avg_intc = 'SELECT AVG(nota_intercorrencia) FROM lancamentos WHERE professor_id = ? AND nota_intercorrencia IS NOT NULL'
        params = (prof_id,)
    
    # Métricas Globais (Cards do Dashboard)
    total_alunos = conn.execute(query_alunos, params if session.get('username') != 'admin' else ()).fetchone()[0]
    total_atividades = conn.execute(query_atividades, params if session.get('username') != 'admin' else ()).fetchone()[0]
    total_intercorrencias = conn.execute(query_intercorrencias, params if session.get('username') != 'admin' else ()).fetchone()[0]
    
    # Médias (Atenção para não dividir por zero caso não existam dados)
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
        media_notas_intercorrencias=media_notas_intercorrencias
    )

@dashboard_bp.route('/api/dados_graficos')
@login_required
def api_dados_graficos():
    """
    Endpoint JSON para alimentar os gráficos via Javascript no Frontend.
    Recebe datas inicial e final como filtro.
    """
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    conn = get_db()
    
    # Monta a query baseada no filtro de data (se fornecido) e restrição de professor
    where_clauses = ["1=1"]
    params = []
    
    if session.get('username') != 'admin':
        where_clauses.append("professor_id = ?")
        params.append(session.get('user_id'))
        
    if data_inicio and data_fim:
        where_clauses.append("data_lancamento BETWEEN ? AND ?")
        params.extend([data_inicio, data_fim])
        
    query_filtro = " WHERE " + " AND ".join(where_clauses)
        
    query = f'''
        SELECT data_lancamento, atividade_id, nota_atividade, intercorrencia_id, nota_intercorrencia
        FROM lancamentos
        {query_filtro}
        ORDER BY data_lancamento ASC
    '''
    
    resultados = conn.execute(query, params).fetchall()
    conn.close()
    
    # O JavaScript (charts.js) irá processar essa lista de dicionários para montar as linhas.
    dados = [dict(row) for row in resultados]
    return jsonify(dados)