# app/controllers/atividade_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.atividade import Atividade
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

atividade_bp = Blueprint('atividade_bp', __name__, url_prefix='/atividades')

@atividade_bp.route('/')
@login_required
def index():
    # NOVA MUDANÇA: O professor só vê suas próprias atividades, a menos que seja admin
    if session.get('username') == 'admin':
        atividades = Atividade.get_all()
    else:
        atividades = Atividade.get_by_professor(session.get('user_id'))
        
    return render_template('atividades/index.html', atividades=atividades)

@atividade_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        sigla = request.form['sigla']
        descricao = request.form['descricao']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        # NOVA MUDANÇA: Atrela a atividade ao professor logado
        professor_id = session.get('user_id') if session.get('username') != 'admin' else None
        
        Atividade.create(sigla, descricao, informacoes_adicionais, professor_id)
        return redirect(url_for('atividade_bp.index'))

    return render_template('atividades/form.html', atividade=None)

@atividade_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        sigla = request.form['sigla']
        descricao = request.form['descricao']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        Atividade.update(id, sigla, descricao, informacoes_adicionais)
        return redirect(url_for('atividade_bp.index'))

    atividade = Atividade.get_by_id(id)
    return render_template('atividades/form.html', atividade=atividade)

@atividade_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    Atividade.delete(id)
    return redirect(url_for('atividade_bp.index'))