// app/static/js/relatorio_geral.js

// Variável global para manter a referência aos gráficos caso precisem ser exportados
let chartInstances = [];

document.addEventListener("DOMContentLoaded", () => {
    
    // Verifica se os dados processados pelo backend chegaram corretamente na view
    if (typeof lancamentosAgrupados === 'undefined' || Object.keys(lancamentosAgrupados).length === 0) {
        const legend = document.getElementById('chartLegend');
        if(legend) {
            legend.innerHTML = '<em>Gráfico não disponível: Sem dados para exibir.</em>';
        }
        return;
    }

    // Função interna para formatar a data que vem no padrão do banco (YYYY-MM-DD)
    // para o padrão brasileiro exigido pelo requisito (DD/MM/YYYY)
    function formatarDataBR(dataIso) {
        const partes = dataIso.split("-");
        if (partes.length !== 3) {
            return dataIso;
        }
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    // Identifica todos os elementos Canvas na página.
    // Como agora o sistema gera um gráfico para CADA atividade selecionada,
    // precisamos iterar sobre todos eles para instanciar os gráficos do ChartJS.
    const canvases = document.querySelectorAll('.relatorioChartCanvas');

    canvases.forEach(canvas => {
        // Pega o nome/sigla da atividade que este canvas específico vai renderizar
        const sigla = canvas.getAttribute('data-sigla');
        
        // Pega apenas os dados pertencentes a esta atividade
        const dados = lancamentosAgrupados[sigla];
        
        if (!dados) {
            return; // Se não houver dados para esta sigla, pula o loop
        }

        let mapData = {};
        
        // Agrupa e soma as notas de atividades e intercorrências pelo dia exato
        dados.forEach(linha => {
            let dataLancamento = linha.data_lancamento;
            
            if (!mapData[dataLancamento]) {
                mapData[dataLancamento] = { 
                    somaAtv: 0, 
                    somaIntc: 0, 
                    count: 0 
                };
            }
            
            mapData[dataLancamento].count++;
            mapData[dataLancamento].somaAtv += linha.soma_atividades;
            mapData[dataLancamento].somaIntc += linha.soma_intercorrencias;
        });

        // Ordenação cronológica correta das datas do eixo X
        const datesIso = Object.keys(mapData).sort();
        
        // Aplica a formatação BR após a ordenação correta ISO
        const datesBr = datesIso.map(d => formatarDataBR(d));
        
        // Arrays de valores finais que irão alimentar a linha verde (Atividades)
        // e a linha vermelha (Intercorrências)
        const dataAtv = datesIso.map(d => mapData[d].somaAtv / mapData[d].count);
        const dataIntc = datesIso.map(d => mapData[d].somaIntc / mapData[d].count);

        // Inicia a renderização do Chart.js para este canvas específico
        const chartInstance = new Chart(canvas, {
            type: 'line',
            data: {
                labels: datesBr,
                datasets: [
                    {
                        label: 'Desempenho da Atividade (Soma das Tentativas)',
                        data: dataAtv,
                        borderColor: '#16a34a', // Linha Verde Contínua conforme solicitado
                        backgroundColor: '#16a34a',
                        borderWidth: 3,
                        pointRadius: 5,
                        fill: false,
                        tension: 0 // Zera a suavização da linha (linha reta estrita)
                    },
                    {
                        label: 'Intensidade de Intercorrências (Soma das Notas)',
                        data: dataIntc,
                        borderColor: '#dc2626', // Linha Vermelha Contínua conforme solicitado
                        backgroundColor: '#dc2626',
                        borderWidth: 3,
                        pointRadius: 5,
                        fill: false,
                        tension: 0 // Zera a suavização da linha (linha reta estrita)
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 50, // Limite máximo estabelecido pela matemática de 5 tentativas x nota 10
                        ticks: { 
                            stepSize: 5 
                        }
                    }
                },
                plugins: {
                    legend: { 
                        position: 'top' 
                    },
                    title: {
                        display: true,
                        text: `Evolução Analítica: ${sigla}`,
                        font: {
                            size: 16
                        }
                    }
                },
                // Plugin customizado para garantir que o fundo do Canvas seja forçado
                // para branco puro. Isso impede que o PDF fique com fundo transparente e preto.
                animation: {
                    onComplete: function() {
                        const ctx = this.ctx;
                        ctx.save();
                        ctx.globalCompositeOperation = 'destination-over';
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, this.width, this.height);
                        ctx.restore();
                    }
                }
            }
        });

        // Salva a instância caso seja necessário manipulá-la globalmente depois
        chartInstances.push(chartInstance);
    });
});

// ============================================================================
// FUNÇÃO DE EXPORTAÇÃO (PDF / EMAIL)
// ============================================================================
// Diferente da versão anterior que convertia apenas um canvas, esta função
// itera por todos os gráficos renderizados na tela e gera uma lista de imagens
// em Base64 para que o backend possa construir múltiplas páginas no PDF.
function baixarPDF() {
    
    // Coleta todos os canvas na página
    const canvases = document.querySelectorAll('.relatorioChartCanvas');
    
    // Pega o formulário de envio
    const formPdf = document.getElementById("formPdf");
    
    if (canvases.length === 0) {
        // Se não houver gráficos, submete o formulário diretamente
        // O relatório em PDF será gerado apenas com a tabela de dados
        formPdf.submit();
        return;
    }

    // Container escondido para injetar os inputs de imagem antes do envio
    const container = document.getElementById('hidden_inputs_container');
    container.innerHTML = ''; // Limpa execuções anteriores para evitar duplicatas

    // Transforma cada Canvas em uma string de imagem (PNG/Base64)
    // e cria um input dinâmico para enviá-lo pelo método POST
    canvases.forEach(canvas => {
        const imgData = canvas.toDataURL("image/png");
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'chart_images[]'; // A notação com [] permite ao backend ler como Array
        input.value = imgData;
        
        container.appendChild(input);
    });

    // Submete o formulário com todas as imagens embutidas
    formPdf.submit();
}