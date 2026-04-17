import os
import json
import time
import shutil 
import re     

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select 
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. FUNÇÕES DE AJUDA ---
def esperar_download(pasta_downloads, timeout=90):
    print(f"  ...Aguardando download do PDF (limite: {timeout}s)...")
    segundos = 0
    while segundos < timeout:
        time.sleep(1)
        segundos += 1
        arquivos_baixando = [f for f in os.listdir(pasta_downloads) if f.endswith('.crdownload')]
        if not arquivos_baixando:
            arquivos_pdf = [f for f in os.listdir(pasta_downloads) if f.endswith('.pdf')]
            if arquivos_pdf:
                time.sleep(2) 
                print("  ...Download detectado.")
                return True
    print(f"  ...ERRO: Download demorou mais de {timeout} segundos ou falhou.")
    return False

def renomear_e_mover_arquivo(pasta_origem, pasta_destino, novo_nome_base, indice_global, termo_pesquisa):
    """Pega o PDF da pasta principal, renomeia e move para a subpasta do termo"""
    try:
        pdfs = [os.path.join(pasta_origem, f) for f in os.listdir(pasta_origem) if f.endswith('.pdf')]
        if not pdfs:
            print(f"  ...ERRO: Nenhum PDF encontrado para renomear e mover.")
            return
            
        arquivo_mais_recente = max(pdfs, key=os.path.getmtime)
        
        termo_limpo = re.sub(r'[\W_]+', '_', termo_pesquisa.lower())
        titulo_limpo = re.sub(r'[\W_]+', '_', novo_nome_base.lower())[:60] 
        novo_nome = f"{termo_limpo}_{indice_global+1:04d}_{titulo_limpo}.pdf"
        
        # Caminho final já na subpasta
        novo_caminho = os.path.join(pasta_destino, novo_nome)
        
        shutil.move(arquivo_mais_recente, novo_caminho)
        print(f"  ...Arquivo movido com sucesso para a pasta: {termo_pesquisa}")
    except Exception as e:
        print(f"  ...ERRO ao renomear e mover arquivo: {e}")

# =======================================================================
# --- 2. A NOVA FUNÇÃO PRINCIPAL ---
# =======================================================================

