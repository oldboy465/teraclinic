// app/static/js/relatorio_geral.js

let chartInstances = [];

document.addEventListener("DOMContentLoaded", () => {

    if (typeof lancamentosAgrupados === 'undefined' || Object.keys(lancamentosAgrupados).length === 0) {
        const legend = document.getElementById('chartLegend');
        if(legend) {
            legend.innerHTML = '<em>Gráfico não disponível: Sem dados para exibir.</em>';
        }
        return;
    }

    function formatarDataBR(dataIso) {
        const partes = dataIso.split("-");
        if (partes.length !== 3) {
            return dataIso;
        }
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    const canvases = document.querySelectorAll('.relatorioChartCanvas');

    canvases.forEach(canvas => {
        const sigla = canvas.getAttribute('data-sigla');
        const dados = lancamentosAgrupados[sigla];

        if (!dados) {
            return;
        }

        let mapData = {};

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

        const datesIso = Object.keys(mapData).sort();
        const datesBr = datesIso.map(d => formatarDataBR(d));

        const dataAtv = datesIso.map(d => mapData[d].somaAtv / mapData[d].count);
        const dataIntc = datesIso.map(d => mapData[d].somaIntc / mapData[d].count);

        const chartInstance = new Chart(canvas, {
            type: 'line',
            data: {
                labels: datesBr,
                datasets: [
                    {
                        label: 'Desempenho da Atividade (Soma das Tentativas)',
                        data: dataAtv,
                        borderColor: '#16a34a',
                        backgroundColor: '#16a34a',
                        borderWidth: 3,
                        pointRadius: 5,
                        fill: false,
                        tension: 0
                    },
                    {
                        label: 'Intensidade de Intercorrências (Soma das Notas)',
                        data: dataIntc,
                        borderColor: '#dc2626',
                        backgroundColor: '#dc2626',
                        borderWidth: 3,
                        pointRadius: 5,
                        fill: false,
                        tension: 0
                    }
                ]
            },
            options: {
                // CORREÇÃO CRÍTICA: Falsa para permitir que o CSS .canvas-container controle a altura
                maintainAspectRatio: false, 
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 50,
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

        chartInstances.push(chartInstance);
    });
});

function baixarPDF() {

    const canvases = document.querySelectorAll('.relatorioChartCanvas');
    const formPdf = document.getElementById("formPdf");

    if (canvases.length === 0) {
        formPdf.submit();
        return;
    }

    const container = document.getElementById('hidden_inputs_container');
    container.innerHTML = ''; 

    canvases.forEach(canvas => {
        // CORREÇÃO CRÍTICA: Definir uma qualidade levemente reduzida ao exportar para PNG
        // e um fundo branco opaco para evitar artefatos ao passar para o PDF.
        const imgData = canvas.toDataURL("image/png", 1.0);

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'chart_images[]'; 
        input.value = imgData;

        container.appendChild(input);
    });

    formPdf.submit();
}