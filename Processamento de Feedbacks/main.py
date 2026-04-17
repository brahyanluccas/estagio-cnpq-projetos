import pandas as pd
import spacy
from pysentimiento import create_analyzer
from collections import Counter
import os

# Configurações
ARQUIVO_ENTRADA = "Dados Pesquisa por questões (1).xls"
ARQUIVO_SAIDA = "Relatorio Dados Pesquisa.xlsx"

print("🤖 Inicializando IA e preparando estrutura do relatório...")
analyzer = create_analyzer(task="sentiment", lang="pt")
nlp = spacy.load("pt_core_news_sm")

GATILHOS_MELHORIA = ["melhorar", "sugiro", "sugestão", "poderia", "seria bom", "falta", "ajustar", "deveria"]

def analisar_termo(termo):
    termo_str = str(termo).lower()
    if any(g in termo_str for g in GATILHOS_MELHORIA):
        return "M"
    res = analyzer.predict(termo_str)
    mapa = {"POS": "P", "NEG": "N", "NEU": "NT"}
    return mapa.get(res.output, "NT")

def extrair_termos(texto):
    if not texto or pd.isna(texto): return []
    doc = nlp(str(texto).lower())
    termos = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            adjs = [child.text for child in token.children if child.pos_ == "ADJ"]
            if adjs:
                for adj in adjs: termos.append(f"{token.text} {adj}")
            elif len(token.text) > 3: termos.append(token.text)
        elif token.pos_ == "ADJ" and len(token.text) > 3:
            termos.append(token.text)
    return list(dict.fromkeys(termos))[:6]

def processar():
    xls_leitura = pd.ExcelFile(ARQUIVO_ENTRADA)
    writer = pd.ExcelWriter(ARQUIVO_SAIDA, engine='openpyxl')

    for aba in xls_leitura.sheet_names:
        print(f"📊 Processando aba: {aba}...")
        
        # 1. Captura a Pergunta (está na linha 1 do arquivo original)
        df_pergunta = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=aba, header=None, nrows=2)
        texto_pergunta = str(df_pergunta.iloc[1, 0]) # Pega o valor da Linha 1

        # 2. Carrega os dados reais (começam na linha 3/header=3)
        df_dados = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=aba, header=3)
        df_dados = df_dados.dropna(subset=['Resposta'])

        col_palavras_chave = []
        qtd_p, qtd_n, qtd_nt, qtd_m = [], [], [], []

        for texto in df_dados['Resposta']:
            termos_extraidos = extrair_termos(texto)
            termos_formatados = []
            contagem_linha = Counter()

            for t in termos_extraidos:
                sent = analisar_termo(t)
                termos_formatados.append(f"{t} ({sent})")
                contagem_linha[sent] += 1
            
            col_palavras_chave.append(", ".join(termos_formatados))
            qtd_p.append(contagem_linha['P'])
            qtd_n.append(contagem_linha['N'])
            qtd_nt.append(contagem_linha['NT'])
            qtd_m.append(contagem_linha['M'])

        # Adiciona as novas colunas
        df_dados['Palavras Chave'] = col_palavras_chave
        df_dados['Qtd Positivo'] = qtd_p
        df_dados['Qtd Negativo'] = qtd_n
        df_dados['Qtd Neutro'] = qtd_nt
        df_dados['Qtd Melhoria'] = qtd_m

        # 3. ESCREVENDO NO EXCEL COM O CABEÇALHO PERSONALIZADO
        # Escreve a legenda na Linha 1
        legenda = "LEGENDA: (P) Positivo | (N) Negativo | (NT) Neutro | (M) Sugestão ou Melhoria"
        pd.DataFrame([legenda]).to_excel(writer, sheet_name=aba, startrow=0, index=False, header=False)
        
        # Escreve a Pergunta na Linha 2
        pd.DataFrame([f"PERGUNTA: {texto_pergunta}"]).to_excel(writer, sheet_name=aba, startrow=1, index=False, header=False)

        # Escreve a tabela de dados começando na Linha 4 (startrow=3)
        df_dados.to_excel(writer, sheet_name=aba, startrow=3, index=False)

    writer.close()
    print(f"\n✅ Relatório Final Gerado com Sucesso!")
    print(f"📁 Local: {os.path.abspath(ARQUIVO_SAIDA)}")

if __name__ == "__main__":
    processar()