def executar_robo_download(lista_termos):
    """Recebe uma LISTA de palavras e cria subpastas para cada uma"""
    
    # ---> ALTERAÇÃO 1: Contador zerado no início
    total_pdfs_baixados = 0
    
    # Sua nova pasta raiz
    pasta_raiz = os.path.abspath("PDFs DGP")
    os.makedirs(pasta_raiz, exist_ok=True)

    # --- OPÇÕES DO CHROME ---
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    settings = {
        "recentDestinations": [{ "id": "Save as PDF", "origin": "local", "account": "" }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isHeaderFooterEnabled": False,
        "isCssBackgroundEnabled": True, 
    }
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': pasta_raiz, # O Chrome sempre baixa aqui
        'download.default_directory': pasta_raiz,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')

    print(f"Iniciando o ROBÔ DOWNLOADER...")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 180) 
        print("Navegador aberto com sucesso!")

        url_busca = "http://dgp.cnpq.br/dgp/faces/consulta/consulta_parametrizada.jsf"
        
        # --- O GRANDE LAÇO QUE RODA CADA PALAVRA ---
        for termo in lista_termos:
            print(f"\n==================================================")
            print(f"🤖 INICIANDO BUSCA PARA: '{termo}'")
            print(f"==================================================")
            
            # Cria a subpasta específica para este termo
            pasta_do_termo = os.path.join(pasta_raiz, termo)
            os.makedirs(pasta_do_termo, exist_ok=True)
            
            driver.get(url_busca)
            pagina_atual = 1
            indice_global_download = 0 

            try:
                campo_busca = wait.until(EC.presence_of_element_located((By.ID, "idFormConsultaParametrizada:idTextoFiltro")))
                campo_busca.clear()
                campo_busca.send_keys(termo)
            except TimeoutException:
                print(f"Erro: Campo de busca não encontrado para '{termo}'. Pulando para o próximo.")
                continue 
                
            botao_pesquisar = wait.until(EC.element_to_be_clickable((By.ID, "idFormConsultaParametrizada:idPesquisar")))
            botao_pesquisar.click()

            link_selector = "a[id^='idFormConsultaParametrizada:resultadoDataList:'][id$=':idBtnVisualizarEspelhoGrupo']"
            try:
                espera_curta = WebDriverWait(driver, 15) 
                espera_curta.until(EC.presence_of_element_located((By.CSS_SELECTOR, link_selector)))
            except TimeoutException:
                print(f"--- Nenhum resultado encontrado para '{termo}'. Pulando... ---")
                continue 
                
            try:
                links_antigos = driver.find_elements(By.CSS_SELECTOR, link_selector)
                dropdown_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ui-paginator-rpp-options")))
                select_obj = Select(dropdown_element)
                select_obj.select_by_value("100")
                wait.until(EC.staleness_of(links_antigos[0]))
            except Exception:
                pass # Se falhar, segue com 25 resultados mesmo

            # Loop de Paginação
            while True: 
                print(f"\n--- Página {pagina_atual} | Termo: '{termo}' ---")
                links_de_artigos = driver.find_elements(By.CSS_SELECTOR, link_selector)
                num_links_pagina = len(links_de_artigos)

                aba_principal = driver.current_window_handle

                for i in range(num_links_pagina):
                    links_atuais = driver.find_elements(By.CSS_SELECTOR, link_selector)
                    if i >= len(links_atuais): continue 

                    link = links_atuais[i]
                    try:
                        titulo_artigo = link.text
                        print(f"Processando: {titulo_artigo[:50]}...")
                    except Exception: continue

                    try:
                        driver.execute_script("arguments[0].click();", link)
                        wait.until(EC.number_of_windows_to_be(2))
                        
                        nova_aba = [aba for aba in driver.window_handles if aba != aba_principal][0]
                        driver.switch_to.window(nova_aba)
                        time.sleep(10) 
                        
                        driver.execute_script('window.print();')
                        
                        if esperar_download(pasta_raiz):
                            # Move da pasta_raiz para a pasta_do_termo
                            renomear_e_mover_arquivo(pasta_raiz, pasta_do_termo, titulo_artigo, indice_global_download, termo)
                            indice_global_download += 1 
                            # ---> ALTERAÇÃO 2: Soma 1 no contador a cada sucesso
                            total_pdfs_baixados += 1
                            
                    except Exception as e_loop:
                        print(f"  ...ERRO ao processar o link: {e_loop}")
                    finally:
                        if len(driver.window_handles) > 1:
                            driver.close()
                        driver.switch_to.window(aba_principal)
                        time.sleep(1) 
                
                # Procura Próxima Página
                try:
                    seletor_proxima_pagina = "span.ui-paginator-next:not(.ui-state-disabled)"
                    botao_proxima = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_proxima_pagina)))
                    driver.execute_script("arguments[0].click();", botao_proxima)
                    pagina_atual += 1 
                    
                    seletor_pagina_ativa = f"//span[contains(@class, 'ui-paginator-page') and contains(@class, 'ui-state-active') and text() = '{pagina_atual}']"
                    wait.until(EC.presence_of_element_located((By.XPATH, seletor_pagina_ativa)))
                except NoSuchElementException:
                    break 
                except Exception:
                    break 

            print(f"✅ Concluídos todos os downloads para: '{termo}'")

        # ---> ALTERAÇÃO 3: Devolve o total para a tela se o laço "for" terminar bem
        return total_pdfs_baixados

    except Exception as e_geral:
        print(f"\n--- ERRO GERAL NO NAVEGADOR --- \nErro: {e_geral}")
        # ---> ALTERAÇÃO 4: Grita para a tela se o bloco "try" geral falhar
        raise Exception(f"Falha de conexão com o navegador. Detalhes: {e_geral}")

    finally:
        if 'driver' in locals():
            driver.quit()
            print("\nRobô DOWNLOADER finalizado com sucesso.")