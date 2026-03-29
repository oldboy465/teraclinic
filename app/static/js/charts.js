// app/static/js/charts.js
document.addEventListener("DOMContentLoaded", () => {
    const btnFiltrar = document.getElementById("btnFiltrar");
    if (!btnFiltrar) return; // Só roda se estiver no dashboard

    // Cores obtidas do CSS (Pastéis)
    function getColors() {
        const root = getComputedStyle(document.documentElement);
        return {
            atv: root.getPropertyValue('--atv-dark').trim() || '#3a8570',
            intc: root.getPropertyValue('--int-dark').trim() || '#cc5c39',
            grid: root.getPropertyValue('--border-color').trim() || '#e2e8f0',
            text: root.getPropertyValue('--text-color').trim() || '#333'
        };
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
        // Agrupar dados por data
        let datasMap = {};
        rawData.forEach(row => {
            let d = row.data_lancamento;
            if (!datasMap[d]) { datasMap[d] = { countAtv: 0, sumAtv: 0, countIntc: 0, sumIntc: 0, notasAtv: [], notasIntc: [] }; }
            
            if (row.nota_atividade !== null) {
                datasMap[d].countAtv++;
                datasMap[d].sumAtv += row.nota_atividade;
                datasMap[d].notasAtv.push(row.nota_atividade);
            }
            if (row.nota_intercorrencia !== null) {
                datasMap[d].countIntc++;
                datasMap[d].sumIntc += row.nota_intercorrencia;
                datasMap[d].notasIntc.push(row.nota_intercorrencia);
            }
        });

        // Ordenar as datas
        let labels = Object.keys(datasMap).sort();
        
        // Preparar arrays de dados
        let avgAtvData = labels.map(d => datasMap[d].notasAtv.length ? (datasMap[d].sumAtv / datasMap[d].countAtv) : null);
        let sumAtvData = labels.map(d => datasMap[d].sumAtv);
        let avgIntcData = labels.map(d => datasMap[d].notasIntc.length ? (datasMap[d].sumIntc / datasMap[d].countIntc) : null);
        let sumIntcData = labels.map(d => datasMap[d].sumIntc);

        const colors = getColors();

        // 1. Atividades por Data (Média da nota, Y: 0 a 10, escala 2)
        drawNativeLineChart("chartAtividades", labels, avgAtvData, 10, 2, colors.atv, colors);
        // 2. Soma das Atividades (Y: 0 a 50, escala 5)
        drawNativeLineChart("chartSomaAtividades", labels, sumAtvData, 50, 5, colors.atv, colors);
        // 3. Intercorrências por Data (Média, Y: 0 a 10, escala 2)
        drawNativeLineChart("chartIntercorrencias", labels, avgIntcData, 10, 2, colors.intc, colors);
        // 4. Soma das Intercorrências (Y: 0 a 50, escala 5)
        drawNativeLineChart("chartSomaIntercorrencias", labels, sumIntcData, 50, 5, colors.intc, colors);
    }

    // Desenha gráfico de linhas com Canvas Puro (Sem Smoothing, dados reais)
    function drawNativeLineChart(canvasId, labels, dataArr, maxY, stepY, lineColor, colors) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        
        // Ajuste de DPI para não ficar embaçado
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = 300; 

        const padding = { top: 20, right: 20, bottom: 40, left: 40 };
        const width = canvas.width;
        const height = canvas.height;
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        ctx.clearRect(0, 0, width, height);

        // Desenhar Grid Eixo Y
        ctx.font = "12px sans-serif";
        ctx.fillStyle = colors.text;
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";

        for (let i = 0; i <= maxY; i += stepY) {
            let y = height - padding.bottom - (i / maxY) * chartHeight;
            // Texto do eixo Y
            ctx.fillText(i.toString(), padding.left - 10, y);
            // Linha do Grid
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.strokeStyle = colors.grid;
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // Se não houver dados, para aqui
        if (labels.length === 0) return;

        // Calcular posições X
        const stepX = labels.length > 1 ? chartWidth / (labels.length - 1) : chartWidth / 2;

        // Desenhar Eixo X Labels
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        labels.forEach((lbl, idx) => {
            let x = padding.left + (idx * stepX);
            let dateStr = lbl.split("-").reverse().slice(0, 2).join("/"); // Formata DD/MM
            ctx.fillText(dateStr, x, height - padding.bottom + 10);
        });

        // Desenhar Linha de Dados (Sem interpolação/smoothing)
        ctx.beginPath();
        let started = false;
        for (let idx = 0; idx < dataArr.length; idx++) {
            let val = dataArr[idx];
            if (val !== null) {
                let x = padding.left + (idx * stepX);
                let y = height - padding.bottom - (val / maxY) * chartHeight;
                if (!started) {
                    ctx.moveTo(x, y);
                    started = true;
                } else {
                    ctx.lineTo(x, y); // Linhas retas e puras!
                }
            }
        }
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 2;
        ctx.stroke();

        // Desenhar Pontos
        for (let idx = 0; idx < dataArr.length; idx++) {
            let val = dataArr[idx];
            if (val !== null) {
                let x = padding.left + (idx * stepX);
                let y = height - padding.bottom - (val / maxY) * chartHeight;
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fillStyle = lineColor;
                ctx.fill();
            }
        }
    }

    // Event Listeners
    btnFiltrar.addEventListener("click", fetchAndDrawCharts);
    window.addEventListener("resize", fetchAndDrawCharts);
    window.addEventListener("themeChanged", fetchAndDrawCharts); // Redesenha se mudar tema

    // Chamada inicial
    fetchAndDrawCharts();
});