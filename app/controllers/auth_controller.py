# app/controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
# NOVA MUDANÇA: O login agora usa a entidade Professor em vez de Usuario
from models.professor import Professor

auth_bp = Blueprint('auth_bp', __name__)

# --- DECORADOR DE SEGURANÇA ---
# Esta função será usada para "envelopar" outras rotas e exigir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se o user_id não estiver na sessão do navegador, bloqueia e manda pro login
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function
# ------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota que exibe o formulário de login e processa a autenticação."""
    # Se o professor já está logado, manda direto pro dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.index'))

    erro = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # NOVA MUDANÇA: Busca agora é diretamente na tabela de professores
        professor = Professor.get_by_username(username)

        # Valida se o professor existe e se a senha bate com o Hash
        if professor and Professor.validar_senha(professor['password_hash'], password):
            # Salva o ID do professor na sessão criptografada do navegador (usamos 'user_id' para manter compatibilidade com o resto do sistema)
            session['user_id'] = professor['id']
            session['username'] = professor['username']
            session['nome_completo'] = professor['nome_completo']
            return redirect(url_for('dashboard_bp.index'))
        else:
            erro = "Usuário ou senha incorretos. Tente novamente."

    return render_template('login.html', erro=erro)

@auth_bp.route('/logout')
def logout():
    """Encerra a sessão do professor."""
    session.clear() # Limpa todos os dados da sessão
    return redirect(url_for('auth_bp.login'))