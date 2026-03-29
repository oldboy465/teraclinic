// app/static/js/validations.js
document.addEventListener("DOMContentLoaded", () => {
    // 1. Validação de Tamanho de Arquivo (Restrição: Máximo 2MB)
    const fileInputs = document.querySelectorAll(".file-input");
    fileInputs.forEach(input => {
        input.addEventListener("change", function() {
            if (this.files && this.files[0]) {
                const maxAllowedSize = 2 * 1024 * 1024; // 2MB
                if (this.files[0].size > maxAllowedSize) {
                    alert("Atenção: O arquivo excede o limite de 2MB. Por favor, escolha uma imagem menor.");
                    this.value = ""; // Limpa o input
                }
            }
        });
    });

    // 2. Máscara de Telefone Padrão Brasileiro
    const phoneInputs = document.querySelectorAll(".telefone-input");
    phoneInputs.forEach(input => {
        input.addEventListener("input", function(e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    });
});