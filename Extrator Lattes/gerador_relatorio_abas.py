import pandas as pd

def gerar_excel_com_abas(caminho_arquivo):
    print(f"[*] Lendo base original: {caminho_arquivo}")
    
    try:
        # Carregamos a sua base extratada original
        df_principal = pd.read_excel(caminho_arquivo)
    except FileNotFoundError:
        print("[-] Erro: Arquivo não encontrado.")
        return

    # Definimos os grupos de colunas para cada "aba" de detalhe
    # O NUMERO-IDENTIFICADOR vai em todas para servir de chave de ligação
    abas_config = {
        'Trabalho Tecnico': ['NUMERO-IDENTIFICADOR', 'TITULO-TRABALHO-TECNICO', 'ANO-TRABALHO-TECNICO', 'TIPO-TRABALHO-TECNICO'],
        'Software': ['NUMERO-IDENTIFICADOR', 'TITULO-SOFTWARE', 'ANO-SOFTWARE', 'FLAG-REGISTRO-SOFTWARE'],
        'Patente': ['NUMERO-IDENTIFICADOR', 'TITULO-PATENTE', 'ANO-DEPOSITO-PATENTE', 'NUMERO-DEPOSITO', 'CATEGORIA-PATENTE'],
        'Transferencia Tecnologia': ['NUMERO-IDENTIFICADOR', 'TITULO-TRANSF-TECNOLOGIA', 'ANO-TRANSF-TECNOLOGIA', 'EMPRESA-RECEPTORA']
    }

    # Criamos o arquivo Excel final com múltiplas abas
    output = "Relatorio_Inova_Talentos_COMPLETO.xlsx"
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        # 1. Salva a aba Principal (do jeito que ela veio, com as barras)
        df_principal.to_excel(writer, sheet_name='Base Consolidada', index=False)
        print("[+] Aba 'Base Consolidada' criada.")

        # 2. Processa e cria cada aba de detalhe "explodida"
        for nome_aba, colunas in abas_config.items():
            # Filtramos apenas as colunas do grupo
            df_aba = df_principal[colunas].copy()
            
            # Removemos quem não tem nada preenchido nesse grupo (para a aba não ficar gigante com linhas vazias)
            coluna_titulo = colunas[1]
            df_aba = df_aba.dropna(subset=[coluna_titulo])
            df_aba = df_aba[df_aba[coluna_titulo].astype(str).str.contains(r'[a-zA-Z0-9]', na=False)]

            # Lógica de explosão (Split e Explode)
            # Isso transforma "Trabalho A | Trabalho B" em duas linhas reais
            for col in colunas[1:]: # Ignora o ID
                df_aba[col] = df_aba[col].astype(str).str.split('|')
            
            # O comando 'explode' do pandas faz a mágica de alinhar as listas perfeitamente
            df_aba = df_aba.explode(list(colunas[1:]))

            # Limpeza final dos espaços
            for col in colunas[1:]:
                df_aba[col] = df_aba[col].str.strip()

            # Salva na aba correspondente
            df_aba.to_excel(writer, sheet_name=nome_aba, index=False)
            print(f"[+] Aba '{nome_aba}' criada com {len(df_aba)} registros detalhados.")

    print("-" * 40)
    print(f"[+++] SUCESSO! O arquivo final foi gerado: {output}")

# Rodar o script
gerar_excel_com_abas('Dados Inova Talentos Extrator Lattes.xlsx')