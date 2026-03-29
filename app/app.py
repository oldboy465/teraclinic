# app/app.py
import os
from flask import Flask, redirect, url_for

# Importação da nossa configuração de banco de dados
from database import init_db

def create_app():
    """
    Função fábrica (Factory) para criar a instância do Flask.
    Isso é uma boa prática para escalabilidade e testes estruturados.
    """
    # Inicializa o Flask, apontando as pastas customizadas de acordo com nossa arquitetura
    app = Flask(__name__, template_folder='views', static_folder='static')
    
    # Configurações de Segurança e Limites (Sessão de Login usa essa secret_key)
    app.secret_key = 'tera_super_secret_key_change_in_production'
    
    # Restrição Importante: Limita o upload de arquivos a 2MB
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 
    
    # Diretório onde as fotos serão salvas
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Inicializa o banco de dados e cria as tabelas se não existirem
    with app.app_context():
        init_db()

    # Importação e Registro de todos os Controllers (Blueprints)
    from controllers.auth_controller import auth_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.aluno_controller import aluno_bp
    from controllers.professor_controller import professor_bp
    from controllers.atividade_controller import atividade_bp
    from controllers.intercorrencia_controller import intercorrencia_bp
    from controllers.nota_controller import nota_bp
    from controllers.lancamento_controller import lancamento_bp
    from controllers.exportacao_controller import exportacao_bp

    # Registrando as rotas no app principal
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(atividade_bp)
    app.register_blueprint(intercorrencia_bp)
    app.register_blueprint(nota_bp)
    app.register_blueprint(lancamento_bp)
    app.register_blueprint(exportacao_bp)

    @app.route('/')
    def index():
        # Agora, acessar a raiz do site redireciona automaticamente para a tela de login
        return redirect(url_for('auth_bp.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    # Roda em localhost na porta 5000, com debug ativado para facilitar o desenvolvimento
    app.run(host='127.0.0.1', port=5000, debug=True)