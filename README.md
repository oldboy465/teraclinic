# 🌳 TERA Clinic - Sistema de Acompanhamento Terapêutico

O **TERA Clinic** é uma plataforma robusta de gestão clínica e acompanhamento terapêutico, projetada para transformar registros qualitativos de sessões em dados analíticos precisos. O sistema atende profissionais que buscam monitorar a evolução de pacientes através de métricas de desempenho em atividades e controle de intercorrências.

## 🚀 Funcionalidades Principais

* **Painel Analítico (Dashboard)**: Visualização em tempo real de métricas globais, incluindo total de alunos, média de notas em atividades e intensidade de intercorrências.
* **Gestão 360°**: Módulos completos para cadastro e edição de Alunos, Terapeutas, Atividades e protocolos de Intercorrências.
* **Diário de Lançamentos**: Registro simplificado de sessões com seleção de níveis de suporte (notas de 0 a 10) para cada intervenção.
* **Relatórios Analíticos Avançados**:
    * Filtros dinâmicos por período, aluno, professor ou atividade.
    * Gráficos de linhas de alta precisão (sem suavização) com cores exclusivas por atividade.
    * Exportação nativa para **PDF** em orientação paisagem.
    * Resumo estruturado para cópia e envio via **WhatsApp**.
* **Dicionário Semântico**: Personalização total do significado das notas de suporte e crise, adaptando-se ao protocolo de cada clínica.

## 🛠️ Tecnologias Utilizadas

* **Backend**: Python 3.12 com Framework Flask.
* **Banco de Dados**: SQLite3 com suporte a chaves estrangeiras.
* **Frontend**: HTML5, CSS3 (com suporte a temas Dark/Light) e JavaScript Vanilla.
* **PDF Engine**: xhtml2pdf para renderização de templates.
* **Segurança**: Werkzeug para hashing de senhas e proteção de rotas via decoradores de sessão.

## 📁 Estrutura do Projeto

O projeto segue a arquitetura **MVC (Model-View-Controller)** para garantir escalabilidade:

* `/app/models`: Lógica de dados e interação com SQLite.
* `/app/controllers`: Regras de negócio e controle de rotas.
* `/app/views`: Templates dinâmicos em Jinja2.
* `/app/static`: Ativos estáticos (CSS, JS, Imagens e Uploads).

## ⚙️ Como Instalar e Rodar

1. **Clonar o repositório**:
   ```bash
   git clone [https://github.com/oldboy465/teraclinic.git](https://github.com/oldboy465/teraclinic.git)
   cd TERA_v1/Tera
