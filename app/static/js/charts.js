// app/static/js/charts.js
document.addEventListener("DOMContentLoaded", () => {
    const btnFiltrar = document.getElementById("btnFiltrar");
    if (!btnFiltrar) return;

    function getColors() {
        const root = getComputedStyle(document.documentElement);
        return {
            atv: root.getPropertyValue('--atv-dark').trim() || '#16a34a', // Verde Contínuo
            intc: root.getPropertyValue('--int-dark').trim() || '#dc2626', // Vermelho Contínuo
            grid: root.getPropertyValue('--border-color').trim() || '#e2e8f0',
            text: root.getPropertyValue('--text-color').trim() || '#333'
        };
    }

    function formatarDataBR(dataIso) {
        const partes = dataIso.split("-");
        if (partes.length !== 3) return dataIso;
        return `${partes[2]}/${partes[1]}/${partes[0]}`; // Formato dd/mm/yyyy exigido
    }

    function fetchAndDrawCharts() {
        const inicio = document.getElementById("filtro_inicio").value;
        const fim = document.getElementById("filtro_fim").value;

        let url = '/dashboard/api/dados_graficos';
        if (inicio && fim) { url += `?data_inicio=${inicio}&data_fim=${fim}`; }

        fetch(url)
            .then(res => res.json())
            .then(data => processAndDraw(data));
    }

    function processAndDraw(rawData) {
        let datasMap = {};
        
        // Agrupa os dados pelo somatório do dia (já pré-calculado na query)
        rawData.forEach(row => {
            let d = row.data_lancamento;
            if (!datasMap[d]) { 
                datasMap[d] = { count: 0, sumAtv: 0, sumIntc: 0 }; 
            }
            datasMap[d].count++;
            datasMap[d].sumAtv += row.soma_atividades;
            datasMap[d].sumIntc += row.soma_intercorrencias;
        });

        let labelsIso = Object.keys(datasMap).sort();
        let labelsBr = labelsIso.map(d => formatarDataBR(d));

        let avgAtvData = labelsIso.map(d => datasMap[d].count ? (datasMap[d].sumAtv / datasMap[d].count) : 0);
        let avgIntcData = labelsIso.map(d => datasMap[d].count ? (datasMap[d].sumIntc / datasMap[d].count) : 0);

        const colors = getColors();

        // O gráfico agora suporta ambas as linhas num único Canvas
        drawCombinedChart("chartAtividades", labelsBr, avgAtvData, avgIntcData, 50, 5, colors);
    }

    function drawCombinedChart(canvasId, labels, dataAtv, dataIntc, maxY, stepY, colors) {
        const canvas = document.getElementById(canvasId);
        if(!canvas) return;
        const ctx = canvas.getContext('2d');

        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = 400;

        const padding = { top: 30, right: 30, bottom: 50, left: 50 };
        const width = canvas.width;
        const height = canvas.height;
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        ctx.clearRect(0, 0, width, height);

        // Fundo Branco
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, width, height);

        ctx.font = "12px Arial";
        ctx.fillStyle = colors.text;
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";

        // Grid Y
        for (let i = 0; i <= maxY; i += stepY) {
            let y = height - padding.bottom - (i / maxY) * chartHeight;
            ctx.fillStyle = colors.text;
            ctx.fillText(i.toString(), padding.left - 10, y);
            
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.strokeStyle = colors.grid;
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        if (labels.length === 0) return;
        const stepX = labels.length > 1 ? chartWidth / (labels.length - 1) : chartWidth / 2;

        // Eixo X
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        labels.forEach((lbl, idx) => {
            let x = padding.left + (idx * stepX);
            ctx.fillStyle = colors.text;
            ctx.fillText(lbl, x, height - padding.bottom + 15);
            
            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, height - padding.bottom);
            ctx.strokeStyle = "rgba(0,0,0,0.05)";
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        // Desenha a linha verde (Atividades) sem suavização
        drawLine(ctx, dataAtv, colors.atv, padding, stepX, chartHeight, height, maxY);
        // Desenha a linha vermelha (Intercorrências) sem suavização
        drawLine(ctx, dataIntc, colors.intc, padding, stepX, chartHeight, height, maxY);

        // Legenda
        ctx.textAlign = "left";
        ctx.fillStyle = colors.atv;
        ctx.fillRect(padding.left, 10, 15, 15);
        ctx.fillStyle = colors.text;
        ctx.fillText("Desempenho (Atividades)", padding.left + 20, 10);

        ctx.fillStyle = colors.intc;
        ctx.fillRect(padding.left + 200, 10, 15, 15);
        ctx.fillStyle = colors.text;
        ctx.fillText("Intensidade (Intercorrências)", padding.left + 220, 10);
    }

    function drawLine(ctx, dataArr, color, padding, stepX, chartHeight, height, maxY) {
        ctx.beginPath();
        let started = false;
        for (let idx = 0; idx < dataArr.length; idx++) {
            let val = dataArr[idx];
            let x = padding.left + (idx * stepX);
            let y = height - padding.bottom - (val / maxY) * chartHeight;
            if (!started) {
                ctx.moveTo(x, y);
                started = true;
            } else {
                ctx.lineTo(x, y); // Linhas contínuas e retas
            }
        }
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.stroke();

        // Pontos
        for (let idx = 0; idx < dataArr.length; idx++) {
            let val = dataArr[idx];
            let x = padding.left + (idx * stepX);
            let y = height - padding.bottom - (val / maxY) * chartHeight;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    }

    btnFiltrar.addEventListener("click", fetchAndDrawCharts);
    window.addEventListener("resize", fetchAndDrawCharts);
    fetchAndDrawCharts();
});