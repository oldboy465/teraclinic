# app/controllers/lancamento_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.lancamento import Lancamento
from models.aluno import Aluno
from models.professor import Professor
from models.atividade import Atividade
from models.intercorrencia import Intercorrencia
from models.nota import NotaSemantica
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

lancamento_bp = Blueprint('lancamento_bp', __name__, url_prefix='/lancamentos')

@lancamento_bp.route('/')
@login_required
def index():
    """Lista o histórico de todos os lançamentos."""
    # NOVA MUDANÇA: O professor só vê o histórico dos seus alunos/lançamentos
    if session.get('username') == 'admin':
        lancamentos = Lancamento.get_all()
    else:
        lancamentos = Lancamento.get_relatorio_avancado({'professor_id': session.get('user_id')})
        
    return render_template('lancamentos/index.html', lancamentos=lancamentos)

@lancamento_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    """Registra eventos em lote (Atividades e Intercorrências) para um aluno."""
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        data_lancamento = request.form.get('data_lancamento')
        
        # NOVA MUDANÇA: Pega o professor_id diretamente da sessão de quem está logado
        professor_id = session.get('user_id')
        
        # Busca todas as atividades do professor e intercorrências gerais para ler as notas do form dinâmico
        if session.get('username') == 'admin':
            atividades_prof = Atividade.get_all()
        else:
            atividades_prof = Atividade.get_by_professor(professor_id)
            
        intercorrencias_gerais = Intercorrencia.get_all()
        
        lancamentos_dados = []

        # NOVA MUDANÇA: Varre as atividades e monta o lote de inserção se a nota foi preenchida
        for atv in atividades_prof:
            nota_atv = request.form.get(f'nota_atividade_{atv["id"]}')
            if nota_atv and nota_atv != '':
                lancamentos_dados.append((aluno_id, professor_id, atv['id'], nota_atv, None, None, data_lancamento))

        # NOVA MUDANÇA: Varre as intercorrências e monta o lote de inserção se a nota foi preenchida
        for intc in intercorrencias_gerais:
            nota_intc = request.form.get(f'nota_intercorrencia_{intc["id"]}')
            if nota_intc and nota_intc != '':
                lancamentos_dados.append((aluno_id, professor_id, None, None, intc['id'], nota_intc, data_lancamento))

        # Se houve preenchimento de alguma nota, salva tudo no banco otimizado de uma vez
        if lancamentos_dados:
            Lancamento.create_many(lancamentos_dados)

        return redirect(url_for('dashboard_bp.index'))

    # GET: Monta o formulário filtrando os dados do professor autenticado
    if session.get('username') == 'admin':
        alunos = Aluno.get_all()
        atividades = Atividade.get_all()
    else:
        alunos = Aluno.get_by_terapeuta(session.get('user_id'))
        atividades = Atividade.get_by_professor(session.get('user_id'))
        
    professores = Professor.get_all()
    intercorrencias = Intercorrencia.get_all()
    
    # Busca as notas editáveis diretamente do banco de dados
    notas_atv = NotaSemantica.get_notas_atividade()
    notas_int = NotaSemantica.get_notas_intercorrencia()

    return render_template(
        'lancamentos/form.html', 
        alunos=alunos, 
        professores=professores, 
        atividades=atividades, 
        intercorrencias=intercorrencias,
        notas_atv=notas_atv,
        notas_int=notas_int
    )