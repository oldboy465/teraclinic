// app/static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
    const themeToggleBtn = document.getElementById("themeToggle");
    const htmlElement = document.documentElement;

    // Checa preferência salva no navegador
    const savedTheme = localStorage.getItem("tera_theme");
    if (savedTheme) {
        htmlElement.setAttribute("data-theme", savedTheme);
        updateBtnText(savedTheme);
    }

    // Alterna o tema
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            let currentTheme = htmlElement.getAttribute("data-theme");
            let newTheme = currentTheme === "light" ? "dark" : "light";
            
            htmlElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("tera_theme", newTheme);
            updateBtnText(newTheme);
            
            // Dispara um evento para os gráficos redesenharem com as novas cores
            window.dispatchEvent(new Event('themeChanged'));
        });
    }

    function updateBtnText(theme) {
        if(themeToggleBtn) {
            themeToggleBtn.innerText = theme === "light" ? "🌙 Modo Escuro" : "☀️ Modo Claro";
        }
    }
});