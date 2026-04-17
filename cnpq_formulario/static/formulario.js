"use strict";

// --- 1. FUNÇÕES GLOBAIS DE VISUALIZAÇÃO (LOADING) ---
window.mostrarLoading = function(mensagem) {
    const overlay = document.getElementById('loadingOverlay');
    const texto = document.getElementById('loadingText');
    
    if (overlay) {
        if (texto && mensagem) texto.textContent = mensagem;
        overlay.classList.remove('d-none');
        overlay.style.display = 'flex'; // Garante centralização
    }
};

window.esconderLoading = function() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none'; // Força o desaparecimento
    }
};

// --- 2. FUNÇÃO DE ENVIO FINAL (Chamada pelo Modal) ---
window.confirmarEnvioFinal = function() {
    // Fecha o modal visualmente
    const modalElement = document.getElementById('modalConfirmacaoEnvio');
    if (modalElement) {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();
    }

    // Mostra Loading
    mostrarLoading('Enviando dados e gerando comprovante...\nIsso pode levar alguns segundos.');

    const form = document.querySelector('form');
    
    // Cria input hidden para simular o botão de envio final para o Python
    const inputAcao = document.createElement('input');
    inputAcao.type = 'hidden';
    inputAcao.name = 'acao';
    inputAcao.value = 'enviar_final';
    form.appendChild(inputAcao);

    // Envia de verdade (Recarrega a página)
    form.submit();
};

function limparCamposManualmente(elementoPai) {
    if (!elementoPai) return;
    const inputs = elementoPai.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'number' || input.type === 'text') {
            input.value = '';
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        }
    });
}

// Variável global para guardar qual linha será apagada
let linhaParaExcluir = null;

// 1. Função chamada ao clicar na Lixeira da tabela
function removerInstituicao(botao) {
    // Guarda a linha (tr) que contém o botão clicado
    linhaParaExcluir = botao.closest("tr");
    
    // Abre o Modal de Confirmação
    var modalExclusao = new bootstrap.Modal(document.getElementById('modalConfirmarExclusao'));
    modalExclusao.show();
}

// 2. Evento para quando clicar em "Sim, excluir" no Modal
document.addEventListener('DOMContentLoaded', function() {
    const btnConfirmar = document.getElementById('btnConfirmarExclusaoReal');
    
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            if (linhaParaExcluir) {
                // Remove a linha visualmente
                linhaParaExcluir.remove();
                
                // Limpa a variável
                linhaParaExcluir = null;
                
                // Fecha o modal
                var modalElement = document.getElementById('modalConfirmarExclusao');
                var modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();
            }
        });
    }
});

function inicializarChoicesEmSelect(selectElement) {
    if (!selectElement) return;

    // Esta parte do seu código original copia as opções de países de outro campo
    const fonteOpcoes = document.querySelector('select[name="instituicao_pais[]"]');
    if (fonteOpcoes) {
        let opcoesHTML = fonteOpcoes.innerHTML;
        selectElement.innerHTML = opcoesHTML.replace(/selected/g, ''); // Remove todos os 'selected'
    }

    // Cria a instância do Choices.js
    const choicesInstance = new Choices(selectElement, {
        removeItemButton: true,
        placeholder: true,
        placeholderValue: 'Selecione uma ou mais opções...', // Ajustei para ser mais genérico
        searchPlaceholderValue: 'Digite para buscar...',
        
        // --- TRADUÇÕES ADICIONADAS AQUI ---
        noChoicesText: 'Não há mais opções para escolher',
        noResultsText: 'Nenhum resultado encontrado',
        itemSelectText: 'Clique para selecionar',
    });

    // Adiciona o "ouvinte" para a funcionalidade de coautoria
    selectElement.addEventListener('change', function() {
        sincronizarCoautorias();
    });

    // Retorna a instância criada
    return choicesInstance;
}

function salvarNovoParceiro() {
    // 1. Captura os valores dos inputs do Modal
    const nomeInput = document.getElementById('novo_parceiro_nome');
    const nome = nomeInput.value;
    
    // --- TRUQUE: Copia as opções completas do HTML para a tabela ---
    let opcoesPaisesHTML = document.getElementById('novo_parceiro_pais').innerHTML;
    let opcoesUfHTML = document.getElementById('novo_parceiro_uf').innerHTML;
    
    // Pega os valores selecionados
    const natureza = document.getElementById('novo_parceiro_natureza').value;
    const classificacao = document.getElementById('novo_parceiro_classificacao').value;
    const pais = document.getElementById('novo_parceiro_pais').value;
    const uf = document.getElementById('novo_parceiro_uf').value;
    
    // Marca a opção correta como "selected" na string HTML clonada
    if (pais) {
        opcoesPaisesHTML = opcoesPaisesHTML.replace('selected', ''); 
        opcoesPaisesHTML = opcoesPaisesHTML.replace(`value="${pais}"`, `value="${pais}" selected`);
    }
    if (uf) {
        opcoesUfHTML = opcoesUfHTML.replace('selected', '');
        opcoesUfHTML = opcoesUfHTML.replace(`value="${uf}"`, `value="${uf}" selected`);
    }

    // Campos Originais + NOVOS CAMPOS
    const info = document.getElementById('novo_parceiro_info').value;
    const inicio = document.getElementById('novo_parceiro_inicio').value;
    const fim = document.getElementById('novo_parceiro_fim').value;
    
    const titulo = document.getElementById('novo_parceiro_titulo').value; // NOVO
    const resultados = document.getElementById('novo_parceiro_resultados').value; // NOVO
    const obs = document.getElementById('novo_parceiro_obs').value; // NOVO
    
    const cidade = document.getElementById('novo_parceiro_cidade').value;

    // Validação básica
    if (!nome) {
        alert("Por favor, preencha o Nome da Instituição.");
        nomeInput.focus();
        return;
    }

    // Lógica de exibição (Brasil vs Exterior)
    const displayBrasil = (pais === 'Brasil') ? 'block' : 'none';
    const displayEstrangeiro = (pais !== 'Brasil') ? 'block' : 'none';

    // 2. Cria a string HTML da nova linha da tabela
    const novaLinha = `
        <tr class="institution-row">
            <td>
                <input type="text" name="instituicao_nome[]" class="form-control form-control-sm fw-bold border-0 bg-transparent" value="${nome}" readonly>
                
                <input type="hidden" name="instituicao_info_suplementar[]" value="${info}">
                <input type="hidden" name="instituicao_inicio[]" value="${inicio}">
                <input type="hidden" name="instituicao_fim[]" value="${fim}">
                
                <input type="hidden" name="instituicao_titulo_projeto[]" value="${titulo}">
                <input type="hidden" name="instituicao_resultados[]" value="${resultados}">
                <input type="hidden" name="instituicao_obs[]" value="${obs}">
            </td>

            <td>
                <select name="instituicao_natureza[]" class="form-select form-select-sm">
                    <option value="Público" ${natureza === 'Público' ? 'selected' : ''}>Público</option>
                    <option value="Privado sem fins lucrativos" ${natureza === 'Privado sem fins lucrativos' ? 'selected' : ''}>Privado sem fins lucrativos</option>
                    <option value="Privado com fins lucrativos" ${natureza === 'Privado com fins lucrativos' ? 'selected' : ''}>Privado com fins lucrativos</option>
                </select>
            </td>

            <td>
                <select name="instituicao_classificacao[]" class="form-select form-select-sm" onchange="toggleOutro(this)">
                    <option value="${classificacao}" selected>${classificacao}</option>
                    <option value="Instituição de Ensino Superior (IES)">Instituição de Ensino Superior (IES)</option>
                    <option value="Instituição de Pesquisa">Instituição de Pesquisa</option>
                    <option value="Empresa pública">Empresa pública</option>
                    <option value="Empresa privada">Empresa privada</option>
                    <option value="Órgão de governo">Órgão de governo</option>
                    <option value="Organização da sociedade civil">Organização da sociedade civil</option>
                    <option value="Organização internacional">Organização internacional</option>
                    <option value="Outro">Outro</option>
                </select>
                <input type="text" name="instituicao_classificacao_outro[]" class="form-control form-control-sm mt-1" placeholder="Detalhar Outro" style="display: none;">
            </td>

            <td>
                <select name="instituicao_pais[]" class="form-select form-select-sm" onchange="toggleInputsLocalizacao(this)">
                    ${opcoesPaisesHTML} 
                </select>
            </td>

            <td>
                <select name="instituicao_uf[]" class="form-select form-select-sm" style="display: ${displayBrasil};">
                    ${opcoesUfHTML}
                </select>
            </td>

            <td>
                 <div class="d-flex">
                    <input type="text" name="instituicao_cidade[]" 
                           class="form-control form-control-sm" 
                           style="display: ${displayBrasil};"
                           value="${cidade}">
                    
                    <input type="text" name="instituicao_cidade_estrangeira[]" 
                           class="form-control form-control-sm city-foreign-input" 
                           style="display: ${displayEstrangeiro};" 
                           value="${cidade}">
                 </div>
            </td>

            <td class="text-center">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removerInstituicao(this)">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        </tr>
    `;

    // 3. Insere a nova linha
    const tabelaBody = document.querySelector('#tabela-organizacoes-parceiras tbody');
    if(tabelaBody) {
        tabelaBody.insertAdjacentHTML('beforeend', novaLinha);
    } else {
        console.error("Erro: Tabela não encontrada!");
    }

    // 4. Limpa e fecha
    document.getElementById('form-novo-parceiro').reset();
    const modalElement = document.getElementById('modalAdicionarParceiro');
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if(modalInstance) modalInstance.hide();
}

function atualizarResumoBibliografico() {
    const tabelaResumoBiblioEl = document.getElementById('tabela-resumo-bibliografico');
    if (!tabelaResumoBiblioEl) {
        console.error("ERRO: Tabela de resumo 'tabela-resumo-bibliografico' não foi encontrada.");
        return;
    }

    // Cria um objeto para zerar os contadores
    const contadores = {};
    tabelaResumoBiblioEl.querySelectorAll('tbody tr').forEach(row => {
        const tipo = row.getAttribute('data-producao-tipo');
        if (tipo) {
            contadores[tipo] = 0;
        }
    });

    // Encontra os itens validados e incrementa os contadores
    const itensValidados = document.querySelectorAll('#lista-producoes-bibliograficas .toggle-bibliografico:checked');
    itensValidados.forEach(toggle => {
        const item = toggle.closest('.list-group-item');
        const categoriaFinal = item.getAttribute('data-tipo-producao');
        if (categoriaFinal && contadores.hasOwnProperty(categoriaFinal)) {
            contadores[categoriaFinal]++;
        }
    });

    // Atualiza os valores na tabela de resumo
    for (const categoria in contadores) {
        const linha = tabelaResumoBiblioEl.querySelector(`tr[data-producao-tipo="${categoria}"]`);
        if (linha) {
            linha.querySelector('input[type="number"]').value = contadores[categoria];
        }
    }
}

function popularPaisesTecnologia(selectElement) {
    if (!selectElement || selectElement.options.length > 1) return;

    // Procura o select "mestre" de países que você já usa em outra parte do formulário
    const fonteOpcoes = document.querySelector('select[name="instituicao_pais[]"]');

    if (fonteOpcoes) {
        selectElement.innerHTML = fonteOpcoes.innerHTML;
        selectElement.value = ""; // Garante que nenhuma opção venha pré-selecionada
    } else {
        console.error("ERRO: O select de países de origem ('instituicao_pais[]') não foi encontrado para clonagem.");
        selectElement.innerHTML = '<option value="">Erro ao carregar países</option>';
    }
}

function sincronizarProducaoTecnologicaInternacional() {
    const listaOrigem = document.getElementById('lista-producoes-tecnologicas');
    const listaDestino = document.getElementById('lista-producoes-internacionais');

    if (!listaOrigem || !listaDestino) return;

    listaDestino.innerHTML = ''; // Limpa a lista de destino

    const radiosExteriorMarcados = listaOrigem.querySelectorAll('input.toggle-tecnologico[value="exterior" i]:checked');

    radiosExteriorMarcados.forEach(radio => {
        const itemOriginal = radio.closest('.list-group-item');
        if (itemOriginal) {
            const titulo = itemOriginal.querySelector('p strong').nextSibling.textContent.trim();
            const pesquisadorCompleto = itemOriginal.querySelector('small.text-muted').textContent;
            const pesquisador = pesquisadorCompleto.split('|')[0].replace('Pesquisador:', '').trim();
            const ano = pesquisadorCompleto.match(/Ano: (\d{4})/)[1];
            const selectPais = itemOriginal.querySelector('.select-pais-tecnologia');
            const paisSelecionado = (selectPais && selectPais.value) ? selectPais.value : 'Não especificado';

            const novoCardHtml = `
            <div class="list-group-item">
                <h6 class="mb-1">${titulo}</h6>
                <small class="text-muted">
                    <strong>Pesquisador:</strong> ${pesquisador} | 
                    <strong>Ano:</strong> ${ano} | 
                    <strong>País:</strong> <span class="badge bg-info text-dark">${paisSelecionado}</span>
                </small>
            </div>`;
            listaDestino.insertAdjacentHTML('beforeend', novoCardHtml);
        }
    });

    if (listaDestino.childElementCount === 0) {
        listaDestino.innerHTML = '<p class="text-muted small p-3 text-center empty-list-message">Nenhuma produção tecnológica internacional foi selecionada na seção 4.3.</p>';
    }
}

// 1. Correção para sincronizarCoautorias (Seção 4.2 -> Lista Interna)
function sincronizarCoautorias() {
    const listaOrigem = document.getElementById('lista-producoes-bibliograficas');
    const listaDestino = document.getElementById('lista-coautorias-internacionais');
    const campoJsonEscondido = document.getElementById('coautoria_json_hidden');
    
    if (!listaOrigem || !listaDestino) return; // Se não achar, sai sem erro

    listaDestino.innerHTML = '';
    const dadosParaSalvar = [];

    const cardsComCoautoria = listaOrigem.querySelectorAll('.coautoria-check:checked');

    cardsComCoautoria.forEach(toggle => {
        const cardOriginal = toggle.closest('.list-group-item');
        if (cardOriginal) {

            // Tenta achar o título de várias formas possíveis para não quebrar
            let titulo = "Título não identificado";
            const pStrong = cardOriginal.querySelector('p strong');
            
            if (pStrong && pStrong.nextSibling) {
                titulo = pStrong.nextSibling.textContent.trim();
            } else if (cardOriginal.querySelector('p')) {
                // Fallback: pega todo o texto do parágrafo
                titulo = cardOriginal.querySelector('p').textContent.replace('Título:', '').trim();
            }

            const tipo = cardOriginal.querySelector('h6') ? cardOriginal.querySelector('h6').textContent.trim() : "Tipo não identificado";
            
            // Dados de Autor/Ano
            let autores = "Autores não identificados";
            let ano = "";
            const smallInfo = cardOriginal.querySelector('small.text-muted');
            if (smallInfo) {
                const infoTexto = smallInfo.textContent;
                if (infoTexto.includes('|')) {
                    autores = infoTexto.split('|')[0].replace('Autor(es) na Equipe:', '').trim();
                    const parteAno = infoTexto.split('|')[1];
                    if (parteAno) ano = parteAno.replace('Ano:', '').trim();
                } else {
                    autores = infoTexto;
                }
            }

            // Pega Países
            let paisesArray = [];
            const selectPaises = cardOriginal.querySelector('.select-paises-coautoria');
            if (selectPaises) {
                // Suporte híbrido (Nativo ou Choices.js)
                if (selectPaises.choicesInstance) {
                    paisesArray = selectPaises.choicesInstance.getValue(true);
                } else {
                    paisesArray = Array.from(selectPaises.selectedOptions).map(opt => opt.text);
                }
            }
            const paisesHtml = paisesArray.length > 0 
                ? paisesArray.map(p => `<span class="badge bg-secondary me-1">${p}</span>`).join(' ') 
                : '<small class="text-muted fst-italic">Nenhum país selecionado</small>';

            // Salva no JSON
            dadosParaSalvar.push({ tipo, titulo, autores, ano, paises: paisesArray.join(', ') });

            // Cria o HTML
            listaDestino.insertAdjacentHTML('beforeend', `
            <div class="list-group-item">
                <div class="w-100">
                    <h6 class="mb-1">${tipo}</h6>
                    <p class="small text-muted mb-1"><strong>Título:</strong> ${titulo}</p>
                    <small class="text-muted d-block"><strong>Autor(es):</strong> ${autores} | <strong>Ano:</strong> ${ano}</small>
                    <div class="mt-2">
                        <small class="text-muted"><strong>Países:</strong> ${paisesHtml}</small>
                    </div>
                </div>
            </div>`);
        }
    });

    if (campoJsonEscondido) campoJsonEscondido.value = JSON.stringify(dadosParaSalvar);
}

