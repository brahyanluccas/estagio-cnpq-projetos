import pandas as pd
import numpy as np

def limpar_e_expandir_lattes(caminho_arquivo):
    print(f"[*] Lendo o arquivo original: {caminho_arquivo}")
    
    try:
        df = pd.read_excel(caminho_arquivo)
    except FileNotFoundError:
        print(f"[-] Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    # Definimos os grupos de colunas que devem ser expandidos JUNTOS
    # Ajustei os nomes para baterem exatamente com o que o extrator gera
    grupos_expansao = [
        # Grupo: Trabalhos Técnicos
        ['TITULO-TRABALHO-TECNICO', 'ANO-TRABALHO-TECNICO', 'TIPO-TRABALHO-TECNICO'],
        
        # Grupo: Softwares
        ['TITULO-SOFTWARE', 'ANO-SOFTWARE', 'FLAG-REGISTRO-SOFTWARE'],
        
        # Grupo: Patentes (Ajustado para os nomes do extrator)
        ['TITULO-PATENTE', 'ANO-DEPOSITO-PATENTE', 'CATEGORIA-PATENTE', 'NUMERO-DEPOSITO'],
        
        # Grupo: Transferência de Tecnologia
        ['TITULO-TRANSF-TECNOLOGIA', 'ANO-TRANSF-TECNOLOGIA', 'EMPRESA-RECEPTORA']
    ]

    def expandir_linha(row):
        novas_rows = []
        max_itens = 1
        listas_processadas = {}

        # 1. Prepara as listas e descobre qual grupo tem mais itens
        for grupo in grupos_expansao:
            for col in grupo:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                    itens = [i.strip() for i in str(row[col]).split('|')]
                    listas_processadas[col] = itens
                    max_itens = max(max_itens, len(itens))
                else:
                    listas_processadas[col] = []

        # 2. Cria as novas linhas
        for i in range(max_itens):
            nova_row = row.copy()
            houve_mudanca = False
            
            for grupo in grupos_expansao:
                for col in grupo:
                    lista = listas_processadas[col]
                    if i < len(lista):
                        valor = lista[i]
                        # Limpeza de resíduos
                        if valor.lower() in ['nan', 'none', '//', '', 'nan | nan']:
                            nova_row[col] = ""
                        else:
                            nova_row[col] = valor
                            houve_mudanca = True
                    else:
                        nova_row[col] = ""
            
            # Só adiciona a linha se ela tiver conteúdo em algum dos campos expandidos
            if houve_mudanca:
                novas_rows.append(nova_row)
        
        # Se a pessoa não tinha nenhuma produção técnica, mantém a linha original (com vazios)
        return novas_rows if novas_rows else [row]

    print("[*] Iniciando o alinhamento das produções técnicas...")
    todas_as_linhas = []
    for _, row in df.iterrows():
        linhas_expandidas = expandir_linha(row)
        todas_as_linhas.extend(linhas_expandidas)

    df_final = pd.DataFrame(todas_as_linhas)

    # Limpeza final de strings indesejadas
    for col in df_final.columns:
        df_final[col] = df_final[col].replace(['nan', 'None', 'nan | nan', '//'], np.nan)
    
    output = "Dados_Inova_Talentos_ALINHADO.xlsx"
    df_final.to_excel(output, index=False)
    
    print("-" * 40)
    print(f"[+] Sucesso! Arquivo gerado: {output}")
    print(f"[*] Total de linhas no original: {len(df)}")
    print(f"[*] Total de linhas no alinhado: {len(df_final)}")

# EXECUÇÃO: Use o nome exato do seu arquivo aqui
limpar_e_expandir_lattes('Dados Inova Talentos Extrator Lattes.xlsx')