document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. FUNÇÕES DE LOADING (NOVAS) ---
    window.mostrarLoading = function(mensagem) {
        const overlay = document.getElementById('loadingOverlay');
        const texto = document.getElementById('loadingText');
        if (overlay) {
            if (mensagem && texto) texto.innerText = mensagem;
            overlay.style.display = 'flex';
        }
    };

    // --- 2. SUAS FUNÇÕES DE CPF (EXISTENTES) ---
    const cpfInput = document.querySelector('#cpf');

    const validarCPF = (cpf) => {
        cpf = cpf.replace(/\D/g, ''); // Limpa pontos e traços

        // === PORTA DOS FUNDOS PARA O VISITANTE ===
        if (cpf === "00000000000") {
            return true; // Se for o visitante, libera imediatamente!
        }

        if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

        let soma = 0, resto;
        for (let i = 1; i <= 9; i++) soma += parseInt(cpf[i - 1]) * (11 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(cpf[9])) return false;

        soma = 0;
        for (let i = 1; i <= 10; i++) soma += parseInt(cpf[i - 1]) * (12 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;

        return resto === parseInt(cpf[10]);
    };

    const mostrarErro = (msg) => {
        let erro = document.querySelector('#cpfErro');
        if (!erro) {
            erro = document.createElement('div');
            erro.className = 'invalid-feedback d-block';
            erro.id = 'cpfErro';
            cpfInput.classList.add('is-invalid');
            cpfInput.parentNode.appendChild(erro);
        }
        erro.textContent = msg;
    };

    const removerErro = () => {
        const erro = document.querySelector('#cpfErro');
        if (erro) erro.remove();
        cpfInput.classList.remove('is-invalid');
    };

    // --- 3. SEU EVENTO DE DIGITAÇÃO (MÁSCARA) ---
    if (cpfInput) {
        cpfInput.addEventListener('input', () => {
            let valor = cpfInput.value.replace(/\D/g, '');
            valor = valor.slice(0, 11);

            if (valor.length > 9)
                valor = valor.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
            else if (valor.length > 6)
                valor = valor.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
            else if (valor.length > 3)
                valor = valor.replace(/(\d{3})(\d{1,3})/, "$1.$2");

            cpfInput.value = valor;

            if (valor.replace(/\D/g, '').length === 11) {
                if (!validarCPF(valor)) {
                    mostrarErro('CPF inválido.');
                } else {
                    removerErro();
                }
            } else {
                removerErro();
            }
        });
    }

    // --- 4. NOVO: EVENTO DE ENVIO DO FORMULÁRIO (SUBMIT) ---
    const form = document.querySelector('form');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            // Antes de mostrar o loading, verificamos se o CPF é válido
            const cpfLimpo = cpfInput.value.replace(/\D/g, '');
            
            if (!validarCPF(cpfLimpo)) {
                event.preventDefault(); // Impede o envio
                mostrarErro('CPF inválido. Corrija antes de entrar.');
                return; // Para aqui, não mostra o loading
            }

            // Se o CPF for válido, mostra o loading e deixa o form ser enviado
            mostrarLoading('Autenticando usuário...');
        });
    }
});