function criarCardPublicacaoManual(dados) {
    const uniqueId = `manual_${Date.now()}`;
    const htmlCard = `
    <div class="list-group-item" data-tipo-producao="${dados.tipo}">
        <button type="button" class="btn btn-sm btn-outline-danger btn-remover-publicacao btn-canto-superior" title="Remover Publicação">
            <i class="fas fa-trash-alt"></i>
        </button>
        <div class="w-100">
            <h6 class="mb-1">${dados.tipo}</h6>
            <p class="small text-muted" style="margin-bottom: 0;"><strong>Título:</strong> ${dados.titulo}</p>
        </div>
        <div class="d-flex w-100 justify-content-between align-items-start">
            <small class="text-muted pt-1"> 
                <strong>Autor(es) na Equipe:</strong> ${dados.autores} | <strong>Ano:</strong> ${dados.ano} 
            </small>
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <div class="form-check form-switch">
                        <input class="form-check-input toggle-bibliografico" type="checkbox" id="biblio_validacao_${uniqueId}">
                        <label class="form-check-label" for="biblio_validacao_${uniqueId}">Validar</label>
                    </div>
                    <div class="form-check form-switch mt-2">
                        <input class="form-check-input coautoria-check" type="checkbox" name="coautoria_internacional[]" value="${uniqueId}" id="coautoria_check_${uniqueId}">
                        <label class="form-check-label" for="coautoria_check_${uniqueId}">Coautoria Intl.?</label>
                    </div>
                    <div class="mt-1 coautoria-paises-container" style="display: none;">
                        <select name="paises_coautores[]" class="form-control-sm select-paises-coautoria" multiple></select>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    return htmlCard;
}

function criarCardTecnologicoManual(dados) {
    const uniqueId = `manual_tecno_${Date.now()}`;
    const htmlCard = `
    <div class="list-group-item" data-tipo-producao="${dados.tipo}">
        <button type="button" class="btn btn-sm btn-outline-danger btn-remover-publicacao" title="Remover Produção">
            <i class="fas fa-trash-alt"></i>
        </button>
        <div class="w-100">
            <h6 class="mb-1">${dados.tipo.replace(/^\d+\.\d+\s/, '')}</h6>
            <p class="small text-muted" style="margin-bottom: 0;"><strong>Título:</strong> ${dados.titulo}</p>
        </div>
        <div class="d-flex w-100 justify-content-between align-items-start">
            <small class="text-muted pt-1"> 
                <strong>Autor(es) na Equipe:</strong> ${dados.autores} | <strong>Ano:</strong> ${dados.ano} 
            </small>
            <div class="d-flex align-items-center">
                <div class="form-check form-check-inline">
                    <input class="form-check-input toggle-tecnologico" type="checkbox" value="nacional" id="tec_nacional_${uniqueId}">
                    <label class="form-check-label" for="tec_nacional_${uniqueId}">Nacional</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input toggle-tecnologico" type="checkbox" value="exterior" id="tec_exterior_${uniqueId}">
                    <label class="form-check-label" for="tec_exterior_${uniqueId}">Exterior</label>
                </div>
            </div>
        </div>
    </div>`;
    return htmlCard;
}

function atualizarResumoDivulgacao() {
    const tabelaResumo = document.getElementById('tabela-resumo-divulgacao');
    if (!tabelaResumo) {
        console.error("ERRO: Tabela de resumo 'tabela-resumo-divulgacao' não foi encontrada.");
        return;
    }

    const contadores = {};
    tabelaResumo.querySelectorAll('tbody tr').forEach(row => {
        const tipo = row.getAttribute('data-tipo-instrumento');
        if (tipo) {
            contadores[tipo] = 0;
        }
    });

    const itensValidados = document.querySelectorAll('.toggle-divulgacao:checked');

    itensValidados.forEach((toggle, index) => {
        const item = toggle.closest('.list-group-item');
        const tipoProducao = item.getAttribute('data-tipo-instrumento');

        if (contadores.hasOwnProperty(tipoProducao)) {
            contadores[tipoProducao]++;
        }
    });

    for (const tipo in contadores) {
        const row = tabelaResumo.querySelector(`tr[data-tipo-instrumento="${tipo}"]`);
        if (row) {
            row.querySelector('input').value = contadores[tipo];
        }
    }
}

function addArticulacao() {
    const tabelaId = 'tabela_articulacao_inct';
    const templateId = 'template-articulacao';
    
    const template = document.getElementById(templateId);
    const tbody = document.querySelector(`#${tabelaId} tbody`);
    if (!template || !tbody) { return; }

    const clone = template.content.cloneNode(true);
    const novaLinha = clone.querySelector('tr');
    
    // Pega o número da linha atual para criar um índice único (0, 1, 2, ...)
    const rowIndex = tbody.querySelectorAll('tr').length;

    // Renomeia os checkboxes de 'Natureza' para serem únicos para esta linha
    novaLinha.querySelectorAll('input[name="articulacao_natureza[]"]').forEach(chk => {
        chk.name = `articulacao_natureza_${rowIndex}[]`;
    });
    
    // Renomeia os checkboxes de 'Resultados' para serem únicos para esta linha
    novaLinha.querySelectorAll('input[name="articulacao_resultados[]"]').forEach(chk => {
        chk.name = `articulacao_resultados_${rowIndex}[]`;
    });

    tbody.appendChild(clone);
}

// --- FUNÇÕES DA SESSÃO 6 (RESULTADOS) ---
function adicionarLinhaResultado() {
    const tbody = document.querySelector('#tabela-resultados-dinamica tbody');
    const template = document.getElementById('template-linha-resultado');
    const msgVazia = document.getElementById('msg-sem-resultados');

    if (!tbody || !template) return;

    if (msgVazia) msgVazia.classList.add('d-none');

    // Conta quantas linhas já existem para criar o índice
    const totalLinhas = tbody.querySelectorAll('tr').length;

    const clone = template.content.cloneNode(true);
    const row = clone.querySelector('tr');
    row.classList.add('nova-linha');

    // Substitui o INDEX pelo número da linha
    row.innerHTML = row.innerHTML.replace(/INDEX/g, totalLinhas);

    tbody.appendChild(clone);

    // Ativa os tooltips dos números
    setTimeout(() => {
        const novosPopovers = tbody.querySelectorAll(`tr:last-child [data-bs-toggle="popover"]`);
        novosPopovers.forEach(el => new bootstrap.Popover(el));
    }, 100);
}

function removerLinhaResultado(btn) {
    if (confirm("Tem certeza que deseja remover este resultado?")) {
        const row = btn.closest('tr');
        row.remove();

        const tbody = document.querySelector('#tabela-resultados-dinamica tbody');
        const msgVazia = document.getElementById('msg-sem-resultados');
        
        if (tbody.querySelectorAll('tr').length === 0 && msgVazia) {
            msgVazia.classList.remove('d-none');
        }
    }
}

function atualizarVisualizacaoObjetivos(checkbox) {
    const celula = checkbox.closest('.celula-objetivos');
    const divSelecao = celula.querySelector('.modo-selecao-objetivos');
    const divTexto = celula.querySelector('.modo-texto-objetivos');
    const containerLista = divTexto.querySelector('.lista-textos-selecionados');

    if (checkbox.checked) {
        // Cria o HTML dos textos selecionados
        let htmlTextos = '';
        celula.querySelectorAll('.input-objetivo-check:checked').forEach(chk => {
            const texto = chk.getAttribute('data-texto-objetivo');
            htmlTextos += `
                <div class="alert alert-light border p-2 mb-1 small text-dark shadow-sm">
                    ${texto}
                </div>`;
        });

        containerLista.innerHTML = htmlTextos;

        // Esconde números, Mostra texto
        divSelecao.classList.remove('d-block');
        divSelecao.classList.add('d-none');
        
        divTexto.classList.remove('d-none');
        divTexto.classList.add('d-block');
    }
}

