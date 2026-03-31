# app/controllers/exportacao_controller.py
import datetime
from flask import Blueprint, render_template, request, make_response
from models.aluno import Aluno
from models.professor import Professor
from models.atividade import Atividade
from models.intercorrencia import Intercorrencia
from models.lancamento import Lancamento
from database import get_db
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

# Importamos o xhtml2pdf e o BytesIO para gerar o PDF nativamente
from xhtml2pdf import pisa
from io import BytesIO

exportacao_bp = Blueprint('exportacao_bp', __name__, url_prefix='/relatorios')

@exportacao_bp.route('/aluno/<int:aluno_id>')
@login_required
def relatorio_aluno(aluno_id):
    """Gera um relatório do aluno (Mantido para compatibilidade)."""
    formato = request.args.get('format', 'html')
    aluno = Aluno.get_by_id(aluno_id)
    
    conn = get_db()
    lancamentos = conn.execute('''
        SELECT l.*, act.sigla as atividade_sigla, intc.sigla as intercorrencia_sigla 
        FROM lancamentos l
        LEFT JOIN atividades act ON l.atividade_id = act.id
        LEFT JOIN intercorrencias intc ON l.intercorrencia_id = intc.id
        WHERE l.aluno_id = ? ORDER BY l.data_lancamento DESC
    ''', (aluno_id,)).fetchall()
    conn.close()

    html_content = render_template('relatorios/relatorio_base.html', aluno=aluno, lancamentos=lancamentos)

    if formato == 'pdf':
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        if pisa_status.err:
            return "Erro ao gerar o documento PDF.", 500
            
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=relatorio_{aluno["nome"].replace(" ", "_")}.pdf'
        return response
        
    elif formato == 'whatsapp':
        texto_whatsapp = f"Relatório Clínico - TERA\nPaciente: {aluno['nome']}\n\nResumo de Lançamentos:\n"
        for l in lancamentos:
            texto_whatsapp += f"- Data: {l['data_lancamento']} | "
            if l['atividade_sigla']: texto_whatsapp += f"Ativ: {l['atividade_sigla']} (Nota: {l['nota_atividade']}) "
            if l['intercorrencia_sigla']: texto_whatsapp += f"Interc: {l['intercorrencia_sigla']} (Nota: {l['nota_intercorrencia']})"
            texto_whatsapp += "\n"
        return render_template('relatorios/relatorio_whatsapp.html', texto_whatsapp=texto_whatsapp, aluno=aluno)

    return html_content

# --- NOVAS ROTAS PARA O RELATÓRIO ANALÍTICO GERAL ---

@exportacao_bp.route('/')
@login_required
def index():
    """Exibe a tela com o formulário de filtros para gerar o relatório."""
    alunos = Aluno.get_all()
    professores = Professor.get_all()
    atividades = Atividade.get_all()
    intercorrencias = Intercorrencia.get_all()
    
    return render_template('relatorios/index.html', 
                           alunos=alunos, 
                           professores=professores, 
                           atividades=atividades, 
                           intercorrencias=intercorrencias)

@exportacao_bp.route('/gerar', methods=['GET', 'POST'])
@login_required
def gerar_relatorio():
    """Recebe os filtros, busca no banco e gera a saída HTML ou PDF."""
    
    # Parâmetros vindos da URL (tanto no GET quanto na Action do POST)
    filtros = {
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
        'aluno_id': request.args.get('aluno_id'),
        'professor_id': request.args.get('professor_id'),
        'atividade_id': request.args.get('atividade_id'),
        'intercorrencia_id': request.args.get('intercorrencia_id')
    }
    
    tipo_grafico = request.args.get('tipo_grafico', 'separado')
    
    # Se for POST, significa que o frontend nos enviou a imagem do gráfico
    chart_image = None
    if request.method == 'POST':
        chart_image = request.form.get('chart_image')
        formato = 'pdf' # Força o formato PDF se for um POST com a imagem
    else:
        formato = request.args.get('format', 'html')

    lancamentos = Lancamento.get_relatorio_avancado(filtros)

    data_geracao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    filtros_aplicados = []
    if filtros['data_inicio'] and filtros['data_fim']: filtros_aplicados.append(f"Período: {filtros['data_inicio']} a {filtros['data_fim']}")
    elif filtros['data_inicio']: filtros_aplicados.append(f"A partir de: {filtros['data_inicio']}")
    elif filtros['data_fim']: filtros_aplicados.append(f"Até: {filtros['data_fim']}")
    
    if filtros['aluno_id']: filtros_aplicados.append(f"Aluno: {Aluno.get_by_id(filtros['aluno_id'])['nome']}")
    if filtros['professor_id']: filtros_aplicados.append(f"Prof: {Professor.get_by_id(filtros['professor_id'])['nome_completo']}")
    if filtros['atividade_id']: filtros_aplicados.append(f"Ativ: {Atividade.get_by_id(filtros['atividade_id'])['sigla']}")
    if filtros['intercorrencia_id']: filtros_aplicados.append(f"Interc: {Intercorrencia.get_by_id(filtros['intercorrencia_id'])['sigla']}")
    
    descricao_filtros = " | ".join(filtros_aplicados) if filtros_aplicados else "Nenhum filtro aplicado (Visão Geral)"

    html_content = render_template('relatorios/relatorio_geral.html', 
                                   lancamentos=lancamentos, 
                                   descricao_filtros=descricao_filtros, 
                                   data_geracao=data_geracao,
                                   tipo_grafico=tipo_grafico,
                                   chart_image=chart_image) # Passamos a imagem para o template

    if formato == 'pdf':
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            return "Erro ao gerar PDF", 500
            
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=relatorio_analitico_tera.pdf'
        return response

    return html_content