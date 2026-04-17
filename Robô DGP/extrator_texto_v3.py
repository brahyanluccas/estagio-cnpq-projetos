import os
import re
import pandas as pd
import pdfplumber
import unicodedata

PASTA_ENTRADA = r"downloads_cnpq"
ARQUIVO_SAIDA = r"Extracao_01_TEXTO_Completo.xlsx"


MODO_TESTE = False 
LIMITE_TESTE = 5 

def normalizar(texto):
    """Remove acentos e converte para minúsculas para facilitar busca"""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()

def extrair_valor_multilinha(linhas, label_procurado):
    """
    Função V4 (Cirúrgica): Extrai valores de linha única ou múltiplas linhas
    com base em listas pré-definidas.
    """
    label_norm = normalizar(label_procurado)
    
    # Lista de rótulos que são SEMPRE de linha única
    single_line_labels = [
        "situacao do grupo:", "ano de formacao:", "data da situacao:", "data do ultimo envio:",
        "unidade:", "logradouro:", "numero:", "complemento:", "bairro:", "uf:", "localidade:",
        "cep:", "latitude:", "longitude:", "telefone:", "fax:", "website:", "contato do grupo:"
    ]
    
    # Lista de rótulos que podem ter MÚLTIPLAS linhas
    multi_line_labels = [
        "lider(es) do grupo:", "area predominante:", "instituicao do grupo:"
    ]

    try:
        # --- LÓGICA PARA CAMPOS DE LINHA ÚNICA ---
        if label_norm in single_line_labels:
            for linha in linhas:
                if normalizar(linha).startswith(label_norm):
                    if ":" in linha:
                        return linha.split(":", 1)[-1].strip()
            return "" # Não encontrou

        # --- LÓGICA PARA CAMPOS DE MÚLTIPLAS LINHAS ---
        if label_norm in multi_line_labels:
            capturando = False
            valores = []
            for linha in linhas:
                if not capturando:
                    if normalizar(linha).startswith(label_norm):
                        capturando = True
                        if ":" in linha:
                            valor = linha.split(":", 1)[-1].strip()
                            if valor: valores.append(valor)
                else: # if capturando
                    if ":" in linha: # Achou um novo rótulo
                         # Exceção: "Longitude:" pode vir logo após "Latitude:"
                         # E "Data do último envio" após "Data da Situação"
                        if not (label_norm == "latitude:" and normalizar(linha).startswith("longitude:")) and \
                           not (label_norm == "data da situacao:" and normalizar(linha).startswith("data do ultimo envio:")):
                            break
                    
                    valores.append(linha.strip())
            return " | ".join(valores).strip() # Usa " | " para separar múltiplas linhas
            
    except Exception as e:
        print(f"  -> Erro ao extrair label '{label_procurado}': {e}")
        
    return "" # Se não for nenhum dos dois, retorna nada

def extrair_multilinha(texto_completo, start_marker, end_marker):
    """Extrai texto entre dois marcadores"""
    try:
        padrao = re.compile(
            re.escape(start_marker) + r"(.*?)" + re.escape(end_marker),
            re.DOTALL | re.IGNORECASE
        )
        match = padrao.search(texto_completo)
        if match:
            texto_limpo = ' '.join(match.group(1).strip().split())
            return texto_limpo
    except Exception:
        pass
    return ""

# --- Execução ---
# Listas separadas para cada ABA do Excel
dados_identificacao = []
dados_endereco = []
dados_contato = []
dados_repressoes = []

print(f"Iniciando PASSO 1 (V4 - MODO COMPLETO): Extração de TODOS os campos de TEXTO...")
print(f"Lendo da pasta: {PASTA_ENTRADA}")

if not os.path.isdir(PASTA_ENTRADA):
    print(f"ERRO: A pasta de entrada '{PASTA_ENTRADA}' não foi encontrada.")
