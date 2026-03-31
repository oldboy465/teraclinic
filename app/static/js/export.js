// app/static/js/export.js

// Mantém a função original funcionando para a tela /relatorios/aluno/<id>
function copiarParaWhatsApp() {
    const nomePaciente = document.querySelector('.info-panel p:nth-child(1)').innerText.replace('Paciente/Aluno:', '').trim();
    let texto = `*Relatório Clínico - TERA*\n*Paciente:* ${nomePaciente}\n\n*Resumo de Lançamentos:*\n`;

    const linhas = document.querySelectorAll('#dadosRelatorio tr');
    
    linhas.forEach(linha => {
        const colunas = linha.querySelectorAll('td');
        const data = colunas[0].innerText.trim();
        const terapeuta = colunas[1].innerText.trim();
        const atividade = colunas[2].innerText.trim();
        const intercorrencia = colunas[3].innerText.trim();

        texto += `📅 *${data}* (Terapeuta: ${terapeuta})\n`;
        if (atividade !== '-') texto += `   ✅ Ativ: ${atividade}\n`;
        if (intercorrencia !== '-') texto += `   ⚠️ Interc: ${intercorrencia}\n`;
        texto += `\n`;
    });

    navigator.clipboard.writeText(texto).then(() => {
        alert('Conteúdo copiado com sucesso! Agora é só colar no WhatsApp do responsável.');
    }).catch(err => {
        alert('Erro ao copiar texto: ' + err);
    });
}

// --- NOVA FUNÇÃO PARA O RELATÓRIO ANALÍTICO GERAL ---
function copiarRelatorioGeralWhatsApp() {
    // Busca dados do cabeçalho estrutural
    const dataGeracao = document.getElementById('infoDataGeracao')?.innerText || '';
    const filtros = document.getElementById('infoFiltros')?.innerText || '';

    let texto = `*📊 RELATÓRIO ANALÍTICO - TERA*\n`;
    texto += `Gerado em: ${dataGeracao}\n`;
    texto += `Filtros: ${filtros}\n\n`;

    // Verifica se os dadosBrutos existem (injetados na view)
    if (typeof dadosBrutos === 'undefined' || dadosBrutos.length === 0) {
        texto += `Nenhum dado localizado para os filtros informados.\n`;
        copiarTexto(texto);
        return;
    }

    texto += `*Histórico de Lançamentos:*\n`;

    // Limite de segurança: envia no máximo os 15 primeiros itens para o WhatsApp
    const limite = Math.min(dadosBrutos.length, 15);

    for (let i = 0; i < limite; i++) {
        const row = dadosBrutos[i];
        
        texto += `📅 *${row.data}* | 👦 ${row.aluno}\n`;
        if (row.atividade) {
            texto += `   ✅ Ativ: ${row.atividade} (Nota: ${row.nota_atividade})\n`;
        }
        if (row.intercorrencia) {
            texto += `   ⚠️ Interc: ${row.intercorrencia} (Nota: ${row.nota_intercorrencia})\n`;
        }
        texto += `\n`;
    }

    if (dadosBrutos.length > 15) {
        texto += `_...e mais ${dadosBrutos.length - 15} registro(s) oculto(s) nesta exportação. Consulte o sistema ou gere o PDF para visualização completa._`;
    }

    copiarTexto(texto);
}

// Função auxiliar genérica para efetuar a cópia
function copiarTexto(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        alert('Relatório geral copiado com sucesso! Pode colar no WhatsApp da coordenação/responsável.');
    }).catch(err => {
        alert('Erro ao copiar texto: ' + err);
    });
}