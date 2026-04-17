import pandas as pd

def formatar_lattes_executivo(caminho_arquivo):
    print(f"[*] Lendo o arquivo: {caminho_arquivo}")
    
    try:
        # Lemos o seu extrato original
        df = pd.read_excel(caminho_arquivo)
    except FileNotFoundError:
        print("[-] Erro: Arquivo não encontrado.")
        return

    # Lista de todas as colunas que podem ter as barras e que queremos "empilhar"
    colunas_com_barras = [
        'TITULO-TRABALHO-TECNICO', 'ANO-TRABALHO-TECNICO', 'TIPO-TRABALHO-TECNICO',
        'TITULO-SOFTWARE', 'ANO-SOFTWARE', 'FLAG-REGISTRO-SOFTWARE',
        'TITULO-PATENTE', 'ANO-DEPOSITO-PATENTE', 'NUMERO-DEPOSITO', 'CATEGORIA-PATENTE',
        'TITULO-TRANSF-TECNOLOGIA', 'ANO-TRANSF-TECNOLOGIA', 'EMPRESA-RECEPTORA'
    ]

    print("[*] Transformando barras em quebras de linha...")

    for col in colunas_com_barras:
        if col in df.columns:
            # Trocamos o '|' pelo caractere de quebra de linha do sistema (\n)
            # Também limpamos resíduos como 'nan' ou '//'
            df[col] = df[col].astype(str).replace(['nan', 'None', '//', 'nan | nan'], "")
            df[col] = df[col].str.replace(' | ', '\n').str.replace('|', '\n')

    # Nome do novo arquivo
    output = "Dados_Inova_Talentos_QUADRANTE.xlsx"

    # Usamos um "engine" especial (xlsxwriter) para avisar ao Excel que o texto deve quebrar linha
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Relatorio')

    # Configuração Visual do Excel
    workbook  = writer.book
    worksheet = writer.sheets['Relatorio']

    # Criamos um formato que permite quebra de linha e alinhamento no topo
    formato_quebra = workbook.add_format({
        'text_wrap': True,
        'valign': 'top'
    })

    # Aplicamos esse formato em todas as colunas
    # (Definimos uma largura de 50 para as colunas de texto ficarem boas de ler)
    worksheet.set_column('A:BZ', 30, formato_quebra)

    writer.close()
    
    print("-" * 40)
    print(f"[+] SUCESSO! Relatório em 'Quadrante' gerado: {output}")
    print("[!] Dica: Ao abrir o Excel, as linhas estarão com a altura certinha para ver tudo.")

# Rodar com o seu arquivo
formatar_lattes_executivo('Dados Inova Talentos Extrator Lattes.xlsx')