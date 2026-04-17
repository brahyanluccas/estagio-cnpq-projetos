import pandas as pd
from pathlib import Path

# Agora os caminhos são relativos à pasta aberta no VS Code
pasta_origem = Path("Arquivos")
arquivo_ref = Path("Sugestão de Tratamento de Dados - INCT.xlsx")

def rodar_diagnostico():
    print(f"\n{'='*60}")
    print(f"DIAGNÓSTICO EM MODO LOCAL")
    print(f"{'='*60}\n")

    # Verifica se a subpasta 'Arquivos' existe aqui dentro
    if not pasta_origem.exists():
        print(f"❌ ERRO: Não encontrei a pasta 'Arquivos' dentro de: {Path('.').absolute()}")
        return

    # Verifica se o arquivo de referência está na raiz
    if not arquivo_ref.exists():
        print(f"❌ ERRO: Arquivo de referência '{arquivo_ref.name}' não encontrado na raiz.")

    arquivos_excel = list(pasta_origem.glob("*.xlsx"))
    
    print(f"🔍 Escaneando subpasta 'Arquivos'...")
    print(f"{'ARQUIVO':<40} | {'COLUNA OK?':<12}")
    print(f"{'-'*55}")

    for caminho in arquivos_excel:
        if caminho.name.startswith("~$"): continue
        
        try:
            df_temp = pd.read_excel(caminho, nrows=0)
            # Limpa espaços extras do nome das colunas
            colunas = [str(c).strip() for c in df_temp.columns]
            
            status = "✅ SIM" if 'Nome Chamada' in colunas else "❌ NÃO"
            print(f"{caminho.name[:40]:<40} | {status:<12}")
            
        except Exception as e:
            print(f"{caminho.name[:40]:<40} | ⚠️ ERRO LER")

    print(f"\n{'='*60}")

if __name__ == "__main__":
    rodar_diagnostico()