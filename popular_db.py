# popular_db.py
import sqlite3
import os
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
DB_PATH = os.path.join(BASE_DIR, 'tera_database.db')

NOMES = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Julia", 
         "Lucas", "Mariana", "Nicolas", "Olivia", "Pedro", "Quintino", "Rafael", "Sofia", "Tiago", "Ursula",
         "Valentina", "Wagner", "Xuxa", "Yuri", "Zelia", "Arthur", "Beatriz", "Caio", "Diana", "Enzo", 
         "Flavia", "Gustavo", "Isabela", "Joao", "Lara", "Matheus", "Natalia", "Otavio", "Priscila", "Ricardo"]

SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
              "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"]

ATIVIDADES_BASE = [
    ("TATO", "Nomeação de itens comuns"),
    ("MANDO", "Pedidos com contato visual"),
    ("IMIT-MOT", "Imitação motora grossa"),
    ("PARE-VIS", "Pareamento visual idêntico"),
    ("R-OUV", "Resposta de ouvinte (seguir instrução)"),
    ("BRINCAR", "Brincar funcional independente"),
    ("ESCRITA", "Traçado de letras e números"),
    ("MAT", "Noções de quantidade e soma"),
    ("ESPERA", "Tolerância à espera (1 min)"),
    ("AVD", "Atividade de Vida Diária (lavar mãos)"),
    ("SOCIAL", "Cumprimentar e responder a saudação"),
    ("FONO-ART", "Articulação de fonemas bilabiais")
]

INTERCORRENCIAS_BASE = [
    ("FUGA", "Fuga de demanda", "Redirecionar fisicamente"),
    ("CHORO", "Choro e vocalização", "Ignorar se for busca de atenção"),
    ("AGRESS", "Agressividade direcionada", "Bloqueio e contenção leve"),
    ("AUTO-AG", "Autoagressão", "Contenção e bloqueio imediato"),
    ("EST-VOC", "Estereotipia vocal alta", "Redirecionar para mando apropriado"),
    ("EST-MOT", "Estereotipia motora", "Bloqueio de resposta se interferir"),
    ("CRISE-SENS", "Desregulação sensorial", "Pausa, redução de estímulos"),
    ("SONO", "Sonolência excessiva", "Pausas ativas e motoras")
]

