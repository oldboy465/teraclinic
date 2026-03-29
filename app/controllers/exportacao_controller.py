# app/controllers/exportacao_controller.py
from flask import Blueprint, render_template, request, make_response
from models.aluno import Aluno
from database import get_db
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

# Importamos o xhtml2pdf e o BytesIO para gerar o PDF nativamente
from xhtml2pdf import pisa
from io import BytesIO

exportacao_bp = Blueprint('exportacao_bp', __name__, url_prefix='/relatorios')

@exportacao_bp.route('/aluno/<int:aluno_id>')
@login_required
def relatorio_aluno(aluno_id):
    """Gera um relatório do aluno. Permite formato HTML, PDF ou WhatsApp via query parameter."""
    formato = request.args.get('format', 'html')
    aluno = Aluno.get_by_id(aluno_id)
    
    conn = get_db()
    # Busca os lançamentos específicos deste aluno
    lancamentos = conn.execute('''
        SELECT l.*, act.sigla as atividade_sigla, intc.sigla as intercorrencia_sigla 
        FROM lancamentos l
        LEFT JOIN atividades act ON l.atividade_id = act.id
        LEFT JOIN intercorrencias intc ON l.intercorrencia_id = intc.id
        WHERE l.aluno_id = ? ORDER BY l.data_lancamento DESC
    ''', (aluno_id,)).fetchall()
    conn.close()

    # Prepara a View HTML baseada nos dados do aluno
    html_content = render_template('relatorios/relatorio_base.html', aluno=aluno, lancamentos=lancamentos)

    if formato == 'pdf':
        # Converte a String HTML em PDF usando xhtml2pdf
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        # Verifica se houve erro na geração
        if pisa_status.err:
            return "Erro ao gerar o documento PDF.", 500
            
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=relatorio_{aluno["nome"].replace(" ", "_")}.pdf'
        return response
        
    elif formato == 'whatsapp':
        # Retorna apenas um HTML simplificado com o texto puro e o botão de "Copiar"
        # Isso será detalhado no front-end em JS.
        texto_whatsapp = f"Relatório Clínico - TERA\nPaciente: {aluno['nome']}\n\nResumo de Lançamentos:\n"
        for l in lancamentos:
            texto_whatsapp += f"- Data: {l['data_lancamento']} | "
            if l['atividade_sigla']: texto_whatsapp += f"Ativ: {l['atividade_sigla']} (Nota: {l['nota_atividade']}) "
            if l['intercorrencia_sigla']: texto_whatsapp += f"Interc: {l['intercorrencia_sigla']} (Nota: {l['nota_intercorrencia']})"
            texto_whatsapp += "\n"
        
        return render_template('relatorios/relatorio_whatsapp.html', texto_whatsapp=texto_whatsapp, aluno=aluno)

    # Padrão: exibe o HTML
    return html_content