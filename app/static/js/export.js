// app/static/js/export.js
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

    // Copia para o Clipboard do sistema
    navigator.clipboard.writeText(texto).then(() => {
        alert('Conteúdo copiado com sucesso! Agora é só colar no WhatsApp do responsável.');
    }).catch(err => {
        alert('Erro ao copiar texto: ' + err);
    });
}