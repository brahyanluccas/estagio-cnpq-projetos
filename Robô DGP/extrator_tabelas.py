import os
import re
import pandas as pd
import pdfplumber
import unicodedata

# === CONFIGURAÇÕES ===
PASTA_ENTRADA = r"downloads_cnpq"
ARQUIVO_SAIDA = r"Extracao_02_TABELAS_Completo.xlsx"

# === MODO DE TESTE (Desativado para o lote completo) ===
MODO_TESTE = False # <<< VERSÃO FINAL
LISTA_PREFIXOS_TESTE = [
    "agricultura_sustentável_0002_agricultura_sustentável_práticas_culturais_fitossanidade_e_p",
    "ecologia_0725_núcleo_de_pesquisa_científica_e_tecnológica_em_meio_ambiente"
]
# ==================================

def limpar_texto_quebrado(texto):
    """
    Função CHAVE V3: Limpa o texto "quebrado" (ex: "NNíívveell ddee...")
    """
    if not texto:
        return ""
    try:
        texto = texto.replace('\n', ' ')
        
        texto_dedup = texto
        for _ in range(3): # Corre 3x para garantir (ex: 'LLLL' -> 'LL' -> 'L')
            texto_dedup = re.sub(r'(.)\1', r'\1', texto_dedup, flags=re.IGNORECASE)

        texto_norm = ''.join(c for c in unicodedata.normalize('NFD', texto_dedup)
                           if unicodedata.category(c) != 'Mn')
        
        texto_limpo = re.sub(r'[\s/]+', '', texto_norm)
        return texto_limpo.lower()
    except Exception as e:
        print(f"  -> ERRO limpando texto: {e}")
        return ""

def extrair_nome_grupo(texto_completo):
    """Extrai o nome do grupo (para usarmos como chave)"""
    try:
        padrao = re.compile(
            r"Grupo de pesquisa(.*?)(Endereço para acessar este espelho:)",
            re.DOTALL | re.IGNORECASE
        )
        match = padrao.search(texto_completo)
        if match:
            return ' '.join(match.group(1).strip().split())
    except Exception:
        pass
    return "NOME DO GRUPO NÃO ENCONTRADO"

# --- Execução ---
# Listas para as abas
dados_redes_pesquisa = []
dados_linhas_pesquisa = []
dados_indicadores_rh = []
dados_inst_parceiras = [] 
dados_inct_parceiras = [] 

# Listas CONSOLIDADAS para RH e Egressos
dados_rh_CONSOLIDADO = []
dados_egressos_CONSOLIDADO = []

print(f"Iniciando PASSO 2 (V12 - MODO COMPLETO): Extração de TODAS as TABELAS...")
print(f"Lendo da pasta: {PASTA_ENTRADA}")

if not os.path.isdir(PASTA_ENTRADA):
    print(f"ERRO: A pasta de entrada '{PASTA_ENTRADA}' não foi encontrada.")
