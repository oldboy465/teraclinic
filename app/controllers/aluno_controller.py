# app/controllers/aluno_controller.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from werkzeug.utils import secure_filename
from models.aluno import Aluno
from models.professor import Professor
from models.atividade import Atividade
from controllers.auth_controller import login_required

aluno_bp = Blueprint('aluno_bp', __name__, url_prefix='/alunos')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@aluno_bp.route('/')
@login_required
def index():
    if session.get('username') == 'admin':
        alunos = Aluno.get_all()
    else:
        alunos = Aluno.get_by_terapeuta(session.get('user_id'))

    return render_template('alunos/index.html', alunos=alunos)

@aluno_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        sexo = request.form['sexo']
        preferencias = request.form['preferencias']
        evitaveis = request.form['evitaveis']
        informacoes_adicionais = request.form['informacoes_adicionais']
        email = request.form.get('email')

        terapeuta_id = request.form['terapeuta_id']
        terapeuta_id = terapeuta_id if terapeuta_id != '' else None

        atividades_ids = request.form.getlist('atividades_ids')

        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        Aluno.create(nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto_filename, email, atividades_ids)
        return redirect(url_for('aluno_bp.index'))

    terapeutas = Professor.get_all()
    
    if session.get('username') == 'admin':
        atividades_disponiveis = Atividade.get_all()
    else:
        atividades_disponiveis = Atividade.get_by_professor(session.get('user_id'))

    return render_template('alunos/form.html', terapeutas=terapeutas, aluno=None, atividades_disponiveis=atividades_disponiveis, atividades_vinculadas=[])

@aluno_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        sexo = request.form['sexo']
        preferencias = request.form['preferencias']
        evitaveis = request.form['evitaveis']
        informacoes_adicionais = request.form['informacoes_adicionais']
        email = request.form.get('email')

        terapeuta_id = request.form['terapeuta_id']
        terapeuta_id = terapeuta_id if terapeuta_id != '' else None
        
        atividades_ids = request.form.getlist('atividades_ids')

        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        Aluno.update(id, nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto_filename, email, atividades_ids)
        return redirect(url_for('aluno_bp.index'))

    aluno = Aluno.get_by_id(id)
    terapeutas = Professor.get_all()
    
    if session.get('username') == 'admin':
        atividades_disponiveis = Atividade.get_all()
    else:
        atividades_disponiveis = Atividade.get_by_professor(session.get('user_id'))
        
    vinculos = Aluno.get_atividades_vinculadas(id)
    atividades_vinculadas = [v['id'] for v in vinculos]

    return render_template('alunos/form.html', terapeutas=terapeutas, aluno=aluno, atividades_disponiveis=atividades_disponiveis, atividades_vinculadas=atividades_vinculadas)

@aluno_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    Aluno.delete(id)
    return redirect(url_for('aluno_bp.index'))