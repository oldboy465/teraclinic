// app/static/js/lancamentos.js
document.addEventListener("DOMContentLoaded", () => {
    const alunoSelect = document.getElementById("aluno_id_select");
    const container = document.getElementById("container_atividades");
    const tbody = document.getElementById("tbody_atividades_dinamico");
    const loadingMsg = document.getElementById("loading_msg");

    // Captura as opções pre-renderizadas no HTML para montar os selects dinamicamente
    const optIntc = document.getElementById("opcoes_intercorrencias").innerHTML;
    const optNotasAtv = document.getElementById("opcoes_notas_atv").innerHTML;
    const optNotasInt = document.getElementById("opcoes_notas_int").innerHTML;

    if (alunoSelect) {
        alunoSelect.addEventListener("change", function() {
            const alunoId = this.value;
            
            if (!alunoId) {
                container.style.display = "none";
                tbody.innerHTML = "";
                return;
            }

            container.style.display = "none";
            loadingMsg.style.display = "block";
            tbody.innerHTML = "";

            // Busca as atividades exclusivas vinculadas ao aluno selecionado
            fetch(`/lancamentos/api/atividades/${alunoId}`)
                .then(res => res.json())
                .then(atividades => {
                    loadingMsg.style.display = "none";
                    
                    if (atividades.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">Nenhuma atividade vinculada a este aluno no cadastro.</td></tr>`;
                    } else {
                        atividades.forEach(atv => {
                            let tr = document.createElement("tr");

                            // Array de IDs para o backend processar os blocos
                            let hiddenInput = `<input type="hidden" name="atividade_ids[]" value="${atv.id}">`;

                            // Bloco 1: 5 Tentativas de Atividades (Agora em Layout Vertical)
                            let tentativasHtml = `<div style="display:flex; flex-direction:column; gap:8px;">`;
                            for(let i=1; i<=5; i++) {
                                tentativasHtml += `
                                    <div style="display:flex; gap:5px; align-items:center; background: var(--hover-color); padding: 5px; border-radius: 5px;">
                                        <small style="font-weight:bold; min-width: 25px; color:var(--primary-color);">T${i}:</small>
                                        <select name="t${i}_${atv.id}" class="input-suave" style="padding:4px; flex: 1; text-align:center;">
                                            ${optNotasAtv}
                                        </select>
                                    </div>
                                `;
                            }
                            tentativasHtml += `</div>`;

                            // Bloco 2: 5 Campos de Intercorrências vinculadas às tentativas (Layout Vertical)
                            let intcHtml = `<div style="display:flex; flex-direction:column; gap:8px;">`;
                            for(let i=1; i<=5; i++) {
                                intcHtml += `
                                    <div style="display:flex; gap:5px; align-items:center; background: var(--hover-color); padding: 5px; border-radius: 5px;">
                                        <small style="font-weight:bold; min-width: 25px;">T${i}:</small>
                                        <select name="i${i}_${atv.id}" class="input-suave" style="padding:4px; flex: 2;" title="Tipo de Intercorrência">
                                            ${optIntc}
                                        </select>
                                        <select name="in${i}_${atv.id}" class="input-suave" style="padding:4px; flex: 1;" title="Nota/Intensidade">
                                            ${optNotasInt}
                                        </select>
                                    </div>
                                `;
                            }
                            intcHtml += `</div>`;

                            // Bloco 3: Observações de texto
                            let obsHtml = `<textarea name="obs_${atv.id}" class="input-suave" rows="10" placeholder="Comportamentos, dados clínicos ou evolução..."></textarea>`;

                            tr.innerHTML = `
                                <td style="vertical-align: top;">
                                    <strong>${atv.sigla}</strong><br>
                                    <small class="muted-text">${atv.descricao}</small>
                                    ${hiddenInput}
                                </td>
                                <td style="vertical-align: top; border-left: 2px solid var(--atv-dark);">${tentativasHtml}</td>
                                <td style="vertical-align: top; border-left: 2px solid var(--int-dark);">${intcHtml}</td>
                                <td style="vertical-align: top;">${obsHtml}</td>
                            `;

                            tbody.appendChild(tr);
                        });
                    }
                    container.style.display = "block";
                })
                .catch(err => {
                    console.error("Erro ao carregar atividades", err);
                    loadingMsg.style.display = "none";
                    alert("Falha de comunicação com o servidor. Tente novamente.");
                });
        });
    }
});