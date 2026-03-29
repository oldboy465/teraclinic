# app/controllers/aluno_controller.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models.aluno import Aluno
from models.professor import Professor
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

# Criamos o Blueprint para alunos. Todas as rotas aqui começarão com /alunos
aluno_bp = Blueprint('aluno_bp', __name__, url_prefix='/alunos')

# Extensões permitidas para upload de imagem
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Verifica se o arquivo enviado possui uma extensão válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@aluno_bp.route('/')
@login_required
def index():
    """Rota para listar todos os alunos."""
    alunos = Aluno.get_all()
    # Chama a view passando a lista de alunos
    return render_template('alunos/index.html', alunos=alunos)

@aluno_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    """Rota para exibir o formulário (GET) e salvar um novo aluno (POST)."""
    if request.method == 'POST':
        # Recebendo os dados do formulário HTML
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        sexo = request.form['sexo']
        preferencias = request.form['preferencias']
        evitaveis = request.form['evitaveis']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        # TRATAMENTO DO ERRO DE FOREIGN KEY:
        # Se o formulário enviar vazio (""), transformamos em None (NULL no banco)
        terapeuta_id = request.form['terapeuta_id']
        terapeuta_id = terapeuta_id if terapeuta_id != '' else None
        
        # Lógica de Upload da Foto
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                # Limpa o nome do arquivo para evitar falhas de segurança
                filename = secure_filename(file.filename)
                # Salva na pasta UPLOAD_FOLDER configurada no app.py
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        # Chama o Model para salvar no banco
        Aluno.create(nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto_filename)
        return redirect(url_for('aluno_bp.index'))

    # Se for GET, busca os terapeutas para preencher o `<select>` do formulário
    terapeutas = Professor.get_all()
    return render_template('alunos/form.html', terapeutas=terapeutas, aluno=None)

@aluno_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Rota para editar um aluno existente."""
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        sexo = request.form['sexo']
        preferencias = request.form['preferencias']
        evitaveis = request.form['evitaveis']
        informacoes_adicionais = request.form['informacoes_adicionais']
        
        # TRATAMENTO DO ERRO DE FOREIGN KEY AQUI TAMBÉM:
        terapeuta_id = request.form['terapeuta_id']
        terapeuta_id = terapeuta_id if terapeuta_id != '' else None
        
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        Aluno.update(id, nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, foto_filename)
        return redirect(url_for('aluno_bp.index'))

    # Para GET: busca o aluno atual e os terapeutas
    aluno = Aluno.get_by_id(id)
    terapeutas = Professor.get_all()
    return render_template('alunos/form.html', terapeutas=terapeutas, aluno=aluno)

@aluno_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Rota para excluir o aluno do sistema."""
    Aluno.delete(id)
    return redirect(url_for('aluno_bp.index'))