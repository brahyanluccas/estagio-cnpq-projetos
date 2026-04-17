import os
import pdfplumber
import pandas as pd
import re
import logging
from tqdm import tqdm

logging.getLogger("pdfminer").setLevel(logging.ERROR)

def eh_portugues(texto):
    if not texto: return False
    # Palavras ultra comuns no português que quase não existem no inglês
    palavras_pt = [r'\bdo\b', r'\bda\b', r'\be\b', r'\bou\b', r'\bcom\b', r'\bpara\b', r'\bque\b', r'\bno\b', r'\bna\b']
    pontos = 0
    for p in palavras_pt:
        if re.search(p, texto.lower()): pontos += 1
    # Se achar pelo menos 3 palavras típicas, assumimos que é PT-BR
    return pontos >= 3

def limpar_texto(texto):
    if not texto: return ""
    # Remove marcas de página e sujeira administrativa
    texto = re.sub(r"P[ÁA]GINA\s+\d+\s+[/DE]+\s+\d+", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"R\$\s?[\d.,]+", "", texto)
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    return re.sub(r'\s+', ' ', texto).strip()

def extrair_v30(caminho_pdf, pasta):
    proc = os.path.basename(caminho_pdf).replace(".pdf", "")
    titulo, resumo = "Não encontrado", "Não encontrado"
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            # Lemos até 60 páginas (para garantir casos de 2014 com muitos anexos)
            texto_todo = ""
            paginas = pdf.pages[:60]
            for p in paginas:
                txt = p.extract_text()
                if txt: texto_todo += txt + "\n"

        texto_up = texto_todo.upper()

        # --- CAÇA AO TÍTULO (Várias tentativas) ---
        marcos_t = ["TÍTULO (EM PORTUGUÊS):", "TÍTULO DO PROJETO:", "TÍTULO:", "NOME DO PROJETO:"]
        for m in marcos_t:
            if m in texto_up:
                ini = texto_up.find(m) + len(m)
                fim = len(texto_todo)
                for trava in ["TÍTULO (EM INGLÊS)", "SIGLA", "COORDENADOR", "RESUMO", "PALAVRAS-CHAVE"]:
                    idx = texto_up.find(trava, ini)
                    if idx != -1 and idx < fim: fim = idx
                titulo = texto_todo[ini:fim]
                break
        
        # Se o título vazar datas ou for muito longo, limpamos
        titulo = re.sub(r"(INÍCIO:|DURAÇÃO:).*?\d+", "", titulo, flags=re.IGNORECASE)

        # --- CAÇA AO RESUMO (Lógica de Segmentação e Idioma) ---
        # 1. Tenta achar pelos marcadores tradicionais (de trás para frente)
        pos_r = -1
        for m in ["RESUMO (PORTUGUÊS)", "RESUMO EXECUTIVO", "RESUMO:", "VIDE PROJETO", "RESUMO"]:
            idx = texto_up.rfind(m) # Busca a última ocorrência
            if idx != -1:
                # Checa se o que vem depois é PT ou EN
                if eh_portugues(texto_todo[idx:idx+400]):
                    pos_r = idx
                    if "VIDE PROJETO" not in m: pos_r += len(m)
                    break

        if pos_r != -1:
            trecho = texto_todo[pos_r:]
            fim_r = len(trecho)
            muros = ["\nOBJETIVOS", "\nEQUIPE", "\nCUSTEIO", "\nMETAS", "\nATIVIDADE ECONÔMICA", "\nABSTRACT", "\nSUMMARY"]
            for muro in muros:
                idx = trecho.upper().find(muro)
                if idx != -1 and idx < fim_r and idx > 50: 
                    fim_r = idx
            resumo = trecho[:fim_r]

        # 2. SEGUNDA CHANCE (Se continuou vazio ou pegou inglês): 
        # Busca o maior bloco de texto corrido que seja Português
        if "NÃO ENCONTRADO" in resumo.upper() or len(resumo) < 150 or not eh_portugues(resumo):
            blocos = texto_todo.split('\n\n')
            # Ordena pelos maiores blocos de texto
            for b in sorted(blocos, key=len, reverse=True):
                if len(b) > 250 and eh_portugues(b) and "R$" not in b:
                    resumo = b
                    break

    except:
        return {"Processo": proc, "Título": "Erro", "Resumo": "Erro", "Ano": pasta}

    return {
        "Processo": proc,
        "Título": limpar_texto(titulo),
        "Resumo": limpar_texto(resumo),
        "Ano": pasta
    }

# --- EXECUÇÃO ---
pastas = ["INCT 2008", "INCT 2010", "INCT 2014"]
final_data = []
for p in pastas:
    if os.path.exists(p):
        arquivos = [f for f in os.listdir(p) if f.lower().endswith(".pdf")]
        for arq in tqdm(arquivos, desc=f"Processando {p}"):
            final_data.append(extrair_v30(os.path.join(p, arq), p))

pd.DataFrame(final_data).to_excel("RESULTADO_UNIVERSAL_V30.xlsx", index=False)