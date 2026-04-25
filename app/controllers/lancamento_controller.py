# app/controllers/lancamento_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models.lancamento import Lancamento
from models.aluno import Aluno
from models.professor import Professor
from models.atividade import Atividade
from models.intercorrencia import Intercorrencia
from models.nota import NotaSemantica
from controllers.auth_controller import login_required

lancamento_bp = Blueprint('lancamento_bp', __name__, url_prefix='/lancamentos')

@lancamento_bp.route('/')
@login_required
def index():
    if session.get('username') == 'admin':
        lancamentos = Lancamento.get_all()
    else:
        lancamentos = Lancamento.get_relatorio_avancado({'professor_id': session.get('user_id')})
    return render_template('lancamentos/index.html', lancamentos=lancamentos)

@lancamento_bp.route('/api/atividades/<int:aluno_id>')
@login_required
def get_atividades_aluno(aluno_id):
    """Retorna JSON com as atividades vinculadas a um aluno específico para preencher a tabela."""
    atividades = Atividade.get_por_aluno(aluno_id)
    return jsonify([dict(a) for a in atividades])

@lancamento_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        data_lancamento = request.form.get('data_lancamento')
        professor_id = session.get('user_id')
        
        atividades_enviadas = request.form.getlist('atividade_ids[]')
        lancamentos_dados = []

        for atv_id in atividades_enviadas:
            # Pega as 5 tentativas
            t1 = request.form.get(f't1_{atv_id}') or None
            t2 = request.form.get(f't2_{atv_id}') or None
            t3 = request.form.get(f't3_{atv_id}') or None
            t4 = request.form.get(f't4_{atv_id}') or None
            t5 = request.form.get(f't5_{atv_id}') or None
            
            # Pega as 5 intercorrências e notas
            i1 = request.form.get(f'i1_{atv_id}') or None
            in1 = request.form.get(f'in1_{atv_id}') or None
            i2 = request.form.get(f'i2_{atv_id}') or None
            in2 = request.form.get(f'in2_{atv_id}') or None
            i3 = request.form.get(f'i3_{atv_id}') or None
            in3 = request.form.get(f'in3_{atv_id}') or None
            i4 = request.form.get(f'i4_{atv_id}') or None
            in4 = request.form.get(f'in4_{atv_id}') or None
            i5 = request.form.get(f'i5_{atv_id}') or None
            in5 = request.form.get(f'in5_{atv_id}') or None
            
            obs = request.form.get(f'obs_{atv_id}') or ""

            # Se houver pelo menos uma tentativa lançada, grava no banco
            if any([t1, t2, t3, t4, t5]):
                lancamentos_dados.append((
                    aluno_id, professor_id, atv_id, data_lancamento,
                    t1, t2, t3, t4, t5,
                    i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs
                ))

        if lancamentos_dados:
            Lancamento.create_many(lancamentos_dados)

        return redirect(url_for('lancamento_bp.index'))

    if session.get('username') == 'admin':
        alunos = Aluno.get_all()
    else:
        alunos = Aluno.get_by_terapeuta(session.get('user_id'))

    intercorrencias = Intercorrencia.get_all()
    notas_atv = NotaSemantica.get_notas_atividade()
    notas_int = NotaSemantica.get_notas_intercorrencia()

    return render_template(
        'lancamentos/form.html',
        alunos=alunos,
        intercorrencias=intercorrencias,
        notas_atv=notas_atv,
        notas_int=notas_int,
        lancamento=None
    )

@lancamento_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    lanc = Lancamento.get_by_id(id)
    if session.get('username') != 'admin' and lanc['professor_id'] != session.get('user_id'):
        return "Acesso Negado.", 403

    if request.method == 'POST':
        t1 = request.form.get('t1') or None
        t2 = request.form.get('t2') or None
        t3 = request.form.get('t3') or None
        t4 = request.form.get('t4') or None
        t5 = request.form.get('t5') or None
        i1 = request.form.get('i1') or None
        in1 = request.form.get('in1') or None
        i2 = request.form.get('i2') or None
        in2 = request.form.get('in2') or None
        i3 = request.form.get('i3') or None
        in3 = request.form.get('in3') or None
        i4 = request.form.get('i4') or None
        in4 = request.form.get('in4') or None
        i5 = request.form.get('i5') or None
        in5 = request.form.get('in5') or None
        obs = request.form.get('obs') or ""

        Lancamento.update(id, t1, t2, t3, t4, t5, i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs)
        return redirect(url_for('lancamento_bp.index'))

    intercorrencias = Intercorrencia.get_all()
    notas_atv = NotaSemantica.get_notas_atividade()
    notas_int = NotaSemantica.get_notas_intercorrencia()
    aluno = Aluno.get_by_id(lanc['aluno_id'])
    atividade = Atividade.get_by_id(lanc['atividade_id'])

    return render_template('lancamentos/form_edit.html', lancamento=lanc, aluno=aluno, atividade=atividade, intercorrencias=intercorrencias, notas_atv=notas_atv, notas_int=notas_int)

@lancamento_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    lanc = Lancamento.get_by_id(id)
    if session.get('username') == 'admin' or lanc['professor_id'] == session.get('user_id'):
        Lancamento.delete(id)
    return redirect(url_for('lancamento_bp.index'))