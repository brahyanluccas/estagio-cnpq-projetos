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

# --- 1. FUNÇÕES DE AJUDA (COM MAIS PACIÊNCIA) ---

def esperar_download(pasta_downloads, timeout=90):
    """
    Espera um arquivo .pdf aparecer na pasta ou até o timeout.
    """
    print(f"  ...Aguardando download do PDF (limite: {timeout}s)...")
    segundos = 0
    while segundos < timeout:
        time.sleep(1)
        segundos += 1
        arquivos_baixando = [f for f in os.listdir(pasta_downloads) if f.endswith('.crdownload')]
        if not arquivos_baixando:
            arquivos_pdf = [f for f in os.listdir(pasta_downloads) if f.endswith('.pdf')]
            if arquivos_pdf:
                time.sleep(2) # Espera extra para o sistema "soltar" o arquivo
                print("  ...Download detectado.")
                return True
    
    print(f"  ...ERRO: Download demorou mais de {timeout} segundos ou falhou.")
    return False

def renomear_ultimo_arquivo(pasta_downloads, novo_nome_base, indice_global, termo_pesquisa):
    """
    Pega o último PDF baixado, o renomeia e o organiza.
    """
    try:
        pdfs = [os.path.join(pasta_downloads, f) for f in os.listdir(pasta_downloads) if f.endswith('.pdf')]
        if not pdfs:
            print(f"  ...ERRO: Nenhum PDF encontrado para renomear.")
            return

        arquivo_mais_recente = max(pdfs, key=os.path.getmtime)
        
        termo_limpo = re.sub(r'[\W_]+', '_', termo_pesquisa.lower())
        titulo_limpo = re.sub(r'[\W_]+', '_', novo_nome_base.lower())
        titulo_limpo = titulo_limpo[:60] 
        
        novo_nome = f"{termo_limpo}_{indice_global+1:04d}_{titulo_limpo}.pdf"
        novo_caminho = os.path.join(pasta_downloads, novo_nome)
        
        shutil.move(arquivo_mais_recente, novo_caminho)
        print(f"  ...Arquivo salvo como: {novo_nome}")

    except Exception as e:
        print(f"  ...ERRO ao renomear arquivo: {e}")


# --- 2. CONFIGURAÇÃO (Igual) ---
download_dir = os.path.abspath("downloads_cnpq")
CAMINHO_DRIVER = "chromedriver.exe" 