else:
    arquivos_pdf_pasta = [f for f in os.listdir(PASTA_ENTRADA) if f.lower().endswith(".pdf")]
    arquivos_pdf = [] # Lista final de PDFs a processar

    if MODO_TESTE:
        print(f"--- MODO DE TESTE ATIVADO (Focado) ---")
        arquivos_pdf_teste = [] # Inicializa a lista de teste
        
        for prefixo in LISTA_PREFIXOS_TESTE:
            prefixo_limpo = prefixo.lower().replace(".pdf", "")
            encontrado = False
            for f_real in arquivos_pdf_pasta:
                if f_real.lower().startswith(prefixo_limpo):
                    arquivos_pdf_teste.append(f_real)
                    encontrado = True
                    break
            if not encontrado:
                print(f"  -> AVISO: Nenhum arquivo começando com '{prefixo}' foi encontrado.")
        
        arquivos_pdf = list(set(arquivos_pdf_teste)) # Remove duplicatas se houver
    
    else:
        print(f"--- MODO COMPLETO ATIVADO ---")
        arquivos_pdf = arquivos_pdf_pasta # Modo completo
    
    total_arquivos = len(arquivos_pdf)

    if total_arquivos == 0:
        print(f"ERRO: Nenhum PDF encontrado para processar.")
    else:
        print(f"Total de {total_arquivos} PDFs para processar.")

    for i, nome_arquivo in enumerate(arquivos_pdf):
        caminho_completo = os.path.join(PASTA_ENTRADA, nome_arquivo)
        print(f"Processando PDF {i+1}/{total_arquivos}: {nome_arquivo}")

        try:
            with pdfplumber.open(caminho_completo) as pdf:
                
                nome_grupo = "NOME NÃO ENCONTRADO"
                try:
                    texto_pagina_1 = pdf.pages[0].extract_text(x_tolerance=2) or ""
                    nome_grupo = extrair_nome_grupo(texto_pagina_1)
                except Exception as e_nome:
                    print(f"  -> Aviso: Não foi possível extrair nome do grupo: {e_nome}")

                for num_pagina, pagina in enumerate(pdf.pages):
                    
                    tabelas_na_pagina = pagina.extract_tables(table_settings={
                        "text_x_tolerance": 2,
                        "vertical_strategy": "lines", 
                        "horizontal_strategy": "lines",
                    })
                    
                    for tabela in tabelas_na_pagina:
                        if not tabela or not tabela[0] or len(tabela[0]) < 2:
                            continue
                        
                        cabecalho = [limpar_texto_quebrado(cel) for cel in tabela[0]]
                        
                        # --- 1. Tabela "Participação em redes de pesquisa" (Item 7) ---
                        if "rededepesquisa" in cabecalho and "websiteblog" in cabecalho:
                            print(f"  -> Tabela 'Rede de Pesquisa' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "nomedalinhadepesquisa" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_redes_pesquisa.append({
                                        "Grupo de pesquisa": nome_grupo,
                                        "Rede de pesquisa": linha[0],
                                        "Website/Blog": linha[1],
                                        "Fonte do PDF": nome_arquivo
                                    })

                        # --- 2. Tabela "Linhas de pesquisa" (Item 8) ---
                        elif "nomedalinhadepesquisa" in cabecalho and "quantidadedeestudantes" in cabecalho:
                            print(f"  -> Tabela 'Linhas de Pesquisa' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "recursoshumanos" in [limpar_texto_quebrado(cel) for cel in linha] or "pesquisadores" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0]:
                                    dados_linhas_pesquisa.append({
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome da linha de pesquisa": linha[0],
                                        "Quantidade de Estudantes": linha[1],
                                        "Quantidade de Pesquisadores": linha[2],
                                        "Fonte do PDF": nome_arquivo
                                    })

                        # --- 3. Tabela "RH - Pesquisadores" (Item 8b) ---
                        elif "pesquisadores" in cabecalho and "titulacaomaxima" in cabecalho:
                            print(f"  -> Tabela 'RH - Pesquisadores' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "estudantes" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_rh_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Pesquisador", 
                                        "Titulação/Formação": linha[1], 
                                        "País": None,
                                        "Data inclusão": linha[2],
                                        "Fonte do PDF": nome_arquivo
                                    })

                        # --- 4. Tabela "RH - Estudantes" (Item 8b) ---
                        elif "estudantes" in cabecalho and ("niveltreinamento" in cabecalho or "niveldetreinamento" in cabecalho):
                            print(f"  -> Tabela 'RH - Estudantes' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "tecnicos" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_rh_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Estudante", 
                                        "Titulação/Formação": linha[1], 
                                        "País": None,
                                        "Data inclusão": linha[2],
                                        "Fonte do PDF": nome_arquivo
                                    })
                        
                        # --- 9. Tabela "Indicadores de RH" (Item 10) ---
                        elif "formacaoacademica" in cabecalho and "pesquisadores" in cabecalho and "total" in cabecalho:
                            print(f"  -> Tabela 'Indicadores de RH' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if linha[0]:
                                    dados_indicadores_rh.append({
                                        "Grupo de pesquisa": nome_grupo,
                                        "Formação acadêmica": linha[0],
                                        "Pesquisadores": linha[1],
                                        "Estudantes": linha[2],
                                        "Técnicos": linha[3],
                                        "Colaboradores estrangeiros": linha[4],
                                        "Total": linha[5],
                                        "Fonte do PDF": nome_arquivo
                                    })

                        # --- 5. Tabela "RH - Técnicos" (Item 8b) ---
                        elif "tecnicos" in cabecalho and "formacaoacademica" in cabecalho:
                            print(f"  -> Tabela 'RH - Técnicos' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                primeira_coluna_limpa = limpar_texto_quebrado(linha[0])
                                
                                if "colaboradoresestrangeiros" in primeira_coluna_limpa or \
                                   "egressos" in primeira_coluna_limpa or \
                                   "instituicoesparceiras" in primeira_coluna_limpa or \
                                   "indicadoresderecursoshumanos" in primeira_coluna_limpa or \
                                   "formacaoacademica" in primeira_coluna_limpa or \
                                   "doutorado" in primeira_coluna_limpa or \
                                   "mestrado" in primeira_coluna_limpa or \
                                   "graduacao" in primeira_coluna_limpa or \
                                   "outros" in primeira_coluna_limpa:
                                    
                                    print(f"    -> 'Data bleed' detectado em RH-Técnicos (linha: {linha[0]}). Parando.")
                                    break # PARA
                                
                                if linha[0] and "nenhumregistroadicionado" not in primeira_coluna_limpa:
                                    dados_rh_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Técnico", 
                                        "Titulação/Formação": linha[1], 
                                        "País": None,
                                        "Data inclusão": linha[2],
                                        "Fonte do PDF": nome_arquivo
                                    })

                        # --- 6. Tabela "RH - Colaboradores" (Item 8b) ---
                        elif "colaboradoresestrangeiros" in cabecalho and "pais" in cabecalho:
                            print(f"  -> Tabela 'RH - Colaboradores' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "egressos" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_rh_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Colaborador Estrangeiro", 
                                        "Titulação/Formação": None,
                                        "País": linha[1], 
                                        "Data inclusão": linha[2],
                                        "Fonte do PDF": nome_arquivo
                                    })
                        
                        # --- 7. Tabela "Egressos - Pesquisadores" (Item 9) ---
                        elif "pesquisadores" in cabecalho and "periododeparticipacaonogrupo" in cabecalho:
                            print(f"  -> Tabela 'Egressos - Pesquisadores' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "estudantes" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_egressos_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Pesquisador", # <<< SUA IDEIA
                                        "Período de participação": linha[1],
                                        "Fonte do PDF": nome_arquivo
                                    })
                        
                        # --- 8. Tabela "Egressos - Estudantes" (Item 9) ---
                        elif "estudantes" in cabecalho and "periododeparticipacaonogrupo" in cabecalho:
                            print(f"  -> Tabela 'Egressos - Estudantes' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "instituicoesparceiras" in [limpar_texto_quebrado(cel) for cel in linha] or "nomedainstituicaoparceira" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_egressos_CONSOLIDADO.append({ 
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome": linha[0],
                                        "Participação no Grupo": "Estudante", # <<< SUA IDEIA
                                        "Período de participação": linha[1],
                                        "Fonte do PDF": nome_arquivo
                                    })
                        
                        # --- 10. NOVA Tabela "Instituições Parceiras" ---
                        elif ("nomedainstituicaoparceira" in cabecalho) and "sigla" in cabecalho:
                            print(f"  -> Tabela 'Instituições Parceiras' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "inctsparceiras" in [limpar_texto_quebrado(cel) for cel in linha] or "nomedainctparceira" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    try:
                                        dados_inst_parceiras.append({
                                            "Grupo de pesquisa": nome_grupo,
                                            "Nome da Instituição Parceira": linha[0],
                                            "Sigla": linha[1],
                                            "UF": linha[2],
                                            "Ações": linha[3],
                                            "Fonte do PDF": nome_arquivo
                                        })
                                    except IndexError:
                                        col_count = len(linha)
                                        dados_linha = {
                                            "Grupo de pesquisa": nome_grupo,
                                            "Nome da Instituição Parceira": linha[0] if col_count > 0 else None,
                                            "Sigla": linha[1] if col_count > 1 else None,
                                            "UF": linha[2] if col_count > 2 else None,
                                            "Ações": linha[3] if col_count > 3 else None,
                                            "Fonte do PDF": nome_arquivo
                                        }
                                        dados_inst_parceiras.append(dados_linha)
                                        print(f"    -> Aviso: Linha mal formada em 'Instituições Parceiras' (colunas: {col_count}). Capturando parcialmente.")

                        # --- 11. NOVA Tabela "INCTs Parceiras" ---
                        elif "nomedainctparceira" in cabecalho:
                            print(f"  -> Tabela 'INCTs Parceiras' encontrada na Pág. {num_pagina+1}")
                            for linha in tabela[1:]:
                                if "indicadoresderecursoshumanos" in [limpar_texto_quebrado(cel) for cel in linha]:
                                    break
                                if linha[0] and "nenhumregistroadicionado" not in limpar_texto_quebrado(linha[0]):
                                    dados_inct_parceiras.append({
                                        "Grupo de pesquisa": nome_grupo,
                                        "Nome da INCT Parceira": linha[0],
                                        "Fonte do PDF": nome_arquivo
                                    })

        except Exception as e:
            if "CropBox missing" not in str(e): # Ignora o aviso de CropBox
                print(f"!!! ERRO no arquivo {nome_arquivo}: {e} !!!")

    # --- SALVANDO TUDO NO EXCEL COM ABAS ---
    print("\nProcessamento de tabelas concluído. Salvando dados em abas do Excel...")
    try:
        listas_de_dados = [
            dados_redes_pesquisa, dados_linhas_pesquisa, dados_rh_CONSOLIDADO,
            dados_egressos_CONSOLIDADO, dados_indicadores_rh,
            dados_inst_parceiras, dados_inct_parceiras
        ]
        
        if not any(listas_de_dados):
            raise ValueError("Nenhuma tabela de interesse foi encontrada nos arquivos.")

        with pd.ExcelWriter(ARQUIVO_SAIDA) as writer:
            
            def salvar_aba(df_list, sheet_name):
                if df_list:
                    print(f"  -> Salvando aba '{sheet_name}'...")
                    pd.DataFrame(df_list).to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    print(f"  -> Aba '{sheet_name}' vazia, pulando.")

            salvar_aba(dados_redes_pesquisa, "Redes de Pesquisa")
            salvar_aba(dados_linhas_pesquisa, "Linhas de Pesquisa")
            
            # --- Renomeado para ficar como você pediu ---
            if dados_rh_CONSOLIDADO:
                print(f"  -> Salvando aba 'Recursos Humanos'...") 
                df_rh = pd.DataFrame(dados_rh_CONSOLIDADO)
                colunas_rh = [
                    "Grupo de pesquisa", "Nome", "Participação no Grupo", 
                    "Titulação/Formação", "País", "Data inclusão", "Fonte do PDF"
                ]
                df_rh = df_rh.reindex(columns=colunas_rh)
                df_rh.to_excel(writer, sheet_name="Recursos Humanos", index=False) 
            else:
                 print(f"  -> Aba 'Recursos Humanos' vazia, pulando.")

            if dados_egressos_CONSOLIDADO:
                print(f"  -> Salvando aba 'Egressos'...") 
                df_egr = pd.DataFrame(dados_egressos_CONSOLIDADO)
                colunas_egr = ["Grupo de pesquisa", "Nome", "Participação no Grupo", "Período de participação", "Fonte do PDF"]
                df_egr = df_egr.reindex(columns=colunas_egr)
                df_egr.to_excel(writer, sheet_name="Egressos", index=False) 
            else:
                 print(f"  -> Aba 'Egressos' vazia, pulando.")

            salvar_aba(dados_indicadores_rh, "Indicadores de RH")
            salvar_aba(dados_inst_parceiras, "Inst. Parceiras")
            salvar_aba(dados_inct_parceiras, "INCTs Parceiras")
            
        print(f"\n✅ PASSO 2 (V12 - MODO COMPLETO) CONCLUÍDO! Arquivo salvo em: {ARQUIVO_SAIDA}")

    except PermissionError:
        print(f"\n!!! ERRO DE PERMISSÃO: O arquivo '{ARQUIVO_SAIDA}' já está aberto. Feche o Excel e tente novamente. !!!")
    except ValueError as e:
        print(f"\n!!! ERRO: {e} !!!") 
    except Exception as e_save:
        print(f"\n!!! ERRO AO SALVAR O EXCEL: {e_save} !!!")