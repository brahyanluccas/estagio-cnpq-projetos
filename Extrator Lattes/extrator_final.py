import pandas as pd
import numpy as np
import zipfile
import io
import time
import xml.etree.ElementTree as ET
from zeep import Client

# =====================================================================
# CONFIGURAÇÕES INICIAIS
# =====================================================================
WSDL_URL = 'http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl'

# COLOQUE O NOME DAS SUAS DUAS (OU MAIS) PLANILHAS AQUI
ARQUIVOS_ENTRADA = ['consolidada_inova_talentos (1).xlsx', 'relatório Karina - Inova Talentos.xlsx'] 
COLUNA_ID = 'id_lattes'

def extrair_dados_lattes(id_lattes, client):
    # =====================================================================
    # DICIONÁRIO OFICIAL INOVA TALENTOS (TODAS AS COLUNAS DO WORD)
    # =====================================================================
    curriculo = {
        'NUMERO-IDENTIFICADOR': str(id_lattes),
        'NOME-COMPLETO': '', 'NOME-EM-CITACOES-BIBLIOGRAFICAS': '', 'PAIS-DE-NASCIMENTO': '', 
        'UF-NASCIMENTO': '', 'CIDADE-NASCIMENTO': '', 'DATA-NASCIMENTO': '', 'ANO-DE-NASCIMENTO': '', 
        'SEXO': '', 'NACIONALIDADE': '',
        'NOME-INSTITUICAO': '', 'UF-INSTITUICAO': '', 'CIDADE-INSTITUICAO': '', 'PAIS-INSTITUICAO': '',
        
        'NOME-CURSO-GRADUACAO': '', 'CODIGO-CURSO-CAPES': '', 'NOME-INSTITUICAO-GRADUACAO': '', 
        'CODIGO-INSTITUICAO': '', 'ANO-DE-INICIO-GRADUACAO': '', 'ANO-DE-CONCLUSAO-GRADUACAO': '', 
        'STATUS-DO-CURSO-GRAD': '', 'UF-INSTITUICAO-GRADUACAO': '', 'PAIS-INSTITUICAO-GRADUACAO': '', 
        'FLAG-BOLSA-GRAD': '', 'TIPO-BOLSA-GRAD': '', 'ENTIDADE-BOLSA-GRAD': '',
        
        'NOME-CURSO-MESTRADO': '', 'CODIGO-PROGRAMA-CAPES-MEST': '', 'NOME-INSTITUICAO-MESTRADO': '', 
        'ANO-DE-INICIO-MESTRADO': '', 'ANO-DE-CONCLUSAO-MESTRADO': '', 'STATUS-DO-CURSO-MEST': '', 
        'TIPO-MESTRADO': '', 'UF-INSTITUICAO-MESTRADO': '', 'PAIS-INSTITUICAO-MESTRADO': '',
        
        'NOME-CURSO-DOUTORADO': '', 'CODIGO-PROGRAMA-CAPES-DOUT': '', 'NOME-INSTITUICAO-DOUTORADO': '', 
        'ANO-DE-INICIO-DOUTORADO': '', 'ANO-DE-CONCLUSAO-DOUTORADO': '', 'STATUS-DO-CURSO-DOUT': '', 
        'UF-INSTITUICAO-DOUTORADO': '', 'PAIS-INSTITUICAO-DOUTORADO': '',

        'GRANDE-AREA-DO-CONHECIMENTO': '', 'AREA-DO-CONHECIMENTO': '', 'SUBAREA-DO-CONHECIMENTO': '', 
        'ESPECIALIDADE': '', 'SETOR-DE-APLICACAO': '',

        'NOME-INSTITUICAO-EMPREGO': '', 'TIPO-INSTITUICAO': '', 'NATUREZA-INSTITUICAO': '', 
        'ANO-INICIO-EMPREGO': '', 'MES-INICIO-EMPREGO': '', 'ANO-FIM-EMPREGO': '', 'MES-FIM-EMPREGO': '', 
        'CARGO-OU-FUNCAO': '', 'FLAG-EMPREGO-EMPRESA-PRIVADA': '', 'UF-INSTITUICAO-EMPREGO': '', 
        'PAIS-INSTITUICAO-EMPREGO': '', 'CNPJ-INSTITUICAO': '', 'DESCRICAO-ATIVIDADE': '', 'FLAG-ATIVIDADE-PD': '',
        'TITULO-LINHA-DE-PESQUISA': '', 'OBJETIVO-LINHA': '',

        'TITULO-PATENTE': '', 'ANO-DEPOSITO-PATENTE': '', 'NUMERO-DEPOSITO': '', 'CATEGORIA-PATENTE': '', 
        'FLAG-PATENTE-CONCEDIDA': '', 'TITULAR-PATENTE': '', 'PAIS-PATENTE': '',

        'TITULO-SOFTWARE': '', 'ANO-SOFTWARE': '', 'FLAG-REGISTRO-SOFTWARE': '',
        'TITULO-PRODUTO-TECN': '', 'TIPO-PRODUTO-TECN': '', 'ANO-PRODUTO-TECN': '',
        'TITULO-PROCESSO-TECNICA': '', 'ANO-PROCESSO': '',

        'TITULO-TRABALHO-TECNICO': '', 'ANO-TRABALHO-TECNICO': '', 'TIPO-TRABALHO-TECNICO': '',
        'TITULO-TRANSF-TECNOLOGIA': '', 'ANO-TRANSF-TECNOLOGIA': '', 'EMPRESA-RECEPTORA': ''
    }

    try:
        resposta_bytes = client.service.getCurriculoCompactado(id=id_lattes)
        if not resposta_bytes:
            return curriculo
            
        with zipfile.ZipFile(io.BytesIO(resposta_bytes)) as z:
            with z.open(z.namelist()[0]) as f:
                root = ET.parse(f).getroot()

        # =====================================================================
        # MAPEAMENTO DE INSTITUIÇÕES (A CAIXA PRETA DAS UFs E PAÍSES)
        # =====================================================================
        mapa_inst = {}
        for info in root.findall('.//INFORMACAO-ADICIONAL-INSTITUICAO'):
            cod = info.get('CODIGO-INSTITUICAO')
            if cod:
                mapa_inst[cod] = {
                    'UF': info.get('SIGLA-UF-INSTITUICAO', ''),
                    'PAIS': info.get('NOME-PAIS-INSTITUICAO', '')
                }

        # =====================================================================
        # GRUPO 1: DADOS PESSOAIS E ENDEREÇO
        # =====================================================================
        gerais = root.find('.//DADOS-GERAIS')
        if gerais is not None:
            curriculo['NOME-COMPLETO'] = gerais.get('NOME-COMPLETO', '')
            curriculo['NOME-EM-CITACOES-BIBLIOGRAFICAS'] = gerais.get('NOME-EM-CITACOES-BIBLIOGRAFICAS', '')
            curriculo['PAIS-DE-NASCIMENTO'] = gerais.get('PAIS-DE-NASCIMENTO', '')
            curriculo['UF-NASCIMENTO'] = gerais.get('UF-NASCIMENTO', '')
            curriculo['CIDADE-NASCIMENTO'] = gerais.get('CIDADE-NASCIMENTO', '')
            curriculo['NACIONALIDADE'] = gerais.get('NACIONALIDADE', '')
            curriculo['SEXO'] = gerais.get('SEXO', '')
            
            data_nasc = gerais.get('DATA-NASCIMENTO', '')
            curriculo['DATA-NASCIMENTO'] = data_nasc
            if len(data_nasc) == 8:
                curriculo['ANO-DE-NASCIMENTO'] = data_nasc[-4:]

        end_prof = root.find('.//ENDERECO-PROFISSIONAL')
        if end_prof is not None:
            curriculo['NOME-INSTITUICAO'] = end_prof.get('NOME-INSTITUICAO-EMPRESA', '')
            curriculo['PAIS-INSTITUICAO'] = end_prof.get('PAIS', '')
            curriculo['UF-INSTITUICAO'] = end_prof.get('UF', '')
            curriculo['CIDADE-INSTITUICAO'] = end_prof.get('CIDADE', '')

        # =====================================================================
        # GRUPO 2: FORMAÇÃO ACADÊMICA
        # =====================================================================
        # GRADUAÇÃO
        l_cur_g, l_codc_g, l_inst_g, l_codi_g, l_anoi_g, l_anof_g, l_stat_g, l_bol_g, l_tipo_b, l_age_g, l_uf_g, l_pais_g = [], [], [], [], [], [], [], [], [], [], [], []
        for grad in root.findall('.//GRADUACAO'):
            cod_inst = grad.get('CODIGO-INSTITUICAO', '')
            l_cur_g.append(grad.get('NOME-CURSO', ''))
            l_codc_g.append(grad.get('CODIGO-CURSO', ''))
            l_inst_g.append(grad.get('NOME-INSTITUICAO', ''))
            l_codi_g.append(cod_inst)
            l_anoi_g.append(grad.get('ANO-DE-INICIO', ''))
            l_anof_g.append(grad.get('ANO-DE-CONCLUSAO', ''))
            l_stat_g.append(grad.get('STATUS-DO-CURSO', ''))
            bolsa = grad.get('FLAG-BOLSA', 'NAO')
            l_bol_g.append(bolsa)
            l_tipo_b.append('Bolsa de Graduação' if bolsa == 'SIM' else '')
            l_age_g.append(grad.get('NOME-AGENCIA', '') if bolsa == 'SIM' else '')
            l_uf_g.append(mapa_inst.get(cod_inst, {}).get('UF', ''))
            l_pais_g.append(mapa_inst.get(cod_inst, {}).get('PAIS', ''))

        curriculo['NOME-CURSO-GRADUACAO'] = ' | '.join(l_cur_g)
        curriculo['CODIGO-CURSO-CAPES'] = ' | '.join(l_codc_g)
        curriculo['NOME-INSTITUICAO-GRADUACAO'] = ' | '.join(l_inst_g)
        curriculo['CODIGO-INSTITUICAO'] = ' | '.join(l_codi_g)
        curriculo['ANO-DE-INICIO-GRADUACAO'] = ' | '.join(l_anoi_g)
        curriculo['ANO-DE-CONCLUSAO-GRADUACAO'] = ' | '.join(l_anof_g)
        curriculo['STATUS-DO-CURSO-GRAD'] = ' | '.join(l_stat_g)
        curriculo['FLAG-BOLSA-GRAD'] = ' | '.join(l_bol_g)
        curriculo['TIPO-BOLSA-GRAD'] = ' | '.join(l_tipo_b)
        curriculo['ENTIDADE-BOLSA-GRAD'] = ' | '.join(l_age_g)
        curriculo['UF-INSTITUICAO-GRADUACAO'] = ' | '.join(l_uf_g)
        curriculo['PAIS-INSTITUICAO-GRADUACAO'] = ' | '.join(l_pais_g)

        # MESTRADO
        l_cur_m, l_codc_m, l_inst_m, l_anoi_m, l_anof_m, l_stat_m, l_tipo_m, l_uf_m, l_pais_m = [], [], [], [], [], [], [], [], []
        for mest in root.findall('.//MESTRADO'):
            cod_inst = mest.get('CODIGO-INSTITUICAO', '')
            l_cur_m.append(mest.get('NOME-CURSO', ''))
            l_codc_m.append(mest.get('CODIGO-CURSO', ''))
            l_inst_m.append(mest.get('NOME-INSTITUICAO', ''))
            l_anoi_m.append(mest.get('ANO-DE-INICIO', ''))
            l_anof_m.append(mest.get('ANO-DE-CONCLUSAO', ''))
            l_stat_m.append(mest.get('STATUS-DO-CURSO', ''))
            l_tipo_m.append(mest.get('TIPO-MESTRADO', ''))
            l_uf_m.append(mapa_inst.get(cod_inst, {}).get('UF', ''))
            l_pais_m.append(mapa_inst.get(cod_inst, {}).get('PAIS', ''))
            
        curriculo['NOME-CURSO-MESTRADO'] = ' | '.join(l_cur_m)
        curriculo['CODIGO-PROGRAMA-CAPES-MEST'] = ' | '.join(l_codc_m)
        curriculo['NOME-INSTITUICAO-MESTRADO'] = ' | '.join(l_inst_m)
        curriculo['ANO-DE-INICIO-MESTRADO'] = ' | '.join(l_anoi_m)
        curriculo['ANO-DE-CONCLUSAO-MESTRADO'] = ' | '.join(l_anof_m)
        curriculo['STATUS-DO-CURSO-MEST'] = ' | '.join(l_stat_m)
        curriculo['TIPO-MESTRADO'] = ' | '.join(l_tipo_m)
        curriculo['UF-INSTITUICAO-MESTRADO'] = ' | '.join(l_uf_m)
        curriculo['PAIS-INSTITUICAO-MESTRADO'] = ' | '.join(l_pais_m)

        # DOUTORADO
        l_cur_d, l_codc_d, l_inst_d, l_anoi_d, l_anof_d, l_stat_d, l_uf_d, l_pais_d = [], [], [], [], [], [], [], []
        for dout in root.findall('.//DOUTORADO'):
            cod_inst = dout.get('CODIGO-INSTITUICAO', '')
            l_cur_d.append(dout.get('NOME-CURSO', ''))
            l_codc_d.append(dout.get('CODIGO-CURSO', ''))
            l_inst_d.append(dout.get('NOME-INSTITUICAO', ''))
            l_anoi_d.append(dout.get('ANO-DE-INICIO', ''))
            l_anof_d.append(dout.get('ANO-DE-CONCLUSAO', ''))
            l_stat_d.append(dout.get('STATUS-DO-CURSO', ''))
            l_uf_d.append(mapa_inst.get(cod_inst, {}).get('UF', ''))
            l_pais_d.append(mapa_inst.get(cod_inst, {}).get('PAIS', ''))

        curriculo['NOME-CURSO-DOUTORADO'] = ' | '.join(l_cur_d)
        curriculo['CODIGO-PROGRAMA-CAPES-DOUT'] = ' | '.join(l_codc_d)
        curriculo['NOME-INSTITUICAO-DOUTORADO'] = ' | '.join(l_inst_d)
        curriculo['ANO-DE-INICIO-DOUTORADO'] = ' | '.join(l_anoi_d)
        curriculo['ANO-DE-CONCLUSAO-DOUTORADO'] = ' | '.join(l_anof_d)
        curriculo['STATUS-DO-CURSO-DOUT'] = ' | '.join(l_stat_d)
        curriculo['UF-INSTITUICAO-DOUTORADO'] = ' | '.join(l_uf_d)
        curriculo['PAIS-INSTITUICAO-DOUTORADO'] = ' | '.join(l_pais_d)

        # =====================================================================
        # FUNÇÃO AUXILIAR PARA PRODUÇÃO TÉCNICA E ÁREAS
        # =====================================================================
        def extrair_lista(caminho, atributos):
            resultados = {attr: [] for attr in atributos}
            for item in root.findall(caminho):
                for attr in atributos:
                    resultados[attr].append(item.get(attr, ''))
            return {k: ' | '.join(v) for k, v in resultados.items()}

        # GRUPO 3: ÁREAS DE ATUAÇÃO E SETOR
        areas = extrair_lista('.//AREA-DE-ATUACAO', ['NOME-GRANDE-AREA-DO-CONHECIMENTO', 'NOME-DA-AREA-DO-CONHECIMENTO', 'NOME-DA-SUB-AREA-DO-CONHECIMENTO', 'NOME-DA-ESPECIALIDADE'])
        curriculo['GRANDE-AREA-DO-CONHECIMENTO'] = areas['NOME-GRANDE-AREA-DO-CONHECIMENTO']
        curriculo['AREA-DO-CONHECIMENTO'] = areas['NOME-DA-AREA-DO-CONHECIMENTO']
        curriculo['SUBAREA-DO-CONHECIMENTO'] = areas['NOME-DA-SUB-AREA-DO-CONHECIMENTO']
        curriculo['ESPECIALIDADE'] = areas['NOME-DA-ESPECIALIDADE']
        
        curriculo['SETOR-DE-APLICACAO'] = extrair_lista('.//SETOR-DE-ATIVIDADE-1', ['NOME-DO-SETOR-DE-ATIVIDADE'])['NOME-DO-SETOR-DE-ATIVIDADE']

        # LINHAS DE PESQUISA (Corrigido para OBJETIVOS-LINHA-DE-PESQUISA)
        linhas = extrair_lista('.//LINHA-DE-PESQUISA', ['TITULO-DA-LINHA-DE-PESQUISA', 'OBJETIVOS-LINHA-DE-PESQUISA'])
        curriculo['TITULO-LINHA-DE-PESQUISA'] = linhas['TITULO-DA-LINHA-DE-PESQUISA']
        curriculo['OBJETIVO-LINHA'] = linhas['OBJETIVOS-LINHA-DE-PESQUISA']

        # GRUPO 5B/C: PRODUTOS, PROCESSOS E TRABALHOS (Corrigido para PROCESSOS-OU-TECNICAS)
        prod = extrair_lista('.//PRODUTO-TECNOLOGICO/DADOS-BASICOS-DO-PRODUTO-TECNOLOGICO', ['TITULO-DO-PRODUTO', 'TIPO-PRODUTO', 'ANO'])
        curriculo['TITULO-PRODUTO-TECN'] = prod['TITULO-DO-PRODUTO']
        curriculo['TIPO-PRODUTO-TECN'] = prod['TIPO-PRODUTO']
        curriculo['ANO-PRODUTO-TECN'] = prod['ANO']

        proc = extrair_lista('.//PROCESSOS-OU-TECNICAS/DADOS-BASICOS-DO-PROCESSOS-OU-TECNICAS', ['TITULO-DO-PROCESSO', 'ANO'])
        curriculo['TITULO-PROCESSO-TECNICA'] = proc['TITULO-DO-PROCESSO']
        curriculo['ANO-PROCESSO'] = proc['ANO']

        trab = extrair_lista('.//TRABALHO-TECNICO/DADOS-BASICOS-DO-TRABALHO-TECNICO', ['TITULO-DO-TRABALHO-TECNICO', 'ANO', 'NATUREZA'])
        curriculo['TITULO-TRABALHO-TECNICO'] = trab['TITULO-DO-TRABALHO-TECNICO']
        curriculo['ANO-TRABALHO-TECNICO'] = trab['ANO']
        curriculo['TIPO-TRABALHO-TECNICO'] = trab['NATUREZA']

        # =====================================================================
        # GRUPO 4: ATUAÇÃO PROFISSIONAL
        # =====================================================================
        l_inst, l_ano_in, l_mes_in, l_ano_fim, l_mes_fim, l_cargo, l_desc, l_uf_emp, l_pais_emp = [], [], [], [], [], [], [], [], []
        for atuacao in root.findall('.//ATUACAO-PROFISSIONAL'):
            nome_inst = atuacao.get('NOME-INSTITUICAO', '')
            cod_inst_emp = atuacao.get('CODIGO-INSTITUICAO', '')
            
            for vinculo in atuacao.findall('.//VINCULOS'):
                l_inst.append(nome_inst)
                l_ano_in.append(vinculo.get('ANO-INICIO', ''))
                l_mes_in.append(vinculo.get('MES-INICIO', ''))
                
                # Dados perfeitamente fiéis ao XML (sem "Atual")
                l_ano_fim.append(vinculo.get('ANO-FIM', ''))
                l_mes_fim.append(vinculo.get('MES-FIM', ''))
                
                cargo = vinculo.get('OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO', '') or vinculo.get('ENQUADRAMENTO-FUNCIONAL', '')
                l_cargo.append(cargo)
                l_desc.append(vinculo.get('OUTRAS-INFORMACOES', '').replace('\n', ' ').strip())
                
                l_uf_emp.append(mapa_inst.get(cod_inst_emp, {}).get('UF', ''))
                l_pais_emp.append(mapa_inst.get(cod_inst_emp, {}).get('PAIS', ''))

        curriculo['NOME-INSTITUICAO-EMPREGO'] = ' | '.join(l_inst)
        curriculo['ANO-INICIO-EMPREGO'] = ' | '.join(l_ano_in)
        curriculo['MES-INICIO-EMPREGO'] = ' | '.join(l_mes_in)
        curriculo['ANO-FIM-EMPREGO'] = ' | '.join(l_ano_fim)
        curriculo['MES-FIM-EMPREGO'] = ' | '.join(l_mes_fim)
        curriculo['CARGO-OU-FUNCAO'] = ' | '.join(l_cargo)
        curriculo['DESCRICAO-ATIVIDADE'] = ' | '.join(l_desc)
        curriculo['UF-INSTITUICAO-EMPREGO'] = ' | '.join(l_uf_emp)
        curriculo['PAIS-INSTITUICAO-EMPREGO'] = ' | '.join(l_pais_emp)

        # =====================================================================
        # GRUPO 5A: PATENTES
        # =====================================================================
        l_tit_pat, l_ano_pat, l_num_pat, l_cat_pat, l_titular_pat, l_pais_pat, l_concessao = [], [], [], [], [], [], []
        for pat in root.findall('.//PATENTE'):
            b = pat.find('.//DADOS-BASICOS-DA-PATENTE')
            d = pat.find('.//DETALHAMENTO-DA-PATENTE')
            if b is not None:
                l_tit_pat.append(b.get('TITULO', ''))
                l_ano_pat.append(b.get('ANO-DESENVOLVIMENTO', ''))
                l_pais_pat.append(b.get('PAIS', ''))
            else:
                l_tit_pat.append(''); l_ano_pat.append(''); l_pais_pat.append('')
                
            if d is not None:
                reg = d.find('.//REGISTRO-OU-PATENTE')
                if reg is not None:
                    l_num_pat.append(reg.get('CODIGO-DO-REGISTRO-OU-PATENTE', ''))
                    l_titular_pat.append(reg.get('NOME-DO-TITULAR', '') or reg.get('NOME-DO-DEPOSITANTE', ''))
                    l_concessao.append('SIM' if reg.get('DATA-DE-CONCESSAO') else 'NAO')
                else:
                    l_num_pat.append(''); l_titular_pat.append(''); l_concessao.append('NAO')
                l_cat_pat.append(d.get('CATEGORIA', ''))
            else:
                l_num_pat.append(''); l_cat_pat.append(''); l_titular_pat.append(''); l_concessao.append('')

        curriculo['TITULO-PATENTE'] = ' | '.join(l_tit_pat)
        curriculo['ANO-DEPOSITO-PATENTE'] = ' | '.join(l_ano_pat)
        curriculo['NUMERO-DEPOSITO'] = ' | '.join(l_num_pat)
        curriculo['CATEGORIA-PATENTE'] = ' | '.join(l_cat_pat)
        curriculo['TITULAR-PATENTE'] = ' | '.join(l_titular_pat)
        curriculo['PAIS-PATENTE'] = ' | '.join(l_pais_pat)
        curriculo['FLAG-PATENTE-CONCEDIDA'] = ' | '.join(l_concessao)

        # =====================================================================
        # GRUPO 5B: SOFTWARE E TRANSFERÊNCIA
        # =====================================================================
        l_tit_soft, l_ano_soft, l_reg_soft = [], [], []
        for soft in root.findall('.//SOFTWARE'):
            b = soft.find('.//DADOS-BASICOS-DO-SOFTWARE')
            d = soft.find('.//DETALHAMENTO-DO-SOFTWARE')
            l_tit_soft.append(b.get('TITULO-DO-SOFTWARE', '') if b is not None else '')
            l_ano_soft.append(b.get('ANO', '') if b is not None else '')
            
            reg = d.find('.//REGISTRO-OU-PATENTE') if d is not None else None
            l_reg_soft.append(reg.get('CODIGO-DO-REGISTRO-OU-PATENTE', '') if reg is not None else '')
            
        curriculo['TITULO-SOFTWARE'] = ' | '.join(l_tit_soft)
        curriculo['ANO-SOFTWARE'] = ' | '.join(l_ano_soft)
        curriculo['FLAG-REGISTRO-SOFTWARE'] = ' | '.join(l_reg_soft)

        l_tit_trans, l_ano_trans, l_emp_trans = [], [], []
        for trans in root.findall('.//TRANSFERENCIA-DE-TECNOLOGIA'):
            b = trans.find('.//DADOS-BASICOS-DA-TRANSFERENCIA-DE-TECNOLOGIA')
            d = trans.find('.//DETALHAMENTO-DA-TRANSFERENCIA-DE-TECNOLOGIA')
            l_tit_trans.append(b.get('TITULO-DA-TRANSFERENCIA-DE-TECNOLOGIA', '') if b is not None else '')
            l_ano_trans.append(b.get('ANO', '') if b is not None else '')
            l_emp_trans.append(d.get('NOME-DA-EMPRESA-OU-INSTITUICAO-RECEPTORA', '') if d is not None else '')
        curriculo['TITULO-TRANSF-TECNOLOGIA'] = ' | '.join(l_tit_trans)
        curriculo['ANO-TRANSF-TECNOLOGIA'] = ' | '.join(l_ano_trans)
        curriculo['EMPRESA-RECEPTORA'] = ' | '.join(l_emp_trans)

        return curriculo

    except zipfile.BadZipFile:
        return curriculo
    except Exception as e:
        return curriculo