# --- 3. OPÇÕES DO CHROME (Igual) ---
chrome_options = Options()
service = Service(CAMINHO_DRIVER)
settings = {
    "recentDestinations": [{ "id": "Save as PDF", "origin": "local", "account": "" }],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
    "isHeaderFooterEnabled": False,
    "isCssBackgroundEnabled": True, 
}
prefs = {
    'printing.print_preview_sticky_settings.appState': json.dumps(settings),
    'savefile.default_directory': download_dir,
    'download.default_directory': download_dir,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')

# --- 4. INICIANDO O NAVEGADOR ---
print("Iniciando o ROBÔ DOWNLOADER (Versão Mestre Completa)...")
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Paciência de 180 segundos (3 minutos)
    wait = WebDriverWait(driver, 180) 
    
    print("Navegador aberto com sucesso!")

    # --- 5. LÓGICA DE BUSCA ---
    
    url_busca = "http://dgp.cnpq.br/dgp/faces/consulta/consulta_parametrizada.jsf"
    
    # !!! --- LISTA COMPLETA E CORRIGIDA (159 TERMOS) --- !!!
    termos_de_pesquisa = [
        # Lista 1 (38 termos)
        "Mudanças Climáticas", "Gases de Efeito Estufa", "Poluição ambiental",
        "Mitigação Climática", "Adaptação Climática", "Sustentabilidade",
        "Preservação Ambiental", "Biodiversidade", "Amazônia", "Cerrado",
        "Caatinga", "Pantanal", "Desmatamento", "Biomas Brasileiros",
        "Energia Renovável", "Agricultura Sustentável", "Uso da água",
        "Uso do Solo", "Resíduos ambientais", "Eventos Climáticos Extremos",
        "Resiliência Ambiental", "Políticas Climáticas", "Economia de Baixo Carbono",
        "Objetivos de Desenvolvimento Sustentável (ODS)", "Justiça Climática",
        "Financiamento Climático", "Tecnologia Verde", "Meio ambiente",
        "Educação Ambiental", "Economia circular", "Biodiversidade e clima",
        "Neutralidade de carbono", "Gestão climática eficaz",
        "Manejo integrado do fogo", "Bioeconomia", "Serviços ambientais",
        "Impacto ambiental", "Chuva ácida",
        
        # Lista 2 (121 termos, corrigido)
        "alterações climáticas", "GEE", "poluentes atmosféricos", "combate ao aquecimento",
        "adaptação ambiental", "práticas sustentáveis", "proteção ambiental",
        "diversidade biológica", "bioma amazônico", "bioma cerrado", "Desertificação",
        "Ecossistema pantaneiro", "perda de cobertura vegetal", "diversidade de biomas",
        "energias sustentáveis", "sistemas integrados", "Segurança hídrica", "manejo do solo",
        "Manejo de resíduos", "enchentes", "sistemas resilientes", "políticas públicas ambientais",
        "economia verde", "metas globais", "responsabilidade ambiental", "recursos climáticos",
        "tecnologia limpa", "ciência ambiental", "programas de educação sobre o clima",
        "reciclagem", "ecossistemas tropicais", "economia de baixo carbono", "políticas climáticas",
        "Recuperação de áreas degradadas", "economia de base biológica", "serviços ecossistêmicos",
        "efeitos ambientais", "precipitação ácida", "mudanças no clima", "emissões antrópicas",
        "poluição atmosférica", "estratégias de mitigação", "estratégias de adaptação",
        "equilíbrio ambiental", 
        "economia circular", 
        "ecologia", "proteção da biodiversidade",
        "preservação da Amazônia", "preservação do cerrado", "Sistemas agroflorestais",
        "degradação do Pantanal", "degradação florestal", "conservação dos biomas",
        "energia solar", "agricultura de baixo carbono", "vulnerabilidade hídrica",
        "práticas agrícolas", "Coleta Seletiva", "ciclones", "fortalecimento ambiental",
        "regulações climáticas", "descarbonização", "ODS relacionados ao clima",
        "racismo ambiental", "apoio financeiro para mudanças climáticas",
        "soluções tecnológicas para o clima", "capacitação ambiental", "reutilização de recursos",
        "proteção de florestas", "redução de emissões", "planejamento climático",
        "Conservação de florestas tropicais", "bioindústria", "benefícios ambientais",
        "degradação ambiental", "poluição atmosférica", "crise climática", "CO2",
        "resíduos sólidos", "economia verde", "preservação de florestas", "amazônia azul",
        "Ecossistema semiárido", "Ecossistemas tropicais", "energia eólica",
        "Planejamento hídrico sustentável", "contaminação do solo", "Logística Reversa",
        "ondas de calor", "estiagens prolongadas", "impactos sociais das mudanças climáticas",
        "conscientização ambiental", "biotecnologia aplicada", "funções ambientais",
        "alteração ecológica", "acidez da chuva", "mercado de carbono", "emissão de poluentes",
        "produtos naturais", "Conservação da vegetação nativa", "Floresta Amazônica",
        "Degradação ambiental", "energia limpa", "contaminação da água",
        "degradação do solo", "Poluição por Resíduos Sólidos", "desastres naturais",
        "efeito estufa", "microplásticos", "poluição do solo", "Rejeitos sólidos",
        "desastres ambientais", "soluções sustentáveis", "crédito de carbono",
        "poluição antrópica", "Uso sustentável da terra", "biofertilizantes", "ilha de calor",
        "Sequestro de carbono", "micropoluentes", "Acidificação dos oceanos"
    ]
    
    for termo in termos_de_pesquisa:
        print(f"\n--- INICIANDO DOWNLOADS PARA: '{termo}' ---")
        driver.get(url_busca)
        pagina_atual = 1
        indice_global_download = 0 # Zera o contador de arquivos para cada termo

        # 1. Digita o termo
        print(f"Digitando: '{termo}'")
        try:
            campo_busca = wait.until(
                EC.presence_of_element_located((By.ID, "idFormConsultaParametrizada:idTextoFiltro"))
            )
            campo_busca.clear()
            campo_busca.send_keys(termo)
        except TimeoutException:
            print(f"Erro: Campo de busca não encontrado. Pulando para próximo termo.")
            continue 

        # 2. Clica em "Pesquisar"
        print("Clicando no botão 'Pesquisar'...")
        botao_pesquisar = wait.until(
            EC.element_to_be_clickable((By.ID, "idFormConsultaParametrizada:idPesquisar"))
        )
        botao_pesquisar.click()

        # 3. VERIFICA SE HÁ RESULTADOS
        link_selector = "a[id^='idFormConsultaParametrizada:resultadoDataList:'][id$=':idBtnVisualizarEspelhoGrupo']"
        try:
            # Espera a primeira página carregar (agora com 3 minutos de paciência)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, link_selector)))
            print("Página de resultados carregada.")
        except TimeoutException:
            print(f"--- Nenhum resultado encontrado para o termo '{termo}' (mesmo com 3 min). Pulando... ---")
            continue 
            
        # 4. ALTERAR PARA 100 RESULTADOS POR PÁGINA
        print("Alterando para 100 resultados por página...")
        try:
            links_antigos = driver.find_elements(By.CSS_SELECTOR, link_selector)
            dropdown_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-paginator-rpp-options"))
            )
            select_obj = Select(dropdown_element)
            select_obj.select_by_value("100")
            print("Aguardando página recarregar com 100 resultados...")
            wait.until(EC.staleness_of(links_antigos[0]))
            print("Página atualizada com 100 resultados.")
        except Exception as e:
            print(f"Não foi possível alterar para 100, continuando com 25. Erro: {e}")


        # --- 5. O GRANDE LOOP (PAGINAÇÃO + DOWNLOAD) ---
        
        while True: 
            print(f"\n--- Processando Página {pagina_atual} para '{termo}' ---")
            
            links_de_artigos = driver.find_elements(By.CSS_SELECTOR, link_selector)
            num_links_pagina = len(links_de_artigos)
            
            if num_links_pagina == 0:
                print("Nenhum link encontrado nesta página.")
            else:
                print(f"Encontrados {num_links_pagina} links na Página {pagina_atual}.")

            aba_principal = driver.current_window_handle

            # Loop de Download (para os links desta página)
            for i in range(num_links_pagina):
                
                links_atuais = driver.find_elements(By.CSS_SELECTOR, link_selector)
                
                if i >= len(links_atuais):
                    print(f"Erro: Não foi possível re-encontrar o link de índice {i}.")
                    continue 

                link = links_atuais[i]
                try:
                    titulo_artigo = link.text
                    print(f"\nProcessando link {indice_global_download+1}: {titulo_artigo[:70]}...")
                except Exception as e_text:
                    print(f"Erro ao pegar texto do link: {e_text}. Pulando.")
                    continue

                try:
                    # 1. Clica no link (V4)
                    print("  ...Clicando no link (via JavaScript)...")
                    driver.execute_script("arguments[0].click();", link)
                    
                    # 2. Espera a nova aba
                    wait.until(EC.number_of_windows_to_be(2))
                    
                    nova_aba = [aba for aba in driver.window_handles if aba != aba_principal][0]
                    driver.switch_to.window(nova_aba)
                    
                    # 3. Espera da nova aba (10s fixos)
                    print("  ...Nova aba aberta. Aguardando 10s para carregar...")
                    time.sleep(10) 
                    
                    # 4. Aciona a impressão
                    print("  ...Acionando impressão para PDF...")
                    driver.execute_script('window.print();')
                    
                    # 5. Espera e Renomeia (agora com 90s de paciência)
                    if esperar_download(download_dir):
                        renomear_ultimo_arquivo(download_dir, titulo_artigo, indice_global_download, termo)
                        indice_global_download += 1 # Incrementa o contador GERAL
                    
                except Exception as e_loop:
                    print(f"  ...ERRO ao processar o link '{titulo_artigo[:50]}...': {e_loop}")
                
                finally:
                    # 6. Fecha aba e volta
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(aba_principal)
                    time.sleep(1) 
            
            # 6. PROCURA O BOTÃO "PRÓXIMA PÁGINA" (LÓGICA DO V4)
            print("\nProcurando botão 'Próxima Página'...")
            try:
                seletor_proxima_pagina = "span.ui-paginator-next:not(.ui-state-disabled)"
                botao_proxima = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, seletor_proxima_pagina))
                )
                
                print("  ... Clicando em 'Próxima Página' (via JavaScript)...")
                driver.execute_script("arguments[0].click();", botao_proxima)
                
                pagina_atual += 1 
                
                print(f"  ... Aguardando Página {pagina_atual} carregar (esperando o botão '{pagina_atual}' ficar ativo)...")
                
                # ESPERA V3 (A "ESPERA INTELIGENTE")
                seletor_pagina_ativa = f"//span[contains(@class, 'ui-paginator-page') and contains(@class, 'ui-state-active') and text() = '{pagina_atual}']"
                wait.until(EC.presence_of_element_located((By.XPATH, seletor_pagina_ativa)))
                
                print(f"  ... Página {pagina_atual} carregada com sucesso.")

            except NoSuchElementException:
                print("  ... Fim da paginação (Botão 'Próxima' desabilitado).")
                break 
            except Exception as e_page:
                print(f"\n--- ERRO AO CARREGAR PÁGINA {pagina_atual} ---")
                print("O site demorou mais de 180s para responder ou o clique foi interceptado.")
                print("O robô vai parar de contar ESTE TERMO e pular para o próximo.")
                print(f"(Detalhe: {e_page})")
                break 

        print(f"\n--- CONCLUÍDOS TODOS OS {indice_global_download} DOWNLOADS PARA: '{termo}' ---")

except Exception as e_geral:
    print(f"\n--- OCORREU UM ERRO GERAL E GRAVE ---")
    print(f"Erro: {e_geral}")

finally:
    if 'driver' in locals():
        driver.quit()
        print("\nRobô DOWNLOADER (Versão Mestre) finalizado.")