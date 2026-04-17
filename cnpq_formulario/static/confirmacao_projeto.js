document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // 1. Função de Loading
    function mostrarLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('d-none');
            overlay.style.display = 'flex'; 
        }
    }

    // 2. Gatilho no Botão
    const btnConfirmar = document.getElementById('btn-confirmar');
    
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function(event) {
            // Não usamos preventDefault() porque queremos que o link funcione
            // Apenas mostramos a tela de carregamento enquanto a próxima página não chega
            mostrarLoading();
        });
    }
});