# app/controllers/dashboard_controller.py
from flask import Blueprint, render_template, request, jsonify
from database import get_db
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Renderiza a página inicial do Dashboard com as métricas gerais."""
    conn = get_db()
    
    # Métricas Globais (Cards do Dashboard)
    total_alunos = conn.execute('SELECT COUNT(*) FROM alunos').fetchone()[0]
    total_atividades = conn.execute('SELECT COUNT(*) FROM atividades').fetchone()[0]
    total_intercorrencias = conn.execute('SELECT COUNT(*) FROM intercorrencias').fetchone()[0]
    
    # Médias (Atenção para não dividir por zero caso não existam dados)
    media_atv_query = conn.execute('SELECT AVG(nota_atividade) FROM lancamentos WHERE nota_atividade IS NOT NULL').fetchone()[0]
    media_int_query = conn.execute('SELECT AVG(nota_intercorrencia) FROM lancamentos WHERE nota_intercorrencia IS NOT NULL').fetchone()[0]
    
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
    
    # Monta a query baseada no filtro de data (se fornecido)
    query_filtro = ""
    params = []
    if data_inicio and data_fim:
        query_filtro = " WHERE data_lancamento BETWEEN ? AND ? "
        params.extend([data_inicio, data_fim])
        
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