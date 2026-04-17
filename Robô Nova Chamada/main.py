import pandas as pd
from pathlib import Path

# Configurações de caminhos locais
pasta_origem = Path("Arquivos")
pasta_destino = Path("Processados")
arquivo_ref = Path("Sugestão de Tratamento de Dados - INCT.xlsx")

# Criar pasta de destino
pasta_destino.mkdir(exist_ok=True)

def carregar_com_cabecalho_flexivel(caminho):
    """Tenta ler o Excel pulando linhas até achar a coluna correta"""
    for i in range(10):  # Tenta procurar o cabeçalho nas primeiras 10 linhas
        df = pd.read_excel(caminho, skiprows=i)
        if 'Nome Chamada' in df.columns:
            return df
    return None

# 1. Carregar Referência
try:
    df_ref = pd.read_excel(arquivo_ref)
    mapeamento = dict(zip(
        df_ref['Nome Chamada - Original'].astype(str).str.strip(), 
        df_ref['Nome Chamada - Padronizado'].astype(str).str.strip()
    ))
    print("✅ Referência carregada!")
except Exception as e:
    print(f"❌ Erro na referência: {e}")
    exit()

# 2. Lógica de Tratamento
def tratar(nome):
    nome_str = str(nome).strip()
    if nome_str in mapeamento:
        return mapeamento[nome_str]
    return nome_str if "INCT" in nome_str.upper() else "Outros"

# 3. Processamento
arquivos = list(pasta_origem.glob("*.xlsx"))

for caminho in arquivos:
    if caminho.name.startswith("~$"): continue
    
    print(f"Processando: {caminho.name}...")
    df = carregar_com_cabecalho_flexivel(caminho)
    
    if df is not None:
        # Cria a nova coluna
        df['Nome Chamada - Tratado'] = df['Nome Chamada'].apply(tratar) 
        
        # Salva o arquivo limpo
        df.to_excel(pasta_destino / caminho.name, index=False)
        print(f"   ✔ Sucesso!")
    else:
        print(f"   ❌ Erro: Coluna 'Nome Chamada' não encontrada mesmo pulando linhas.")

print("\n🚀 FIM! Verifique a pasta 'Processados'.")