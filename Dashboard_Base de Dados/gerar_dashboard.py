import os

# --- 1. CONFIGURAÇÃO DE IMAGENS E ÍCONES ---

LOGO_BASE64 = """data:image/png;base64,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"""

# Ícones SVG (Design System Corporativo)
ICON_DB = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>"""
ICON_LATTES = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>"""
ICON_FORM = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>"""


# --- 2. DADOS DETALHADOS (REGRAS DE NEGÓCIO DO CÓDIGO FONTE) ---
dados = {
    "col1": {
        "titulo": "PICC - PROPOSTA",
        "icon": ICON_DB,
        "cor": "#1e3a8a",
        "itens": [
            {"nome": "1. Identificação do Projeto", "status": "ORIGEM: SISTEMA", 
             "sub": [
                 "<strong>Campos Protegidos:</strong> Nome do INCT, Processo, Chamada Pública, Coordenador Responsável e Instituição Sede.",
                 "<strong>Integridade de Dados:</strong> Estas informações são carregadas diretamente da Base Institucional e exibidas em modo de leitura para garantir a fidelidade contratual.",
                 "<strong>Exceção Editável:</strong> Apenas o campo 'Sigla do Projeto' permite ajuste manual pelo pesquisador para facilitar a identificação em relatórios."
             ]},
            
            {"nome": "2. Perfil do INCT - Composição de Rede", "status": "GESTÃO DE LISTAS",
             "sub": [
                 "<strong>2.1) Alterações na Composição da Rede:</strong> O sistema apresenta a lista original de membros aprovada na proposta.",
                 "<strong>Ação de Validação:</strong> O pesquisador deve confirmar a permanência de cada membro marcando os status 'Original', 'Novo' ou 'Excluído'.",
                 "<strong>Regra de Preenchimento:</strong> Ao adicionar um novo membro, caso a função selecionada seja 'Aluno de Graduação', o sistema define automaticamente a titulação como 'Ensino Médio', agilizando o cadastro.",
                 "<strong>2.2) Articulações e Parcerias:</strong> Interface dedicada ao cadastro e gestão das instituições parceiras (Órgãos Públicos ou Organizações da Sociedade Civil)."
             ]},
            
            {"nome": "3. Aspectos Gerenciais (Orçamento Aprovado)", "status": "ORIGEM: SISTEMA",
             "sub": [
                 "<strong>3.1) Execução Financeira:</strong> Exibição consolidada dos valores de 'Total Aprovado' para todas as rubricas (Custeio, Capital e Bolsas) e fontes (CNPq, CAPES, FAPs).",
                 "<strong>Função de Controle:</strong> Estes valores atuam como teto orçamentário para as regras de validação aplicadas na coluna de preenchimento, impedindo inconsistências financeiras."
             ]},

            {"nome": "5. Alcance de Metas e Objetivos (Cronograma)", "status": "ORIGEM: SISTEMA",
             "sub": [
                 "Importação automática das metas e objetivos estratégicos definidos no cronograma original do projeto.",
                 "Estes dados formam a estrutura base para a tabela de acompanhamento de progresso, garantindo que o monitoramento esteja alinhado ao planejado."
             ]}
        ]
    },
    "col2": {
        "titulo": "PICC - CURRÍCULO LATTES",
        "icon": ICON_LATTES,
        "cor": "#ca8a04",
        "itens": [
            {"nome": "4.2.1) Produção Bibliográfica", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "O sistema realiza a leitura inteligente do Currículo Lattes do coordenador e lista as produções do período.",
                 "<strong>Ação de Curadoria:</strong> O pesquisador utiliza a chave de seleção 'Validar' para confirmar os itens pertinentes ao projeto.",
                 "<strong>Lógica de Internacionalização:</strong> Ao marcar uma produção como 'Coautoria Internacional', o sistema habilita automaticamente o campo para seleção múltipla dos países envolvidos.",
                 "<strong>Consolidação:</strong> Os itens validados alimentam instantaneamente o quadro resumo quantitativo."
             ]},
            
            {"nome": "4.2.2) Produção Técnica", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Importação automática de produtos técnicos e tecnológicos.",
                 "Requer validação unitária. O sistema permite a classificação da abrangência (Nacional ou Exterior), dado essencial para os indicadores de internacionalização."
             ]},

            {"nome": "4.2.3) Produção Artística/Cultural", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Listagem de produções artísticas importadas do Lattes.",
                 "Validação manual necessária para inclusão no relatório de atividades, com opção de marcação de coautoria internacional."
             ]},
             
            {"nome": "4.2.4) Resultados de inovação e com potencial inovador", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Identificação visual automática de itens com 'Potencial Inovador Declarado'.",
                 "<strong>Regra de Negócio:</strong> Se o escopo for definido como 'Internacional', o sistema exige o preenchimento detalhado dos países de depósito ou registro."
             ]},

            {"nome": "4.3.1) Projetos Desenvolvidos em Parceria com Empresas", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Importação de projetos cooperativos listados na aba 'Inovação' do Lattes.",
                 "O sistema solicita a validação obrigatória do escopo da parceria (Nacional ou Internacional) para correta classificação nos relatórios."
             ]},
            
            {"nome": "4.4 Formação de Recursos Humanos", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Listagem completa de orientações (IC, Mestrado, Doutorado, Pós-Doc) extraída do Lattes.",
                 "<strong>Cálculo Automático:</strong> O sistema processa as datas de início e fim para segregar automaticamente as orientações 'Em andamento' das 'Concluídas', gerando a tabela estatística consolidada."
             ]},

             {"nome": "4.5 Educação, Divulgação e Popularização de CT&I", "status": "VALIDAÇÃO REQUERIDA",
             "sub": [
                 "Validação de ações de divulgação científica extraídas do Lattes.",
                 "<strong>Enriquecimento de Dados:</strong> Permite a seleção detalhada do Público-Alvo e da Abrangência, qualificando o impacto social do projeto."
             ]}
        ]
    },
    "col3": {
        "titulo": "PREENCHIMENTO MANUAL - PESQUISADOR",
        "icon": ICON_FORM,
        "cor": "#15803d",
        "itens": [
            {"nome": "3.1) Execução Financeira (Prestação)", "status": "CÁLCULO E VALIDAÇÃO",
             "sub": [
                 "<strong>Total Pago:</strong> Inserção manual do valor efetivamente recebido.",
                 "<strong>Validação Crítica:</strong> O sistema monitora a entrada de dados e bloqueia o salvamento caso o valor informado seja superior ao 'Total Aprovado' (origem: Proposta), prevenindo inconsistências.",
                 "<strong>Total Gasto:</strong> Soma automática realizada a partir do preenchimento dos itens detalhados (Passagens, Diárias, Equipamentos, etc.).",
                 "<strong>Visualização:</strong> Barras de progresso indicam visualmente o percentual de execução e o saldo disponível."
             ]},

            {"nome": "3.2) Captação de Recursos Externos", "status": "SEÇÃO CONDICIONAL",
             "sub": [
                 "Seletor condicional 'Houve captação de recursos de outras fontes?'.",
                 "Se a resposta for 'Sim', o sistema expande a interface exibindo a tabela dinâmica para cadastro detalhado das fontes (FAPs, Empresas, Internacional) e valores."
             ]},

             {"nome": "3.3) Avaliação de Infraestrutura e Apoio", "status": "PREENCHIMENTO MANUAL",
             "sub": [
                 "Avaliação qualitativa da infraestrutura da Instituição Sede e Parceiras.",
                 "Utiliza escala de 1 a 5 e torna obrigatório o preenchimento do campo de justificativa para fundamentar a nota atribuída."
             ]},
            
            {"nome": "4.1) Mobilização e Articulação de Redes", "status": "SEÇÃO CONDICIONAL",
             "sub": [
                 "Seletor para indicar a existência de articulação com outros INCTs.",
                 "<strong>Busca Integrada:</strong> A ferramenta oferece um modal de pesquisa com filtro em tempo real sobre a base de todos os INCTs, permitindo o preenchimento automático dos dados da rede parceira selecionada."
             ]},

            {"nome": "4.3 Interação com Empresas (Detalhamento)", "status": "AUTOMAÇÃO INTELIGENTE",
             "sub": [
                 "<strong>4.3.2) Parceria com Empresas:</strong> Tabelas para cadastro manual de empresas Nacionais e Estrangeiras, com lógica de campos territoriais aplicada.",
                 "<strong>4.3.3) Contratos (Espelhamento):</strong> O sistema monitora continuamente a seção 4.3.2. Ao identificar uma parceria com 'Transferência de Tecnologia' formalizada, gera automaticamente o registro correspondente nesta tabela.",
                 "<strong>4.3.4) Contratos e Acordos (NDA):</strong> Interface para cadastro manual de acordos de sigilo."
             ]},
            
            {"nome": "4.6 Visibilidade e Cooperação Internacional", "status": "CONSOLIDAÇÃO AUTOMÁTICA",
             "sub": [
                 "Painel de inteligência que agrega automaticamente todos os itens internacionais validados:",
                 "• Produção Bibliográfica, Técnica, Artística e Divulgação (Seções 4.2 e 4.5).",
                 "• Inovação e Projetos com Empresas (Seções 4.2.4 e 4.3).",
                 "• Parcerias, Contratos e NDAs (Seção 4.3).",
                 "• Recursos Humanos e Membros Estrangeiros (Seções 4.4 e 2.1).",
                 "<strong>4.6.11) Cooperação Internacional:</strong> Única tabela desta seção que permite inserção manual (condicional)."
             ]},

            {"nome": "5. Alcance de Metas e Objetivos", "status": "CÁLCULO AUTOMÁTICO",
             "sub": [
                 "Tabela de controle interativo com barras deslizantes (0-100%) para cada meta.",
                 "<strong>Algoritmo de Progresso:</strong> O sistema calcula a média ponderada dos valores inseridos e atualiza instantaneamente os gráficos de velocímetro e as barras de progresso por missão."
             ]},

            {"nome": "6. Resultados", "status": "MATRIZ DINÂMICA",
             "sub": [
                 "Interface para relato qualitativo dos resultados.",
                 "O pesquisador descreve o impacto e utiliza uma matriz dinâmica para associá-lo a Contextos (Nacional/Intl), Dimensões e Tags dos Objetivos Específicos impactados."
             ]},

            {"nome": "7. Governança, Gestão e Comunicação Pública", "status": "PREENCHIMENTO MANUAL",
             "sub": [
                 "<strong>Dificuldades:</strong> Controle inteligente de seleção. Se 'Sim', exige descrição detalhada (limite de 2000 caracteres).",
                 "<strong>Sugestões e Divulgação:</strong> Campos de texto livre para feedback de gestão e elaboração de texto jornalístico para o público leigo."
             ]},

            {"nome": "8. Finalização e Autorização", "status": "AÇÃO FINAL",
             "sub": [
                 "Checkboxes obrigatórios para aceite dos Termos de Veracidade e Autorização de Uso de Dados.",
                 "<strong>Envio Seguro:</strong> O botão 'Enviar Formulário' aciona uma rotina de verificação, exibe um modal de confirmação definitiva e executa a submissão e travamento dos dados."
             ]}
        ]
    }
}

# --- 3. LÓGICA VISUAL (CORES E BADGES) ---

def get_badge_style(texto):
    if "ORIGEM: SISTEMA" in texto: return "#eff6ff", "#1d4ed8", "fas fa-database"
    if "PREENCHIMENTO MANUAL" in texto: return "#f3e8ff", "#7e22ce", "fas fa-pen-to-square"
    if "VALIDAÇÃO REQUERIDA" in texto: return "#fef9c3", "#a16207", "fas fa-clipboard-check"
    if "GESTÃO DE LISTAS" in texto or "MATRIZ" in texto: return "#e0e7ff", "#4338ca", "fas fa-list-ul"
    if "SEÇÃO CONDICIONAL" in texto: return "#f3f4f6", "#4b5563", "fas fa-code-branch"
    if "CÁLCULO" in texto or "PROCESSAMENTO" in texto: return "#dcfce7", "#15803d", "fas fa-calculator"
    if "AUTOMAÇÃO" in texto or "CONSOLIDAÇÃO" in texto: return "#cffafe", "#0e7490", "fas fa-sync-alt"
    if "AÇÃO FINAL" in texto: return "#0f172a", "#f8fafc", "fas fa-paper-plane"
    return "#f3f4f6", "#374151", "fas fa-circle"

def render_card(item, cor_tema):
    sub_html = ""
    if "sub" in item:
        lista_itens = "".join([f'<li class="sub-item">{sub}</li>' for sub in item["sub"]])
        sub_html = f'<ul class="sub-list">{lista_itens}</ul>'
    
    badge_html = ""
    if "status" in item:
        bg, color, icon = get_badge_style(item["status"])
        badge_html = f'<div class="card-badge" style="background-color: {bg}; color: {color}; border-color: {bg};"><i class="{icon} me-1"></i> {item["status"]}</div>'

    return f"""
    <div class="card">
        <div class="card-accent" style="background-color: {cor_tema};"></div>
        <div class="card-header">
            <span class="card-title">{item['nome']}</span>
            {badge_html}
        </div>
        {sub_html}
    </div>
    """

# --- 4. HTML TEMPLATE ---
html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento INCT - Especificação Técnica</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #f8fafc;
            --text-main: #1e293b;
            --text-secondary: #475569;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }}

        /* CABEÇALHO */
        header {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .logo-container img {{
            height: 70px;
            width: auto;
            margin-bottom: 15px;
        }}

        h1 {{
            font-weight: 800;
            font-size: 2.2rem;
            margin: 0 0 5px 0;
            color: #0f172a;
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 500;
        }}

        /* LEGENDA DETALHADA */
        .legend-container {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 50px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        .legend-title {{
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 20px;
            text-align: center;
            letter-spacing: 0.05em;
        }}

        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }}

        .legend-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            font-size: 0.8rem;
            color: #334155;
            padding: 10px;
            border-radius: 8px;
            transition: background-color 0.2s;
        }}
        
        .legend-item:hover {{
            background-color: #f1f5f9;
        }}
        
        .legend-icon-box {{
            width: 36px;
            height: 36px;
            background: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e2e8f0;
            color: #475569;
            font-size: 1.1rem;
            flex-shrink: 0;
        }}

        .legend-desc {{
            display: flex;
            flex-direction: column;
        }}
        
        .legend-name {{
            font-weight: 700;
            font-size: 0.85rem;
            color: #0f172a;
            margin-bottom: 2px;
        }}
        
        .legend-info {{
            font-size: 0.8rem;
            color: #64748b;
            line-height: 1.3;
        }}

        /* GRID SYSTEM */
        .container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            max_width: 1600px;
            margin: 0 auto;
        }}

        .column-header {{
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            padding-bottom: 15px;
            border-bottom: 3px solid;
            min-height: 50px;
        }}
        
        /* CARDS */
        .card {{
            background: white;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 24px;
            position: relative;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease-in-out;
        }}

        .card:hover {{
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
            border-color: #cbd5e1;
        }}

        .card-accent {{
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 6px;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 18px;
            gap: 10px;
            padding-bottom: 12px;
            border-bottom: 1px solid #f1f5f9;
        }}

        .card-title {{
            font-weight: 700;
            font-size: 1.05rem;
            color: #0f172a;
            line-height: 1.4;
        }}

        .card-badge {{
            font-size: 0.65rem;
            padding: 5px 10px;
            border-radius: 6px;
            font-weight: 700;
            text-transform: uppercase;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.05em;
        }}

        /* LISTAS */
        .sub-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .sub-item {{
            font-size: 0.9rem;
            color: #475569;
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
            margin-bottom: 4px;
        }}
        .sub-item:last-child {{ border-bottom: none; }}
        
        .sub-item strong {{
            color: #1e293b;
            font-weight: 600;
        }}
        
        .sub-item::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 18px;
            width: 6px;
            height: 6px;
            background-color: #cbd5e1;
            border-radius: 50%;
        }}

        footer {{
            text-align: center;
            margin-top: 80px;
            padding-top: 30px;
            border-top: 1px solid #e2e8f0;
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 500;
        }}
    </style>
</head>
<body>

    <header>
        <div class="logo-container">
            <img src="{LOGO_BASE64}" alt="Logo INCT">
        </div>
        <h1>Monitoramento de Projetos INCT</h1>
        <div class="subtitle">Especificação Técnica de Fluxo de Dados (Chamada 58/2022)</div>
    </header>

    <div class="legend-container">
        <div class="legend-title">Legenda de Funcionalidades e Status</div>
        <div class="legend-grid">
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-database text-primary"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Origem: Sistema</span>
                    <span class="legend-info">Dado imutável vindo da Base</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-clipboard-check text-warning"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Validação Requerida</span>
                    <span class="legend-info">Conferência obrigatória</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-pen-to-square text-info"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Preenchimento Manual</span>
                    <span class="legend-info">Inserção de texto/valores</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-list-ul text-secondary"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Gestão de Listas</span>
                    <span class="legend-info">Adição/remoção dinâmica</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-code-branch text-dark"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Seção Condicional</span>
                    <span class="legend-info">Exibe campos por lógica</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-calculator text-success"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Cálculo Automático</span>
                    <span class="legend-info">Processamento pelo sistema</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-sync-alt text-info"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Automação Inteligente</span>
                    <span class="legend-info">Espelhamento entre seções</span>
                </div>
            </div>
            <div class="legend-item">
                <div class="legend-icon-box"><i class="fas fa-paper-plane text-dark"></i></div>
                <div class="legend-desc">
                    <span class="legend-name">Ação Final</span>
                    <span class="legend-info">Submissão e travamento</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="column">
            <div class="column-header" style="color: {dados['col1']['cor']}; border-color: {dados['col1']['cor']};">
                {dados['col1']['icon']} {dados['col1']['titulo']}
            </div>
            {"".join([render_card(item, dados["col1"]["cor"]) for item in dados["col1"]["itens"]])}
        </div>

        <div class="column">
            <div class="column-header" style="color: {dados['col2']['cor']}; border-color: {dados['col2']['cor']};">
                {dados['col2']['icon']} {dados['col2']['titulo']}
            </div>
            {"".join([render_card(item, dados["col2"]["cor"]) for item in dados["col2"]["itens"]])}
        </div>

        <div class="column">
            <div class="column-header" style="color: {dados['col3']['cor']}; border-color: {dados['col3']['cor']};">
                {dados['col3']['icon']} {dados['col3']['titulo']}
            </div>
            {"".join([render_card(item, dados["col3"]["cor"]) for item in dados["col3"]["itens"]])}
        </div>
    </div>

    <footer>
        Documento de Especificação Técnica e Funcional • Gerado em 2024
    </footer>

</body>
</html>
"""

# --- 5. SALVAR ARQUIVO ---
nome_arquivo = "dashboard_inct_final_executivo.html"
with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Sucesso! Arquivo '{nome_arquivo}' gerado.")
try:
    os.startfile(nome_arquivo)
except:
    pass