def gerar_telefone():
    return f"(98) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def popular_banco():
    print("Iniciando injeção massiva de dados...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Limpando dados antigos (mantendo admin e notas)...")
        cursor.execute("DELETE FROM lancamentos")
        cursor.execute("DELETE FROM aluno_atividades")
        cursor.execute("DELETE FROM alunos")
        cursor.execute("DELETE FROM atividades")
        cursor.execute("DELETE FROM intercorrencias")
        cursor.execute("DELETE FROM professores WHERE username != 'admin'")
        
        # Resetando AUTOINCREMENT
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('lancamentos', 'aluno_atividades', 'alunos', 'atividades', 'intercorrencias', 'professores')")

        print("Gerando 20 Professores...")
        professores_ids = []
        senha_padrao = generate_password_hash("123456")
        
        for i in range(1, 21):
            nome = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"
            username = f"prof{i}"
            email = f"{username}@clinica.com"
            telefone = gerar_telefone()
            cursor.execute('''
                INSERT INTO professores (nome_completo, telefone, email, username, password_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, telefone, email, username, senha_padrao))
            professores_ids.append(cursor.lastrowid)

        print("Gerando Catálogo de Intercorrências...")
        intercorrencias_ids = []
        for sigla, desc, info in INTERCORRENCIAS_BASE:
            cursor.execute('''
                INSERT INTO intercorrencias (sigla, descricao, informacoes_adicionais)
                VALUES (?, ?, ?)
            ''', (sigla, desc, info))
            intercorrencias_ids.append(cursor.lastrowid)

        print("Gerando Catálogos de Atividades e 300 Alunos (15 por Professor)...")
        alunos_ids = []
        todas_atividades = {}

        for prof_id in professores_ids:
            # 10 atividades por professor
            atvs_prof = random.sample(ATIVIDADES_BASE, k=10)
            atvs_ids_prof = []
            for sigla, desc in atvs_prof:
                cursor.execute('''
                    INSERT INTO atividades (sigla, descricao, informacoes_adicionais, professor_id)
                    VALUES (?, ?, ?, ?)
                ''', (sigla, desc, f"Protocolo padrão do prof {prof_id}", prof_id))
                atvs_ids_prof.append(cursor.lastrowid)
            
            todas_atividades[prof_id] = atvs_ids_prof

            # 15 alunos por professor
            for _ in range(15):
                nome_aluno = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
                data_nasc = f"{random.randint(2014, 2022)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
                sexo = random.choice(["M", "F"])
                email_aluno = f"resp_{nome_aluno.split()[0].lower()}@email.com"
                
                cursor.execute('''
                    INSERT INTO alunos (nome, data_nascimento, terapeuta_id, sexo, preferencias, evitaveis, informacoes_adicionais, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nome_aluno, data_nasc, prof_id, sexo, "Brinquedos musicais, cócegas", "Barulho alto, luz forte", "Alergia a corante", email_aluno))
                aluno_id = cursor.lastrowid
                alunos_ids.append((aluno_id, prof_id))

                # Vincula de 4 a 7 atividades por aluno (dentre as do professor dele)
                qtd_atv = random.randint(4, 7)
                atvs_vinculadas = random.sample(atvs_ids_prof, k=qtd_atv)
                for atv_id in atvs_vinculadas:
                    cursor.execute('INSERT INTO aluno_atividades (aluno_id, atividade_id) VALUES (?, ?)', (aluno_id, atv_id))

        print("Gerando milhares de Lançamentos de Diário (Jan a Abr 2026)...")
        data_inicial = date(2026, 1, 1)
        data_final = date(2026, 4, 30)
        dias_totais = (data_final - data_inicial).days + 1
        
        lancamentos_lote = []

        for dia_delta in range(dias_totais):
            data_atual = data_inicial + timedelta(days=dia_delta)
            
            # Pula finais de semana para dar mais realismo
            if data_atual.weekday() >= 5:
                continue

            # Para cada aluno, 40% de chance de ter sessão neste dia útil
            for aluno_id, prof_id in alunos_ids:
                if random.random() > 0.40:
                    continue
                
                # Pega as atividades vinculadas a este aluno
                cursor.execute('SELECT atividade_id FROM aluno_atividades WHERE aluno_id = ?', (aluno_id,))
                atvs_do_aluno = [r[0] for r in cursor.fetchall()]
                
                # Na sessão, o professor aplica 3 a 5 atividades
                atvs_sessao = random.sample(atvs_do_aluno, k=min(len(atvs_do_aluno), random.randint(3, 5)))
                
                for atv_id in atvs_sessao:
                    # Gera as tentativas (0 a 10) - Simulando evolução (notas melhores no final de abril)
                    fator_evolucao = min(10, int((dia_delta / dias_totais) * 5))
                    
                    t1 = min(10, random.randint(0, 5) + fator_evolucao)
                    t2 = min(10, random.randint(0, 5) + fator_evolucao)
                    t3 = min(10, random.randint(0, 5) + fator_evolucao)
                    t4 = min(10, random.randint(0, 6) + fator_evolucao)
                    t5 = min(10, random.randint(0, 6) + fator_evolucao)
                    
                    # Intercorrências (15% de chance de ocorrer em alguma tentativa)
                    i1, in1, i2, in2, i3, in3, i4, in4, i5, in5 = [None]*10
                    
                    if random.random() < 0.15:
                        i1 = random.choice(intercorrencias_ids)
                        in1 = random.randint(1, 10)
                    if random.random() < 0.15:
                        i3 = random.choice(intercorrencias_ids)
                        in3 = random.randint(1, 10)

                    obs = random.choice([
                        "Realizou com bom engajamento.",
                        "Apresentou leve resistência no início.",
                        "Precisou de reforço constante.",
                        "Excelente desempenho hoje.",
                        ""
                    ])

                    lancamentos_lote.append((
                        aluno_id, prof_id, atv_id, data_atual.strftime("%Y-%m-%d"),
                        t1, t2, t3, t4, t5,
                        i1, in1, i2, in2, i3, in3, i4, in4, i5, in5, obs
                    ))

        # Insere em lotes pesados
        print(f"Salvando {len(lancamentos_lote)} registros de notas e intercorrências no banco...")
        cursor.executemany('''
            INSERT INTO lancamentos (
                aluno_id, professor_id, atividade_id, data_lancamento,
                tentativa1, tentativa2, tentativa3, tentativa4, tentativa5,
                intercorrencia1_id, int_nota1, intercorrencia2_id, int_nota2,
                intercorrencia3_id, int_nota3, intercorrencia4_id, int_nota4,
                intercorrencia5_id, int_nota5, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', lancamentos_lote)

        conn.commit()
        print("✅ Populamento Massivo Concluído com Sucesso!")
        print(f"- 20 Professores cadastrados (Login: prof1 a prof20 | Senha: 123456)")
        print(f"- 300 Alunos gerados")
        print(f"- {len(lancamentos_lote)} registros de atividades avaliadas!")

    except Exception as e:
        print(f"❌ Erro crítico ao popular o banco: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    popular_banco()