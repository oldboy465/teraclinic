# app/controllers/lancamento_controller.py
from flask import Blueprint, render_template, request, redirect, url_for
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
    lancamentos = Lancamento.get_all()
    return render_template('lancamentos/index.html', lancamentos=lancamentos)

@lancamento_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    """Registra um novo evento (Atividade ou Intercorrência) para um aluno."""
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        professor_id = request.form.get('professor_id')
        data_lancamento = request.form.get('data_lancamento')
        
        # Tratamento de campos opcionais
        atividade_id = request.form.get('atividade_id') or None
        nota_atividade = request.form.get('nota_atividade') or None
        intercorrencia_id = request.form.get('intercorrencia_id') or None
        nota_intercorrencia = request.form.get('nota_intercorrencia') or None

        Lancamento.create(
            aluno_id=aluno_id, 
            professor_id=professor_id, 
            data_lancamento=data_lancamento,
            atividade_id=atividade_id, 
            nota_atividade=nota_atividade, 
            intercorrencia_id=intercorrencia_id, 
            nota_intercorrencia=nota_intercorrencia
        )
        # CORREÇÃO SOLICITADA: Agora redireciona para o Dashboard após salvar
        return redirect(url_for('dashboard_bp.index'))

    # Para montar o formulário de Lançamento, buscamos todas as entidades
    alunos = Aluno.get_all()
    professores = Professor.get_all()
    atividades = Atividade.get_all()
    intercorrencias = Intercorrencia.get_all()
    
    # CORREÇÃO SOLICITADA: Busca as notas editáveis diretamente do banco de dados
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