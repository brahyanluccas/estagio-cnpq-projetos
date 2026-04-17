import pandas as pd

print("--- INICIANDO O TIRA-TEIMA (INVESTIGADOR) ---")

# ================= CONFIGURAÇÕES =================
arquivo_pgd = 'Planilha de Autorização PGD - Novembro2025.xlsx'
arquivo_pocket = 'Usuários-Pocket.xlsx'
linha_cabecalho_pgd = 1  

# Colunas de Nome
col_nome_pgd = 'Nome do Participante'
col_nome_pocket = 'Nome Completo'

# Colunas de Email
col_email_pgd = 'E-mail'
col_email_pocket = 'Email'
# =================================================

try:
    # 1. Leitura
    print("Lendo arquivos...")
    df_pgd = pd.read_excel(arquivo_pgd, header=linha_cabecalho_pgd)
    df_pocket = pd.read_excel(arquivo_pocket)

    # 2. Padronização para comparação
    # Cria colunas normalizadas (Maiúsculo e sem espaço) para usar de chave
    df_pgd['NOME_KEY'] = df_pgd[col_nome_pgd].astype(str).str.strip().str.upper()
    df_pgd['EMAIL_KEY'] = df_pgd[col_email_pgd].astype(str).str.strip().str.upper()
    
    df_pocket['NOME_KEY'] = df_pocket[col_nome_pocket].astype(str).str.strip().str.upper()
    df_pocket['EMAIL_KEY'] = df_pocket[col_email_pocket].astype(str).str.strip().str.upper()

    # 3. O Grande Cruzamento (Merge)
    # Vamos juntar as duas planilhas baseados no NOME
    # O sufixo _PGD será usado para dados da planilha 1 e _POCKET para planilha 2
    resultado = pd.merge(df_pgd, df_pocket, on='NOME_KEY', how='inner', suffixes=('_PGD', '_POCKET'))

    # 4. Analisando os Conflitos
    # Vamos verificar linha por linha: O e-mail é igual ou diferente?
    def analisar_situacao(row):
        email1 = str(row['EMAIL_KEY_PGD'])
        email2 = str(row['EMAIL_KEY_POCKET'])
        
        if email1 == email2:
            return "OK - Confirmado"
        else:
            return "ATENÇÃO - E-mails Diferentes"

    resultado['STATUS'] = resultado.apply(analisar_situacao, axis=1)

    # 5. Selecionar apenas as colunas úteis para você ler
    colunas_finais = [
        col_nome_pgd,           # Nome
        col_email_pgd,          # Email na planilha PGD
        col_email_pocket,       # Email na planilha Pocket
        'STATUS'                # Nosso veredito
    ]
    
    # Renomeando para ficar bonito no Excel
    relatorio = resultado[colunas_finais].copy()
    relatorio.columns = ['Nome', 'Email_no_PGD', 'Email_no_Pocket', 'Situação']

    # 6. Separar o Joio do Trigo
    # Cria um Excel com todos, mas ordena para os problemas aparecerem primeiro
    relatorio = relatorio.sort_values(by='Situação')

    nome_saida = 'Relatorio_Tira_Teima.xlsx'
    relatorio.to_excel(nome_saida, index=False)

    print("\n" + "="*40)
    print(f"ANÁLISE CONCLUÍDA!")
    print(f"Total de nomes analisados: {len(relatorio)}")
    print(f"Abra o arquivo '{nome_saida}'.")
    print("No topo da lista estarão os casos de 'ATENÇÃO' onde o nome bate, mas o email não.")
    print("="*40)

except Exception as e:
    print(f"Erro: {e}")