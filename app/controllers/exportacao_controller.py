# app/controllers/exportacao_controller.py
import datetime
from flask import Blueprint, render_template, request, make_response, session, flash, redirect, url_for, jsonify
from models.aluno import Aluno
from models.professor import Professor
from models.atividade import Atividade
from models.intercorrencia import Intercorrencia
from models.lancamento import Lancamento
from database import get_db
from controllers.auth_controller import login_required
from xhtml2pdf import pisa
from io import BytesIO
from utils.email_service import enviar_email_com_anexo

exportacao_bp = Blueprint('exportacao_bp', __name__, url_prefix='/relatorios')

@exportacao_bp.route('/api/alunos/<int:professor_id>')
@login_required
def api_get_alunos_por_professor(professor_id):
    alunos = Aluno.get_by_terapeuta(professor_id)
    return jsonify([{'id': a['id'], 'nome': a['nome']} for a in alunos])

@exportacao_bp.route('/api/atividades/<int:aluno_id>')
@login_required
def api_get_atividades_por_aluno(aluno_id):
    atividades = Atividade.get_por_aluno(aluno_id)
    return jsonify([{'id': a['id'], 'sigla': a['sigla'], 'descricao': a['descricao']} for a in atividades])

@exportacao_bp.route('/aluno/<int:aluno_id>')
@login_required
def relatorio_aluno(aluno_id):
    formato = request.args.get('format', 'html')
    aluno = Aluno.get_by_id(aluno_id)
    if session.get('username') != 'admin' and aluno['terapeuta_id'] != session.get('user_id'):
        return "Acesso Negado: Este aluno não está vinculado a você.", 403
    conn = get_db()
    lancamentos = conn.execute('''
        SELECT l.*, act.sigla as atividade_sigla,
               COALESCE(l.tentativa1,0) + COALESCE(l.tentativa2,0) + COALESCE(l.tentativa3,0) + COALESCE(l.tentativa4,0) + COALESCE(l.tentativa5,0) as soma_atividades,
               COALESCE(l.int_nota1,0) + COALESCE(l.int_nota2,0) + COALESCE(l.int_nota3,0) + COALESCE(l.int_nota4,0) + COALESCE(l.int_nota5,0) as soma_intercorrencias
        FROM lancamentos l
        LEFT JOIN atividades act ON l.atividade_id = act.id
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
    return html_content

@exportacao_bp.route('/')
@login_required
def index():
    if session.get('username') == 'admin':
        alunos = Aluno.get_all()
        atividades = Atividade.get_all()
    else:
        alunos = Aluno.get_by_terapeuta(session.get('user_id'))
        atividades = Atividade.get_by_professor(session.get('user_id'))
    professores = Professor.get_all()
    intercorrencias = Intercorrencia.get_all()
    return render_template('relatorios/index.html',
                           alunos=alunos,
                           professores=professores,
                           atividades=atividades,
                           intercorrencias=intercorrencias)

@exportacao_bp.route('/gerar', methods=['GET', 'POST'])
@login_required
def gerar_relatorio():
    filtros = {
        'data_inicio': request.args.get('data_inicio') or request.form.get('data_inicio'),
        'data_fim': request.args.get('data_fim') or request.form.get('data_fim'),
        'aluno_id': request.args.get('aluno_id') or request.form.get('aluno_id'),
        'professor_id': request.args.get('professor_id') or request.form.get('professor_id'),
        'atividades_ids': request.args.getlist('atividades_ids') or request.form.getlist('atividades_ids')
    }
    incluir_obs = request.args.get('incluir_obs') == 'true' or request.form.get('incluir_obs') == 'true'
    if session.get('username') != 'admin':
        filtros['professor_id'] = session.get('user_id')
    chart_images = []
    enviar_email = False
    enviar_para_professor = False
    if request.method == 'POST':
        chart_images = request.form.getlist('chart_images[]')
        formato = 'pdf'
        enviar_email = request.form.get('enviar_email') == 'true'
        enviar_para_professor = request.form.get('enviar_professor') == 'true'
    else:
        formato = request.args.get('format', 'html')
    lancamentos_brutos = Lancamento.get_relatorio_avancado(filtros)
    lancamentos = [dict(row) for row in lancamentos_brutos]
    data_geracao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    filtros_aplicados = []
    aluno_selecionado = None
    prof_selecionado = None
    if filtros['data_inicio'] and filtros['data_fim']:
        filtros_aplicados.append(f"Período: {filtros['data_inicio']} a {filtros['data_fim']}")
    if filtros['aluno_id']:
        aluno_selecionado = Aluno.get_by_id(filtros['aluno_id'])
        if aluno_selecionado: filtros_aplicados.append(f"Aluno: {aluno_selecionado['nome']}")
    if filtros['professor_id']:
        prof_selecionado = Professor.get_by_id(filtros['professor_id'])
        if prof_selecionado: filtros_aplicados.append(f"Prof: {prof_selecionado['nome_completo']}")
    if filtros['atividades_ids']:
        nomes_atvs = [Atividade.get_by_id(aid)['sigla'] for aid in filtros['atividades_ids'] if Atividade.get_by_id(aid)]
        filtros_aplicados.append(f"Atividades: {', '.join(nomes_atvs)}")
    descricao_filtros = " | ".join(filtros_aplicados) if filtros_aplicados else "Nenhum filtro aplicado (Visão Geral)"
    lancamentos_por_atividade = {}
    for l in lancamentos:
        sigla = l['atividade_sigla'] or 'Sem Atividade'
        if sigla not in lancamentos_por_atividade:
            lancamentos_por_atividade[sigla] = []
        lancamentos_por_atividade[sigla].append(l)
    html_content = render_template('relatorios/relatorio_geral.html',
                                   lancamentos_por_atividade=lancamentos_por_atividade,
                                   lancamentos_lista=lancamentos,
                                   descricao_filtros=descricao_filtros,
                                   data_geracao=data_geracao,
                                   chart_images=chart_images,
                                   incluir_obs=incluir_obs)
    if formato == 'pdf' or enviar_email:
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        if pisa_status.err:
            return "Erro ao gerar PDF", 500
        pdf_bytes = pdf_file.getvalue()
        if enviar_email and aluno_selecionado:
            destinatarios = []
            if aluno_selecionado['email']:
                destinatarios.append(aluno_selecionado['email'])
            if enviar_para_professor and prof_selecionado and prof_selecionado['email']:
                destinatarios.append(prof_selecionado['email'])
            elif enviar_para_professor and session.get('username') != 'admin':
                prof_logado = Professor.get_by_id(session.get('user_id'))
                if prof_logado and prof_logado['email']: destinatarios.append(prof_logado['email'])
            if destinatarios:
                sucesso = enviar_email_com_anexo(
                    destinatarios=destinatarios,
                    assunto=f"Relatório Clínico - TERA - {aluno_selecionado['nome']}",
                    corpo="Segue em anexo o relatório analítico de acompanhamento terapêutico.",
                    pdf_bytes=pdf_bytes,
                    nome_arquivo=f"Relatorio_{aluno_selecionado['nome'].replace(' ', '_')}.pdf"
                )
                if sucesso:
                    flash('Relatório enviado por e-mail com sucesso!', 'success')
                else:
                    flash('Erro ao enviar e-mail. Verifique as configurações.', 'danger')
                return redirect(url_for('exportacao_bp.index'))
            else:
                flash('Nenhum e-mail de destinatário encontrado.', 'warning')
                return redirect(url_for('exportacao_bp.index'))
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=relatorio_analitico_tera.pdf'
        return response
    return html_content