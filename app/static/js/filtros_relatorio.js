// app/static/js/filtros_relatorio.js
document.addEventListener("DOMContentLoaded", () => {
    const professorSelect = document.getElementById("professor_select");
    const alunoSelect = document.getElementById("aluno_select");
    const atividadesContainer = document.getElementById("atividades_container");

    const atualizarAlunos = (professorId) => {
        if (!professorId) return;
        fetch(`/relatorios/api/alunos/${professorId}`)
            .then(res => res.json())
            .then(alunos => {
                alunoSelect.innerHTML = '<option value="">Todos os Alunos</option>';
                alunos.forEach(a => {
                    alunoSelect.innerHTML += `<option value="${a.id}">${a.nome}</option>`;
                });
                atualizarAtividades(""); // Limpa atividades
            });
    };

    const atualizarAtividades = (alunoId) => {
        if (!alunoId) {
            atividadesContainer.innerHTML = '<span class="muted-text">Selecione um aluno para listar as atividades.</span>';
            return;
        }
        fetch(`/relatorios/api/atividades/${alunoId}`)
            .then(res => res.json())
            .then(atividades => {
                atividadesContainer.innerHTML = '';
                if (atividades.length === 0) {
                    atividadesContainer.innerHTML = '<span class="muted-text">Nenhuma atividade vinculada.</span>';
                } else {
                    atividades.forEach(atv => {
                        atividadesContainer.innerHTML += `
                            <label style="display: block; margin-bottom: 8px; cursor: pointer; font-weight: normal;">
                                <input type="checkbox" name="atividades_ids" value="${atv.id}" style="margin-right: 8px;">
                                ${atv.sigla} <small class="muted-text">- ${atv.descricao}</small>
                            </label>`;
                    });
                }
            });
    };

    if (professorSelect) {
        professorSelect.addEventListener("change", (e) => atualizarAlunos(e.target.value));
    }

    if (alunoSelect) {
        alunoSelect.addEventListener("change", (e) => atualizarAtividades(e.target.value));
        // Se já houver um aluno pré-selecionado (ex: volta de erro)
        if (alunoSelect.value) atualizarAtividades(alunoSelect.value);
    }
});