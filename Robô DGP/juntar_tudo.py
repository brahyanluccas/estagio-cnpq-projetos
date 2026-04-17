import pandas as pd
import os

# === CONFIGURAÇÕES ===
ARQUIVO_TEXTO   = r"Extracao_01_TEXTO_Completo.xlsx"
ARQUIVO_TABELAS = r"Extracao_02_TABELAS_Completo.xlsx"

ARQUIVO_MESTRE_FINAL = r"Grupos DGP.xlsx"
# =====================

print(f"Iniciando PASSO 3: Unificação dos arquivos Excel...")

# Dicionário para armazenar todas as abas (DataFrames)
abas_para_salvar = {}

# --- 1. Lendo o Arquivo 1 (Texto) ---
try:
    print(f"Lendo abas do arquivo: {ARQUIVO_TEXTO}...")
    # pd.read_excel com sheet_name=None lê TODAS as abas de uma vez
    excel_texto = pd.read_excel(ARQUIVO_TEXTO, sheet_name=None)
    
    for nome_aba, df in excel_texto.items():
        print(f"  -> Aba '{nome_aba}' carregada.")
        abas_para_salvar[nome_aba] = df
        
except FileNotFoundError:
    print(f"!!! ERRO: Arquivo '{ARQUIVO_TEXTO}' não encontrado. !!!")
    exit()
except Exception as e:
    print(f"!!! ERRO ao ler '{ARQUIVO_TEXTO}': {e} !!!")
    exit()

# --- 2. Lendo o Arquivo 2 (Tabelas) ---
try:
    print(f"\nLendo abas do arquivo: {ARQUIVO_TABELAS}...")
    excel_tabelas = pd.read_excel(ARQUIVO_TABELAS, sheet_name=None)
    
    for nome_aba, df in excel_tabelas.items():
        print(f"  -> Aba '{nome_aba}' carregada.")
        
        # Verifica se o nome da aba já existe (ex: "Linhas de Pesquisa")
        if nome_aba in abas_para_salvar:
            abas_para_salvar[f"{nome_aba}_2"] = df # Adiciona sufixo se já existir
        else:
            abas_para_salvar[nome_aba] = df

except FileNotFoundError:
    print(f"!!! ERRO: Arquivo '{ARQUIVO_TABELAS}' não encontrado. !!!")
    exit()
except Exception as e:
    print(f"!!! ERRO ao ler '{ARQUIVO_TABELAS}': {e} !!!")
    exit()

# --- 3. Salvando o Arquivo Mestre Final ---
if abas_para_salvar:
    print(f"\nSalvando todas as {len(abas_para_salvar)} abas no arquivo mestre: {ARQUIVO_MESTRE_FINAL}...")
    try:
        with pd.ExcelWriter(ARQUIVO_MESTRE_FINAL) as writer:
            for nome_aba, df in abas_para_salvar.items():
                print(f"  -> Escrevendo aba '{nome_aba}'...")
                df.to_excel(writer, sheet_name=nome_aba, index=False)
        
        print(f"\n✅✅✅ TRABALHO 100% CONCLUÍDO! ✅✅✅")
        print(f"O arquivo mestre foi salvo com sucesso em: {ARQUIVO_MESTRE_FINAL}")

    except PermissionError:
        print(f"\n!!! ERRO DE PERMISSÃO: O arquivo '{ARQUIVO_MESTRE_FINAL}' já está aberto. Feche o Excel e tente novamente. !!!")
    except Exception as e_save:
        print(f"\n!!! ERRO AO SALVAR O EXCEL MESTRE: {e_save} !!!")
else:
    print("Nenhuma aba foi encontrada para salvar.")