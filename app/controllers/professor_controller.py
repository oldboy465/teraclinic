# app/controllers/professor_controller.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models.professor import Professor
from controllers.auth_controller import login_required  # Importação do bloqueio de segurança

professor_bp = Blueprint('professor_bp', __name__, url_prefix='/professores')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@professor_bp.route('/')
@login_required
def index():
    professores = Professor.get_all()
    return render_template('professores/index.html', professores=professores)

@professor_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        telefone = request.form['telefone']
        email = request.form['email']
        
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        Professor.create(nome_completo, telefone, email, foto_filename)
        return redirect(url_for('professor_bp.index'))

    return render_template('professores/form.html', professor=None)

@professor_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        telefone = request.form['telefone']
        email = request.form['email']
        
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                foto_filename = filename

        Professor.update(id, nome_completo, telefone, email, foto_filename)
        return redirect(url_for('professor_bp.index'))

    professor = Professor.get_by_id(id)
    return render_template('professores/form.html', professor=professor)

@professor_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    Professor.delete(id)
    return redirect(url_for('professor_bp.index'))