else:
    arquivos_pdf = [f for f in os.listdir(PASTA_ENTRADA) if f.lower().endswith(".pdf")]
    
    if MODO_TESTE:
        print(f"--- MODO DE TESTE ATIVADO ---")
        print(f"Processando apenas os primeiros {LIMITE_TESTE} arquivos.")
        arquivos_pdf = arquivos_pdf[:LIMITE_TESTE] # Pega só os 5 primeiros
    
    total_arquivos = len(arquivos_pdf)
    print(f"Total de {total_arquivos} PDFs para processar.")

    for i, nome_arquivo in enumerate(arquivos_pdf):
        caminho_completo = os.path.join(PASTA_ENTRADA, nome_arquivo)
        print(f"Processando PDF {i+1}/{total_arquivos}: {nome_arquivo}")

        try:
            with pdfplumber.open(caminho_completo) as pdf:
                texto_completo = "\n".join(
                    pagina.extract_text(x_tolerance=2) or "" for pagina in pdf.pages
                )
                linhas = [linha.strip() for linha in texto_completo.split("\n") if linha.strip()]

                # --- !! A IDEIA DO USUÁRIO: Extrair o nome do grupo PRIMEIRO !! ---
                nome_grupo = extrair_multilinha(texto_completo, "Grupo de pesquisa", "Endereço para acessar este espelho:")

                # --- 1. Extrai campos de IDENTIFICAÇÃO (Item 1 e 2 da sua lista) ---
                dados_pdf_id = {
                    "Grupo de pesquisa": nome_grupo,
                    "Situação do grupo": extrair_valor_multilinha(linhas, "Situação do grupo:"),
                    "Ano de formação": extrair_valor_multilinha(linhas, "Ano de formação:"),
                    "Data da Situação": extrair_valor_multilinha(linhas, "Data da Situação:"),
                    "Data do último envio": extrair_valor_multilinha(linhas, "Data do último envio:"),
                    "Líder(es) do grupo": extrair_valor_multilinha(linhas, "Líder(es) do grupo:"),
                    "Área predominante": extrair_valor_multilinha(linhas, "Área predominante:"),
                    "Instituição do grupo": extrair_valor_multilinha(linhas, "Instituição do grupo:"),
                    "Unidade": extrair_valor_multilinha(linhas, "Unidade:"),
                    "Fonte do PDF": nome_arquivo
                }
                dados_identificacao.append(dados_pdf_id)

                # --- 2. Extrai campos de ENDEREÇO (Item 3 e 4) ---
                dados_pdf_end = {
                    "Grupo de pesquisa": nome_grupo,
                    "Logradouro": extrair_valor_multilinha(linhas, "Logradouro:"),
                    "Número": extrair_valor_multilinha(linhas, "Número:"),
                    "Complemento": extrair_valor_multilinha(linhas, "Complemento:"),
                    "Bairro": extrair_valor_multilinha(linhas, "Bairro:"),
                    "UF": extrair_valor_multilinha(linhas, "UF:"),
                    "Localidade": extrair_valor_multilinha(linhas, "Localidade:"),
                    "CEP": extrair_valor_multilinha(linhas, "CEP:"),
                    "Latitude": extrair_valor_multilinha(linhas, "Latitude:"),
                    "Longitude": extrair_valor_multilinha(linhas, "Longitude:"),
                    "Fonte do PDF": nome_arquivo
                }
                dados_endereco.append(dados_pdf_end)

                # --- 3. Extrai campos de CONTATO (Item 5) ---
                dados_pdf_contato = {
                    "Grupo de pesquisa": nome_grupo,
                    "Telefone": extrair_valor_multilinha(linhas, "Telefone:"),
                    "Fax": extrair_valor_multilinha(linhas, "Fax:"),
                    "Website": extrair_valor_multilinha(linhas, "Website:"),
                    "Contato do grupo": extrair_valor_multilinha(linhas, "Contato do grupo:"),
                    "Fonte do PDF": nome_arquivo
                }
                dados_contato.append(dados_pdf_contato)
                
                # --- 4. Extrai REPERCUSSÕES (Item 6) ---
                dados_pdf_rep = {
                    "Grupo de pesquisa": nome_grupo,
                    "Repercussões dos trabalhos do grupo": extrair_multilinha(texto_completo, "Repercussões dos trabalhos do grupo", "Participação em redes de pesquisa"),
                    "Fonte do PDF": nome_arquivo
                }
                dados_repressoes.append(dados_pdf_rep)

        except Exception as e:
            print(f"!!! ERRO no arquivo {nome_arquivo}: {e} !!!")

    # --- SALVANDO TUDO NO EXCEL COM ABAS ---
    print("\nProcessamento concluído. Salvando dados em abas do Excel...")
    try:
        with pd.ExcelWriter(ARQUIVO_SAIDA) as writer:
            # Salva a Aba 1 - Identificação
            df_id = pd.DataFrame(dados_identificacao)
            colunas_id = [
                "Grupo de pesquisa", "Situação do grupo", "Ano de formação",
                "Data da Situação", "Data do último envio", "Líder(es) do grupo", 
                "Área predominante", "Instituição do grupo", "Unidade", "Fonte do PDF"
            ]
            df_id.reindex(columns=colunas_id).to_excel(writer, sheet_name="Identificacao", index=False)
            
            # Salva a Aba 2 - Endereço
            df_end = pd.DataFrame(dados_endereco)
            colunas_end = [
                "Grupo de pesquisa", "Logradouro", "Número", "Complemento", "Bairro", "UF", 
                "Localidade", "CEP", "Latitude", "Longitude", "Fonte do PDF"
            ]
            df_end.reindex(columns=colunas_end).to_excel(writer, sheet_name="Endereco", index=False)
            
            # Salva a Aba 3 - Contato
            df_contato = pd.DataFrame(dados_contato)
            colunas_contato = ["Grupo de pesquisa", "Telefone", "Fax", "Website", "Contato do grupo", "Fonte do PDF"]
            df_contato.reindex(columns=colunas_contato).to_excel(writer, sheet_name="Contato", index=False)
            
            # Salva a Aba 4 - Repercussões
            df_rep = pd.DataFrame(dados_repressoes)
            colunas_rep = ["Grupo de pesquisa", "Repercussões dos trabalhos do grupo", "Fonte do PDF"]
            df_rep.reindex(columns=colunas_rep).to_excel(writer, sheet_name="Repercussoes", index=False)
            
        print(f"\n✅ PASSO 1 (V4 - MODO COMPLETO) CONCLUÍDO! Arquivo salvo em: {ARQUIVO_SAIDA}")

    except PermissionError:
        print(f"\n!!! ERRO DE PERMISSÃO: O arquivo '{ARQUIVO_SAIDA}' já está aberto. Feche o Excel e tente novamente. !!!")
    except Exception as e_save:
        print(f"\n!!! ERRO AO SALVAR O EXCEL: {e_save} !!!")