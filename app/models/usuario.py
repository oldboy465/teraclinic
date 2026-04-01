# app/models/usuario.py
from database import get_db
from werkzeug.security import check_password_hash

class Usuario:
    """
    Classe Model responsável pela autenticação e gestão de usuários.
    (Mantida para compatibilidade legada - o sistema agora utiliza autenticação focada no Professor)
    """

    @staticmethod
    def get_by_username(username):
        """Busca um usuário pelo nome de login."""
        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        conn.close()
        return usuario

    @staticmethod
    def get_by_id(usuario_id):
        """Busca um usuário pelo seu ID (útil para gerenciar sessões)."""
        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
        conn.close()
        return usuario

    @staticmethod
    def validar_senha(usuario_hash, senha_digitada):
        """
        Compara a senha digitada pelo usuário com o hash salvo no banco.
        Retorna True se estiver correta, False caso contrário.
        """
        return check_password_hash(usuario_hash, senha_digitada)