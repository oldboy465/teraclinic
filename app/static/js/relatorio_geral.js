// app/static/js/relatorio_geral.js

// Tornei a variável legend HTML global para o PDF poder pegá-la caso precise,
// mas a imagem já vai capturar o gráfico em si.
let myCanvas;

document.addEventListener("DOMContentLoaded", () => {
    if (typeof dadosBrutos === 'undefined' || dadosBrutos.length === 0) {
        const legend = document.getElementById('chartLegend');
        if(legend) legend.innerHTML = '<em>Gráfico não disponível: Sem dados para exibir.</em>';
        return;
    }

    myCanvas = document.getElementById('relatorioChart');
    if (!myCanvas) return; // Se não tem canvas, estamos no PDF renderizado
    const ctx = myCanvas.getContext('2d');

    const container = myCanvas.parentElement;
    myCanvas.width = container.clientWidth;
    myCanvas.height = 400;

    const colorPalette = [
        '#2563eb', '#16a34a', '#d97706', '#9333ea', '#db2777', 
        '#0891b2', '#ea580c', '#4f46e5', '#65a30d', '#dc2626'
    ];
    let colorIndex = 0;
    const activityColors = {};

    function getColorForActivity(name) {
        if (!activityColors[name]) {
            activityColors[name] = colorPalette[colorIndex % colorPalette.length];
            colorIndex++;
        }
        return activityColors[name];
    }

    const datesRaw = [...new Set(dadosBrutos.map(d => d.data))].sort();
    const labelsX = datesRaw.map(d => {
        const parts = d.split('-');
        return `${parts[2]}/${parts[1]}`; 
    });

    let datasets = [];
    let maxY = 10;

    if (configGrafico === 'separado') {
        const mapAtividades = {};
        const mapIntercorrencias = {};

        dadosBrutos.forEach(row => {
            if (row.atividade && row.nota_atividade !== null) {
                if (!mapAtividades[row.atividade]) {
                    mapAtividades[row.atividade] = { color: getColorForActivity(row.atividade), dataMap: {} };
                }
                if (!mapAtividades[row.atividade].dataMap[row.data]) {
                    mapAtividades[row.atividade].dataMap[row.data] = { sum: 0, count: 0 };
                }
                mapAtividades[row.atividade].dataMap[row.data].sum += row.nota_atividade;
                mapAtividades[row.atividade].dataMap[row.data].count++;
            }

            if (row.intercorrencia && row.nota_intercorrencia !== null) {
                const labelIntc = `⚠️ ${row.intercorrencia}`;
                if (!mapIntercorrencias[labelIntc]) {
                    mapIntercorrencias[labelIntc] = { color: '#ef4444', dataMap: {} };
                }
                if (!mapIntercorrencias[labelIntc].dataMap[row.data]) {
                    mapIntercorrencias[labelIntc].dataMap[row.data] = { sum: 0, count: 0 };
                }
                mapIntercorrencias[labelIntc].dataMap[row.data].sum += row.nota_intercorrencia;
                mapIntercorrencias[labelIntc].dataMap[row.data].count++;
            }
        });

        for (const [name, obj] of Object.entries(mapAtividades)) {
            let dataArr = datesRaw.map(d => obj.dataMap[d] ? (obj.dataMap[d].sum / obj.dataMap[d].count) : null);
            datasets.push({ name: name, color: obj.color, data: dataArr });
        }
        for (const [name, obj] of Object.entries(mapIntercorrencias)) {
            let dataArr = datesRaw.map(d => obj.dataMap[d] ? (obj.dataMap[d].sum / obj.dataMap[d].count) : null);
            datasets.push({ name: name, color: obj.color, data: dataArr });
        }

    } else {
        let somatorioAtv = datesRaw.map(() => 0);
        let somatorioIntc = datesRaw.map(() => 0);
        let maxSoma = 0;

        dadosBrutos.forEach(row => {
            const dateIdx = datesRaw.indexOf(row.data);
            if (row.nota_atividade !== null) somatorioAtv[dateIdx] += row.nota_atividade;
            if (row.nota_intercorrencia !== null) somatorioIntc[dateIdx] += row.nota_intercorrencia;
            
            if (somatorioAtv[dateIdx] > maxSoma) maxSoma = somatorioAtv[dateIdx];
            if (somatorioIntc[dateIdx] > maxSoma) maxSoma = somatorioIntc[dateIdx];
        });

        maxY = maxSoma < 10 ? 10 : Math.ceil(maxSoma / 5) * 5; 

        datasets.push({ name: 'Soma Total de Atividades', color: '#16a34a', data: somatorioAtv });
        datasets.push({ name: 'Soma Total de Intercorrências', color: '#dc2626', data: somatorioIntc });
    }

    function renderChart() {
        const padding = { top: 20, right: 30, bottom: 40, left: 40 };
        const w = myCanvas.width;
        const h = myCanvas.height;
        const chartW = w - padding.left - padding.right;
        const chartH = h - padding.top - padding.bottom;

        // Fundo branco no Canvas para garantir que a imagem salva fique com fundo branco no PDF
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, w, h);

        ctx.font = "11px Arial";
        ctx.fillStyle = "#64748b";
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";

        const stepsY = 5;
        for (let i = 0; i <= stepsY; i++) {
            let val = (maxY / stepsY) * i;
            let y = h - padding.bottom - (val / maxY) * chartH;
            
            ctx.fillStyle = "#64748b";
            ctx.fillText(Math.round(val), padding.left - 10, y);
            
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(w - padding.right, y);
            ctx.strokeStyle = "#e2e8f0"; 
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        const stepX = labelsX.length > 1 ? chartW / (labelsX.length - 1) : chartW / 2;

        // --- Adicionando as linhas de grade Verticais (Dias) ---
        labelsX.forEach((lbl, idx) => {
            let x = padding.left + (idx * stepX);
            
            // Desenha a linha vertical fina e suave
            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, h - padding.bottom);
            ctx.strokeStyle = "#f1f5f9"; // Cor bem sutil
            ctx.lineWidth = 1;
            ctx.stroke();

            // Escreve a data
            ctx.fillStyle = "#64748b";
            ctx.fillText(lbl, x, h - padding.bottom + 10);
        });

        datasets.forEach(ds => {
            ctx.beginPath();
            let hasStarted = false;

            ds.data.forEach((val, idx) => {
                if (val !== null) {
                    let x = padding.left + (idx * stepX);
                    let y = h - padding.bottom - (val / maxY) * chartH;

                    if (!hasStarted) {
                        ctx.moveTo(x, y);
                        hasStarted = true;
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
            });
            ctx.strokeStyle = ds.color;
            ctx.lineWidth = 2.5;
            ctx.stroke();

            ds.data.forEach((val, idx) => {
                if (val !== null) {
                    let x = padding.left + (idx * stepX);
                    let y = h - padding.bottom - (val / maxY) * chartH;
                    ctx.beginPath();
                    ctx.arc(x, y, 4, 0, Math.PI * 2);
                    ctx.fillStyle = ds.color;
                    ctx.fill();
                    ctx.strokeStyle = "#fff";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }
            });
        });

        // Legenda html
        const legendContainer = document.getElementById('chartLegend');
        if (legendContainer) {
            legendContainer.innerHTML = '';
            datasets.forEach(ds => {
                const badge = document.createElement('span');
                badge.style.display = 'inline-block';
                badge.style.margin = '0 10px';
                badge.innerHTML = `<span style="display:inline-block; width:12px; height:12px; background-color:${ds.color}; border-radius:50%; margin-right:5px; vertical-align:middle;"></span>${ds.name}`;
                legendContainer.appendChild(badge);
            });
        }
    }

    renderChart();
});

// Função chamada pelo botão "Baixar em PDF"
function baixarPDF() {
    if (!myCanvas) {
        alert("Gráfico não carregado.");
        return;
    }
    
    // Captura a imagem do canvas como Base64 (PNG)
    const imgData = myCanvas.toDataURL("image/png");
    
    // Coloca a string Base64 no input oculto
    document.getElementById("chart_image_input").value = imgData;
    
    // Submete o formulário para a mesma rota (já contém os query params)
    const form = document.getElementById("formPdf");
    form.action = window.location.href; // Mantém os filtros da URL
    form.submit();
}