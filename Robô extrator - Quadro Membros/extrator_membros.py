import pdfplumber
import pandas as pd
import os
import re

caminho_base = r'C:\Users\brahyan.souza\Documents\Robô extrator - Quadro Membros'

def limpar(texto):
    if not texto: return ""
    return " ".join(texto.split()).strip()

def extrair_quadro_geral():
    lista_final = []
    pasta_2014 = os.path.join(caminho_base, 'INCT 2014')
    
    if not os.path.exists(pasta_2014):
        print("❌ Pasta INCT 2014 não encontrada!")
        return

    # Agora o robô vai ler TUDO o que estiver na pasta
    arquivos = [f for f in os.listdir(pasta_2014) if f.endswith('.pdf')]
    print(f"🔍 Iniciando processamento total de {len(arquivos)} arquivos de 2014...")

    for arquivo in arquivos:
        nome_processo = arquivo.replace('.pdf', '')
        encontrou_dados = False
        
        with pdfplumber.open(os.path.join(pasta_2014, arquivo)) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t: texto_completo += t + "\n"
            
            secao = re.search(r'Quadro\s*Geral\s*\n(.*?)(?=RESUMO|Este documento|$)', texto_completo, re.DOTALL | re.IGNORECASE)
            
            if secao:
                bloco = secao.group(1)
                linhas = bloco.split('\n')
                
                temp_categoria = ""
                temp_quantidade = None
                
                for linha in linhas:
                    linha = linha.strip()
                    
                    # Filtro de rodapé: Ignora o texto que começa com (*)
                    if any(obs in linha.upper() for obs in ["(*)", "LISTA DETALHADA", "MEMBROS DA EQUIPE"]):
                        break

                    if not linha or any(x in linha.upper().replace(" ", "") for x in ["CATEGORIA", "NÚMERODE", "PARTICIPANTES", "PÁGINA"]):
                        continue
                    
                    # Procura o número da quantidade no final da linha
                    match_num = re.search(r'\s+(\d+)$', linha)
                    
                    if match_num:
                        if temp_categoria and temp_quantidade is not None:
                            lista_final.append({'Processo': nome_processo, 'Categoria': limpar(temp_categoria), 'Quantidade': temp_quantidade})
                            encontrou_dados = True
                        
                        temp_quantidade = int(match_num.group(1))
                        temp_categoria = linha[:match_num.start()].strip()
                    else:
                        # Acumula o texto (resolve a quebra do "Tecnológica")
                        temp_categoria += " " + linha
                
                # Salva o último item do bloco
                if temp_categoria and temp_quantidade is not None:
                    if "LISTA DETALHADA" not in temp_categoria.upper():
                        lista_final.append({'Processo': nome_processo, 'Categoria': limpar(temp_categoria), 'Quantidade': temp_quantidade})
                        encontrou_dados = True
            
        if encontrou_dados:
            print(f"✅ {nome_processo}: OK")
        else:
            lista_final.append({'Processo': nome_processo, 'Categoria': 'REVISÃO MANUAL', 'Quantidade': 0})
            print(f"⚠️ {nome_processo}: Requer atenção.")

    if lista_final:
        df = pd.DataFrame(lista_final)
        df_pivot = df.pivot_table(index='Processo', columns='Categoria', values='Quantidade', aggfunc='sum').fillna(0)
        df_pivot = df_pivot.astype(int)
        
        # Soma total ignorando a coluna de erro
        colunas_validas = [c for c in df_pivot.columns if c != 'REVISÃO MANUAL']
        df_pivot['Total Geral'] = df_pivot[colunas_validas].sum(axis=1)
        
        df_pivot.to_excel('Relatorio_Final_INCT_2014.xlsx')
        print(f"\n🚀 FINALIZADO! {len(arquivos)} processos processados.")
        print("Planilha gerada: Relatorio_Final_INCT_2014.xlsx")

if __name__ == "__main__":
    extrair_quadro_geral()