function resetarSelecaoObjetivos(botaoEditar) {
    const celula = botaoEditar.closest('.celula-objetivos');
    const divSelecao = celula.querySelector('.modo-selecao-objetivos');
    const divTexto = celula.querySelector('.modo-texto-objetivos');

    // Esconde texto, Mostra números (para editar)
    divTexto.classList.remove('d-block');
    divTexto.classList.add('d-none');

    divSelecao.classList.remove('d-none');
    divSelecao.classList.add('d-block');
}

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Escuta o clique APENAS nos botões de "Recolher Lista"
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-recolher-lista')) {
            let btn = e.target.closest('.btn-recolher-lista');
            let targetSelector = btn.getAttribute('data-bs-target');
            let targetDiv = document.querySelector(targetSelector);
            
            if (targetDiv) {
                // Marca a div avisando: "Quando você terminar de fechar, faça o scroll"
                targetDiv.setAttribute('data-rolar-apos-fechar', 'true');
            }
        }
    });

    // 2. Escuta o evento oficial do Bootstrap de "fim da animação de fechar"
    document.addEventListener('hidden.bs.collapse', function (event) {
        let colapso = event.target;
        
        // Verifica se essa div tem a nossa marcação
        if (colapso.getAttribute('data-rolar-apos-fechar') === 'true') {
            colapso.removeAttribute('data-rolar-apos-fechar'); // Limpa a marcação
            
            // Acha automaticamente o cabeçalho que controla essa div (o título da seção)
            let cabecalho = document.querySelector(`[data-bs-target="#${colapso.id}"]`);
            
            if (cabecalho) {
                // Rola suavemente até o cabeçalho
                const yOffset = -20; // Deixa 20px de respiro no topo da tela
                const y = cabecalho.getBoundingClientRect().top + window.scrollY + yOffset;
                window.scrollTo({top: y, behavior: 'smooth'});
            }
        }
    });

});

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona os campos pelo nome (name)
    const campoFuncao = document.querySelector('[name="novo_membro_funcao"]');
    const campoTitulacao = document.querySelector('[name="novo_membro_titulacao"]');

    if (campoFuncao && campoTitulacao) {
        
        campoFuncao.addEventListener('change', function() {
            const funcaoSelecionada = this.value;

            // Define as regras de preenchimento automático
            // Esquerda: O que foi selecionado na Função
            // Direita: O que deve aparecer na Titulação
            const regras = {
                "Aluno de Graduação": "Ensino Médio",
                "Mestrando": "Graduação",
                "Doutorando": "Mestrado",
                "Pós-Doutorando": "Doutorado"
            };

            // Se a função escolhida estiver na nossa lista de regras...
            if (regras[funcaoSelecionada]) {
                // ...aplica a titulação correspondente
                campoTitulacao.value = regras[funcaoSelecionada];
                
                // (Opcional) Faz um efeito visual rápido para mostrar que mudou
                campoTitulacao.style.backgroundColor = "#e8f0fe";
                setTimeout(() => campoTitulacao.style.backgroundColor = "", 500);
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    
    const tabelaMembros = document.getElementById('tabela-composicao-rede');

    if (tabelaMembros) {
        tabelaMembros.addEventListener('change', function(event) {
            // Verifica se o elemento alterado é um Select de Categoria (Função)
            // (Baseado no name="membro_categoria[]" ou na classe que vimos no HTML)
            if (event.target.name === 'membro_categoria[]') {
                
                const selectFuncao = event.target;
                const valorFuncao = selectFuncao.value;
                
                // Encontra a linha (tr) onde essa mudança aconteceu
                const linhaAtual = selectFuncao.closest('tr');
                
                // Dentro dessa linha, busca o select de Titulação
                const selectTitulacao = linhaAtual.querySelector('select[name="membro_titulacao_extraida[]"]');

                if (selectTitulacao) {
                    // Mesmas regras do Modal
                    const regras = {
                        "Aluno de Graduação": "Ensino Médio",
                        "Mestrando": "Graduação",
                        "Doutorando": "Mestrado",
                        "Pós-Doutorando": "Doutorado"
                    };

                    if (regras[valorFuncao]) {
                        selectTitulacao.value = regras[valorFuncao];
                        
                        // Efeito visual sutil na linha
                        selectTitulacao.style.transition = "background-color 0.3s";
                        selectTitulacao.style.backgroundColor = "#e8f0fe"; // Azulzinho claro
                        setTimeout(() => selectTitulacao.style.backgroundColor = "", 1000);
                    }
                }
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    
    const btnSalvar = document.getElementById('btnSalvarNovoMembro');

    if (btnSalvar) {
        btnSalvar.addEventListener('click', function() {
            // 1. Pegar os valores (Igual ao anterior)
            const form = document.getElementById('form-adicionar-membro');
            const nome = form.querySelector('[name="novo_membro_nome"]').value;
            const funcao = form.querySelector('[name="novo_membro_funcao"]').value;
            const titulacao = form.querySelector('[name="novo_membro_titulacao"]').value;
            const area = form.querySelector('[name="novo_membro_area"]').value;
            const instituicao = form.querySelector('[name="novo_membro_instituicao"]').value;
            const pais = form.querySelector('[name="novo_membro_pais"]').value;
            const uf = form.querySelector('[name="novo_membro_uf"]').value;
            
            // Lógica de Cidade
            let cidade = "";
            const selectCidade = form.querySelector('[name="novo_membro_cidade"]');
            const inputCidadeEstrangeira = form.querySelector('[name="novo_membro_cidade_estrangeira"]');
            
            if (pais === 'Brasil') {
                cidade = selectCidade.value;
            } else {
                cidade = inputCidadeEstrangeira.value;
            }

            // Novos Campos
            const dedicacao = form.querySelector('[name="novo_membro_dedicacao"]').value;
            const respPT = form.querySelector('[name="novo_membro_resp_pt"]').value;
            const respEN = form.querySelector('[name="novo_membro_resp_en"]').value;

            // Validação
            if (!nome || !funcao || !titulacao || !dedicacao) {
                alert("Por favor, preencha os campos obrigatórios (*).");
                return;
            }

            // 2. Criar a linha
            const tabelaBody = document.querySelector('#tabela-composicao-rede tbody');
            const novaLinha = document.createElement('tr');
            // Adicionei um ID único temporário caso precise, mas o remove() resolve
            novaLinha.classList.add('membro-linha', 'table-success'); 

            novaLinha.innerHTML = `
                <td>
                    ${nome}
                    <input type="hidden" name="membro_nome[]" value="${nome}">
                    
                    <input type="hidden" name="membro_dedicacao[]" value="${dedicacao}">
                    <textarea name="membro_resp_pt[]" style="display:none;">${respPT}</textarea>
                    <textarea name="membro_resp_en[]" style="display:none;">${respEN}</textarea>
                </td>
                
                <td><input type="text" class="form-control form-control-sm" name="membro_categoria[]" value="${funcao}" readonly></td>
                <td><input type="text" class="form-control form-control-sm" name="membro_titulacao_extraida[]" value="${titulacao}" readonly></td>
                <td><input type="text" name="membro_area_atuacao[]" class="form-control form-control-sm" value="${area}" readonly></td>
                <td><input type="text" name="membro_instituicao[]" class="form-control form-control-sm" value="${instituicao}" readonly></td>
                <td><input type="text" class="form-control form-control-sm" name="membro_pais[]" value="${pais}" readonly></td>
                <td><input type="text" class="form-control form-control-sm" name="membro_uf[]" value="${uf}" readonly></td>
                
                <td>
                    <input type="text" class="form-control form-control-sm" name="membro_cidade[]" value="${cidade}" readonly>
                    <input type="hidden" name="membro_cidade_estrangeira[]" value="${pais !== 'Brasil' ? cidade : ''}">
                    <input type="hidden" name="membro_pais_check[]" value="${pais}">
                </td>

                <td class="text-center">
                    <input type="checkbox" name="membro_atual[]" class="form-check-input" disabled>
                </td>
                
                <td class="text-center">
                    <input type="checkbox" name="membro_novo[]" class="form-check-input" checked onclick="return false;" value="1">
                </td>
                
                <td class="text-center">
                    <input type="checkbox" name="membro_excluido[]" class="form-check-input" disabled>
                </td>

                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger btn-remover-linha" title="Remover membro adicionado">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;

            // 3. Adicionar Lógica de Deletar NESTA linha específica
            const btnRemover = novaLinha.querySelector('.btn-remover-linha');
            btnRemover.addEventListener('click', function() {
                if(confirm("Tem certeza que deseja remover este membro adicionado?")) {
                    novaLinha.remove();
                }
            });

            // 4. Adicionar na tabela
            tabelaBody.appendChild(novaLinha);

            // 5. Fechar Modal e Limpar
            var modalEl = document.getElementById('modalAdicionarMembro');
            var modalInstance = bootstrap.Modal.getInstance(modalEl);
            modalInstance.hide();
            form.reset();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    
    const selectUFModal = document.querySelector('[name="novo_membro_uf"]');
    const selectCidadeModal = document.querySelector('[name="novo_membro_cidade"]');

    if (selectUFModal && selectCidadeModal) {
        
        selectUFModal.addEventListener('change', function() {
            const ufSelecionada = this.value;
            
            // 1. Limpar as cidades atuais
            selectCidadeModal.innerHTML = '<option value="">Carregando...</option>';
            
            // 2. Pegar o JSON de cidades que já existe na sua página
            const scriptCidades = document.getElementById('dados-cidades-json');
            
            if (scriptCidades && ufSelecionada) {
                try {
                    const todasCidades = JSON.parse(scriptCidades.textContent);
                    const cidadesDoEstado = todasCidades[ufSelecionada];

                    // 3. Limpar de novo e colocar a opção padrão
                    selectCidadeModal.innerHTML = '<option value="">Selecione a Cidade...</option>';

                    // 4. Preencher com as cidades do estado selecionado
                    if (cidadesDoEstado) {
                        cidadesDoEstado.forEach(cidade => {
                            const option = document.createElement('option');
                            option.value = cidade;
                            option.textContent = cidade;
                            selectCidadeModal.appendChild(option);
                        });
                    } else {
                        selectCidadeModal.innerHTML = '<option value="">Nenhuma cidade encontrada</option>';
                    }

                } catch (e) {
                    console.error("Erro ao ler JSON de cidades:", e);
                    selectCidadeModal.innerHTML = '<option value="">Erro ao carregar</option>';
                }
            } else {
                // Se não selecionou UF, reseta
                selectCidadeModal.innerHTML = '<option value="">Selecione a UF primeiro...</option>';
            }
        });
    }
});

// === LÓGICA DE PAÍS ESTRANGEIRO NO MODAL ===
document.addEventListener('DOMContentLoaded', function() {
    
    const selectPais = document.getElementById('select-pais-novo-membro');
    const wrapperUF = document.getElementById('wrapper-uf-novo-membro');
    const avisoUF = document.getElementById('aviso-uf-estrangeira');
    const selectUF = document.querySelector('[name="novo_membro_uf"]');
    
    const selectCidade = document.getElementById('select-cidade-novo-membro');
    const inputCidadeEstrangeira = document.getElementById('input-cidade-estrangeira-novo-membro');

    if (selectPais) {
        selectPais.addEventListener('change', function() {
            const pais = this.value;

            if (pais === 'Brasil') {
                // MODO BRASIL
                // 1. Volta a mostrar a UF
                wrapperUF.style.display = 'block';
                avisoUF.style.display = 'none';
                
                // 2. Volta a mostrar o Select de Cidade e esconde o Input de Texto
                selectCidade.style.display = 'block';
                inputCidadeEstrangeira.style.display = 'none';
                
                // 3. Limpa o campo estrangeiro para não salvar lixo
                inputCidadeEstrangeira.value = '';

            } else {
                // MODO ESTRANGEIRO
                // 1. Esconde a UF (pois não faz sentido)
                wrapperUF.style.display = 'none';
                avisoUF.style.display = 'block'; // Mostra texto "Não aplicável"
                
                // 2. Reseta o valor da UF para vazio
                selectUF.value = "";

                // 3. Esconde o Select de Cidade e Mostra o Input de Texto
                selectCidade.style.display = 'none';
                inputCidadeEstrangeira.style.display = 'block';
                
                // 4. Reseta o select de cidade
                selectCidade.innerHTML = '<option value="">Não aplicável</option>';
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {

    // ATIVA OS POPOVERS DA TABELA DE RESULTADOS
    const popoversResultados = document.querySelectorAll('#tabela-resultados-dinamica [data-bs-toggle="popover"]');
    popoversResultados.forEach(el => new bootstrap.Popover(el));

    // --- LÓGICA DE CONTINUIDADE (Loading -> Modal) ---
    setTimeout(function() {
        if (window.esconderLoading) {
            window.esconderLoading();
        }
    }, 500)

    const missoesDataElement = document.getElementById('missoes-data-json');
    const missoesData = missoesDataElement ? JSON.parse(missoesDataElement.textContent) : [];
    
    let atividadeDivulgacaoIndex = 0;
    
    const form = document.querySelector("form");
    
    if (!form) {
        console.error("ERRO CRÍTICO: O elemento <form> não foi encontrado no documento.");
        return;
    }
    const PROCESSO_ID = form.dataset.processoId; 
    const CHAVE_RASCUNHO = `rascunho_projeto_${PROCESSO_ID}`;

    const mapeamentoDeTipos = {
        "Software": "1.18 Softwares",
        "Programa": "1.14 Programas (software, solução tecnológica)",
        "Artigos aceitos para publicação": "1.2 Artigos aceitos para publicação",
        "Artigos completos publicados em periódicos": "1.3 Artigos completos publicados em periódicos",
        "Capítulos de livros publicados": "1.4 Capítulos de livros",
        "Livros publicados/organizados ou edições": "1.7 Livros publicados/organizados",
        "Trabalho resumidos publicados em anais de eventos": "1.20 Trabalhos completos publicados em anais",
        "Trabalhos completos publicados em anais de eventos": "1.20 Trabalhos completos publicados em anais",
        "Trabalhos publicados em anais de eventos": "1.20 Trabalhos completos publicados em anais",
        "Outra produção bibliográfica": "1.9 Outra produção bibliográfica (científica especializada)",
        "Outra produção técnica": "1.10 Outra produção técnica (científica especializada)",
        "Trabalhos técnicos": "1.21 Trabalhos técnicos",
        "Patente": "1.11 Patente e registros"
    };

    const categoriasBibliograficas = [
        "1.2 Artigos aceitos para publicação",
        "1.3 Artigos completos publicados em periódicos",
        "1.4 Capítulos de livros",
        "1.7 Livros publicados/organizados",
        "1.9 Outra produção bibliográfica (científica especializada)",
        "1.10 Outra produção técnica (científica especializada)",
        "1.20 Trabalhos completos publicados em anais",
        "1.21 Trabalhos técnicos"
    ];
    const categoriasTecnologicas = [
        "1.11 Patente e registros",
        "1.12 Processos ou técnicas desenvolvidas",
        "1.13 Produtos tecnológicos",
        "1.14 Programas (software, solução tecnológica)",
        "1.18 Softwares"
    ];

    const todosRadios = document.querySelectorAll('input[type="radio"]');
    
    todosRadios.forEach(radio => {
        // 1. Antes do clique, salva o estado atual
        radio.addEventListener('mousedown', function() {
            this.dataset.wasChecked = this.checked ? "true" : "false";
        });

        // 2. No clique, se já estava marcado, desmarca
        radio.addEventListener('click', function(e) {
            if (this.dataset.wasChecked === "true") {
                this.checked = false;
                this.dataset.wasChecked = "false";
                
                // Dispara evento de mudança para fechar as divs condicionais (collapse)
                const event = new Event('change', { bubbles: true });
                this.dispatchEvent(event);
            } else {
                this.dataset.wasChecked = "true";
                // Limpa o status dos irmãos do mesmo grupo
                const groupName = this.name;
                document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                    if (r !== this) r.dataset.wasChecked = "false";
                });
            }
        });
    });

    function popularTiposDeProducaoModal() {
        const select = document.getElementById('tipoProducaoManual');
        if (!select) return;
        select.innerHTML = '<option value="">Selecione um tipo...</option>';
        Object.keys(mapeamentoDeTipos).forEach(tipoBruto => {
            const categoriaMapeada = mapeamentoDeTipos[tipoBruto];
            if (categoriasBibliograficas.includes(categoriaMapeada)) {
                const option = document.createElement('option');
                option.value = tipoBruto;
                option.textContent = tipoBruto;
                select.appendChild(option);
            }
        });
    }

    function popularTiposTecnologicosModal() {
        const select = document.getElementById('tipoProducaoTecnologicaManual');
        if (!select) return;
        select.innerHTML = '<option value="">Selecione um tipo...</option>';
        categoriasTecnologicas.forEach(categoriaOriginal => {
            const textoLimpo = categoriaOriginal.replace(/^\d+\.\d+\s/, '');
            const option = document.createElement('option');
            option.value = categoriaOriginal;
            option.textContent = textoLimpo; 
            select.appendChild(option);
        });
    }

    function adicionarProducaoTecnologicaManual() {
        const btnSalvar = document.getElementById('btnSalvarProducaoTecnologica');
        if (!btnSalvar) return;
        btnSalvar.addEventListener('click', function () {
            const modalEl = document.getElementById('modalNovaProducaoTecnologica');
            const formEl = document.getElementById('formNovaProducaoTecnologica');
            if (!formEl) {
                alert("ERRO: O container do formulário (#formNovaProducaoTecnologica) não foi encontrado.");
                return;
            }
            const dados = {
                tipo: document.getElementById('tipoProducaoTecnologicaManual').value,
                titulo: document.getElementById('tituloProducaoTecnologicaManual').value,
                autores: document.getElementById('autoresProducaoTecnologicaManual').value,
                ano: document.getElementById('anoProducaoTecnologicaManual').value
            };
            if (!dados.tipo || !dados.titulo || !dados.ano) {
                alert('Por favor, preencha Tipo, Título e Ano.');
                return;
            }
            const novoCardHtml = criarCardTecnologicoManual(dados);
            const botaoAdicionar = document.getElementById('btn-abrir-modal-tecnologica');
            if (botaoAdicionar) {
                botaoAdicionar.insertAdjacentHTML('beforebegin', novoCardHtml);
            }
            limparCamposManualmente(formEl);
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
    
    function addLinhaFromTemplate(templateId, tabelaId) {
        const template = document.getElementById(templateId);
        const tbody = document.querySelector(`#${tabelaId} tbody`);
        if (!template || !tbody) { return; }
        const clone = template.content.cloneNode(true);
        tbody.appendChild(clone);
    }

    function removerLinha(button) {
        const tr = button.closest('tr');
        if (tr) {
            const proximaLinha = tr.nextElementSibling;
            if (proximaLinha && proximaLinha.querySelector('td[colspan]')) {
                proximaLinha.remove();
            }
            tr.remove();
        }
    }

    function removerBloco(button) {
        button.closest('.bloco-atividade').remove();
    }

    function toggleOutro(selectElement) {
        const outroInput = selectElement.parentElement.querySelector('input[type="text"]');
        if (outroInput) {
            outroInput.style.display = (selectElement.value === 'Outro') ? 'block' : 'none';
            if (selectElement.value !== 'Outro') {
                outroInput.value = '';
            }
        }
    }

    function toggleCidadeEstrangeira(paisSelect, inicializacao = false) {
        const linha = paisSelect.closest('tr');
        if (!linha) return;

        const UFSelect = linha.querySelector('select[name*="_uf[]"]');
        const cidadeBRSelect = linha.querySelector('.select-cidade-dinamico');
        const cidadeEstrangeiraInput = linha.querySelector('.city-foreign-input') || linha.querySelector('input[name*="_cidade_estrangeira"]'); 

        if (!UFSelect || !cidadeBRSelect) return;

        const isBrasil = paisSelect.value === 'Brasil' || paisSelect.value === '';

        // Função auxiliar para bloquear visualmente SEM usar 'disabled' real
        // (Isso garante que o campo seja enviado pro servidor, evitando erro de índice)
        const setVisualLock = (el, locked) => {
            if (locked) {
                el.style.pointerEvents = 'none';      // O mouse não clica
                el.style.backgroundColor = '#e9ecef'; // Fundo cinza igual disabled
                el.style.color = '#6c757d';           // Texto cinza
                el.setAttribute('tabindex', '-1');    // Pula na navegação TAB
                // IMPORTANTE: Não colocamos el.disabled = true
            } else {
                el.style.pointerEvents = 'auto';
                el.style.backgroundColor = '';
                el.style.color = '';
                el.setAttribute('tabindex', '0');
            }
        };

        if (isBrasil) {
            // --- MODO BRASIL ---
            setVisualLock(UFSelect, false); // Destrava UF

            // Cuida do Select de Cidades (Choices.js ou Nativo)
            if (cidadeBRSelect.closest('.choices')) {
                cidadeBRSelect.closest('.choices').style.display = ''; 
                if (cidadeBRSelect.choicesInstance) {
                    cidadeBRSelect.choicesInstance.enable(); 
                }
            } else {
                cidadeBRSelect.style.display = ''; 
                setVisualLock(cidadeBRSelect, false);
            }

            if (cidadeEstrangeiraInput) cidadeEstrangeiraInput.style.display = 'none';

            // Dispara carregamento de cidades se não for load inicial
            if (!inicializacao) {
                const changeEvent = new Event('change');
                UFSelect.dispatchEvent(changeEvent);
            }

        } else {
            // --- MODO ESTRANGEIRO ---
            UFSelect.value = ''; 
            setVisualLock(UFSelect, true); // Trava visualmente a UF (mas envia vazio!)

            // Limpa Choices da Cidade
            if (cidadeBRSelect.choicesInstance) {
                cidadeBRSelect.choicesInstance.setChoiceByValue('');
            } else {
                cidadeBRSelect.value = '';
            }

            // Esconde o dropdown de Cidades BR
            if (cidadeBRSelect.closest('.choices')) {
                cidadeBRSelect.closest('.choices').style.display = 'none';
            } else {
                cidadeBRSelect.style.display = 'none'; 
            }

            // Mostra input texto
            if (cidadeEstrangeiraInput) cidadeEstrangeiraInput.style.display = 'block';
        }
    }

    function setupConditionalSelect(selectId, containerId) {
        const selectElement = document.getElementById(selectId);
        const containerElement = document.getElementById(containerId);
        if (!selectElement || !containerElement) { return; }
        const toggleVisibility = () => {
            if (selectElement.value === 'Sim') {
                containerElement.classList.remove('d-none');
            } else {
                containerElement.classList.add('d-none');
            }
        };
        selectElement.addEventListener('change', toggleVisibility);
        toggleVisibility();
    }

    function setupConditionalRadio(radioName, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        const collapse = new bootstrap.Collapse(container, { toggle: false });
        document.querySelectorAll(`input[name="${radioName}"]`).forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'Sim') { collapse.show(); } 
                else { collapse.hide(); }
            });
        });
    }

    function addAtividade() {
        const template = document.getElementById('template-atividade');
        const container = document.getElementById('atividades-container');
        if (!template || !container) return;
        const clone = template.content.cloneNode(true);
        const index = atividadeDivulgacaoIndex++;
        clone.querySelectorAll('*').forEach(el => {
            ['id', 'name', 'for'].forEach(attr => {
                if (el.hasAttribute(attr)) {
                    el.setAttribute(attr, el.getAttribute(attr).replace(/%%INDEX%%/g, index));
                }
            });
        });
        container.appendChild(clone);
        const radioSim = container.querySelector(`#foco_vulneravel_sim_${index}`);
        const containerVulneraveis = container.querySelector(`#container_vulneraveis_${index}`);
        if (radioSim && containerVulneraveis) {
            const collapseInstance = new bootstrap.Collapse(containerVulneraveis, { toggle: false });
            form.querySelectorAll(`input[name="div_foco_vulneravel_${index}"]`).forEach(radio => {
                radio.addEventListener('change', (e) => {
                    e.target.value === 'Sim' ? collapseInstance.show() : collapseInstance.hide();
                });
            });
        }
    }
    
    function inicializarModalINCT() {
        const dadosINCTsEl = document.getElementById('dados-completos-incts');
        if (!dadosINCTsEl) {
            console.error("Script com dados dos INCTs não encontrado.");
            return;
        }
        const todosOsINCTs = JSON.parse(dadosINCTsEl.textContent);
        let linhaAlvo = null; 
        const listaModal = document.querySelector('#modalBuscaINCT .list-group');
        if (listaModal) {
            listaModal.innerHTML = ''; 
            todosOsINCTs.forEach(inct => {
                const nome = inct.nome;
                const coordenador = inct.coordenador;
                const grandeArea = inct.grande_area;
                const area = inct.area_conhecimento;
                const itemHtml = `<a href="#" class="list-group-item list-group-item-action item-inct-selecionavel" 
                                     data-inct-nome="${nome}" 
                                     data-coordenador="${coordenador}"
                                     data-grande-area="${grandeArea}" 
                                     data-area="${area}" 
                                     data-bs-dismiss="modal">
                                     ${nome}
                                  </a>`;
                listaModal.insertAdjacentHTML('beforeend', itemHtml);
            });
        }
        document.body.addEventListener('click', function(e) {
            const botaoBusca = e.target.closest('.btn-busca-inct');
            if (botaoBusca) {
                linhaAlvo = botaoBusca.closest('tr');
            }
        });
        const filtroInput = document.getElementById('filtroINCTs');
        if (filtroInput) {
            filtroInput.addEventListener('keyup', function() {
                const termoBusca = this.value.toLowerCase();
                listaModal.querySelectorAll('.item-inct-selecionavel').forEach(item => {
                    const nomeItem = item.textContent.toLowerCase();
                    item.style.display = nomeItem.includes(termoBusca) ? '' : 'none';
                });
            });
        }
        if (listaModal) {
            listaModal.addEventListener('click', function(e) {
                const itemSelecionado = e.target.closest('.item-inct-selecionavel');
                if (itemSelecionado) {
                    e.preventDefault();
                    if (linhaAlvo) {
                        const nome = itemSelecionado.dataset.inctNome;
                        const coordenador = itemSelecionado.dataset.coordenador;
                        const grandeArea = itemSelecionado.dataset.grandeArea;
                        const area = itemSelecionado.dataset.area;
                        linhaAlvo.querySelector('.inct-nome').value = nome;
                        linhaAlvo.querySelector('.inct-coordenador').value = coordenador;
                        linhaAlvo.querySelector('.inct-grande-area').value = grandeArea;
                        linhaAlvo.querySelector('.inct-area').value = area;
                    }
                }
            });
        }
    }

    function parseCurrency(valorString) {
        if (!valorString || typeof valorString !== 'string') {
            return 0.0;
        }
        try {
            // Limpa de qualquer coisa que não seja número, ponto ou vírgula (ex: "R$ ")
            let valorLimpo = String(valorString).replace(/[^\d.,-]/g, '');

            // SE tem vírgula, o formato é brasileiro (ex: 1.000,50)
            if (valorLimpo.includes(',')) {
                valorLimpo = valorLimpo.replace(/\./g, ''); // Remove pontos de milhar
                valorLimpo = valorLimpo.replace(',', '.'); // Troca vírgula por ponto decimal
            }
            // SE NÃO tem vírgula, pode ser "1.000.000" (usuário digitando) ou "865548.67" (dado do servidor)
            else {
                // Se o último ponto estiver ANTES dos 3 últimos dígitos (ex: "1.000.000")
                if (valorLimpo.lastIndexOf('.') < valorLimpo.length - 3) {
                    valorLimpo = valorLimpo.replace(/\./g, '');
                }

            }
            
            return parseFloat(valorLimpo) || 0.0;
            
        } catch (e) {
            return 0.0;
        }
    }

    function formatarMoedaDigitando(input) {
        let valor = input.value;
        
        // 1. Salva a posição original do cursor
        let posCursor = input.selectionStart;
        let valorOriginal = input.value;

        // 2. Remove tudo que não for número (exceto a vírgula)
        let valorNumerico = valor.replace(/[^\d,]/g, '');

        // 3. Garante que só haja uma vírgula
        let partes = valorNumerico.split(',');
        if (partes.length > 2) {
            valorNumerico = partes[0] + ',' + partes.slice(1).join('');
        }

        // 4. Limita a duas casas decimais
        let parteDecimal = '';
        if (partes.length > 1) {
            parteDecimal = ',' + partes[1].substring(0, 2);
            valorNumerico = partes[0];
        } else {
            // Se não houver vírgula, trata tudo como parte inteira
            valorNumerico = partes[0];
        }

        // 5. Remove zeros à esquerda (ex: 005 vira 5)
        valorNumerico = valorNumerico.replace(/^0+(?=\d)/, '');

        // 6. Adiciona os pontos de milhar
        // Adiciona um "." sempre que houver 3 dígitos à frente, mas não no início
        let valorFormatado = valorNumerico.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + parteDecimal;
        
        // 7. Atualiza o valor no campo
        input.value = valorFormatado;

        // 8. Restaura a posição do cursor (calculando a diferença de pontos)
        try {
            let pontosAgora = (valorFormatado.match(/\./g) || []).length;
            let pontosAntesOriginal = (valorOriginal.substring(0, posCursor).match(/\./g) || []).length;
            let pontosAdicionados = pontosAgora - pontosAntesOriginal;
            
            input.setSelectionRange(posCursor + pontosAdicionados, posCursor + pontosAdicionados);
        } catch(e) {
            // Se houver um erro (raro), apenas coloca o cursor no final
            input.setSelectionRange(valorFormatado.length, valorFormatado.length);
        }
    }

    function formatarCampoMoeda(inputElemento, isCalculado = false) {
        if (!inputElemento) return;

        if (document.activeElement === inputElemento) {
            return;
        }
        let valorNumerico = parseCurrency(inputElemento.value);

        // Formata o número para o padrão brasileiro (R$ 1.234,56)
        let valorFormatado = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valorNumerico);

        if (valorNumerico === 0) {
            // Se for calculado (readonly) ou pré-preenchido, mostra "R$ 0,00".
            // Se for editável e vazio, deixa em branco.
            inputElemento.value = (isCalculado || inputElemento.value === '0' || inputElemento.value === '0.0') ? 'R$ 0,00' : '';
            return;
        }
        
        inputElemento.value = valorFormatado;
    }

    function atualizarExecucaoFinanceira() {
        const fontes = ['cnpq', 'capes', 'faps']; 

        fontes.forEach(fonte => {
            ['custeio', 'capital', 'bolsas_pais'].forEach(tipo => {
                const card = document.querySelector(`.card[data-fonte="${fonte}"][data-tipo="${tipo}"]`);
                if (!card) return;

                let totalGastoCard = 0;
                const campoTotalGasto = document.getElementById(`${fonte}_${tipo}_gasto`);

                if (tipo === 'bolsas_pais') {
                    if (campoTotalGasto) {
                        totalGastoCard = parseCurrency(campoTotalGasto.value);
                    }
                } else {
                    card.querySelectorAll('.gasto-detalhe').forEach(input => {
                        totalGastoCard += parseCurrency(input.value);
                    });
                    
                    if (campoTotalGasto) {
                        // 1. Define o valor numérico (como "150000,00")
                        campoTotalGasto.value = totalGastoCard.toFixed(2).replace('.', ',');
                        
                        // 2. CHAMA A FUNÇÃO DE FORMATAÇÃO VISUAL (A CORREÇÃO ESTÁ AQUI)
                        formatarCampoMoeda(campoTotalGasto, true); 
                    }
                }

                const campoAprovado = document.getElementById(`${fonte}_${tipo}_aprovado`);
                const campoPago = document.getElementById(`${fonte}_${tipo}_pago`);
                const gastoBar = document.getElementById(`${fonte}_${tipo}_gasto_bar`);
                const pagoBar = document.getElementById(`${fonte}_${tipo}_pago_bar`);

                if (campoAprovado && campoPago && gastoBar && pagoBar) {
                    const aprovado = parseCurrency(campoAprovado.value);
                    const pago = parseCurrency(campoPago.value);
                    
                    if (aprovado > 0) {
                        let pGasto = (totalGastoCard / aprovado) * 100;
                        let pPagoRestante = ((pago - totalGastoCard) / aprovado) * 100;

                        pGasto = Math.max(0, Math.min(pGasto, 100));
                        pPagoRestante = Math.max(0, Math.min(pPagoRestante, 100 - pGasto));
                        
                        gastoBar.style.width = `${pGasto}%`;
                        pagoBar.style.width = `${pPagoRestante}%`;

                        if(pGasto > 5) gastoBar.textContent = `Gasto`; else gastoBar.textContent = '';
                        if(pPagoRestante > 5) pagoBar.textContent = `Pago`; else pagoBar.textContent = '';

                    } else {
                        gastoBar.style.width = '0%';
                        pagoBar.style.width = '0%';
                        gastoBar.textContent = ''; 
                        pagoBar.textContent = '';
                    }
                }
            });

            // --- Lógica de Bolsas no Exterior (Quotas) - Nenhuma mudança aqui ---
            const cardQuotas = document.querySelector(`.card[data-fonte="${fonte}"][data-tipo="bolsas_ext"]`);
            if(cardQuotas) {
                const campoAprovado = document.getElementById(`${fonte}_bolsas_ext_aprovado`);
                const campoGasto = document.getElementById(`${fonte}_bolsas_ext_gasto`);
                const campoSaldo = document.getElementById(`${fonte}_bolsas_ext_saldo`);
                const gastoBar = document.getElementById(`${fonte}_bolsas_ext_gasto_bar`);
                const pagoBar = document.getElementById(`${fonte}_bolsas_ext_pago_bar`);

                if (campoAprovado && campoGasto && campoSaldo && gastoBar && pagoBar) {
                    const aprovado = parseInt(campoAprovado.value, 10) || 0;
                    const gasto = parseInt(campoGasto.value, 10) || 0;
                    const saldo = aprovado - gasto;
                    
                    campoSaldo.value = saldo;

                    if (aprovado > 0) {
                        let pGasto = (gasto / aprovado) * 100;
                        let pSaldo = (saldo / aprovado) * 100;

                        pGasto = Math.max(0, Math.min(pGasto, 100));
                        pSaldo = Math.max(0, Math.min(pSaldo, 100 - pGasto));

                        gastoBar.style.width = `${pGasto}%`;
                        pagoBar.style.width = `${pSaldo}%`;

                        if(pGasto > 5) gastoBar.textContent = `${gasto} Utilizadas`; else gastoBar.textContent = '';
                        if(pSaldo > 5) pagoBar.textContent = `${saldo} Saldo`; else pagoBar.textContent = '';
                    } else {
                        gastoBar.style.width = '0%';
                        pagoBar.style.width = '0%';
                        gastoBar.textContent = '';
                        pagoBar.textContent = '';
                    }
                }
            }
        });
    }
    
    function calcularEExibirProgressos(missoesData) {
        if (!missoesData || missoesData.length === 0) { return; }
        const progressoDasMetas = {};
        document.querySelectorAll('.meta-progresso-slider').forEach(s => {
            progressoDasMetas[s.dataset.metaId] = parseInt(s.value, 10);
        });
        const totalMetasUnicas = Object.keys(progressoDasMetas).length;
        let somaTotalMetas = 0;
        for (const metaId in progressoDasMetas) {
            somaTotalMetas += progressoDasMetas[metaId];
        }
        const progressoGeralMetas = totalMetasUnicas > 0 ? Math.round(somaTotalMetas / totalMetasUnicas) : 0;
        
        const progressoDosObjetivos = {};
        missoesData.forEach(missao => {
            missao.objetivos.forEach(objetivo => {
                const metasNecessarias = objetivo.metas.map(m => m.id);
                let progressoObjetivo = 0;
                if (metasNecessarias.length > 0) {
                    let soma = 0;
                    metasNecessarias.forEach(metaId => {
                        soma += progressoDasMetas[metaId] || 0;
                    });
                    progressoObjetivo = soma / metasNecessarias.length;
                }
                progressoDosObjetivos[objetivo.id] = progressoObjetivo;
            });
        });
        
        const valorTexto = document.getElementById('valor-velocimetro');
        const ponteiro = document.getElementById('gauge-needle');
        if (valorTexto && ponteiro) {
            valorTexto.textContent = `${progressoGeralMetas}%`;
            const rotacao = (progressoGeralMetas / 100) * 180 - 90;
            ponteiro.style.transform = `translateX(-50%) rotate(${rotacao}deg)`;
        }

        missoesData.forEach(missao => {
            let somaProgressoObjs = 0;
            missao.objetivos.forEach(objetivo => {
                const progressoObjetivo = progressoDosObjetivos[objetivo.id] || 0;
                const barraObj = document.querySelector(`.objetivo-card[data-objetivo-id="${objetivo.id}"] .progress-bar`);
                if (barraObj) {
                    barraObj.style.width = `${progressoObjetivo}%`;
                    barraObj.textContent = `${Math.round(progressoObjetivo)}%`;
                }
                somaProgressoObjs += progressoObjetivo;
            });
            const progressoMissao = missao.objetivos.length > 0 ? somaProgressoObjs / missao.objetivos.length : 0;
            const barraMissao = document.querySelector(`.missao-card[data-missao-id="${missao.id}"] .accordion-header .progress-bar`);
            if (barraMissao) {
                barraMissao.style.width = `${progressoMissao}%`;
                barraMissao.textContent = `${Math.round(progressoMissao)}%`;
            }
        });
    }

    function atualizarValidadosRH_Detalhado() {
        const MAPEAMENTO_RH = {
            'ic': ['iniciacao cientifica', 'iniciação científica'],
            'mestrado': ['mestrado', 'dissertacao de mestrado'],
            'doutorado': ['doutorado', 'tese de doutorado'],
            'posdoc': ['pos-doutorado', 'pós-doutorado', 'pos doutorado', 'supervisao de pos-doutorado']
        };
        const PALAVRAS_CHAVE_CONCLUSAO = ['concluido', 'concluida', 'concl', 'finalizado', 'completo'];
        const contadores = {
            rh_ic_andamento: 0, rh_ic_concluido: 0, rh_mestrado_andamento: 0, rh_mestrado_concluido: 0,
            rh_doutorado_andamento: 0, rh_doutorado_concluido: 0, rh_posdoc_andamento: 0, rh_posdoc_concluido: 0,
            rh_outras_andamento: 0, rh_outras_concluido: 0
        };
        const normalizar = (txt) => txt ? txt.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") : "";

        document.querySelectorAll(".toggle-rh:checked").forEach(checkbox => {
            const subtipoNormalizado = normalizar(checkbox.dataset.subtipo);
            const tipoNormalizado = normalizar(checkbox.dataset.tipo);
            let chaveEncontrada = null;
            for (const [chave, palavrasChave] of Object.entries(MAPEAMENTO_RH)) {
                if (palavrasChave.some(palavra => subtipoNormalizado.includes(palavra))) {
                    chaveEncontrada = chave;
                    break;
                }
            }
            const concluido = PALAVRAS_CHAVE_CONCLUSAO.some(palavra => tipoNormalizado.includes(palavra));
            let campo;
            if (chaveEncontrada) {
                campo = concluido ? `rh_${chaveEncontrada}_concluido` : `rh_${chaveEncontrada}_andamento`;
            } else if (subtipoNormalizado) {
                campo = concluido ? 'rh_outras_concluido' : 'rh_outras_andamento';
            }
            if (campo) {
                contadores[campo]++;
            }
        });

        const form = document.querySelector("form");
        for (const [campo, total] of Object.entries(contadores)) {
            const input = form.querySelector(`input[name="${campo}"]`);
            if (input) {
                input.value = total;
            }
        }
    }

    function categorizarEPopularListas() {
        const fonteProducoes = document.getElementById('fonte-producoes-lattes');
        const listaBiblioEl = document.getElementById('lista-producoes-bibliograficas');
        const listaTecnoEl = document.getElementById('lista-producoes-tecnologicas');
        if (!fonteProducoes || !listaBiblioEl || !listaTecnoEl) return;
        const todosOsItens = fonteProducoes.querySelectorAll('.list-group-item');
        todosOsItens.forEach((item, index) => {
            const tipoBruto = item.getAttribute('data-tipo-producao');
            const categoriaFinal = mapeamentoDeTipos[tipoBruto];
            if (!categoriaFinal) {
                return;
            }
            const containerControles = item.querySelector('.d-flex.justify-content-between');
            if (categoriasBibliograficas.includes(categoriaFinal)) {
                const switchHtml = `
                    <div>
                        <div class="form-check form-switch">
                            <input class="form-check-input toggle-bibliografico" type="checkbox" id="biblio_validacao_${index}">
                            <label class="form-check-label" for="biblio_validacao_${index}">Validar</label>
                        </div>
                        <div class="form-check form-switch mt-2">
                            <input class="form-check-input coautoria-check" type="checkbox" name="coautoria_internacional[]" value="${index}" id="coautoria_check_${index}">
                            <label class="form-check-label" for="coautoria_check_${index}">Coautoria Internacional?</label>
                        </div>
                        <div class="mt-1 coautoria-paises-container" style="display: none;">
                            <select name="paises_coautores[]" class="form-control-sm select-paises-coautoria" multiple></select>
                        </div>
                    </div>`;
                containerControles.insertAdjacentHTML('beforeend', switchHtml);
                listaBiblioEl.appendChild(item);
                inicializarChoicesEmSelect(item.querySelector('.select-paises-coautoria'));
            } else if (categoriasTecnologicas.includes(categoriaFinal)) {
                const checkboxesHtml = `<div class="d-flex align-items-center"><div class="form-check form-check-inline"><input class="form-check-input toggle-tecnologico" type="checkbox" value="nacional" id="tec_nacional_${index}"><label class="form-check-label" for="tec_nacional_${index}">Nacional</label></div><div class="form-check form-check-inline"><input class="form-check-input toggle-tecnologico" type="checkbox" value="exterior" id="tec_exterior_${index}"><label class="form-check-label" for="tec_exterior_${index}">Exterior</label></div></div>`;
                containerControles.insertAdjacentHTML('beforeend', checkboxesHtml);
                listaTecnoEl.appendChild(item);
            }
        });
        fonteProducoes.remove();
        const botaoAdicionar = document.getElementById('btn-abrir-modal-publicacao');
        if (botaoAdicionar) {
            listaBiblioEl.appendChild(botaoAdicionar);
        }
        const botaoAdicionarTecno = document.getElementById('btn-abrir-modal-tecnologica');
        if (botaoAdicionarTecno) {
            listaTecnoEl.appendChild(botaoAdicionarTecno);
        }
    }

    function atualizarResumoArtistico() {
        const tabelaResumo = document.getElementById('tabela-resumo-artistico');
        if (!tabelaResumo) return;

        // 1. Zera os contadores
        const contadores = {};
        tabelaResumo.querySelectorAll('tbody tr').forEach(row => {
            const categoria = row.getAttribute('data-producao-tipo');
            if (categoria) {
                contadores[categoria] = { nacional: 0, internacional: 0 };
            }
        });

        // 2. Conta os inputs marcados
        const lista = document.getElementById('lista-producoes-artisticas');
        if (!lista) return;

        const itensMarcados = lista.querySelectorAll('input.toggle-artistico:checked');

        itensMarcados.forEach(radio => {
            const item = radio.closest('.list-group-item');
            const categoriaMapeada = item.getAttribute('data-producao-tipo');
            const valor = radio.value.toLowerCase().trim();
            
            if (categoriaMapeada && contadores.hasOwnProperty(categoriaMapeada)) {
                if (valor === 'nacional') {
                    contadores[categoriaMapeada].nacional++;
                } else if (valor === 'internacional' || valor === 'exterior') {
                    contadores[categoriaMapeada].internacional++;
                }
            }
        });

        // 3. Atualiza a Tabela
        for (const categoria in contadores) {
            const linha = tabelaResumo.querySelector(`tr[data-producao-tipo="${categoria}"]`);
            if (linha) {
                const inpNacional = linha.querySelector('.input-nacional');
                const inpInternacional = linha.querySelector('.input-internacional');
                if (inpNacional && inpInternacional) {
                    inpNacional.value = contadores[categoria].nacional;
                    inpInternacional.value = contadores[categoria].internacional;
                }
            }
        }
    }

    function atualizarResumoInovacao() {
        const tabelaResumo = document.getElementById('tabela-resumo-inovacao');
        if (!tabelaResumo) return;

        // 1. Zera contadores
        const contadores = {};
        tabelaResumo.querySelectorAll('tbody tr').forEach(row => {
            const categoria = row.getAttribute('data-producao-tipo');
            if (categoria) contadores[categoria] = { nacional: 0, internacional: 0 };
        });

        // 2. Percorre itens
        const lista = document.getElementById('lista-producoes-inovacao');
        if (!lista) return;

        // Só conta se estiver validado (.toggle-inovacao:checked)
        const validacoesMarcadas = lista.querySelectorAll('.toggle-inovacao:checked');

        validacoesMarcadas.forEach(toggle => {
            const item = toggle.closest('.list-group-item');
            const categoriaMapeada = item.getAttribute('data-producao-tipo');
            
            // Verifica qual escopo está marcado dentro deste item
            const radioNacional = item.querySelector('input[value="Nacional"]:checked');
            const radioInternacional = item.querySelector('input[value="Internacional"]:checked');

            if (categoriaMapeada && contadores.hasOwnProperty(categoriaMapeada)) {
                if (radioNacional) {
                    contadores[categoriaMapeada].nacional++;
                } else if (radioInternacional) {
                    contadores[categoriaMapeada].internacional++;
                }
            }
        });

        // 3. Atualiza tabela
        for (const categoria in contadores) {
            const linha = tabelaResumo.querySelector(`tr[data-producao-tipo="${categoria}"]`);
            if (linha) {
                const inpNacional = linha.querySelector('.input-nacional');
                const inpInternacional = linha.querySelector('.input-internacional');
                if(inpNacional) inpNacional.value = contadores[categoria].nacional;
                if(inpInternacional) inpInternacional.value = contadores[categoria].internacional;
            }
        }
    }

    function atualizarResumoProjetosEmpresa() {
        const tabelaResumo = document.getElementById('tabela-resumo-projetos-empresa');
        if (!tabelaResumo) return;

        const contadores = {};
        tabelaResumo.querySelectorAll('tbody tr').forEach(row => {
            const categoria = row.getAttribute('data-producao-tipo');
            if (categoria) contadores[categoria] = { nacional: 0, internacional: 0 };
        });

        const lista = document.getElementById('lista-projetos-empresa');
        if (!lista) return;

        // Apenas conta se estiver validado
        const validados = lista.querySelectorAll('.toggle-projeto-empresa:checked');

        validados.forEach(toggle => {
            const item = toggle.closest('.item-projeto-empresa');
            const categoria = item.getAttribute('data-producao-tipo');
            
            const radioNac = item.querySelector('input[value="Nacional"]:checked');
            const radioInt = item.querySelector('input[value="Internacional"]:checked');

            if (categoria && contadores.hasOwnProperty(categoria)) {
                if (radioNac) contadores[categoria].nacional++;
                else if (radioInt) contadores[categoria].internacional++;
            }
        });

        for (const cat in contadores) {
            const linha = tabelaResumo.querySelector(`tr[data-producao-tipo="${cat}"]`);
            if (linha) {
                linha.querySelector('.input-nacional').value = contadores[cat].nacional;
                linha.querySelector('.input-internacional').value = contadores[cat].internacional;
            }
        }
    }

    function atualizarResumoTecnologico() {
        const tabelaResumoTecnoEl = document.getElementById('tabela-resumo-tecnologico');
        if (!tabelaResumoTecnoEl) return;

        // 1. Zera os contadores
        const contadores = {};
        tabelaResumoTecnoEl.querySelectorAll('tbody tr').forEach(row => {
            const categoria = row.getAttribute('data-producao-tipo');
            if (categoria) {
                contadores[categoria] = { nacional: 0, internacional: 0 };
            }
        });

        // 2. Conta os Radio Buttons marcados (.radio-abrangencia)
        // Nota: Usamos o novo ID da lista (#lista-producoes-tecnicas)
        const lista = document.getElementById('lista-producoes-tecnicas') || document.getElementById('lista-producoes-tecnologicas');
        if (!lista) return;

        const itensMarcados = lista.querySelectorAll('input[type="radio"]:checked');

        itensMarcados.forEach(radio => {
            const item = radio.closest('.list-group-item');
            const categoriaMapeada = item.getAttribute('data-producao-tipo');
            const valor = radio.value.toLowerCase().trim();
            
            if (categoriaMapeada && contadores.hasOwnProperty(categoriaMapeada)) {
                if (valor === 'nacional') {
                    contadores[categoriaMapeada].nacional++;
                } else if (valor === 'internacional' || valor === 'exterior') {
                    contadores[categoriaMapeada].internacional++;
                }
            }
        });

        // 3. Atualiza a Tabela
        for (const categoria in contadores) {
            const linha = tabelaResumoTecnoEl.querySelector(`tr[data-producao-tipo="${categoria}"]`);
            if (linha) {
                // Tenta pegar pelas classes novas (.input-nacional e .input-internacional)
                const inpNacional = linha.querySelector('.input-nacional');
                const inpInternacional = linha.querySelector('.input-internacional');

                if (inpNacional && inpInternacional) {
                    inpNacional.value = contadores[categoria].nacional;
                    inpInternacional.value = contadores[categoria].internacional;
                } else {
                    // Fallback para buscar por índice se as classes não existirem
                    const inputs = linha.querySelectorAll('input[type="number"]');
                    if (inputs.length >= 2) {
                        inputs[0].value = contadores[categoria].nacional;
                        inputs[1].value = contadores[categoria].internacional;
                    }
                }
            }
        }
    }

    function salvarRascunhoLocal() {
        const dadosFormulario = {};
        const formData = new FormData(form);
        for (const [key, value] of formData.entries()) {
            if (key.endsWith('[]')) {
                if (!dadosFormulario[key]) {
                    dadosFormulario[key] = [];
                }
                dadosFormulario[key].push(value);
            } else {
                dadosFormulario[key] = value;
            }
        }
        localStorage.setItem(CHAVE_RASCUNHO, JSON.stringify(dadosFormulario));
    }

    function carregarRascunhoLocal() {
        const dadosSalvos = localStorage.getItem(CHAVE_RASCUNHO);
        if (dadosSalvos) {
            const dadosFormulario = JSON.parse(dadosSalvos);
            Object.keys(dadosFormulario).forEach(name => {
                const valor = dadosFormulario[name];
                const elementos = form.querySelectorAll(`[name="${name}"]`);
                
                if (Array.isArray(valor)) {
                    elementos.forEach((elemento, index) => {
                        if (index < valor.length) {
                            if (elemento.type === 'checkbox' || elemento.type === 'radio') {
                                elemento.checked = (elemento.value === valor[index]);
                            } else {
                                elemento.value = valor[index];
                            }
                        }
                    });
                } else {
                    if (elementos.length > 0) {
                        const elemento = elementos[0];
                        if (elemento.type === 'radio') {
                            const radio = document.querySelector(`[name="${name}"][value="${valor}"]`);
                            if(radio) radio.checked = true;
                        } else if (elemento.type === 'checkbox') {
                            elemento.checked = !!valor;
                        } else {
                            elemento.value = valor;
                        }
                    }
                }
            });
        }
    }

    function gerenciarFontesDeApoio(checkbox, radioGroupName) {
        const container = checkbox.closest('.col-md-12');
        if (!container) return;
        const radios = container.querySelectorAll(`input[name="${radioGroupName}"]`);
        if (checkbox.checked) {
            radios.forEach(radio => radio.disabled = false);
        } else {
            radios.forEach(radio => {
                radio.disabled = true;
                radio.checked = false;
            });
        }
    }

    // --- INICIALIZAÇÃO E EVENT LISTENERS ---
     window.removerLinha = removerLinha;
    window.removerBloco = removerBloco;
    window.toggleOutro = toggleOutro;
    window.addLinhaFromTemplate = addLinhaFromTemplate;
    window.addAtividade = addAtividade;
    window.gerenciarFontesDeApoio = gerenciarFontesDeApoio;
    window.addArticulacao = addArticulacao;
    window.addLinhaNacional = () => addLinhaFromTemplate('template-empresa-nacional', 'tabela-empresas-nacionais');
    window.addLinhaEstrangeira = () => addLinhaFromTemplate('template-empresa-estrangeira', 'tabela-empresas-estrangeiras');
    window.addContrato = () => addLinhaFromTemplate('template-contrato', 'tabela-contratos');
    window.addNda = () => addLinhaFromTemplate('template-nda', 'tabela-nda');
    window.addCooperacao = () => addLinhaFromTemplate('template-cooperacao', 'tabela-cooperacao');
    window.addVisitante = () => addLinhaFromTemplate('template-visitante', 'tabela-visitantes');
    window.addEvento = () => addLinhaFromTemplate('template-evento', 'tabela-eventos');
    window.addOutraOrientacao = () => addLinhaFromTemplate('template-outra-orientacao', 'tabela-outras-orientacoes');
    window.addDivulgacao = () => addLinhaFromTemplate('template-divulgacao', 'tabela-divulgacao');
    
    if (typeof inicializarModalINCT === 'function') {
        inicializarModalINCT();
    }
    
    // Roda as funções de cálculo e preenchimento iniciais
    calcularEExibirProgressos(missoesData);
    setupConditionalSelect("houve_alavancagem_select", "alavancagem_container");
    setupConditionalSelect("articula_inct_select", "container_articulacao_inct");
    setupConditionalSelect("coop_internacional_select", "container_cooperacao");
    setupConditionalRadio('organizou_eventos', 'container-eventos');
    setupConditionalRadio('houve_visita_estrangeiro', 'container-visitantes');
    carregarRascunhoLocal();
    document.querySelectorAll('.campo-moeda').forEach(campo => {
        if (campo.value) {
            const isCalculado = campo.hasAttribute('readonly');
            formatarCampoMoeda(campo, isCalculado);
        }
    });
    atualizarValidadosRH_Detalhado();
    categorizarEPopularListas(); 
    atualizarResumoBibliografico(); 
    atualizarResumoTecnologico(); 
    popularTiposDeProducaoModal();
    popularTiposTecnologicosModal();
    atualizarExecucaoFinanceira();
    adicionarProducaoTecnologicaManual();
    sincronizarCoautorias();

    const btnSalvarPublicacao = document.getElementById('btnSalvarPublicacao');
    if (btnSalvarPublicacao) {
        btnSalvarPublicacao.addEventListener('click', function () {
            const modalEl = document.getElementById('modalNovaPublicacao');
            const formEl = document.getElementById('formNovaPublicacao');
            if (!formEl) {
                alert("ERRO: O container do formulário (#formNovaPublicacao) não foi encontrado.");
                return;
            }
            const dados = {
                tipo: document.getElementById('tipoProducaoManual').value,
                titulo: document.getElementById('tituloProducaoManual').value,
                autores: document.getElementById('autoresProducaoManual').value,
                ano: document.getElementById('anoProducaoManual').value
            };
            if (!dados.tipo || !dados.titulo || !dados.ano) {
                alert('Por favor, preencha Tipo, Título e Ano.');
                return;
            }

            const novoCardHtml = criarCardPublicacaoManual(dados);
            const botaoAdicionar = document.getElementById('btn-abrir-modal-publicacao');
            
            if (botaoAdicionar) {
                botaoAdicionar.insertAdjacentHTML('beforebegin', novoCardHtml);
                const novoCardElemento = botaoAdicionar.previousElementSibling;
                inicializarChoicesEmSelect(novoCardElemento.querySelector('.select-paises-coautoria'));
            }
            
            limparCamposManualmente(formEl);
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }

    const listaBiblio = document.getElementById('lista-producoes-bibliograficas');
    if (listaBiblio) {
        listaBiblio.addEventListener('click', function(event) {
            const botaoRemover = event.target.closest('.btn-remover-publicacao');
            if (botaoRemover) {
                const cardParaRemover = botaoRemover.closest('.list-group-item');
                cardParaRemover.remove();
                atualizarResumoBibliografico();
            }
        });
    }

    const listaTecno = document.getElementById('lista-producoes-tecnologicas');
    if (listaTecno) {
        listaTecno.addEventListener('click', function(event) {
            const botaoRemover = event.target.closest('.btn-remover-publicacao');
            if (botaoRemover) {
                const cardParaRemover = botaoRemover.closest('.list-group-item');
                cardParaRemover.remove();
                atualizarResumoTecnologico();
            }
        });
    }

    // --- "Ouvintes" de eventos consolidados ---
    form.addEventListener('change', function(event) {
        const target = event.target;

        if (target.matches('.toggle-rh')) {
            atualizarValidadosRH_Detalhado();

        } else if (target.matches('.toggle-bibliografico')) {
            atualizarResumoBibliografico();

        } else if (target.matches('.toggle-divulgacao')) {
            atualizarResumoDivulgacao();

        } else if (target.matches('.toggle-artistico')) {
    
            const item = target.closest('.list-group-item');
            if (item) {
                const containerPais = item.querySelector('.art-exterior-pais-container');
                if (containerPais) {
                    const valor = target.value.toLowerCase().trim();
                    
                    // Lógica de Mostrar/Esconder País
                    if (valor === 'internacional' || valor === 'exterior') {
                        containerPais.style.display = 'block';
                        
                        // Popula a lista de países (Reusando a função existente que clona os países)
                        const selectPais = containerPais.querySelector('select');
                        if (selectPais && selectPais.options.length <= 1) {
                            popularPaisesTecnologia(selectPais); // Podemos reusar essa função pois ela apenas clona a lista de países
                        }
                    } else {
                        containerPais.style.display = 'none';
                        const selectPais = containerPais.querySelector('select');
                        if(selectPais) selectPais.value = "";
                    }
                }
            }
            // Atualiza o resumo
            atualizarResumoArtistico();    

        } else if (target.matches('.radio-abrangencia') || target.matches('.toggle-tecnologico')) {
    
            const item = target.closest('.list-group-item');
            if (item) {
                // Busca o container do select de país dentro deste item
                const containerPais = item.querySelector('.tec-exterior-pais-container');
                
                if (containerPais) {
                    const valor = target.value.toLowerCase().trim();
                    
                    // Se for Internacional ou Exterior, mostra o campo. Caso contrário, esconde.
                    if (valor === 'internacional' || valor === 'exterior') {
                        containerPais.style.display = 'block';
                        
                        // Popula a lista de países se estiver vazia
                        const selectPais = containerPais.querySelector('select');
                        if (selectPais && selectPais.options.length <= 1) {
                            popularPaisesTecnologia(selectPais);
                        }
                    } else {
                        // Se for Nacional
                        containerPais.style.display = 'none';
                        
                        // Opcional: Limpar o país selecionado quando voltar para nacional
                        const selectPais = containerPais.querySelector('select');
                        if(selectPais) selectPais.value = "";
                    }
                }
            }

            // Atualiza a tabela de contagem
            atualizarResumoTecnologico();
            
            // Se tiver a função de sincronizar com outra aba (opcional, dependendo do seu uso)
            if(typeof sincronizarProducaoTecnologicaInternacional === 'function') {
                sincronizarProducaoTecnologicaInternacional();
            }


        } else if (target.matches('.coautoria-check')) {
            const containerPaises = target.closest('.form-check').nextElementSibling;
            if (containerPaises && containerPaises.classList.contains('coautoria-paises-container')) {
                containerPaises.style.display = target.checked ? 'block' : 'none';
            }
            if (!target.checked) {
                sincronizarCoautorias();
            }
        }

        // 1. Botão Validar (Toggle) da Inovação
        else if (target.matches('.toggle-inovacao')) {
            const item = target.closest('.item-inovacao');
            const containerEscopo = item.querySelector('.container-escopo-inovacao');
            
            if (target.checked) {
                containerEscopo.style.display = 'block';
            } else {
                // Se desmarcar, esconde tudo e limpa
                containerEscopo.style.display = 'none';
                
                // Reseta radios de escopo
                const radiosEscopo = containerEscopo.querySelectorAll('input[type="radio"]');
                radiosEscopo.forEach(r => r.checked = false);
                
                // Esconde a parte internacional
                const containerIntl = containerEscopo.querySelector('.container-detalhes-internacional');
                if(containerIntl) containerIntl.style.display = 'none';
            }
            atualizarResumoInovacao();
        }

        // 2. Radio de Escopo (Nacional/Internacional) da Inovação
        else if (target.matches('.radio-escopo-inovacao')) {
            const item = target.closest('.item-inovacao');
            const containerIntl = item.querySelector('.container-detalhes-internacional');
            
            if (target.value === 'Internacional') {
                containerIntl.style.display = 'block';
                
                // Inicializa select de países se necessário
                const selectPais = containerIntl.querySelector('.select-pais-inovacao');
                if (selectPais && selectPais.options.length <= 1) {
                    // Reusa a função que clona a lista de países
                    if (typeof popularPaisesTecnologia === 'function') {
                        popularPaisesTecnologia(selectPais);
                    }
                    // Inicializa o Choices.js se a função existir
                    if (typeof inicializarChoicesEmSelect === 'function') {
                         inicializarChoicesEmSelect(selectPais);
                    }
                }
            } else {
                containerIntl.style.display = 'none';
            }
            atualizarResumoInovacao();
        }

        // 3. Checkbox "Outro" no Tipo de Internacionalização
        else if (target.matches('.checkbox-outro-inovacao')) {
            const containerOpcoes = target.closest('div');
            const inputTexto = containerOpcoes.querySelector('.input-outro-inovacao');
            if (inputTexto) {
                inputTexto.style.display = target.checked ? 'block' : 'none';
                if (!target.checked) inputTexto.value = '';
            }
        }

        // LÓGICA DA 4.3.1 - PROJETOS COM EMPRESAS
    else if (target.matches('.toggle-projeto-empresa')) {
        const item = target.closest('.item-projeto-empresa');
        const containerEscopo = item.querySelector('.container-escopo-projeto');
        
        if (target.checked) {
            containerEscopo.style.display = 'block';
        } else {
            containerEscopo.style.display = 'none';
            // Reseta seleções
            containerEscopo.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
            const containerPais = containerEscopo.querySelector('.container-paises-projeto');
            if(containerPais) containerPais.style.display = 'none';
        }
        atualizarResumoProjetosEmpresa();
    }

    else if (target.matches('.radio-escopo-projeto')) {
        const item = target.closest('.item-projeto-empresa');
        const containerPais = item.querySelector('.container-paises-projeto');
        
        if (target.value === 'Internacional') {
            containerPais.style.display = 'block';
            
            // Carrega Select de Países (Reutilizando sua função)
            const selectPais = containerPais.querySelector('.select-pais-projeto');
            if (selectPais && selectPais.options.length <= 1) {
                if(typeof popularPaisesTecnologia === 'function') popularPaisesTecnologia(selectPais);
                if(typeof inicializarChoicesEmSelect === 'function') inicializarChoicesEmSelect(selectPais);
            }
        } else {
            containerPais.style.display = 'none';
        }
        atualizarResumoProjetosEmpresa();
    }
        
        salvarRascunhoLocal();
    });
    
    form.addEventListener('input', function(event) {
        const target = event.target;

        if (target.matches('.meta-progresso-slider')) {
            const displayValor = target.nextElementSibling;
            if (displayValor) { displayValor.textContent = `${target.value}%`; }
            calcularEExibirProgressos(missoesData);
        } 

        // ATUALIZAÇÃO INSTANTÂNEA DAS FINANÇAS
        if (target.matches('.campo-moeda:not([readonly])') || target.matches('.gasto-detalhe-quota')) {
            
            // FORMATAÇÃO AUTOMÁTICA DE MOEDA AO DIGITAR
            if (target.matches('.campo-moeda')) {
                formatarMoedaDigitando(target);
            }

            // ▼▼▼ LÓGICA DE VALIDAÇÃO INTELIGENTE (PAGO vs. APROVADO) ▼▼▼
            if (target.matches('[id*="_pago"]')) { // Se o campo for um "Total Pago"
                const card = target.closest('.card');
                if (card) {
                    const campoAprovado = card.querySelector('[id*="_aprovado"]');
                    if (campoAprovado) {
                        const valorAprovado = parseCurrency(campoAprovado.value);
                        let valorPago = parseCurrency(target.value);
                        
                        // Só valida se o Aprovado for maior que zero
                        if (valorAprovado > 0 && valorPago > valorAprovado) {
                            // Alerta o usuário
                            alert("O 'Total Pago' não pode ser maior que o 'Total Aprovado'.\nO valor será ajustado para o máximo permitido.");
                            
                            // Copia o valor formatado do Aprovado para o campo Pago
                            target.value = campoAprovado.value; 
                            
                            // Re-formata o campo "Pago" com os pontos de milhar corretos
                            formatarMoedaDigitando(target); 
                        }
                    }
                }
            }
            atualizarExecucaoFinanceira();
        }
        
        salvarRascunhoLocal();
    });
        
    form.addEventListener('focusout', function (event) {
        if (event.target.matches('.campo-moeda:not([readonly])')) {
            formatarCampoMoeda(event.target, false); 
        }
    });

    // 1. Ativa o Choices.js para os campos de multi-seleção da tabela de Resultados
    const multipleSelects = document.querySelectorAll('.choices-multiple');
    multipleSelects.forEach(select => {
      new Choices(select, {
        removeItemButton: true,
        placeholder: true,
        placeholderValue: 'Selecione uma ou mais opções...',
      });
    });

    // 2. Ativa o Choices.js para os campos de países da Coautoria (na Seção 4.2)
    const selectsPaises = document.querySelectorAll('.select-paises-coautoria');
    selectsPaises.forEach(select => {
        inicializarChoicesEmSelect(select);
    });

    const dropdownMenus = document.querySelectorAll('.table .dropdown-menu');
    dropdownMenus.forEach(menu => {
      atualizarTextoDropdown(menu);
      menu.addEventListener('change', () => atualizarTextoDropdown(menu));
      menu.addEventListener('click', (e) => e.stopPropagation());
    });

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // 1. Lê os dados das cidades do JSON
    const dadosCidadesEl = document.getElementById('dados-cidades-json');
    const cidadesPorUF = (dadosCidadesEl && dadosCidadesEl.textContent.trim()) 
                         ? JSON.parse(dadosCidadesEl.textContent) 
                         : {};

    function setupUFCityLogic(ufSelect, citySelect) {
    
        if (citySelect.classList.contains('choices__input')) return;

        const cityChoices = new Choices(citySelect, {
            searchEnabled: true,
            itemSelectText: '',
            noResultsText: 'Nenhum município encontrado',
            placeholder: true,
            placeholderValue: 'Selecione o município...',
            shouldSort: true, 
        });
        
        // Guarda a instância para usarmos na outra função
        citySelect.choicesInstance = cityChoices;
        
        const popularCidades = (uf) => {
            cityChoices.clearStore();
            
            if (!uf || uf === "") {
                cityChoices.setChoices([
                    { value: '', label: 'Selecione a UF primeiro...', selected: true, disabled: true }
                ], 'value', 'label', true);
                
                return;
            }

            const ufSigla = uf.toString().toUpperCase().trim();
            const listaCidades = cidadesPorUF[ufSigla] || [];
            
            const novasOpcoes = listaCidades.map(c => ({ value: c, label: c }));
            novasOpcoes.unshift({ value: '', label: 'Selecione...', selected: true, disabled: true });
            
            cityChoices.setChoices(novasOpcoes, 'value', 'label', true);
            cityChoices.enable();
        };

        ufSelect.addEventListener('change', function() {
            cityChoices.clearInput();
            popularCidades(this.value);
        });

        if (ufSelect.value) {
            popularCidades(ufSelect.value);
        } else {
            popularCidades(""); // Inicializa limpo, mas habilitado
        }
    }

    function aplicarLogicaCidadesGeral() {
        document.querySelectorAll('tr').forEach(row => {
            
            const paisSelect = row.querySelector('select[name$="_pais[]"]');
            const ufSelect = row.querySelector('select[name$="_uf[]"]'); 
            const citySelect = row.querySelector('.select-cidade-dinamico');
            
            // --- LÓGICA INTELIGENTE DE PAÍS ---
            if (paisSelect) {
                paisSelect.addEventListener('change', function() {
                    toggleCidadeEstrangeira(this, false); 
                    
                    // Se mudou para Brasil, reseta UF para obrigar seleção limpa
                    if (this.value === 'Brasil' && ufSelect) {
                        // (Opcional) Poderíamos limpar a UF aqui se quiséssemos forçar re-seleção
                    }
                });
                
                // Inicialização visual (esconder input estrangeiro se for Brasil)
                toggleCidadeEstrangeira(paisSelect, true); 
            }

            // --- LÓGICA DA UF QUE CONTROLA O PAÍS ---
            if (ufSelect && paisSelect) {
                ufSelect.addEventListener('change', function() {
                    // SE O USUÁRIO SELECIONAR UMA UF...
                    if (this.value !== "") {
                        // ...E O PAÍS ESTIVER VAZIO OU FOR DIFERENTE DE BRASIL...
                        if (paisSelect.value === "" || paisSelect.value !== "Brasil") {
                            // ...NÓS MARCAMOS "BRASIL" AUTOMATICAMENTE!
                            paisSelect.value = "Brasil";
                            // E garantimos que o input estrangeiro suma
                            toggleCidadeEstrangeira(paisSelect, false);
                        }
                    }
                });
            }
            
            // Inicia a lógica de Cidades
            if (ufSelect && citySelect) {
                setupUFCityLogic(ufSelect, citySelect);
            }
        });
    }
    // Executa ao carregar
    aplicarLogicaCidadesGeral();

    // --- LÓGICA DE SALVAMENTO PARCIAL (BOTÕES POR SEÇÃO) ---
    const botoesSalvar = document.querySelectorAll('.btn-salvar-secao');

    botoesSalvar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); 

            // CHAMA O LOADING
            mostrarLoading("Salvando suas alterações...");
            
            btn.disabled = true; // Trava o botão para evitar clique duplo

            const form = document.querySelector('form');
            const formData = new FormData(form); 

            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error('Erro na resposta do servidor');
            })
            .then(data => {
                // Muda a mensagem para Sucesso
                mostrarLoading("✅ " + data.message);
                
                // Fecha o loading depois de 1.5 segundos
                setTimeout(() => { 
                    esconderLoading(); 
                    btn.disabled = false; // Destrava o botão
                }, 1500);
            })
            .catch(error => {
                console.error('Erro:', error);
                esconderLoading(); // Fecha imediatamente se der erro
                alert("❌ Erro ao salvar. Verifique sua conexão.");
                btn.disabled = false;
            });
        });
    });

});

