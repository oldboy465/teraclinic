# app/controllers/nota_controller.py
from flask import Blueprint, render_template, request, redirect, url_for
from models.nota import NotaSemantica
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

nota_bp = Blueprint('nota_bp', __name__, url_prefix='/notas')

@nota_bp.route('/')
@login_required
def index():
    """
    Lista a configuração semântica do sistema. 
    Busca os dados dinamicamente do banco de dados.
    """
    # Buscamos as listas completas para a gestão
    notas_atividade = NotaSemantica.get_all(tipo='atividade')
    notas_intercorrencia = NotaSemantica.get_all(tipo='intercorrencia')
    
    return render_template(
        'notas/index.html', 
        notas_atividade=notas_atividade, 
        notas_intercorrencia=notas_intercorrencia
    )

@nota_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    """Cria uma nova definição de nota no dicionário."""
    if request.method == 'POST':
        tipo = request.form['tipo']
        valor = request.form['valor']
        descricao = request.form['descricao']
        
        NotaSemantica.create(tipo, valor, descricao)
        return redirect(url_for('nota_bp.index'))
    
    return render_template('notas/form.html', nota=None)

@nota_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edita o significado ou valor de uma nota existente."""
    if request.method == 'POST':
        tipo = request.form['tipo']
        valor = request.form['valor']
        descricao = request.form['descricao']
        
        NotaSemantica.update(id, tipo, valor, descricao)
        return redirect(url_for('nota_bp.index'))
    
    nota = NotaSemantica.get_by_id(id)
    return render_template('notas/form.html', nota=nota)

@nota_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Remove uma nota do dicionário institucional."""
    NotaSemantica.delete(id)
    return redirect(url_for('nota_bp.index'))