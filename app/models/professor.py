# app/models/professor.py
from database import get_db
from werkzeug.security import check_password_hash

class Professor:
    """
    Classe Model responsável por gerenciar os dados dos Professores/Terapeutas e suas credenciais.
    """

    @staticmethod
    def get_all():
        """Busca todos os professores cadastrados, ordenados por nome."""
        conn = get_db()
        professores = conn.execute('SELECT * FROM professores ORDER BY nome_completo ASC').fetchall()
        conn.close()
        return professores

    @staticmethod
    def get_by_id(professor_id):
        """Busca um professor específico pelo seu ID."""
        conn = get_db()
        professor = conn.execute('SELECT * FROM professores WHERE id = ?', (professor_id,)).fetchone()
        conn.close()
        return professor

    # NOVA MUDANÇA: Adicionado método de busca por username para login
    @staticmethod
    def get_by_username(username):
        """Busca um professor pelo seu nome de usuário (login)."""
        conn = get_db()
        professor = conn.execute('SELECT * FROM professores WHERE username = ?', (username,)).fetchone()
        conn.close()
        return professor

    # NOVA MUDANÇA: Adicionado método de validação de senha
    @staticmethod
    def validar_senha(usuario_hash, senha_digitada):
        """Valida a senha do professor com o hash do banco."""
        if not usuario_hash:
            return False
        return check_password_hash(usuario_hash, senha_digitada)

    @staticmethod
    def create(nome_completo, telefone, email, foto=None, username=None, password_hash=None):
        """Insere um novo professor no banco de dados, incluindo credenciais opcionais."""
        conn = get_db()
        conn.execute('''
            INSERT INTO professores (nome_completo, telefone, email, foto, username, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome_completo, telefone, email, foto, username, password_hash))
        conn.commit()
        conn.close()

    @staticmethod
    def update(professor_id, nome_completo, telefone, email, foto=None):
        """Atualiza os dados cadastrais básicos de um professor."""
        conn = get_db()
        if foto:
            conn.execute('''
                UPDATE professores SET nome_completo = ?, telefone = ?, email = ?, foto = ?
                WHERE id = ?
            ''', (nome_completo, telefone, email, foto, professor_id))
        else:
            conn.execute('''
                UPDATE professores SET nome_completo = ?, telefone = ?, email = ?
                WHERE id = ?
            ''', (nome_completo, telefone, email, professor_id))
        conn.commit()
        conn.close()

    # NOVA MUDANÇA: Método específico para atualizar credenciais de acesso
    @staticmethod
    def update_credentials(professor_id, username, password_hash):
        """Atualiza as credenciais de login de um professor."""
        conn = get_db()
        conn.execute('''
            UPDATE professores SET username = ?, password_hash = ?
            WHERE id = ?
        ''', (username, password_hash, professor_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(professor_id):
        """Remove um professor do sistema."""
        conn = get_db()
        conn.execute('DELETE FROM professores WHERE id = ?', (professor_id,))
        conn.commit()
        conn.close()