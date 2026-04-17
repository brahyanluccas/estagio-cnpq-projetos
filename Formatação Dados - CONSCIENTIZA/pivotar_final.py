import pandas as pd

# --- CONFIGURAÇÃO ---
nome_arquivo_original = 'DASD - Todos os ciclos.xlsx'
nome_arquivo_final = 'DASD - Formato Achatado (Filtros OK).xlsx' # Novo nome

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

    # 1. Pivota a tabela (como antes)
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
    
    # 3. [A SOLUÇÃO] Achatar os cabeçalhos das colunas
    #    Isso transforma os cabeçalhos ('Ciclo 1', 'Treino A')
    #    em uma string única: 'Ciclo 1 - Treino A'
    print("Achatando cabeçalhos das colunas para evitar o bug...")
    df_pivot.columns = [f'{col[0]} - {col[1]}' for col in df_pivot.columns]
    
    # 4. Transforma o índice (Email, Nome...) em colunas normais
    #    (Isso corrige o alinhamento dos filtros)
    df_pivot = df_pivot.reset_index()

    # 5. Salva o novo arquivo
    #    Agora o Pandas vê uma tabela "plana", sem MultiIndex
    #    e pode salvar com index=False sem NENHUM bug.
    print("Salvando arquivo final...")
    df_pivot.to_excel(nome_arquivo_final, index=False)

    print(f"\nSUCESSO! 🚀")
    print(f"Sua nova planilha ACHATADA foi salva como '{nome_arquivo_final}'.")
    print("Isso evita o bug do Pandas. Os filtros agora devem funcionar perfeitamente.")

except FileNotFoundError:
    print(f"!!! ERRO: Arquivo '{nome_arquivo_original}' não encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")