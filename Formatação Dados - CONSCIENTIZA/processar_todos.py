import pandas as pd
import glob # Biblioteca para encontrar arquivos
import os   # Biblioteca para lidar com nomes de arquivos

# --- CONFIGURAÇÃO ---
# Sufixo para os arquivos formatados
sufixo_saida = '_formatado.xlsx'

# Colunas que identificam a pessoa
colunas_identificadoras = [
    'Email',
    'Nome Completo',
    'Diretoria',
    'Coordenação-Geral',
    'Coordenação',
    'Serviço'
]

# Colunas de dados
coluna_ciclo = 'Campanha'
coluna_treinamento = 'Content Name'
coluna_status = 'Status'
# --- FIM DA CONFIGURAÇÃO ---

# 1. Encontra todos os arquivos Excel na pasta atual
arquivos_para_processar = glob.glob('*.xlsx')
print(f"Iniciando... Encontrados {len(arquivos_para_processar)} arquivos .xlsx na pasta.")
print("-" * 30)

# 2. Inicia o loop para processar cada arquivo
for nome_arquivo_original in arquivos_para_processar:
    
    # --- Verificações de Segurança ---
    # Pular arquivos temporários do Excel (que começam com ~)
    if nome_arquivo_original.startswith('~'):
        print(f"Pulando arquivo temporário: {nome_arquivo_original}")
        continue # Vai para o próximo arquivo do loop
        
    # Pular arquivos que já foram formatados (para não processar de novo)
    if sufixo_saida in nome_arquivo_original:
        print(f"Pulando arquivo já formatado: {nome_arquivo_original}")
        continue # Vai para o próximo arquivo do loop
    
    # Define o nome do arquivo de saída
    # Ex: 'Relatorio.xlsx' vira 'Relatorio_formatado.xlsx'
    nome_base = os.path.splitext(nome_arquivo_original)[0]
    nome_arquivo_final = f"{nome_base}{sufixo_saida}"

    print(f"Processando: {nome_arquivo_original}...")

    try:
        # Carrega a planilha original
        df_original = pd.read_excel(nome_arquivo_original)

        # 3. Pivota a tabela (formato agrupado)
        df_pivot = df_original.pivot_table(
            index=colunas_identificadoras,
            columns=[coluna_ciclo, coluna_treinamento],
            values=coluna_status,
            aggfunc='first'
        )

        # 4. Limpeza (remove 'Campanha' e 'Content Name' do topo)
        df_pivot = df_pivot.fillna('')
        df_pivot.columns.names = [None, None] 
        
        # 5. Salva o novo arquivo (com index=True, que causa o bug visual)
        df_pivot.to_excel(nome_arquivo_final, index=True)

        print(f"==> SUCESSO! Salvo como: {nome_arquivo_final}")

    except KeyError as e:
        print(f"==> !!! ERRO: Coluna {e} não encontrada em '{nome_arquivo_original}'.")
        print("    Verifique se as colunas deste arquivo são iguais às configuradas.")
    except Exception as e:
        print(f"==> !!! ERRO inesperado em '{nome_arquivo_original}': {e}")
    
    print("-" * 30) # Separador

print("\nProcesso concluído para todos os arquivos!")