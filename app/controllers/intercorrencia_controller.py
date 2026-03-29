# app/controllers/intercorrencia_controller.py
from flask import Blueprint, render_template, request, redirect, url_for
from models.intercorrencia import Intercorrencia
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

intercorrencia_bp = Blueprint('intercorrencia_bp', __name__, url_prefix='/intercorrencias')

@intercorrencia_bp.route('/')
@login_required
def index():
    intercorrencias = Intercorrencia.get_all()
    return render_template('intercorrencias/index.html', intercorrencias=intercorrencias)

@intercorrencia_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        sigla = request.form['sigla']
        descricao = request.form['descricao']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        Intercorrencia.create(sigla, descricao, informacoes_adicionais)
        return redirect(url_for('intercorrencia_bp.index'))

    return render_template('intercorrencias/form.html', intercorrencia=None)

@intercorrencia_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        sigla = request.form['sigla']
        descricao = request.form['descricao']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        Intercorrencia.update(id, sigla, descricao, informacoes_adicionais)
        return redirect(url_for('intercorrencia_bp.index'))

    intercorrencia = Intercorrencia.get_by_id(id)
    return render_template('intercorrencias/form.html', intercorrencia=intercorrencia)

@intercorrencia_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    Intercorrencia.delete(id)
    return redirect(url_for('intercorrencia_bp.index'))