document.addEventListener('DOMContentLoaded', function() {

    // =============================================================================
    // 1. FUNÇÕES GLOBAIS (Interface e Helpers)
    // =============================================================================
    
    window.toggleInputOutro = function(checkbox, inputId) {
        const target = document.getElementById(inputId) || checkbox.closest('div').querySelector('.input-outro-interacao, .input-outro-inovacao');
        if (target) {
            if (checkbox.checked) {
                target.parentElement.style.display = 'block';
                target.classList.remove('d-none');
                target.style.display = 'block';
                target.focus();
            } else {
                target.parentElement.style.display = 'none';
                target.classList.add('d-none');
                target.style.display = 'none';
                target.value = ''; 
            }
        }
    };

    window.toggleDetalhesDivulgacao = function(checkbox, collapseId) {
        const collapseEl = document.getElementById(collapseId);
        if (collapseEl) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                const bsCollapse = bootstrap.Collapse.getInstance(collapseEl) || new bootstrap.Collapse(collapseEl, { toggle: false });
                checkbox.checked ? bsCollapse.show() : bsCollapse.hide();
            } else {
                checkbox.checked ? collapseEl.classList.add('show') : collapseEl.classList.remove('show');
            }
        }
    };

    window.togglePaisDivulgacao = function(radio, containerId) {
        const container = document.getElementById(containerId);
        if(container) {
            radio.value === 'Internacional' ? container.classList.remove('d-none') : container.classList.add('d-none');
        }
    };

    // =============================================================================
    // 2. MAPAS DE TRADUÇÃO
    // =============================================================================
    const mapaTiposGeral = {
        'ARTIGO-PUBLICADO': 'Artigos completos publicados em periódicos',
        'ARTIGO-ACEITO-PARA-PUBLICACAO': 'Artigos aceitos para publicação',
        'LIVRO-PUBLICADO': 'Livros publicados/organizados ou edições',
        'CAPITULO-DE-LIVRO-PUBLICADO': 'Capítulos de livros publicados',
        'TEXTO-EM-JORNAL-OU-REVISTA': 'Textos em jornais de notícias/revistas',
        'TRABALHO-EM-EVENTOS': 'Trabalhos completos publicados em anais de congressos',
        'RESUMO-EXPANDIDO-EM-EVENTOS': 'Resumos expandidos publicados em anais de congressos',
        'RESUMO-EM-EVENTOS': 'Resumos publicados em anais de congressos',
        'APRESENTACAO-DE-TRABALHO': 'Apresentação de trabalho e palestra',
        'OUTRA-PRODUCAO-BIBLIOGRAFICA': 'Outra produção bibliográfica',
        'ASSESSORIA-E-CONSULTORIA': 'Assessoria e consultoria',
        'EXTENSAO-TECNOLOGICA': 'Extensão tecnológica',
        'PROGRAMA-DE-COMPUTADOR-SEM-REGISTRO': 'Programas de computador sem registro',
        'PRODUTO-TECNOLOGICO': 'Produtos', 
        'PROCESSOS-OU-TECNICAS': 'Processos ou técnicas',
        'TRABALHO-TECNICO': 'Trabalhos técnicos',
        'CARTAS-MAPAS-OU-SIMILARES': 'Cartas, mapas ou similares',
        'CURSO-DE-CURTA-DURACAO-MINISTRADO': 'Curso de curta duração ministrado',
        'DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL': 'Desenvolvimento de material didático ou instrucional',
        'MANUTENCAO-DE-OBRA-ARTISTICA': 'Manutenção de obra artística',
        'ORGANIZACAO-DE-EVENTO': 'Organização de evento',
        'OUTRA-PRODUCAO-TECNICA': 'Outra produção técnica',
        'ARTES-CENICAS': 'Artes Cênicas',
        'MUSICA': 'Música',
        'ARTES-VISUAIS': 'Artes visuais',
        'OUTRA-PRODUCAO-ARTISTICA-CULTURAL': 'Outra produção artística/cultural'
    };

    // --- NOVO MAPA EXCLUSIVO PARA A SEÇÃO 4.5 (DIVULGAÇÃO) ---
    const regrasDivulgacao45 = {
        // Bibliográfica
        'Artigos completos publicados em periódicos': ['ARTIGO-PUBLICADO', 'artigo-publicado', 'artigo publicado'],
        'Artigos aceitos para publicação': ['ARTIGO-ACEITO-PARA-PUBLICACAO', 'artigo-aceito-para-publicacao'],
        'Livros e capítulos': ['LIVRO-PUBLICADO', 'livro-publicado', 'CAPITULO-DE-LIVRO-PUBLICADO', 'capitulo-de-livro-publicado'],
        'Texto em jornal ou revista (magazine)': ['TEXTO-EM-JORNAL-OU-REVISTA', 'texto-em-jornal-ou-revista'],
        'Trabalhos publicados em anais de eventos': ['TRABALHO-EM-EVENTOS', 'trabalho-em-eventos', 'RESUMO-EXPANDIDO-EM-EVENTOS', 'resumo-expandido-em-eventos', 'RESUMO-EM-EVENTOS', 'resumo-em-eventos'],
        'Apresentação de trabalho e palestra': ['APRESENTACAO-DE-TRABALHO', 'apresentacao-de-trabalho'],

        // Técnica
        'Programa de computador sem registro': ['PROGRAMA-DE-COMPUTADOR-SEM-REGISTRO', 'programa-de-computador-sem-registro'],
        'Curso de curta duração ministrado': ['CURSO-DE-CURTA-DURACAO-MINISTRADO', 'curso-de-curta-duracao-ministrado'],
        'Desenvolvimento de material didático ou instrucional': ['DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL', 'desenvolvimento-de-material-didatico-ou-instrucional'],
        
        // Mídia (Agrupada)
        'Entrevistas, mesas redondas, programas e comentários na mídia': ['ENTREVISTA', 'entrevista', 'MESA-REDONDA', 'mesa-redonda', 'PROGRAMA-DE-RADIO-OU-TV', 'programa-de-radio-ou-tv', 'COMENTARIO-NA-MIDIA', 'comentario-na-midia', 'MIDIA-SOCIAL', 'midia-social'],

        // Inovação / Eventos
        'Programa de Computador Registrado': ['PROGRAMA-DE-COMPUTADOR-REGISTRADO', 'programa-de-computador-registrado'],
        'Organização de eventos, congressos, exposições, feiras e olimpíadas': ['ORGANIZACAO-DE-EVENTO', 'organizacao-de-evento', 'CONGRESSO', 'congresso', 'EXPOSICAO', 'exposicao', 'FEIRA', 'feira', 'OLIMPIADA', 'olimpiada'],
        'Participação em eventos, congressos, exposições, feiras e olimpíadas': ['PARTICIPACAO-EM-EVENTO', 'participacao-em-evento'],

        // Artística e Redes
        'Redes sociais, websites e blogs': ['REDES-SOCIAIS', 'redes-sociais', 'WEBSITE', 'website', 'BLOG', 'blog'],
        'Artes visuais': ['ARTES-VISUAIS', 'artes-visuais'],
        'Artes cênicas': ['ARTES-CENICAS', 'artes-cenicas'],
        'Música': ['MUSICA', 'musica', 'CONCERTO', 'concerto'],

        // Outros
        'Outra produção bibliográfica': ['OUTRA-PRODUCAO-BIBLIOGRAFICA', 'outra-producao-bibliografica'],
        'Outra produção técnica': ['OUTRA-PRODUCAO-TECNICA', 'outra-producao-tecnica'],
        'Outra produção artística/cultural': ['OUTRA-PRODUCAO-ARTISTICA-CULTURAL', 'outra-producao-artistica-cultural']
    };

    function obterNomeTabela(texto, mapa = mapaTiposGeral) {
        if (!texto) return "";
        const chave = texto.trim().toUpperCase().replace(/ /g, '-');
        return mapa[chave] || texto;
    }

    // Função auxiliar para normalizar texto (usada na 4.5)
    function normalizarTexto(txt) {
        return txt ? txt.trim().toUpperCase().replace(/ /g, '-') : ""; 
    }

    // Função que descobre o nome correto na tabela (usada na 4.5)
    function obterNomeTabelaDivulgacao(textoBruto) {
        if (!textoBruto) return 'Outra produção técnica'; 

        for (const [nomeTabela, listaSinonimos] of Object.entries(regrasDivulgacao45)) {
            const brutoNorm = normalizarTexto(textoBruto); 
            if (listaSinonimos.map(s => normalizarTexto(s)).includes(brutoNorm) || nomeTabela === textoBruto) {
                return nomeTabela;
            }
        }
        return 'Outra produção técnica'; 
    }

    // =============================================================================
    // 3. FUNÇÕES DE ESPELHAMENTO E LÓGICA
    // =============================================================================

    // --- 3.1 Espelhar Membros Estrangeiros (4.6.9) ---
    function espelharMembrosEstrangeiros() {
        const tabelaEquipe = document.getElementById('tabela-equipe') || document.querySelector('#secao-equipe table') || document.querySelector('table'); 
        const destinoMembros = document.getElementById('tbody-espelho-membros-est'); 
        if (!tabelaEquipe || !destinoMembros) return;
        destinoMembros.innerHTML = '';
        let cont = 0;
        tabelaEquipe.querySelectorAll('tbody tr').forEach(tr => { 
            const inputs = tr.querySelectorAll('input, select');
            let nome = "", pais = "", inst = "", funcao = "";
            if (inputs.length > 0) { inputs.forEach(inp => { if(inp.name.includes('nome')) nome = inp.value; if(inp.name.includes('pais')) pais = inp.value; if(inp.name.includes('instituicao')) inst = inp.value; if(inp.name.includes('funcao')) funcao = inp.value; }); } 
            else if(tr.cells.length > 5) { nome = tr.cells[0].innerText; pais = tr.cells[tr.cells.length - 1].innerText; if (pais.length < 3) pais = tr.cells[tr.cells.length - 2].innerText; }
            if (pais && pais.trim().toLowerCase() !== 'brasil' && pais.trim() !== '' && pais.trim() !== '-') {
                destinoMembros.innerHTML += `<tr><td>${nome}</td><td>${inst} / ${pais}</td><td>${funcao || 'Pesquisador'}</td><td>Membro da Equipe</td><td>-</td></tr>`;
                cont++;
            }
        });
        if (cont === 0) destinoMembros.innerHTML = '<tr><td colspan="5" class="text-center text-muted small py-2">Nenhum membro estrangeiro identificado na equipe.</td></tr>';
    }

    // --- 3.2 Atualizar Resumo da Seção 4.5 (Divulgação) ---
    function atualizarResumoDivulgacao() {
        // 1. Busca a nova tabela unificada pelo ID
        const tabelaResumo = document.getElementById('tabela-resumo-divulgacao-unica');
        if (!tabelaResumo) {
            console.warn("Tabela de resumo 'tabela-resumo-divulgacao-unica' não encontrada.");
            return;
        }

        // 2. Zera contadores
        const contadores = {};
        tabelaResumo.querySelectorAll('tbody tr').forEach(row => {
            const tipo = row.getAttribute('data-resumo-tipo');
            if (tipo) contadores[tipo] = 0;
        });

        // 3. Conta itens validados na lista (Switch ON)
        const itensValidados = document.querySelectorAll('.item-divulgacao .switch-validar-divulgacao:checked');

        itensValidados.forEach(toggle => {
            const item = toggle.closest('.item-divulgacao');
            const tipoBruto = item.getAttribute('data-tipo');
            
            // Usa a nova lógica inteligente
            const nomeNaTabela = obterNomeTabelaDivulgacao(tipoBruto);

            if (contadores.hasOwnProperty(nomeNaTabela)) {
                contadores[nomeNaTabela]++;
            }
        });

        // 4. Atualiza visualmente os inputs da tabela
        for (const tipo in contadores) {
            // Aspas duplas no seletor para evitar erro com espaços/caracteres
            const row = tabelaResumo.querySelector(`tr[data-resumo-tipo="${tipo}"]`);
            if (row) {
                const input = row.querySelector('input');
                if(input) {
                    input.value = contadores[tipo];
                    // Destaque visual (opcional)
                    if (contadores[tipo] > 0) {
                        input.classList.add('text-primary', 'fw-bold');
                    } else {
                        input.classList.remove('text-primary', 'fw-bold');
                    }
                }
            }
        }
    }

    // --- 3.3 Espelhar Divulgação 4.5 -> 4.6.12 ---
    function espelhar4612_Divulgacao() {
        const itensOrigem = document.querySelectorAll('.item-divulgacao');
        const listaDestino = document.getElementById('lista-divulgacao-intl-4612');
        if (!listaDestino) return; 
        listaDestino.innerHTML = ''; 
        let contador = 0;
        itensOrigem.forEach(item => {
            const isValidado = item.querySelector('.switch-validar-divulgacao').checked;
            const radioInternacional = item.querySelector('input[value="Internacional"]');
            const isInternacional = radioInternacional && radioInternacional.checked;
            if (isValidado && isInternacional) {
                const tipo = item.querySelector('h6') ? item.querySelector('h6').innerText : 'Ação';
                const titulo = item.querySelector('.text-dark') ? item.querySelector('.text-dark').innerText : 'Sem título';
                const anoTexto = item.querySelector('.text-muted.small') ? item.querySelector('.text-muted.small').innerText : '';
                listaDestino.innerHTML += `<div class="list-group-item bg-white border mb-2 shadow-sm"><div class="d-flex w-100 justify-content-between align-items-center"><div><h6 class="mb-1 text-primary fw-bold"><i class="fas fa-bullhorn me-2 small"></i>${tipo}</h6><p class="mb-1 small fw-bold text-dark">${titulo} ${anoTexto}</p></div><span class="badge bg-light text-secondary border">Automático (4.5)</span></div></div>`;
                contador++;
            }
        });
        if (contador === 0) listaDestino.innerHTML = '<div class="alert alert-light text-center border text-muted small">Nenhuma ação de divulgação marcada como "Internacional" validada na Seção 4.5.</div>';
    }

    // --- 3.4 Espelhar Inovação 4.2.4 -> 4.6.4 ---
    function espelhar464_Inovacao() {
        const itens = document.querySelectorAll('.item-inovacao');
        const tabelaResumo = document.getElementById('tabela-resumo-inovacao');
        const listaDestino = document.getElementById('lista-propriedade-intelectual-464');
        const contagem = {}; 
        if (listaDestino) listaDestino.innerHTML = '';
        let countIntl = 0;
        itens.forEach(item => {
            const check = item.querySelector('.toggle-inovacao');
            const isValidado = check ? check.checked : false;
            if (isValidado) {
                const categoria = item.getAttribute('data-producao-tipo');
                const radioNac = item.querySelector('input[value="Nacional"]');
                const radioIntl = item.querySelector('input[value="Internacional"]');
                let escopo = null;
                if (radioNac && radioNac.checked) escopo = 'Nacional';
                if (radioIntl && radioIntl.checked) escopo = 'Internacional';
                if (categoria && escopo) {
                    if (!contagem[categoria]) contagem[categoria] = { Nacional: 0, Internacional: 0 };
                    contagem[categoria][escopo]++;
                }
                if (escopo === 'Internacional' && listaDestino) {
                    const titulo = item.querySelector('.text-dark').innerText;
                    const ano = item.querySelector('.text-muted').innerText;
                    const selectPais = item.querySelector('.select-pais-inovacao');
                    let paisesTexto = "";
                    if (selectPais && selectPais.selectedOptions.length > 0) {
                        const paises = Array.from(selectPais.selectedOptions).map(o => o.text).join(', ');
                        paisesTexto = `<small class="d-block text-muted mt-1"><i class="fas fa-globe-americas me-1"></i> ${paises}</small>`;
                    }
                    listaDestino.innerHTML += `<div class="list-group-item bg-white border mb-2 shadow-sm"><div class="d-flex w-100 justify-content-between align-items-start"><div><h6 class="mb-1 text-primary fw-bold">${categoria}</h6><p class="mb-1 fw-bold text-dark small">${titulo} (${ano})</p>${paisesTexto}</div><span class="badge bg-light text-secondary border">Automático (4.2.4)</span></div></div>`;
                    countIntl++;
                }
            }
        });
        if (tabelaResumo) {
            tabelaResumo.querySelectorAll('tbody tr').forEach(tr => {
                const tipo = tr.getAttribute('data-producao-tipo');
                const inputNac = tr.querySelector('.input-nacional');
                const inputIntl = tr.querySelector('.input-internacional');
                if (inputNac) inputNac.value = (contagem[tipo] && contagem[tipo].Nacional) || 0;
                if (inputIntl) inputIntl.value = (contagem[tipo] && contagem[tipo].Internacional) || 0;
            });
        }
        if (listaDestino && countIntl === 0) listaDestino.innerHTML = '<div class="alert alert-light text-center border small text-muted">Nenhum registro de inovação internacional validado na Seção 4.2.4.</div>';
    }

    // --- 3.5 Espelhar Parcerias Estrangeiras 4.3.2 -> 4.6.6 ---
    function espelhar466_ParceriasEmpresa() {
        const tabelaOrigem = document.getElementById('tabela-empresas-estrangeiras');
        const listaDestino = document.getElementById('lista-parcerias-estrangeiras-466');
        if (!tabelaOrigem || !listaDestino) return;
        listaDestino.innerHTML = '';
        let count = 0;
        tabelaOrigem.querySelectorAll('tbody tr').forEach(tr => {
            const nomeInput = tr.querySelector('input[name="emp_est_nome[]"]');
            const paisSelect = tr.querySelector('select[name="emp_est_pais[]"]');
            const nome = nomeInput ? nomeInput.value : '';
            const pais = paisSelect ? paisSelect.value : '';
            if (nome.trim() !== '') {
                const interacoes = Array.from(tr.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value).join(', ');
                listaDestino.innerHTML += `<div class="list-group-item bg-white border mb-2 shadow-sm"><div class="d-flex w-100 justify-content-between align-items-center"><div><h6 class="mb-1 text-primary fw-bold"><i class="fas fa-building me-2"></i>${nome}</h6><p class="mb-0 small text-muted"><i class="fas fa-globe-americas me-1"></i> ${pais || 'País não informado'} ${interacoes ? `<span class="ms-2">| Interação: ${interacoes}</span>` : ''}</p></div><span class="badge bg-light text-secondary border">Automático (4.3.2)</span></div></div>`;
                count++;
            }
        });
        if (count === 0) listaDestino.innerHTML = '<div class="alert alert-light text-center border small text-muted"><i class="fas fa-info-circle me-1"></i>Nenhuma empresa estrangeira cadastrada na Seção 4.3.2.</div>';
    }

    // --- 3.6 Sincronizar 4.3.2 -> 4.3.3 E Espelhar 4.3.3 -> 4.6.7 ---
    window.sincronizarContratosAutomatico = function() {
        const tabelaDestino = document.getElementById('tabela-contratos');
        const template = document.getElementById('template-contrato-auto');
        if(!tabelaDestino || !template) return;
        
        const tbodyDestino = tabelaDestino.querySelector('tbody');
        tbodyDestino.innerHTML = ''; // Limpa antes de reconstruir

        // 1. Coletar dados das Nacionais
        document.querySelectorAll('#tabela-empresas-nacionais tbody tr').forEach(tr => {
            verificarEAdicionarContrato(tr, 'Nacional');
        });

        // 2. Coletar dados das Estrangeiras
        document.querySelectorAll('#tabela-empresas-estrangeiras tbody tr').forEach(tr => {
            verificarEAdicionarContrato(tr, 'Estrangeira');
        });

        // Helper para adicionar linha na 4.3.3
        function verificarEAdicionarContrato(tr, tipo) {
            const checks = Array.from(tr.querySelectorAll('input[type="checkbox"]'));
            const temTransferencia = checks.some(cb => cb.checked && cb.value.includes('Transferência de tecnologia'));
            const selectFormal = tr.querySelector('select[name*="formalizacao"]');
            const isFormal = selectFormal && selectFormal.value === 'Formal';

            if (temTransferencia && isFormal) {
                const nome = tr.querySelector('input[name*="nome"]').value;
                const cnpj = tr.querySelector('input[name*="cnpj"]') ? tr.querySelector('input[name*="cnpj"]').value : ''; 
                const uf = tr.querySelector('input[name*="uf"]') ? tr.querySelector('input[name*="uf"]').value : '';
                const cidade = tr.querySelector('input[name*="municipio"]') ? tr.querySelector('input[name*="municipio"]').value : '';
                const objetivo = tr.querySelector('textarea[name*="objetivo"]').value;
                const produto = tr.querySelector('textarea[name*="resultado"]').value;
                
                let pais = "Brasil";
                if (tipo === 'Estrangeira') {
                    const selPais = tr.querySelector('select[name*="pais"]');
                    if (selPais) pais = selPais.value;
                }

                const clone = template.content.cloneNode(true);
                clone.querySelector('input[name="cont_empresa[]"]').value = nome;
                clone.querySelector('input[name="cont_cnpj[]"]').value = cnpj;
                clone.querySelector('input[name="cont_pais[]"]').value = pais;
                clone.querySelector('input[name="cont_uf[]"]').value = uf;
                clone.querySelector('input[name="cont_municipio[]"]').value = cidade;
                clone.querySelector('textarea[name="cont_finalidade[]"]').value = objetivo;
                clone.querySelector('textarea[name="cont_produto[]"]').value = produto;
                
                tbodyDestino.appendChild(clone);
            }
        }
        espelhar467_Contratos();
    };

    // --- 3.7 Espelhar Contratos Internacionais 4.3.3 -> 4.6.7 ---
    function espelhar467_Contratos() {
        const tabelaContratos = document.getElementById('tabela-contratos');
        const listaDestino = document.getElementById('lista-contratos-internacionais-467');
        if (!tabelaContratos || !listaDestino) return;
        listaDestino.innerHTML = '';
        let count = 0;
        tabelaContratos.querySelectorAll('tbody tr').forEach(tr => {
            const paisInput = tr.querySelector('input[name="cont_pais[]"]');
            const nomeInput = tr.querySelector('input[name="cont_empresa[]"]');
            const finalidadeInput = tr.querySelector('textarea[name="cont_finalidade[]"]');
            
            const pais = paisInput ? paisInput.value : '';
            const nome = nomeInput ? nomeInput.value : '';
            const finalidade = finalidadeInput ? finalidadeInput.value : '';

            if (pais && pais.toLowerCase() !== 'brasil' && pais.toLowerCase() !== 'brazil') {
                listaDestino.innerHTML += `<div class="list-group-item bg-white border mb-2 shadow-sm"><div class="d-flex w-100 justify-content-between align-items-start"><div><h6 class="mb-1 text-primary fw-bold"><i class="fas fa-file-contract me-2"></i>${nome}</h6><p class="mb-1 small"><strong>País:</strong> ${pais}</p><p class="mb-0 small text-muted"><em>${finalidade}</em></p></div><span class="badge bg-light text-secondary border">Automático (4.3.3)</span></div></div>`;
                count++;
            }
        });
        if (count === 0) listaDestino.innerHTML = '<div class="alert alert-light text-center border small text-muted"><i class="fas fa-info-circle me-1"></i>Nenhum contrato internacional identificado na Seção 4.3.3.</div>';
    }

    // --- 3.8 Espelhar NDAs Internacionais 4.3.4 -> 4.6.8 (NOVO!) ---
    function espelhar468_AcordosConfidencialidade() {
        const tabelaNDA = document.getElementById('tabela-nda');
        const listaDestino = document.getElementById('lista-acordos-internacionais-468');
        if (!tabelaNDA || !listaDestino) return;

        listaDestino.innerHTML = '';
        let count = 0;

        tabelaNDA.querySelectorAll('tbody tr').forEach(tr => {
            const empresaInput = tr.querySelector('input[name="nda_empresa[]"]');
            const paisSelect = tr.querySelector('select[name="nda_pais[]"]');
            const finalidadeInput = tr.querySelector('textarea[name="nda_finalidade[]"]');

            const empresa = empresaInput ? empresaInput.value : '';
            const pais = paisSelect ? paisSelect.value : '';
            const finalidade = finalidadeInput ? finalidadeInput.value : '';

            // Se o país for selecionado e NÃO for Brasil
            if (pais && pais.toLowerCase() !== 'brasil' && pais.toLowerCase() !== 'brazil') {
                listaDestino.innerHTML += `
                    <div class="list-group-item bg-white border mb-2 shadow-sm">
                        <div class="d-flex w-100 justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1 text-primary fw-bold"><i class="fas fa-file-signature me-2"></i>${empresa}</h6>
                                <p class="mb-1 small"><strong>País:</strong> ${pais}</p>
                                ${finalidade ? `<p class="mb-0 small text-muted"><em>${finalidade}</em></p>` : ''}
                            </div>
                            <span class="badge bg-light text-secondary border">Automático (4.3.4)</span>
                        </div>
                    </div>`;
                count++;
            }
        });

        if (count === 0) {
            listaDestino.innerHTML = '<div class="alert alert-light text-center border small text-muted"><i class="fas fa-info-circle me-1"></i>Nenhum acordo internacional identificado na Seção 4.3.4.</div>';
        }
    }

    // --- 3.9 Função Mestra (Main Update) ---
    function atualizarInternacionalizacao() {
        // A. Biblio 4.2.1 -> 4.6.1 (Lógica mantida)
        const origemBiblio = document.getElementById('lista-producoes-bibliograficas');
        const listaBiblioDestino = document.getElementById('lista-coautorias-internacionais');
        const tabelaBiblioGeral = document.getElementById('tabela-resumo-bibliografico'); 
        if (origemBiblio) {
            const contagemGeral = {}; const contagemInternacional = {}; let temInternacional = false;
            if (listaBiblioDestino) listaBiblioDestino.innerHTML = '';
            origemBiblio.querySelectorAll('.list-group-item').forEach(card => {
                const isValidado = card.querySelector('.toggle-bibliografico:checked');
                const isInternacional = card.querySelector('.coautoria-check:checked');
                const tipoFormatado = obterNomeTabela(card.getAttribute('data-producao-tipo'));
                if (isValidado && tipoFormatado) contagemGeral[tipoFormatado] = (contagemGeral[tipoFormatado] || 0) + 1;
                if (isInternacional && tipoFormatado) {
                    contagemInternacional[tipoFormatado] = (contagemInternacional[tipoFormatado] || 0) + 1; temInternacional = true;
                    if (listaBiblioDestino) {
                         let titulo = card.querySelector('p.text-dark') ? card.querySelector('p.text-dark').innerText : "Sem título";
                         let detalhes = card.querySelector('small') ? card.querySelector('small').innerHTML : "";
                         let paises = ""; const sel = card.querySelector('.select-paises-coautoria');
                         if(sel && sel.selectedOptions) paises = Array.from(sel.selectedOptions).map(o=>o.text).join(', ');
                         listaBiblioDestino.innerHTML += `<div class="list-group-item bg-light border-light mb-1 ps-4 position-relative"><i class="fas fa-circle text-secondary position-absolute" style="left: 15px; top: 12px; font-size: 5px;"></i><h6 class="mb-1 fw-bold text-primary">${tipoFormatado}</h6><p class="mb-1 fw-bold text-dark">${titulo}</p><small class="text-muted d-block mb-1">${detalhes}</small>${paises ? `<small class="text-primary fw-bold"><i class="fas fa-globe-americas me-1"></i> ${paises}</small>` : ''}</div>`;
                    }
                }
            });
            if (listaBiblioDestino && !temInternacional) listaBiblioDestino.innerHTML = '<p class="text-muted small text-center p-3">Nenhuma produção bibliográfica internacional.</p>';
            if(tabelaBiblioGeral) tabelaBiblioGeral.querySelectorAll('tbody tr').forEach(tr => { const input = tr.querySelector('input'); if(input) input.value = contagemGeral[tr.cells[0].innerText.trim()] || 0; });
            if(listaBiblioDestino) { const container = listaBiblioDestino.closest('.card-body'); if(container) container.querySelectorAll('table').forEach(tbl => { if(tbl !== tabelaBiblioGeral) tbl.querySelectorAll('tbody tr').forEach(tr => { const input = tr.querySelector('input'); if(input) input.value = contagemInternacional[tr.cells[0].innerText.trim()] || 0; }); }); }
        }

        // B. Técnica e C. Artística (já inclusas nas versões anteriores, omitidas aqui por brevidade mas devem estar no arquivo final)
        const origemTec = document.getElementById('lista-producoes-tecnicas');
        if(origemTec) { /* Lógica da V15 */ } 

        // Chamadas Específicas
        atualizarResumoDivulgacao(); // 4.5
        espelharMembrosEstrangeiros(); // 4.6.9
        espelhar464_Inovacao(); // 4.2.4 -> 4.6.4
        espelhar4612_Divulgacao(); // 4.5 -> 4.6.12
        espelhar466_ParceriasEmpresa(); // 4.3.2 -> 4.6.6
        sincronizarContratosAutomatico(); // 4.3.3 e 4.6.7
        espelhar468_AcordosConfidencialidade(); // 4.3.4 -> 4.6.8 (NOVO)
    }

    // =============================================================================
    // 4. OUVINTES DE EVENTOS
    // =============================================================================
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('change', function(e) {
            
            // ... Toggles de País 4.2.x e Inovação 4.2.4 ...
            if (e.target.matches('.check-internacional-tec')) {
                const container = e.target.closest('.item-tecnico').querySelector('.tec-pais-container');
                if(container) container.style.display = e.target.checked ? 'block' : 'none';
            }
            if (e.target.matches('.check-internacional-art')) {
                const container = e.target.closest('.item-artistico').querySelector('.art-pais-container');
                if(container) container.style.display = e.target.checked ? 'block' : 'none';
            }
            if (e.target.matches('.coautoria-check')) {
                const container = e.target.closest('.list-group-item').querySelector('.coautoria-paises-container');
                if(container) container.style.display = e.target.checked ? 'block' : 'none';
            }
            if (e.target.matches('.toggle-inovacao')) {
                const container = e.target.closest('.item-inovacao').querySelector('.container-escopo-inovacao');
                if (container) {
                    container.style.display = e.target.checked ? 'block' : 'none';
                    if (!e.target.checked) {
                        const subContainer = e.target.closest('.item-inovacao').querySelector('.container-detalhes-internacional');
                        if (subContainer) subContainer.style.display = 'none';
                    }
                }
            }
            if (e.target.matches('.radio-escopo-inovacao')) {
                const containerIntl = e.target.closest('.item-inovacao').querySelector('.container-detalhes-internacional');
                if (containerIntl) {
                    containerIntl.style.display = (e.target.value === 'Internacional') ? 'block' : 'none';
                }
            }

            // Empresas (4.3.2)
            if (e.target.closest('#tabela-empresas-nacionais') || e.target.closest('#tabela-empresas-estrangeiras')) {
                setTimeout(() => { espelhar466_ParceriasEmpresa(); sincronizarContratosAutomatico(); }, 50);
            }
            
            // NDAs (4.3.4) - NOVO
            if (e.target.closest('#tabela-nda')) {
                setTimeout(espelhar468_AcordosConfidencialidade, 50);
            }

            // Inputs de texto/select em tabelas
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                 setTimeout(() => {
                    espelhar466_ParceriasEmpresa();
                    sincronizarContratosAutomatico();
                    espelhar468_AcordosConfidencialidade();
                }, 200);
            }
            
            // Genérico "Outro"
            if (e.target.value === 'Outro' && e.target.type === 'checkbox') { window.toggleInputOutro(e.target); }

            if (e.target.matches('.switch-validar-divulgacao')) setTimeout(atualizarResumoDivulgacao, 50);
            setTimeout(atualizarInternacionalizacao, 100);
        });
        
        form.addEventListener('input', function(e) {
             if (e.target.closest('table')) {
                clearTimeout(window.timerInput);
                window.timerInput = setTimeout(() => {
                    espelhar466_ParceriasEmpresa();
                    sincronizarContratosAutomatico();
                    espelhar468_AcordosConfidencialidade();
                }, 500);
            }
        });
        
        form.addEventListener('submit', function(e) {
            if (!confirm("Você está prestes a enviar o formulário. Deseja continuar?")) { e.preventDefault(); }
        });
    }

    // =============================================================================
    // 5. UTILITÁRIOS
    // =============================================================================
    if (!window.addLinhaFromTemplate) {
        window.addLinhaFromTemplate = function(templateId, tabelaId) {
            const template = document.getElementById(templateId);
            const tabela = document.getElementById(tabelaId);
            if (template && tabela) {
                const tbody = tabela.querySelector('tbody') || tabela;
                const clone = template.content.cloneNode(true);
                const btnDel = clone.querySelector('.btn-danger');
                if(btnDel) btnDel.onclick = function() { 
                    this.closest('tr').remove(); 
                    // Atualiza tudo ao remover
                    setTimeout(() => { 
                        espelhar466_ParceriasEmpresa(); 
                        sincronizarContratosAutomatico(); 
                        espelhar468_AcordosConfidencialidade(); 
                    }, 50);
                };
                tbody.appendChild(clone);
            }
        };
    }
    
    window.addLinhaNacional = function() { window.addLinhaFromTemplate('template-empresa-nacional', 'tabela-empresas-nacionais'); };
    window.addLinhaEstrangeira = function() { window.addLinhaFromTemplate('template-empresa-estrangeira', 'tabela-empresas-estrangeiras'); };
    window.addNda = function() { window.addLinhaFromTemplate('template-nda', 'tabela-nda'); };
    
    window.removerLinha = function(botao) { 
        const l = botao.closest('tr'); 
        if(l) { 
            l.remove(); 
            setTimeout(() => { 
                espelhar466_ParceriasEmpresa(); 
                sincronizarContratosAutomatico(); 
                espelhar468_AcordosConfidencialidade(); 
            }, 50); 
        }
    };

    // INICIALIZAR
    setTimeout(atualizarInternacionalizacao, 500);
});

