import pandas as pd
import time
import shutil
from pathlib import Path
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURAÇÕES DE CAMINHOS ---
# Certifique-se de que os nomes abaixo batem com os seus arquivos reais
ARQUIVO_LINKS = "chamadas INCT's (1).xlsx"
ARQUIVO_REF = "Lista de Processos Favoráveis INCT 2008 - 2022.xlsx"
PASTA_RAIZ = Path.cwd()
PASTA_DESTINO = PASTA_RAIZ / "Downloads_Finalizados"
PASTA_TEMP = PASTA_RAIZ / "temp_processando"

# Criar pastas iniciais
PASTA_DESTINO.mkdir(exist_ok=True)
PASTA_TEMP.mkdir(exist_ok=True)

# --- 2. TRATAMENTO DOS DADOS (PANDAS) ---
print("📊 Carregando bases de dados completas...")
df_links = pd.read_excel(ARQUIVO_LINKS)
# skiprows=3 pula as linhas vazias no topo do seu excel de referência
df_ref = pd.read_excel(ARQUIVO_REF, skiprows=3)

# Cruzamento dos dados (Merge/Join)
df_final = pd.merge(df_links, df_ref, left_on='Processo', right_on='Processo mãe', how='left')

def definir_pasta(linha):
    """Lógica para classificar a pasta baseada na Chamada ou exclusão para 2024"""
    chamada = str(linha.get('Chamada', '')).upper()
    if pd.isna(linha.get('Chamada')) or 'NAN' in chamada:
        return "INCT 2024"
    
    for ano in ["2008", "2010", "2014", "2022"]:
        if ano in chamada:
            return f"INCT {ano}"
    return "INCT 2024"

# --- 3. CONFIGURAÇÃO DO NAVEGADOR (CHROME) ---
chrome_options = Options()
prefs = {
    "download.default_directory": str(PASTA_TEMP.absolute()),
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True # Impede de abrir o PDF na aba, força download
}
chrome_options.add_experimental_option("prefs", prefs)
# chrome_options.add_argument("--headless") # Descomente para rodar em segundo plano

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Lista para gerar o relatório de auditoria final
resultados_log = []

# --- 4. EXECUÇÃO DO FLUXO ---
print(f"\n🚀 Iniciando processamento de {len(df_final)} processos...")

try:
    # Barra de progresso visual no terminal
    for index, linha in tqdm(df_final.iterrows(), total=len(df_final), desc="Progresso Geral"):
        processo_original = str(linha['Processo'])
        # Limpa caracteres que o Windows não aceita em nomes de arquivos
        processo_limpo = processo_original.replace("/", "-").replace(".", "")
        link = linha['LINK DA PROPOSTA']
        pasta_nome = definir_pasta(linha)
        
        caminho_final = PASTA_DESTINO / pasta_nome
        caminho_final.mkdir(exist_ok=True)

        status = "Falha"
        detalhe = "Erro desconhecido"

        try:
            if pd.isna(link) or str(link).strip() == "":
                status = "Pulado"
                detalhe = "Link vazio no Excel"
            else:
                driver.get(link)
                # Tempo de espera para o download completar (ajuste se necessário)
                time.sleep(5) 

                # Verifica se o arquivo caiu na pasta temporária
                arquivos_baixados = list(PASTA_TEMP.glob("*"))
                if arquivos_baixados:
                    for arquivo in arquivos_baixados:
                        # Move para a pasta definitiva renomeando para o número do processo
                        shutil.move(str(arquivo), caminho_final / f"{processo_limpo}.pdf")
                    status = "Sucesso"
                    detalhe = f"Movido para {pasta_nome}"
                else:
                    detalhe = "Download não iniciado pelo servidor"

        except Exception as e:
            detalhe = f"Erro técnico: {str(e)}"

        # Salva o resultado desta linha para o relatório
        resultados_log.append({
            "Processo": processo_original,
            "Chamada Identificada": pasta_nome,
            "Status": status,
            "Detalhe": detalhe,
            "Link Utilizado": link
        })

finally:
    # Garante que o navegador feche e a pasta temp seja limpa
    print("\n🏁 Finalizando sessões...")
    driver.quit()
    if PASTA_TEMP.exists():
        shutil.rmtree(PASTA_TEMP)

    # --- 5. GERAÇÃO DO RELATÓRIO DE AUDITORIA ---
    df_relatorio = pd.DataFrame(resultados_log)
    df_relatorio.to_excel("relatorio_final_processamento.xlsx", index=False)
    
    print(f"📊 Relatório gerado com sucesso: relatorio_final_processamento.xlsx")
    print(f"📂 Verifique seus arquivos em: {PASTA_DESTINO}")