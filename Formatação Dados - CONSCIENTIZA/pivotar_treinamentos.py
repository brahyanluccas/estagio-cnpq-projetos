import pandas as pd

# --- CONFIGURAÇÃO ---

# 1. Nome do arquivo de origem
nome_arquivo_original = 'DASD - Todos os ciclos.xlsx'

# 2. Nome do arquivo que será criado
nome_arquivo_final = 'DASD - Formato Pivotado.xlsx'

# 3. Colunas de identificação (baseado na sua verificação)
colunas_identificadoras = [
    'Email',
    'Nome Completo',
    'Diretoria',
    'Coordenação-Geral',  # <-- CORRIGIDO AQUI (com hífen)
    'Coordenação',
    'Serviço'
]
# Nota: Seu arquivo também tem 'Past Due', 'Enrolled On', etc.
# Se você quiser que essas colunas também apareçam na planilha final,
# adicione-as a esta lista 'colunas_identificadoras'.
# Se não, pode deixar como está.

# 4. Nomes das colunas de dados
coluna_ciclo = 'Campanha'
coluna_treinamento = 'Content Name'
coluna_status = 'Status'

# --- FIM DA CONFIGURAÇÃO ---


try:
    # Carrega a planilha original
    print(f"Carregando arquivo '{nome_arquivo_original}'...")
    df_original = pd.read_excel(nome_arquivo_original)
    print("Arquivo carregado com sucesso.")

    # Verifica se todas as colunas necessárias existem
    colunas_necessarias = colunas_identificadoras + [coluna_ciclo, coluna_treinamento, coluna_status]
    for col in colunas_necessarias:
        if col not in df_original.columns:
            print("-" * 30)
            print(f"!!! ERRO: A coluna '{col}' não foi encontrada no arquivo!")
            print("Isso não deveria acontecer agora. Verifique se salvou o script.")
            print("-" * 30)
            exit()

    
    # 1. Cria a coluna combinada (Ex: "Ciclo 2 - Ameaças comuns 2025")
    print("Combinando colunas 'Ciclo' e 'Treinamento'...")
    df_original['Treinamento_Completo'] = df_original[coluna_ciclo].astype(str) + ' - ' + df_original[coluna_treinamento].astype(str)

    # 2. Pivota a tabela
    print("Pivotando os dados... (Isso pode levar alguns segundos)")
    df_pivot = df_original.pivot_table(
        index=colunas_identificadoras,  # Suas colunas de identificação
        columns='Treinamento_Completo', # Novas colunas (Ciclo - Treinamento)
        values=coluna_status,           # O que vai preencher as células
        aggfunc='first'                 # Pega o primeiro status
    )

    # 3. Limpeza
    print("Limpando a tabela final...")
    df_pivot = df_pivot.fillna('')      # Preenche células vazias
    df_pivot = df_pivot.reset_index() # Transforma o índice em colunas

    # 4. Salva o novo arquivo
    df_pivot.to_excel(nome_arquivo_final, index=False)

    print(f"\nSUCESSO! 🚀")
    print(f"Sua nova planilha formatada foi salva como '{nome_arquivo_final}'.")

except FileNotFoundError:
    print("-" * 30)
    print(f"!!! ERRO: Arquivo não encontrado.")
    print(f"Não consegui encontrar o arquivo '{nome_arquivo_original}'.")
    print("-" * 30)
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")