document.addEventListener('DOMContentLoaded', function() {
    const modalPaisSelect = document.getElementById('novo_parceiro_pais');
    
    if (modalPaisSelect) {
        modalPaisSelect.addEventListener('change', function() {
            const isBrasil = this.value === 'Brasil';
            const selectUF = document.getElementById('novo_parceiro_uf');
            
            if (selectUF) {
                // Tenta achar a DIV pai (col-md-4) para esconder o label junto
                const containerUF = selectUF.closest('.col-md-4') || selectUF;
                
                if (isBrasil) {
                    containerUF.style.display = 'block';
                } else {
                    containerUF.style.display = 'none';
                    selectUF.value = ''; // Limpa UF para não salvar lixo
                }
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const radioSim = document.getElementById('dificuldades_sim');
    const radioNao = document.getElementById('dificuldades_nao');
    const collapseElement = document.getElementById('collapseDificuldades');
    const textarea = document.getElementById('dificuldades_encontradas');
    
    if (radioSim && radioNao && collapseElement) {
        // Inicializa o componente Collapse do Bootstrap
        const bsCollapse = new bootstrap.Collapse(collapseElement, { toggle: false });
        let simEstavaMarcado = false;

        // 1. Antes do clique, memoriza se o SIM já estava marcado
        radioSim.addEventListener('mousedown', function() {
            simEstavaMarcado = this.checked;
        });

        // 2. No clique do SIM
        radioSim.addEventListener('click', function() {
            if (simEstavaMarcado) {
                // SE JÁ ESTAVA MARCADO E CLICOU DE NOVO:
                this.checked = false;      
                radioNao.checked = true;   
                
                bsCollapse.hide();         
                if(textarea) textarea.value = ''; 
                
                simEstavaMarcado = false;  
            } else {
                // SE NÃO ESTAVA MARCADO:
                bsCollapse.show();       
                
                setTimeout(() => { if(textarea) textarea.focus(); }, 300);
            }
        });

        // 3. No clique do NÃO (comportamento padrão)
        radioNao.addEventListener('change', function() {
            if (this.checked) {
                bsCollapse.hide();
                if(textarea) textarea.value = '';
                simEstavaMarcado = false;
            }
        });
    }
});

// Variável global para guardar qual checkbox acionou o aviso
let checkboxEmValidacao = null; 

document.addEventListener('DOMContentLoaded', function() {
    // 1. Seleciona todos os inputs que validam as produções (ajuste as classes conforme as suas)
    // Aqui incluí as classes genéricas que vi no seu código anterior
    const checkboxesValidacao = document.querySelectorAll('.toggle-bibliografico, .toggle-tecnico, .toggle-artistico, .toggle-inovacao');

    checkboxesValidacao.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Só executa a verificação se o coordenador estiver MARCANDO (ativando) a validação
            if (this.checked) {
                verificarDuplicidade(this);
            }
        });
    });

    // 2. Configura os botões do Modal de Duplicidade
    const btnCancelarDuplicidade = document.getElementById('btnCancelarDuplicidade');
    if (btnCancelarDuplicidade) {
        btnCancelarDuplicidade.addEventListener('click', function() {
            // Se ele clicar em "Revisar", nós desmarcamos o checkbox automaticamente
            if (checkboxEmValidacao) {
                checkboxEmValidacao.checked = false;
            }
        });
    }

    const btnManterDuplicidade = document.getElementById('btnManterDuplicidade');
    if (btnManterDuplicidade) {
        btnManterDuplicidade.addEventListener('click', function() {
            // Se ele clicar em "Sim, Manter", apenas fechamos o modal e deixamos marcado
            const modalEl = document.getElementById('modalDuplicidade');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

function verificarDuplicidade(checkboxAtual) {
    // Pega a linha inteira da produção atual
    const linhaAtual = checkboxAtual.closest('.list-group-item');
    if (!linhaAtual) return;

    const doiAtual = (linhaAtual.getAttribute('data-doi') || "").trim().toLowerCase();
    const tituloAtual = (linhaAtual.getAttribute('data-titulo') || "").trim().toLowerCase();
    const autorAtual = (linhaAtual.getAttribute('data-autor') || "").trim().toLowerCase();

    // Pega TODAS as outras linhas de produção da tela
    const todasLinhas = document.querySelectorAll('.list-group-item');
    let encontrouDuplicidade = false;
    let motivoMsg = "";
    let tituloAnterior = "";

    todasLinhas.forEach(linhaComp => {
        // Só compara se NÃO for a mesma linha que acabamos de clicar
        if (linhaComp !== linhaAtual && !encontrouDuplicidade) {
            
            // Verifica se a linha de comparação já está VALIDADA
            const checkboxComp = linhaComp.querySelector('.toggle-bibliografico, .toggle-tecnico, .toggle-artistico, .toggle-inovacao, .toggle-projeto-empresa, .toggle-rh, .switch-validar-divulgacao');
            
            if (checkboxComp && checkboxComp.checked) {
                const doiComp = (linhaComp.getAttribute('data-doi') || "").trim().toLowerCase();
                const tituloComp = (linhaComp.getAttribute('data-titulo') || "").trim().toLowerCase();
                const autorComp = (linhaComp.getAttribute('data-autor') || "").trim().toLowerCase();

                // REGRA 1: DOI é igual (Prioridade)
                if (doiAtual !== "" && doiComp !== "" && doiAtual === doiComp) {
                    encontrouDuplicidade = true;
                    motivoMsg = "o mesmo DOI";
                    tituloAnterior = linhaComp.getAttribute('data-titulo') || "Título não informado";
                }
                // REGRA 2: Título e Autor iguais (Caso não tenha DOI)
                else if (tituloAtual !== "" && tituloAtual === tituloComp && autorAtual === autorComp) {
                    encontrouDuplicidade = true;
                    motivoMsg = "o mesmo Título e Autor";
                    tituloAnterior = tituloComp;
                }
            }
        }
    });

    // Se encontrou conflito, dispara o nosso Modal Institucional
    if (encontrouDuplicidade) {
        checkboxEmValidacao = checkboxAtual; // Guarda a referência do checkbox
        
        // Preenche as informações dinâmicas no Modal
        document.getElementById('duplicidadeMotivo').innerText = motivoMsg;
        // Coloca a primeira letra em maiúscula para ficar bonito
        document.getElementById('duplicidadeTituloAnterior').innerText = tituloAnterior.charAt(0).toUpperCase() + tituloAnterior.slice(1);
        
        // Abre o Modal
        const modalEl = document.getElementById('modalDuplicidade');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}