# =====================================================================
# BLOCO PRINCIPAL: MÚLTIPLOS ARQUIVOS E GERAÇÃO DO EXCEL
# =====================================================================
if __name__ == "__main__":
    print("[*] Iniciando leitura dos arquivos de entrada...")
    lista_de_ids_total = []
    
    # Lendo todas as planilhas definidas na lista ARQUIVOS_ENTRADA
    for arquivo in ARQUIVOS_ENTRADA:
        try:
            print(f"    -> Lendo {arquivo}...")
            df_temp = pd.read_excel(arquivo)
            
            # PADRONIZADOR INTELIGENTE (Resolve "ID LATTES", "Id Lattes", etc)
            df_temp.columns = df_temp.columns.str.strip().str.lower().str.replace(' ', '_')
            
            if 'id_lattes' not in df_temp.columns:
                print(f"    [-] ERRO: Coluna de ID não encontrada no arquivo {arquivo}.")
                continue
                
            ids_temp = df_temp['id_lattes'].dropna().astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(16).tolist()
            lista_de_ids_total.extend(ids_temp)
            
        except Exception as e:
            print(f"[-] Erro ao ler o arquivo {arquivo}: {e}")

    # Remove duplicidades juntando as duas planilhas
    lista_de_ids = pd.Series(lista_de_ids_total).drop_duplicates().tolist()
    
    if not lista_de_ids:
        print("[-] Nenhum ID foi encontrado. Encerrando.")
        exit()

    print(f"[*] Total de IDs ÚNICOS para processar: {len(lista_de_ids)}")
    print("[*] Iniciando extração na API do CNPq. Isso pode levar um bom tempo...")
    
    cliente_soap = Client(WSDL_URL)
    dados_extraidos = []
    
    for i, id_lattes in enumerate(lista_de_ids, 1):
        print(f"[{i}/{len(lista_de_ids)}] Coletando Lattes: {id_lattes}")
        dados_extraidos.append(extrair_dados_lattes(id_lattes, cliente_soap))
        time.sleep(0.5)

    df_principal = pd.DataFrame(dados_extraidos)

    # Configuração das Abas (Nenhum campo abreviado)
    abas_config = {
        'Graduacao': ['NUMERO-IDENTIFICADOR', 'NOME-CURSO-GRADUACAO', 'CODIGO-CURSO-CAPES', 'NOME-INSTITUICAO-GRADUACAO', 'CODIGO-INSTITUICAO', 'ANO-DE-INICIO-GRADUACAO', 'ANO-DE-CONCLUSAO-GRADUACAO', 'STATUS-DO-CURSO-GRAD', 'UF-INSTITUICAO-GRADUACAO', 'PAIS-INSTITUICAO-GRADUACAO', 'FLAG-BOLSA-GRAD', 'TIPO-BOLSA-GRAD', 'ENTIDADE-BOLSA-GRAD'],
        'Mestrado': ['NUMERO-IDENTIFICADOR', 'NOME-CURSO-MESTRADO', 'CODIGO-PROGRAMA-CAPES-MEST', 'NOME-INSTITUICAO-MESTRADO', 'ANO-DE-INICIO-MESTRADO', 'ANO-DE-CONCLUSAO-MESTRADO', 'STATUS-DO-CURSO-MEST', 'TIPO-MESTRADO', 'UF-INSTITUICAO-MESTRADO', 'PAIS-INSTITUICAO-MESTRADO'],
        'Doutorado': ['NUMERO-IDENTIFICADOR', 'NOME-CURSO-DOUTORADO', 'CODIGO-PROGRAMA-CAPES-DOUT', 'NOME-INSTITUICAO-DOUTORADO', 'ANO-DE-INICIO-DOUTORADO', 'ANO-DE-CONCLUSAO-DOUTORADO', 'STATUS-DO-CURSO-DOUT', 'UF-INSTITUICAO-DOUTORADO', 'PAIS-INSTITUICAO-DOUTORADO'],
        'Areas de Atuacao': ['NUMERO-IDENTIFICADOR', 'GRANDE-AREA-DO-CONHECIMENTO', 'AREA-DO-CONHECIMENTO', 'SUBAREA-DO-CONHECIMENTO', 'ESPECIALIDADE'],
        'Atuacao Profissional': ['NUMERO-IDENTIFICADOR', 'NOME-INSTITUICAO-EMPREGO', 'TIPO-INSTITUICAO', 'NATUREZA-INSTITUICAO', 'ANO-INICIO-EMPREGO', 'MES-INICIO-EMPREGO', 'ANO-FIM-EMPREGO', 'MES-FIM-EMPREGO', 'CARGO-OU-FUNCAO', 'FLAG-EMPREGO-EMPRESA-PRIVADA', 'UF-INSTITUICAO-EMPREGO', 'PAIS-INSTITUICAO-EMPREGO', 'CNPJ-INSTITUICAO', 'DESCRICAO-ATIVIDADE', 'FLAG-ATIVIDADE-PD'],
        'Linhas de Pesquisa': ['NUMERO-IDENTIFICADOR', 'TITULO-LINHA-DE-PESQUISA', 'OBJETIVO-LINHA'],
        'Patentes': ['NUMERO-IDENTIFICADOR', 'TITULO-PATENTE', 'ANO-DEPOSITO-PATENTE', 'NUMERO-DEPOSITO', 'CATEGORIA-PATENTE', 'FLAG-PATENTE-CONCEDIDA', 'TITULAR-PATENTE', 'PAIS-PATENTE'],
        'Software': ['NUMERO-IDENTIFICADOR', 'TITULO-SOFTWARE', 'ANO-SOFTWARE', 'FLAG-REGISTRO-SOFTWARE'],
        'Produto Tecnologico': ['NUMERO-IDENTIFICADOR', 'TITULO-PRODUTO-TECN', 'TIPO-PRODUTO-TECN', 'ANO-PRODUTO-TECN'],
        'Processo Tecnico': ['NUMERO-IDENTIFICADOR', 'TITULO-PROCESSO-TECNICA', 'ANO-PROCESSO'],
        'Trabalho Tecnico': ['NUMERO-IDENTIFICADOR', 'TITULO-TRABALHO-TECNICO', 'ANO-TRABALHO-TECNICO', 'TIPO-TRABALHO-TECNICO'],
        'Transferencia Tecnologia': ['NUMERO-IDENTIFICADOR', 'TITULO-TRANSF-TECNOLOGIA', 'ANO-TRANSF-TECNOLOGIA', 'EMPRESA-RECEPTORA']
    }

    output = "Relatorio_Avaliacao_Impacto_UNIFICADO.xlsx"
    print("\n[*] Salvando dados em arquivo Excel...")
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        # ABA 1: BASE CONSOLIDADA (Apenas 1 linha por ID, sem repetições)
        colunas_base = [
            'NUMERO-IDENTIFICADOR', 'NOME-COMPLETO', 'NOME-EM-CITACOES-BIBLIOGRAFICAS', 
            'PAIS-DE-NASCIMENTO', 'UF-NASCIMENTO', 'CIDADE-NASCIMENTO', 'DATA-NASCIMENTO', 
            'ANO-DE-NASCIMENTO', 'SEXO', 'NACIONALIDADE', 
            'NOME-INSTITUICAO', 'UF-INSTITUICAO', 'CIDADE-INSTITUICAO', 'PAIS-INSTITUICAO',
            'SETOR-DE-APLICACAO'
        ]
        
        col_existem = [c for c in colunas_base if c in df_principal.columns]
        df_resumo = df_principal[col_existem].copy()
        
        if 'SETOR-DE-APLICACAO' in df_resumo.columns:
            df_resumo['SETOR-DE-APLICACAO'] = df_resumo['SETOR-DE-APLICACAO'].str.replace(' | ', ', ', regex=False)
            
        df_resumo['NUMERO-IDENTIFICADOR'] = df_resumo['NUMERO-IDENTIFICADOR'].astype(str)
        
        # O Filtro anti-duplicidade garantindo a aba limpa
        df_resumo = df_resumo.drop_duplicates(subset=['NUMERO-IDENTIFICADOR'], keep='first')
        
        df_resumo.to_excel(writer, sheet_name='Base Consolidada', index=False)
        print("[+] Aba 'Base Consolidada' salva com sucesso.")

        # ABAS SECUNDÁRIAS (A mágica da explosão de linhas)
        for nome_aba, colunas in abas_config.items():
            colunas_existem = [c for c in colunas if c in df_principal.columns]
            if len(colunas_existem) > 1:
                df_aba = df_principal[colunas_existem].copy()
                col_chave = colunas_existem[1] 
                
                df_aba = df_aba.dropna(subset=[col_chave])
                df_aba = df_aba[df_aba[col_chave].astype(str).str.contains(r'[a-zA-Z0-9]', na=False)]

                for col in colunas_existem[1:]:
                    df_aba[col] = df_aba[col].astype(str).str.split('|')
                
                # Sincronização e Padding para evitar erro do Pandas
                for index, row in df_aba.iterrows():
                    tamanhos = [len(row[col]) for col in colunas_existem[1:] if isinstance(row[col], list)]
                    max_len = max(tamanhos) if tamanhos else 1
                    
                    for col in colunas_existem[1:]:
                        lst = row[col]
                        if isinstance(lst, list):
                            if len(lst) < max_len:
                                if len(lst) == 1 and str(lst[0]).strip().lower() in ['', 'nan', 'none']:
                                    df_aba.at[index, col] = [''] * max_len
                                else:
                                    lst.extend([''] * (max_len - len(lst)))
                                    df_aba.at[index, col] = lst
                            elif len(lst) > max_len:
                                df_aba.at[index, col] = lst[:max_len]

                df_aba = df_aba.explode(colunas_existem[1:])
                
                for col in colunas_existem[1:]:
                    df_aba[col] = df_aba[col].str.strip().replace(['nan', 'None', ''], pd.NA)

                df_aba.to_excel(writer, sheet_name=nome_aba, index=False)
                print(f"[+] Aba '{nome_aba}' gerada com sucesso.")

    print("=" * 60)
    print(f"[🚀 PROJETO CONCLUÍDO] Arquivo final salvo com todas as planilhas unificadas em: {output}")
    print("=" * 60)