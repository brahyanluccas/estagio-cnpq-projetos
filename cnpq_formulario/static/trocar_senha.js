document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. FUNÇÃO DE LOADING ---
    function mostrarLoading(mensagem) {
        const overlay = document.getElementById('loadingOverlay');
        const texto = document.getElementById('loadingText');
        if (overlay) {
            if (mensagem && texto) texto.innerText = mensagem;
            overlay.classList.remove('d-none');
            // Força o display flex caso a classe d-none não seja suficiente em alguns contextos
            overlay.style.display = 'flex'; 
        }
    }

    const form = document.getElementById('form-troca-senha');

    if (form) {
        form.addEventListener('submit', function(event) {
            
            // Verifica se a validação falhou
            if (!validarSenha()) {
                event.preventDefault(); // Impede o envio se a senha for ruim
            } else {
                // --- 2. SE PASSOU NA VALIDAÇÃO, MOSTRA O LOADING ---
                mostrarLoading('Salvando nova senha...');
            }
        });
    }
});

function validarSenha() {
    const novaSenha = document.getElementById('nova').value;
    const confirmarSenha = document.getElementById('confirmar').value;
    const erroDiv = document.getElementById('erro-senha');
    
    // 1. Verifica se as senhas coincidem
    if (novaSenha !== confirmarSenha) {
        erroDiv.textContent = "As senhas não coincidem.";
        erroDiv.classList.remove('d-none');
        return false; 
    }

    // 2. Verifica o comprimento mínimo
    if (novaSenha.length < 8) {
        erroDiv.textContent = "A senha deve ter no mínimo 8 caracteres.";
        erroDiv.classList.remove('d-none');
        return false; 
    }

    // 3. Verifica se tem letras e números
    const regex = /^(?=.*[A-Za-z])(?=.*\d).+$/;
    if (!regex.test(novaSenha)) {
        erroDiv.textContent = "A senha deve conter letras e números.";
        erroDiv.classList.remove('d-none');
        return false; 
    }

    erroDiv.classList.add('d-none'); // Esconde o erro se tudo estiver certo
    return true; 
}