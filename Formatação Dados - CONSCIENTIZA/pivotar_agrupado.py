import pandas as pd

# --- CONFIGURAÇÃO ---
nome_arquivo_original = 'DASD - Todos os ciclos.xlsx'
nome_arquivo_final = 'DASD - Formato Agrupado Super-Limpo.xlsx' # Novo nome

colunas_identificadoras = [
    'Email',
    'Nome Completo',
    'Diretoria',
    'Coordenação-Geral',
    'Coordenação',
    'Serviço'
]
coluna_ciclo = 'Campanha'
coluna_treinamento = 'Content Name'
coluna_status = 'Status'
# --- FIM DA CONFIGURAÇÃO ---

try:
    print(f"Carregando arquivo '{nome_arquivo_original}'...")
    df_original = pd.read_excel(nome_arquivo_original)
    print("Arquivo carregado com sucesso.")

    # Verifica se todas as colunas existem
    colunas_necessarias = colunas_identificadoras + [coluna_ciclo, coluna_treinamento, coluna_status]
    for col in colunas_necessarias:
        if col not in df_original.columns:
            print(f"!!! ERRO: A coluna '{col}' não foi encontrada.")
            print("Verifique os nomes na configuração do script.")
            exit()
            
    # 1. Pivota a tabela
    print("Pivotando os dados com colunas agrupadas...")
    df_pivot = df_original.pivot_table(
        index=colunas_identificadoras,
        columns=[coluna_ciclo, coluna_treinamento],
        values=coluna_status,
        aggfunc='first'
    )

    # 2. Limpeza
    print("Limpando a tabela final...")
    df_pivot = df_pivot.fillna('')
    
    # --- LIMPEZA DOS CABEÇALHOS ---
    # Remove 'Campanha' e 'Content Name' do topo das colunas
    df_pivot.columns.names = [None, None]
    
    # [NOVA LINHA] Remove 'Email', 'Nome Completo', etc., da lateral
    df_pivot.index.names = [None] * len(colunas_identificadoras)
    # ---------------------------------
    
    # 3. Salva o novo arquivo (mantendo a correção do 'index=True')
    df_pivot.to_excel(nome_arquivo_final, index=True)

    print(f"\nSUCESSO! 🚀")
    print(f"Sua nova planilha 'Super-Limpa' foi salva como '{nome_arquivo_final}'.")
    print("Agora os cabeçalhos laterais (Email, Nome...) também foram removidos.")

except FileNotFoundError:
    print(f"!!! ERRO: Arquivo '{nome_arquivo_original}' não encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")