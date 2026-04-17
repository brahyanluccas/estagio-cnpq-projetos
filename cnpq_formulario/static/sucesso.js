document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // 1. Função para Mostrar Loading com Temporizador
    function ativarLoadingPDF() {
        const overlay = document.getElementById('loadingOverlay');
        
        if (overlay) {
            // Mostra o loading
            overlay.classList.remove('d-none');
            overlay.style.display = 'flex'; 

            // O SEGREDO: Esconde sozinho após 5 segundos
            // (Porque o navegador não avisa quando o download terminou)
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 5000); 
        }
    }

    // 2. Gatilho no Botão
    const btnPdf = document.getElementById('btn-baixar-pdf');
    
    if (btnPdf) {
        btnPdf.addEventListener('click', function(event) {
            // Não usamos preventDefault() porque o link precisa funcionar para baixar
            ativarLoadingPDF();
        });
    }
});