from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pandas as pd
import os
import re
import unicodedata
import logging
import asyncio
import json
import base64

from moldes import db, Usuario, Resposta, MembroEquipe, OrganizacaoParceira, RecursoAlavancado, ContratoTecnologia, ProducaoTecnologicaValidada, AcordoNDA, OutraOrientacao, CooperacaoInternacional, MetaProgresso, PesquisadorVisitante, EventoOrganizado, AtividadeDivulgacao, ArticulacaoINCT, EmpresaNacional, EmpresaEstrangeira, ResultadoProposto, PublicacaoCoautoria, ProducaoBibliograficaValidada, ProducaoArtisticaValidada, FormacaoRHValidada
from utils.pdf_playwright import gerar_pdf_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'segredo-super-seguro-padrao-para-desenvolvimento')

# --- CONFIGURAÇÕES DE BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 1. Remove limite de tamanho do arquivo (Peso em MB)
app.config['MAX_CONTENT_LENGTH'] = None 

# 2. Aumenta o limite de campos (Inputs) de 1.000 para 50.000
app.config['MAX_FORM_PARTS'] = 50000

db.init_app(app)

DADOS_PATH = 'dados/'

# Função de Segurança para Listas
def get_safe(lista, indice):
    """Retorna o item da lista no índice ou None se não existir."""
    try:
        if indice < len(lista):
            return lista[indice]
    except:
        pass
    return None

def remover_acentos(txt):
    if not isinstance(txt, str): return str(txt)
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8')

def buscar_arquivo_em_pasta(caminho_pasta, tipo_arquivo):
    try:
        for nome_arquivo in os.listdir(caminho_pasta):
            if tipo_arquivo in remover_acentos(nome_arquivo.lower()):
                return os.path.join(caminho_pasta, nome_arquivo)
    except FileNotFoundError: return None
    return None

def formatar_numero_processo(numero_str):
    numeros = re.sub(r'\D', '', str(numero_str))
    if len(numeros) == 15: return f"{numeros[:6]}/{numeros[6:10]}-{numeros[-1]}"
    return numeros

def find_header_row(excel_path, required_cols):
    try:
        df_test = pd.read_excel(excel_path, header=None, nrows=20)
        for index, row in df_test.iterrows():
            row_values = [str(c).strip() for c in row.values] 
            if all(col in row_values for col in required_cols): return index
    except Exception: return None
    return None

def parse_moeda(valor_str):
    """Converte uma string de moeda no formato brasileiro (ex: '1.234,56') para float."""
    if not isinstance(valor_str, str):
        return 0.0
    try:
        valor_limpo = valor_str.replace('.', '').replace(',', '.')
        return float(valor_limpo)
    except (ValueError, TypeError):
        return 0.0

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    mensagem = None
    if request.args.get('senha_alterada') == '1':
        mensagem = "✅ Senha atualizada com sucesso."
    
    if request.method == 'POST':
        cpf = re.sub(r'\D', '', request.form.get('cpf', '').strip())
        senha = request.form.get('senha', '').strip()
        user = Usuario.query.filter_by(cpf=cpf).first()
        
        if user and check_password_hash(user.senha_hash, senha):
            session['cpf'] = user.cpf
            session['nome'] = user.nome
            session['numero_processo'] = user.numero_processo
            
            if user.primeiro_acesso:
                return redirect(url_for('trocar_senha'))
            return redirect(url_for('confirmacao_projeto')) 
        else:
            erro = 'CPF ou senha inválidos.'
            
    # Se não for POST ou se o login falhar, MOSTRA a página de login
    return render_template('login.html', erro=erro, mensagem=mensagem)

@app.route('/trocar_senha', methods=['GET', 'POST'])
def trocar_senha():
    if 'cpf' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        nova = request.form['nova']
        if nova != request.form['confirmar']: return render_template('trocar_senha.html', erro="Senhas não coincidem.")
        hash_nova = generate_password_hash(nova)
        user = Usuario.query.filter_by(cpf=session['cpf']).first()
        if user:
            user.senha_hash = hash_nova
            user.primeiro_acesso = False
            db.session.commit()
        return redirect(url_for('login', senha_alterada=1))
    return render_template('trocar_senha.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/confirmacao_projeto')
def confirmacao_projeto():
    # Garante que apenas usuários logados acessem esta página
    if 'cpf' not in session:
        return redirect(url_for('login'))

    # === LÓGICA DO VISITANTE (Para não travar a tela) ===
    if session['cpf'] == "00000000000":
        nome_coordenador = "Dalila Andrade Oliveira" 
        numero_processo = "40686120226"
    else:
        # Se for usuário normal
        nome_coordenador = session.get('nome')
        numero_processo = session.get('numero_processo')

    processo_formatado = formatar_numero_processo(numero_processo)
    
    return render_template(
        'confirmacao_projeto.html',
        coordenador=nome_coordenador,
        processo=processo_formatado
    )

@app.route('/formulario/<coordenador>', methods=['GET', 'POST'])
def formulario(coordenador):
    # --- BLOCO 1: Configuração Inicial ---
    if 'cpf' not in session or 'numero_processo' not in session:
        return redirect(url_for('login'))

    # === [INÍCIO] LÓGICA DO MODO VISITANTE (ESPELHAMENTO) ===
    CPF_VISITANTE = "00000000000"
    CPF_DO_DONO_REAL = "60326352600" 
    PASTA_DO_DONO_REAL = "40686120226"

    # Verifica quem está logado
    if session['cpf'] == CPF_VISITANTE:
        # Se for o visitante, enganamos o sistema:
        cpf_usado = CPF_DO_DONO_REAL       # Usa o CPF do dono real para buscar no banco
        numero_proc = PASTA_DO_DONO_REAL   # Usa a pasta do dono real para ler arquivos
        print(f"👀 MODO VISITANTE: Exibindo e Salvando dados de {cpf_usado}")
    else:
        # Se for usuário normal, segue a vida:
        cpf_usado = session['cpf']
        numero_proc = session['numero_processo']

    caminho_pasta_projeto = os.path.join(DADOS_PATH, numero_proc)
    processo_formatado = formatar_numero_processo(numero_proc)
    
    # --- BLOCO 2: Lógica de Salvamento (POST) ---
    if request.method == 'POST':
        try:
            # 1. Busca Inteligente (Evita Duplicidade)
            resposta_atual = Resposta.query.filter_by(usuario_cpf=cpf_usado).first()

            if resposta_atual:
                # --- MODO EDIÇÃO ---
                resposta_atual.nome_projeto = request.form.get('nome_projeto')
                resposta_atual.sigla = request.form.get('sigla')
                resposta_atual.instituicao_sede = request.form.get('instituicao')
                
                # Atualiza Financeiro
                resposta_atual.cnpq_custeio_gasto = parse_moeda(request.form.get('cnpq_custeio_gasto'))
                resposta_atual.cnpq_capital_gasto = parse_moeda(request.form.get('cnpq_capital_gasto'))
                resposta_atual.cnpq_bolsas_pais_gasto = parse_moeda(request.form.get('cnpq_bolsas_pais_gasto'))
                resposta_atual.cnpq_bolsas_ext_gasto = int(request.form.get('cnpq_bolsas_ext_gasto') or 0)
                resposta_atual.capes_custeio_gasto = parse_moeda(request.form.get('capes_custeio_gasto'))
                resposta_atual.capes_capital_gasto = parse_moeda(request.form.get('capes_capital_gasto'))
                resposta_atual.capes_bolsas_pais_gasto = parse_moeda(request.form.get('capes_bolsas_pais_gasto'))
                resposta_atual.capes_bolsas_ext_gasto = int(request.form.get('capes_bolsas_ext_gasto') or 0)
                resposta_atual.faps_custeio_gasto = parse_moeda(request.form.get('faps_custeio_gasto'))
                resposta_atual.faps_capital_gasto = parse_moeda(request.form.get('faps_capital_gasto'))
                resposta_atual.faps_bolsas_pais_gasto = parse_moeda(request.form.get('faps_bolsas_pais_gasto'))
                resposta_atual.faps_bolsas_ext_gasto = int(request.form.get('faps_bolsas_ext_gasto') or 0)
                
                # Atualiza Outros Campos
                resposta_atual.houve_alavancagem = request.form.get('houve_alavancagem')
                resposta_atual.infra_demanda_inct = request.form.get('infra_demanda_inct')
                resposta_atual.infra_adequada_ponta = request.form.get('infra_adequada_ponta')
                resposta_atual.articulacao_com_incts = request.form.get('articula_inct_select')
                resposta_atual.possui_coop_internacional = request.form.get('possui_coop_internacional')
                resposta_atual.houve_visita_estrangeiro = request.form.get('houve_visita_estrangeiro')
                resposta_atual.apoio_bolsa_fonte = request.form.get('apoio_bolsa_fonte')
                resposta_atual.apoio_diarias_fonte = request.form.get('apoio_diarias_fonte')
                resposta_atual.qtd_visitantes = int(request.form.get('qtd_visitantes') or 0)
                resposta_atual.organizou_eventos = request.form.get('organizou_eventos')
                resposta_atual.dificuldades_encontradas = request.form.get('dificuldades_encontradas')
                resposta_atual.sugestoes_aprimoramento = request.form.get('sugestoes_aprimoramento')
                resposta_atual.divulgacao_leigos = request.form.get('divulgacao_leigos')
                resposta_atual.autorizacoes = ','.join(request.form.getlist('autorizacao_compartilhamento[]'))

                # --- LIMPEZA (Apaga filhos antigos) ---
                MembroEquipe.query.filter_by(resposta_id=resposta_atual.id).delete()
                OrganizacaoParceira.query.filter_by(resposta_id=resposta_atual.id).delete()
                RecursoAlavancado.query.filter_by(resposta_id=resposta_atual.id).delete()
                ArticulacaoINCT.query.filter_by(resposta_id=resposta_atual.id).delete()
                PublicacaoCoautoria.query.filter_by(resposta_id=resposta_atual.id).delete()
                ProducaoTecnologicaValidada.query.filter_by(resposta_id=resposta_atual.id).delete()
                EmpresaNacional.query.filter_by(resposta_id=resposta_atual.id).delete()
                EmpresaEstrangeira.query.filter_by(resposta_id=resposta_atual.id).delete()
                ContratoTecnologia.query.filter_by(resposta_id=resposta_atual.id).delete()
                AcordoNDA.query.filter_by(resposta_id=resposta_atual.id).delete()
                CooperacaoInternacional.query.filter_by(resposta_id=resposta_atual.id).delete()
                PesquisadorVisitante.query.filter_by(resposta_id=resposta_atual.id).delete()
                OutraOrientacao.query.filter_by(resposta_id=resposta_atual.id).delete()
                AtividadeDivulgacao.query.filter_by(resposta_id=resposta_atual.id).delete()
                EventoOrganizado.query.filter_by(resposta_id=resposta_atual.id).delete()
                MetaProgresso.query.filter_by(resposta_id=resposta_atual.id).delete()
                ResultadoProposto.query.filter_by(resposta_id=resposta_atual.id).delete()
                ProducaoBibliograficaValidada.query.filter_by(resposta_id=resposta_atual.id).delete()
                ProducaoArtisticaValidada.query.filter_by(resposta_id=resposta_atual.id).delete()
                FormacaoRHValidada.query.filter_by(resposta_id=resposta_atual.id).delete()

            else:
                # --- MODO CRIAÇÃO ---
                resposta_atual = Resposta(
                    usuario_cpf=cpf_usado,
                    nome_projeto=request.form.get('nome_projeto'),
                    sigla=request.form.get('sigla'),
                    instituicao_sede=request.form.get('instituicao'),
                    cnpq_custeio_gasto=parse_moeda(request.form.get('cnpq_custeio_gasto')),
                    cnpq_capital_gasto=parse_moeda(request.form.get('cnpq_capital_gasto')),
                    cnpq_bolsas_pais_gasto=parse_moeda(request.form.get('cnpq_bolsas_pais_gasto')),
                    cnpq_bolsas_ext_gasto=int(request.form.get('cnpq_bolsas_ext_gasto') or 0),
                    capes_custeio_gasto=parse_moeda(request.form.get('capes_custeio_gasto')),
                    capes_capital_gasto=parse_moeda(request.form.get('capes_capital_gasto')),
                    capes_bolsas_pais_gasto=parse_moeda(request.form.get('capes_bolsas_pais_gasto')),
                    capes_bolsas_ext_gasto=int(request.form.get('capes_bolsas_ext_gasto') or 0),
                    faps_custeio_gasto=parse_moeda(request.form.get('faps_custeio_gasto')),
                    faps_capital_gasto=parse_moeda(request.form.get('faps_capital_gasto')),
                    faps_bolsas_pais_gasto=parse_moeda(request.form.get('faps_bolsas_pais_gasto')),
                    faps_bolsas_ext_gasto=int(request.form.get('faps_bolsas_ext_gasto') or 0),
                    houve_alavancagem=request.form.get('houve_alavancagem'),
                    infra_demanda_inct=request.form.get('infra_demanda_inct'),
                    infra_adequada_ponta=request.form.get('infra_adequada_ponta'),
                    articulacao_com_incts=request.form.get('articula_inct_select'),
                    possui_coop_internacional=request.form.get('possui_coop_internacional'),
                    houve_visita_estrangeiro=request.form.get('houve_visita_estrangeiro'),
                    apoio_bolsa_fonte=request.form.get('apoio_bolsa_fonte'),
                    apoio_diarias_fonte=request.form.get('apoio_diarias_fonte'),
                    qtd_visitantes=int(request.form.get('qtd_visitantes') or 0),
                    organizou_eventos=request.form.get('organizou_eventos'),
                    dificuldades_encontradas=request.form.get('dificuldades_encontradas'),
                    sugestoes_aprimoramento=request.form.get('sugestoes_aprimoramento'),
                    divulgacao_leigos=request.form.get('divulgacao_leigos'),
                    autorizacoes=','.join(request.form.getlist('autorizacao_compartilhamento[]'))
                )
                db.session.add(resposta_atual)

            # Salva para garantir o ID
            db.session.commit()

           # 2.1 Membros da Equipe 
            membros_nomes = request.form.getlist('membro_nome[]')
            
            # Carrega as listas em variáveis para ficar mais limpo
            listas_membros = {
                'titulacao': request.form.getlist('membro_titulacao_extraida[]'),
                'area': request.form.getlist('membro_area_atuacao[]'),
                'inst': request.form.getlist('membro_instituicao[]'),
                'uf': request.form.getlist('membro_uf[]'),
                'pais': request.form.getlist('membro_pais[]'),
                'cat': request.form.getlist('membro_categoria[]'),
                'atual': request.form.getlist('membro_atual[]'),
                'novo': request.form.getlist('membro_novo[]'),
                'excluido': request.form.getlist('membro_excluido[]')
            }

            for i in range(len(membros_nomes)):
                nome = membros_nomes[i]
                if nome:
                    db.session.add(MembroEquipe(
                        nome=nome,
                        # Aqui usamos o get_safe para evitar erro de índice!
                        titulacao=get_safe(listas_membros['titulacao'], i),
                        area_atuacao=get_safe(listas_membros['area'], i),
                        instituicao=get_safe(listas_membros['inst'], i),
                        uf=get_safe(listas_membros['uf'], i),
                        pais=get_safe(listas_membros['pais'], i),
                        categoria=get_safe(listas_membros['cat'], i),
                        
                        # Checkboxes não precisam de get_safe pois verificamos se 'i' está na lista
                        status_atual=(str(i) in listas_membros['atual']),
                        status_novo=(str(i) in listas_membros['novo']),
                        status_excluido=(str(i) in listas_membros['excluido']),
                        resposta=resposta_atual
                    ))

            # 2.2 Organizações Parceiras 
            org_nomes = request.form.getlist('instituicao_nome[]')
            
            listas_orgs = {
                'pesq': request.form.getlist('instituicao_pesquisador[]'),
                'nat': request.form.getlist('instituicao_natureza[]'),
                'class': request.form.getlist('instituicao_classificacao[]'),
                'pais': request.form.getlist('instituicao_pais[]'),
                'uf': request.form.getlist('instituicao_uf[]'),
                'cid': request.form.getlist('instituicao_cidade[]'),
                'tipo': request.form.getlist('instituicao_tipo[]'),
                'nat_out': request.form.getlist('instituicao_natureza_outro[]'),
                'class_out': request.form.getlist('instituicao_classificacao_outro[]'),
                'tipo_out': request.form.getlist('instituicao_tipo_outro[]')
            }

            for i in range(len(org_nomes)):
                nome = org_nomes[i]
                if nome:
                    # Pega os valores com segurança antes
                    natureza_val = get_safe(listas_orgs['nat'], i)
                    classificacao_val = get_safe(listas_orgs['class'], i)
                    tipo_val = get_safe(listas_orgs['tipo'], i)

                    db.session.add(OrganizacaoParceira(
                        nome=nome,
                        pesquisador_responsavel=get_safe(listas_orgs['pesq'], i),
                        natureza=natureza_val,
                        classificacao=classificacao_val,
                        pais=get_safe(listas_orgs['pais'], i),
                        uf=get_safe(listas_orgs['uf'], i),
                        cidade=get_safe(listas_orgs['cid'], i),
                        natureza_outro=get_safe(listas_orgs['nat_out'], i) if natureza_val == 'Outro' else None,
                        classificacao_outro=get_safe(listas_orgs['class_out'], i) if classificacao_val == 'Outro' else None,
                        tipo_outro=get_safe(listas_orgs['tipo_out'], i) if tipo_val == 'Outro' else None,
                        resposta=resposta_atual
                    ))
            
            # 3.2 Recursos Alavancados
            fontes_recursos = request.form.getlist('alav_fonte[]')
            for i in range(len(fontes_recursos)):
                fonte = fontes_recursos[i]
                if fonte:
                    tipo_recurso_val = request.form.getlist('alav_tipo[]')[i]
                    forma_aporte_val = request.form.getlist('alav_forma[]')[i]
                    db.session.add(RecursoAlavancado(
                        fonte=fonte,
                        tipo_recurso=tipo_recurso_val,
                        valor=parse_moeda(request.form.getlist('alav_valor[]')[i]),
                        periodo_aporte=request.form.getlist('alav_periodo[]')[i],
                        natureza_fonte=request.form.getlist('alav_natureza[]')[i],
                        forma_aporte=forma_aporte_val,
                        tipo_recurso_outro=request.form.getlist('alav_tipo_outro[]')[i] if tipo_recurso_val == 'Outro' else None,
                        forma_aporte_outro=request.form.getlist('alav_forma_outro[]')[i] if forma_aporte_val == 'Outro' else None,
                        resposta=resposta_atual
                    ))

            # 4.1 Articulação com INCTs
            nomes_inct = request.form.getlist('articulacao_inct_nome[]')
            for i in range(len(nomes_inct)):
                nome = nomes_inct[i]
                if nome:
                    inicio_str = request.form.getlist('articulacao_vigencia_inicio[]')[i]
                    fim_str = request.form.getlist('articulacao_vigencia_fim[]')[i]
                    data_inicio = datetime.strptime(inicio_str, '%Y-%m-%d').date() if inicio_str else None
                    data_fim = datetime.strptime(fim_str, '%Y-%m-%d').date() if fim_str else None
                    db.session.add(ArticulacaoINCT(
                        inct_nome=nome,
                        coordenador=request.form.getlist('articulacao_coordenador[]')[i],
                        grande_area=request.form.getlist('articulacao_grande_area[]')[i],
                        area_conhecimento=request.form.getlist('articulacao_area[]')[i],
                        objetivo=request.form.getlist('articulacao_objetivo[]')[i],
                        vigencia_inicio=data_inicio,
                        vigencia_fim=data_fim,
                        status=request.form.getlist('articulacao_status[]')[i],
                        natureza=','.join(request.form.getlist(f'articulacao_natureza_{i}[]')),
                        natureza_outro=request.form.getlist('articulacao_natureza_outro[]')[i],
                        resultados=','.join(request.form.getlist(f'articulacao_resultados_{i}[]')),
                        resultados_outro=request.form.getlist('articulacao_resultados_outro[]')[i],
                        periodicidade=request.form.getlist('articulacao_periodicidade[]')[i],
                        formalizacao=request.form.getlist('articulacao_formalizacao[]')[i],
                        resposta=resposta_atual
                    ))
            
            # 4.2 Publicações com Coautoria
            coautoria_json_str = request.form.get('coautoria_json')
            if coautoria_json_str:
                try:
                    lista_coautorias = json.loads(coautoria_json_str)
                    for item in lista_coautorias:
                        db.session.add(PublicacaoCoautoria(
                            tipo=item.get('tipo'),
                            titulo=item.get('titulo'),
                            autores=item.get('autores'),
                            ano=item.get('ano'),
                            paises=item.get('paises'),
                            resposta=resposta_atual
                        ))
                except json.JSONDecodeError:
                    logging.warning("Não foi possível decodificar o JSON de coautorias.")

            # 4.3 Produção Tecnológica Validada
            i = 0
            while f'tec_titulo_{i}' in request.form:
                abrangencia = request.form.get(f'tec_abrangencia_{i}')
                if abrangencia:
                    db.session.add(ProducaoTecnologicaValidada(
                        titulo=request.form.get(f'tec_titulo_{i}'),
                        pesquisador=request.form.get(f'tec_pesquisador_{i}'),
                        ano=int(request.form.get(f'tec_ano_{i}') or 0),
                        pais_origem=request.form.get(f'tec_pais_origem_{i}'),
                        categoria=request.form.get(f'tec_categoria_{i}'),
                        abrangencia=abrangencia,
                        pais_colaboracao=request.form.get(f'tec_pais_colaboracao_{i}') if abrangencia == 'Exterior' else None,
                        resposta=resposta_atual
                    ))
                i += 1      

            # 4.2.1 Produção Bibliográfica Validada
            i = 0
            while f'biblio_titulo_{i}' in request.form:
                if request.form.get(f'biblio_validado_{i}'): # Só salva se a caixinha "Validar" foi marcada
                    paises = request.form.getlist(f'paises_coautores_{i}[]')
                    db.session.add(ProducaoBibliograficaValidada(
                        titulo=request.form.get(f'biblio_titulo_{i}'),
                        autor=request.form.get(f'biblio_autor_{i}'),
                        ano=int(request.form.get(f'biblio_ano_{i}') or 0),
                        categoria=request.form.get(f'biblio_categoria_{i}'),
                        internacional='Sim' if paises else 'Não',
                        paises_colaboracao=','.join(paises),
                        resposta=resposta_atual
                    ))
                i += 1

            # 4.2.3 Produção Artística Validada
            i = 0
            while f'art_titulo_{i}' in request.form:
                if request.form.get(f'art_validado_{i}'):
                    pais_art = request.form.get(f'art_pais_{i}')
                    db.session.add(ProducaoArtisticaValidada(
                        titulo=request.form.get(f'art_titulo_{i}'),
                        autor=request.form.get(f'art_autor_{i}'),
                        ano=int(request.form.get(f'art_ano_{i}') or 0),
                        categoria=request.form.get(f'art_categoria_{i}'),
                        internacional='Sim' if pais_art else 'Não',
                        paises_colaboracao=pais_art,
                        resposta=resposta_atual
                    ))
                i += 1

            # 4.4 Formação de RH Validada
            i = 0
            while f'rh_orientando_{i}' in request.form:
                if request.form.get(f'rh_validado_{i}'):
                    db.session.add(FormacaoRHValidada(
                        orientando=request.form.get(f'rh_orientando_{i}'),
                        orientador=request.form.get(f'rh_orientador_{i}'),
                        tipo=request.form.get(f'rh_tipo_{i}'),
                        subtipo=request.form.get(f'rh_subtipo_{i}'),
                        pais=request.form.get(f'rh_pais_{i}'),
                        resposta=resposta_atual
                    ))
                i += 1      

            # 4.4.2 Empresas (Nacionais e Estrangeiras)
            emp_nac_nomes = request.form.getlist('emp_nac_nome[]')
            for i in range(len(emp_nac_nomes)):
                nome = emp_nac_nomes[i]
                if nome:
                    tipo_interacao_val = request.form.getlist('emp_nac_tipo_interacao[]')[i]
                    db.session.add(EmpresaNacional(
                        nome=nome,
                        cnpj=request.form.getlist('emp_nac_cnpj[]')[i],
                        cnae=request.form.getlist('emp_nac_cnae[]')[i],
                        uf=request.form.getlist('emp_nac_uf[]')[i],
                        municipio=request.form.getlist('emp_nac_municipio[]')[i],
                        tipo_interacao=tipo_interacao_val,
                        tipo_interacao_outro=request.form.getlist('emp_nac_tipo_interacao_outro[]')[i] if tipo_interacao_val == 'Outro' else None,
                        formalizacao=request.form.getlist('emp_nac_formalizacao[]')[i],
                        objetivo=request.form.getlist('emp_nac_objetivo[]')[i],
                        resultado=request.form.getlist('emp_nac_resultado[]')[i],
                        resposta=resposta_atual
                    ))

            emp_est_nomes = request.form.getlist('emp_est_nome[]')
            for i in range(len(emp_est_nomes)):
                nome = emp_est_nomes[i]
                if nome:
                    tipo_interacao_val = request.form.getlist('emp_est_tipo_interacao[]')[i]
                    db.session.add(EmpresaEstrangeira(
                        nome=nome,
                        pais=request.form.getlist('emp_est_pais[]')[i],
                        area_atuacao=request.form.getlist('emp_est_area[]')[i],
                        vigencia=request.form.getlist('emp_est_vigencia[]')[i],
                        tipo_interacao=tipo_interacao_val,
                        tipo_interacao_outro=request.form.getlist('emp_est_tipo_interacao_outro[]')[i] if tipo_interacao_val == 'Outro' else None,
                        formalizacao=request.form.getlist('emp_est_formalizacao[]')[i],
                        objetivo=request.form.getlist('emp_est_objetivo[]')[i],
                        resultado=request.form.getlist('emp_est_resultado[]')[i],
                        resposta=resposta_atual
                    ))

            # 4.5 Contratos de Transferência de Tecnologia
            contratos_empresas = request.form.getlist('cont_empresa[]')
            for i in range(len(contratos_empresas)):
                empresa = contratos_empresas[i]
                if empresa:
                    data_str = request.form.getlist('cont_data[]')[i]
                    data_assinatura = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None
                    tipo_acordo_val = request.form.getlist('cont_tipo_acordo[]')[i]
                    db.session.add(ContratoTecnologia(
                        empresa=empresa,
                        cnpj=request.form.getlist('cont_cnpj[]')[i],
                        cnae=request.form.getlist('cont_cnae[]')[i],
                        pais=request.form.getlist('cont_pais[]')[i],
                        uf=request.form.getlist('cont_uf[]')[i],
                        municipio=request.form.getlist('cont_municipio[]')[i],
                        tipo_acordo=tipo_acordo_val,
                        tipo_acordo_outro=request.form.getlist('cont_tipo_acordo_outro[]')[i] if tipo_acordo_val == 'Outro' else None,
                        finalidade=request.form.getlist('cont_finalidade[]')[i],
                        data_assinatura=data_assinatura,
                        vigencia=request.form.getlist('cont_vigencia[]')[i],
                        contrapartida_financeira=parse_moeda(request.form.getlist('cont_contrapartida[]')[i]),
                        resposta=resposta_atual
                    ))
            
            # 4.6 Acordos de Confidencialidade (NDA)
            empresas_nda = request.form.getlist('nda_empresa[]')
            for i in range(len(empresas_nda)):
                empresa = empresas_nda[i]
                if empresa:
                    db.session.add(AcordoNDA(
                        empresa=empresa,
                        localizacao=request.form.getlist('nda_localizacao[]')[i],
                        vigencia=request.form.getlist('nda_vigencia[]')[i],
                        finalidade=request.form.getlist('nda_finalidade[]')[i],
                        vinculado_contrato=request.form.getlist('nda_vinculado[]')[i],
                        resposta=resposta_atual
                    ))

            # 4.7.1 Cooperação Internacional
            instituicoes_coop = request.form.getlist('coop_instituicao[]')
            for i in range(len(instituicoes_coop)):
                instituicao = instituicoes_coop[i]
                if instituicao:
                    tipo_interacao_val = request.form.getlist('coop_tipo_interacao[]')[i]
                    db.session.add(CooperacaoInternacional(
                        instituicao=instituicao,
                        pais=request.form.getlist('coop_pais[]')[i],
                        tipo_interacao=tipo_interacao_val,
                        tipo_interacao_outro=request.form.getlist('coop_tipo_interacao_outro[]')[i] if tipo_interacao_val == 'Outro' else None,
                        objetivo=request.form.getlist('coop_objetivo[]')[i],
                        vigencia=request.form.getlist('coop_vigencia[]')[i],
                        status=request.form.getlist('coop_status[]')[i],
                        resultados=request.form.getlist('coop_resultados[]')[i],
                        resposta=resposta_atual
                    ))
            
            # 4.7.3 Pesquisadores Visitantes
            nomes_visitantes = request.form.getlist('visitante_nome[]')
            for i in range(len(nomes_visitantes)):
                nome = nomes_visitantes[i]
                if nome:
                    natureza_val = request.form.getlist('visitante_natureza[]')[i]
                    objetivo_val = request.form.getlist('visitante_objetivo[]')[i]
                    db.session.add(PesquisadorVisitante(
                        nome=nome,
                        origem=request.form.getlist('visitante_origem[]')[i],
                        area_atuacao=request.form.getlist('visitante_area[]')[i],
                        natureza_participacao=natureza_val,
                        natureza_outro=request.form.getlist('visitante_natureza_outro[]')[i] if natureza_val == 'Outro' else None,
                        duracao_tempo=int(request.form.getlist('visitante_duracao_tempo[]')[i] or 0),
                        duracao_unidade=request.form.getlist('visitante_duracao_unidade[]')[i],
                        objetivo=objetivo_val,
                        objetivo_outro=request.form.getlist('visitante_objetivo_outro[]')[i] if objetivo_val == 'Outro' else None,
                        resposta=resposta_atual
                    ))
            
            # 4.8 Outras Orientações
            tipos_orientacao = request.form.getlist('outra_orient_tipo[]')
            for i in range(len(tipos_orientacao)):
                tipo = tipos_orientacao[i]
                if tipo:
                    inicio_str = request.form.getlist('outra_orient_inicio[]')[i]
                    data_inicio = datetime.strptime(inicio_str, '%Y-%m-%d').date() if inicio_str else None
                    db.session.add(OutraOrientacao(
                        tipo=tipo,
                        tipo_outro=request.form.getlist('outra_orient_tipo_outro[]')[i],
                        orientando=request.form.getlist('outra_orient_nome[]')[i],
                        vinculo=request.form.getlist('outra_orient_vinculo[]')[i],
                        vinculo_outro=request.form.getlist('outra_orient_vinculo_outro[]')[i],
                        titulo=request.form.getlist('outra_orient_titulo[]')[i],
                        inicio=data_inicio,
                        status=request.form.getlist('outra_orient_status[]')[i],
                        resposta=resposta_atual
                    ))

            # 4.9 Atividades de Divulgação
            indices_atividades = set(match.group(1) for key in request.form for match in [re.search(r'div_descricao_(\d+)', key)] if match)
            for index in sorted(indices_atividades, key=int):
                db.session.add(AtividadeDivulgacao(
                    instrumentos=','.join(request.form.getlist(f'div_instrumento_{index}[]')),
                    instrumento_outro=request.form.get(f'div_instrumento_outro_{index}'),
                    publicos_alvo=','.join(request.form.getlist(f'div_publico_{index}[]')),
                    publico_outro=request.form.get(f'div_publico_outro_{index}'),
                    descricao=request.form.get(f'div_descricao_{index}'),
                    periodicidade=request.form.get(f'div_periodicidade_{index}'),
                    abrangencia=request.form.get(f'div_abrangencia_{index}'),
                    alcance_estimado=int(request.form.get(f'div_alcance_{index}') or 0),
                    municipio=request.form.get(f'div_municipio_{index}'),
                    uf=request.form.get(f'div_uf_{index}'),
                    foco_vulneraveis=request.form.get(f'div_foco_vulneravel_{index}'),
                    pop_vulneraveis=','.join(request.form.getlist(f'div_pop_vulneravel_{index}[]')),
                    pop_vulneravel_outro=request.form.get(f'div_pop_vulneravel_outro_{index}'),
                    resposta=resposta_atual
                ))
            
            # 5. Eventos Organizados
            nomes_eventos = request.form.getlist('evento_nome[]')
            for i in range(len(nomes_eventos)):
                nome = nomes_eventos[i]
                if nome:
                    tipo_val = request.form.getlist('evento_tipo[]')[i]
                    db.session.add(EventoOrganizado(
                        nome=nome,
                        tipo=tipo_val,
                        tipo_outro=request.form.getlist('evento_tipo_outro[]')[i] if tipo_val == 'Outro' else None,
                        publico_alvo=request.form.getlist('evento_publico[]')[i],
                        abrangencia=request.form.getlist('evento_abrangencia[]')[i],
                        num_participantes=int(request.form.getlist('evento_participantes[]')[i] or 0),
                        data=request.form.getlist('evento_data[]')[i],
                        local=request.form.getlist('evento_local[]')[i],
                        resposta=resposta_atual
                    ))
            
            # 6. Progresso das Metas
            for key, value in request.form.items():
                if key.startswith('progresso_meta_'):
                    meta_id_original = key.replace('progresso_meta_', '')
                    progresso_valor = int(value)
                    db.session.add(MetaProgresso(
                        meta_id_original=meta_id_original,
                        progresso=progresso_valor,
                        resposta=resposta_atual
                    ))
            
            # 6. Resultados 
            i = 0
            while f'resultado_descricao_{i}' in request.form:
                desc = request.form.get(f'resultado_descricao_{i}')
                if desc:
                    contexto_lista = request.form.getlist(f'resultado_contexto_{i}[]')
                    contexto_str = ', '.join(contexto_lista)
                    dimensoes_lista = request.form.getlist(f'resultado_dimensoes_{i}[]')
                    dimensoes_str = ', '.join(dimensoes_lista)
                    produtos_lista = request.form.getlist(f'resultado_produtos_{i}[]')
                    produtos_str = ', '.join(produtos_lista)

                    db.session.add(ResultadoProposto(
                        descricao=desc,
                        contexto=contexto_str,
                        dimensoes=dimensoes_str,
                        objetivos_especificos=request.form.get(f'resultado_objetivos_{i}'),
                        produtos=produtos_str,
                        resposta=resposta_atual
                    ))
                i += 1

            db.session.commit()
            
            # Resposta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'multipart/form-data' in request.content_type:
                 return jsonify({'status': 'success', 'message': 'Progresso salvo com sucesso!'})

            return render_template('sucesso.html', nome=coordenador, resposta_id=resposta_atual.id)

        except Exception as e:
            db.session.rollback()
            logging.error(f"ERRO AO SALVAR FORMULÁRIO: {e}")
            return "Ocorreu um erro ao salvar o formulário.", 500

    # --- 1. Inicializa as variáveis de pré-preenchimento ---
    orcamento_data = {}
    nome_projeto_preenchido = ""
    instituicao_sede_preenchida = ""

    # Caminho da nova planilha limpa
    planilha_mestre_path = os.path.join(DADOS_PATH, 'Dados INCT 58_22.xlsx')
    if not os.path.exists(planilha_mestre_path):
        planilha_mestre_path = os.path.join(DADOS_PATH, 'Dados INCT 58_22.xls')

    if os.path.exists(planilha_mestre_path):
        try:
            logging.info(f"Carregando Planilha Mestre LIMPA: {planilha_mestre_path}")
            
            # Lê com header=0 (Linha 1 é o cabeçalho)
            df_mestre = pd.read_excel(planilha_mestre_path, header=0)
            
            # Renomeia colunas para garantir padrão (remove espaços)
            df_mestre.columns = [str(c).strip().replace(' ', '_') for c in df_mestre.columns]

            if 'Processo' in df_mestre.columns:
                df_mestre['Processo_limpo'] = df_mestre['Processo'].astype(str).str.replace(r'\D', '', regex=True)
                numero_proc_limpo = re.sub(r'\D', '', str(numero_proc))

                projeto_linha_df = df_mestre[df_mestre['Processo_limpo'] == numero_proc_limpo]

                if not projeto_linha_df.empty:
                    dados_projeto = projeto_linha_df.iloc[0] 

                    # 3.a) Seção 1
                    nome_projeto_preenchido = dados_projeto.get('INCT')
                    instituicao_sede_preenchida = dados_projeto.get('Instituição_Sede')

                    def converter_seguro(chave, valor):

                        resultado = 0.0
                        
                        if pd.isna(valor) or valor == '': 
                            resultado = 0.0
                        
                        # Se já é número
                        elif isinstance(valor, (int, float)): 
                            resultado = float(valor)
                            
                        # Se é texto
                        else:
                            try:
                                val_str = str(valor).replace('R$', '').strip()
                                if ',' in val_str:
                                    val_str = val_str.replace('.', '').replace(',', '.')
                                resultado = float(val_str)
                            except:
                                resultado = 0.0
                        
                        return round(resultado, 2)

                    # --- ATUALIZANDO AS CHAMADAS PARA PASSAR O NOME DO CAMPO ---
                    orcamento_data['cnpq_capital_aprovado'] = converter_seguro('Capital_CNPq', dados_projeto.get('Capital_CNPq'))
                    orcamento_data['capes_capital_aprovado'] = converter_seguro('Capital_CAPES', dados_projeto.get('Capital_CAPES'))
                    orcamento_data['faps_capital_aprovado'] = converter_seguro('Capital_FAP', dados_projeto.get('Capital_FAP'))

                    orcamento_data['cnpq_custeio_aprovado'] = converter_seguro('Custeio_CNPq', dados_projeto.get('Custeio_CNPq'))
                    orcamento_data['capes_custeio_aprovado'] = converter_seguro('Custeio_CAPES', dados_projeto.get('Custeio_CAPES'))
                    
                    # ESTE É O DO BUG:
                    orcamento_data['faps_custeio_aprovado'] = converter_seguro('Custeio_FAP', dados_projeto.get('Custeio_FAP')) 

                    orcamento_data['cnpq_bolsas_pais_aprovado'] = converter_seguro('Bolsa_CNPq', dados_projeto.get('Bolsa_CNPq'))
                    orcamento_data['capes_bolsas_pais_aprovado'] = converter_seguro('Bolsa_CAPES', dados_projeto.get('Bolsa_CAPES'))
                    orcamento_data['faps_bolsas_pais_aprovado'] = converter_seguro('Bolsa_FAP', dados_projeto.get('Bolsa_FAP'))
                    
                    # Zera os campos que não existem na planilha
                    for fonte in ['cnpq', 'capes', 'faps']:
                        orcamento_data[f'{fonte}_custeio_pago'] = 0
                        orcamento_data[f'{fonte}_capital_pago'] = 0
                        orcamento_data[f'{fonte}_bolsas_pais_pago'] = 0
                        orcamento_data[f'{fonte}_bolsas_ext_aprovadas'] = 0
                else:
                    logging.warning(f"Processo {numero_proc_limpo} não encontrado na Planilha Mestre.")
            else:
                logging.error(f"Coluna 'Processo' não encontrada. Colunas: {list(df_mestre.columns)}")

        except Exception as e:
            logging.error(f"ERRO ao processar a Planilha Mestre LIMPA: {e}", exc_info=True)
    else:
        logging.warning(f"Arquivo Planilha Mestre não encontrado.")

    form_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'formacao')
    producao_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'producao')
    instituicoes_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'instituicoes')
    membros_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'membros')

    rh_records = pd.DataFrame() # Começa com um DataFrame vazio por padrão
    if form_path:
        try:
            df_rh = pd.read_excel(form_path)
            rh_records = df_rh.copy()
            
            if 'TPO_ORIENT' in rh_records.columns:
                rh_records['ordem'] = rh_records['TPO_ORIENT'].str.lower().apply(lambda x: 0 if 'conclu' in str(x) else 1)
                rh_records = rh_records.sort_values(by=['ordem', 'TPO_ORIENT', 'TPO_SUBTIPO'])

        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de formação: {e}")

    MAPEAMENTO_INTELIGENTE_CIENTIFICO = {
        'Artigos aceitos para publicação': ['ARTIGO-ACEITO'],
        'Artigos completos publicados em periódicos': ['ARTIGO-COMPLETO', 'ARTIGOS-PUBLICADOS', 'ARTIGO-PUBLICADO'],
        'Capítulos de livros publicados': ['CAPITULO', 'CAPITULOS'],  
        'Livros publicados/organizados ou edições': ['LIVRO', 'LIVROS'], 
        'Trabalhos completos publicados em anais de congressos': ['TRABALHO-COMPLETO', 'TRABALHOS-PUBLICADOS'],
        'Resumos expandidos publicados em anais de congressos': ['TRABALHO-RESUMIDO', 'RESUMO-EXPANDIDO'], # Separado do resumo simples
        'Resumos publicados em anais de congressos': ['RESUMO-EM-EVENTO', 'RESUMO'],
        'Apresentações de Trabalho': ['APRESENTACAO'],
        'Outras produções bibliográficas': ['OUTRA-PRODUCAO-BIBLIOGRAFICA'],
        # Caso sobre algo, cai no padrão da função
    }

    # 2. Função de mapeamento aprimorada
    def mapear_tipo_producao(texto_bruto, mapa):
        if not isinstance(texto_bruto, str):
            return 'Outra produção bibliográfica (científica especializada)'

        texto_limpo = remover_acentos(texto_bruto.upper()).replace(' ', '-').replace('_', '-')
        
        for categoria_final, palavras_chave in mapa.items():
            for palavra in palavras_chave:
                if palavra in texto_limpo:
                    return categoria_final
        
        # Se não encontrar nenhuma correspondência, retorna um valor padrão
        return 'Outra produção bibliográfica (científica especializada)'

    # 3. Lemos a planilha, mapeamos e ordenamos os dados
    dados_producao_cientifica = []
    bibliografica_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'bibliografica') 
    
    if bibliografica_path:
        try:
            df_cientifica = pd.read_excel(bibliografica_path)
            
            # Garante que a coluna 'Nome' existe antes de filtrar
            if 'Nome' in df_cientifica.columns:
                # 1. Remove linhas onde a coluna 'Nome' é um valor nulo (células vazias de verdade)
                df_cientifica.dropna(subset=['Nome'], inplace=True)
                
                # 2. Garante que a coluna 'Nome' seja tratada como texto para as próximas checagens
                df_cientifica['Nome'] = df_cientifica['Nome'].astype(str)

                # 3. Remove linhas onde o 'Nome', depois de remover espaços, é '#N/D' ou uma string vazia
                df_cientifica = df_cientifica[~df_cientifica['Nome'].str.strip().isin(['#N/D', ''])]

            df_cientifica = df_cientifica.fillna('')

            if 'tipo_producao' in df_cientifica.columns:
                df_cientifica['categoria_mapeada'] = df_cientifica['tipo_producao'].apply(
                    lambda texto: mapear_tipo_producao(texto, MAPEAMENTO_INTELIGENTE_CIENTIFICO)
                )
                df_cientifica = df_cientifica.sort_values(by='categoria_mapeada')
            else:
                df_cientifica['categoria_mapeada'] = ''

            dados_producao_cientifica = df_cientifica.to_dict('records')
        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de produção bibliográfica: {e}")

    # 1. Mapeamento Tecnológico (Ajustado Plurais e Minúsculas)
    MAPEAMENTO_INTELIGENTE_TECNOLOGICO = {
        'Assessoria e consultoria': ['CONSULTORIA'],
        'Extensão tecnológica': ['EXTENSAO-TECNOLOGICA', 'EXTENSAO TECNOLOGICA'], 
        'Programas de computador sem registro': ['PROGRAMA', 'SOFTWARE'], 
        'Produtos tecnológicos': ['PRODUTO'], 
        'Processos ou técnicas': ['PROCESSO', 'TECNICA'],
        'Trabalhos técnicos': ['TRABALHO-TECNICO', 'TRABALHO TECNICO', 'RELATORIO'], 
        'Cartas, mapas ou similares': ['CARTA', 'MAPA'],
        'Curso de curta duração ministrado': ['CURSO', 'OFICINA'],
        'Desenvolvimento de material didático ou instrucional': ['DIDATICO', 'INSTRUCIONAL'],
        'Manutenção de obras artísticas/restauração': ['MANUTENCAO', 'RESTAURACAO'],
        'Organização de evento': ['ORGANIZACAO'],
        'Outras produções técnicas': ['OUTRO']
    }

    def mapear_tipo_producao(texto_bruto, mapa):
        if not isinstance(texto_bruto, str): return 'Outros'
        texto_limpo = remover_acentos(texto_bruto.upper()).replace(' ', '-').replace('_', '-')
        for categoria_final, palavras_chave in mapa.items():
            for palavra in palavras_chave:
                if palavra in texto_limpo:
                    return categoria_final
        return 'Outros'

    dados_producao_tecnologica = []
    tecnologica_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'tecnologica') 

    if tecnologica_path:
        try:
            # 1. Lê a primeira aba da planilha, sem o .fillna('') inicial
            df_tecnologica = pd.read_excel(tecnologica_path)
            
            # Filtro 1: Ano (a partir de 2023)
            if 'ano' in df_tecnologica.columns:
                df_tecnologica['ano'] = pd.to_numeric(df_tecnologica['ano'], errors='coerce')
                df_tecnologica.dropna(subset=['ano'], inplace=True)
                df_tecnologica = df_tecnologica[df_tecnologica['ano'] >= 2023]

            # Filtro 2: Natureza (apenas os valores que você especificou)
            if 'natureza' in df_tecnologica.columns:
                valores_permitidos = ['CONSULTORIA', 'EXTENSAO_TECNOLOGICA']
                df_tecnologica = df_tecnologica[df_tecnologica['natureza'].isin(valores_permitidos)]

            df_tecnologica = df_tecnologica.fillna('')
            
            if 'titulo_trabalho_tecnico' in df_tecnologica.columns:
                df_tecnologica.dropna(subset=['titulo_trabalho_tecnico'], inplace=True)
                df_tecnologica['titulo_trabalho_tecnico'] = df_tecnologica['titulo_trabalho_tecnico'].astype(str)
                df_tecnologica = df_tecnologica[~df_tecnologica['titulo_trabalho_tecnico'].str.strip().isin(['#N/D', ''])]

            if 'natureza' in df_tecnologica.columns:
                df_tecnologica['categoria_mapeada'] = df_tecnologica['natureza'].apply(
                    lambda texto: mapear_tipo_producao(texto, MAPEAMENTO_INTELIGENTE_TECNOLOGICO)
                )
                df_tecnologica = df_tecnologica.sort_values(by='categoria_mapeada')
            else:
                df_tecnologica['categoria_mapeada'] = 'Outra produção técnica'

            dados_producao_tecnologica = df_tecnologica.to_dict('records')
        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de produção tecnológica: {e}") 

    MAPEAMENTO_INTELIGENTE_DIVULGACAO = {
        'Textos em jornais de notícias/revistas': ['JORNAL', 'REVISTA', 'MAGAZINE'], 
        'Trabalhos publicados em anais de eventos': ['ANAIS', 'TRABALHO-EM-EVENTOS'], 
        'Apresentação de trabalho e palestra': ['APRESENTACAO', 'PALESTRA'],
        'Curso de curta duração ministrado': ['CURSO', 'OFICINA'],
        'Desenvolvimento de material didático ou instrucional': ['DIDATICO', 'INSTRUCIONAL', 'CARTILHA', 'MANUAL'],
        'Entrevistas, mesas redondas, programas e comentários na mídia': ['ENTREVISTA', 'MESA-REDONDA', 'PROGRAMA', 'MIDIA'],
        'Redes sociais, websites e blogs': ['REDES-SOCIAIS', 'WEBSITE', 'BLOG', 'SITE']
    }

    # Reutilizamos a mesma função de mapeamento
    def mapear_tipo_producao(texto_bruto, mapa):
        if not isinstance(texto_bruto, str):
            return 'Outros'
        texto_limpo = remover_acentos(texto_bruto.upper()).replace(' ', '-').replace('_', '-')
        for categoria_final, palavras_chave in mapa.items():
            for palavra in palavras_chave:
                if palavra in texto_limpo:
                    return categoria_final
        return 'Outros' 

    # 2. Lemos a planilha, filtramos, mapeamos e ordenamos os dados
    dados_divulgacao = []
    divulgacao_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'divulgacao') 

    if divulgacao_path:
        try:
            df_divulgacao = pd.read_excel(divulgacao_path)
            
            if 'Título' in df_divulgacao.columns:
                df_divulgacao = df_divulgacao.fillna('')
                df_divulgacao.dropna(subset=['Título'], inplace=True)
                df_divulgacao['Título'] = df_divulgacao['Título'].astype(str)
                df_divulgacao = df_divulgacao[~df_divulgacao['Título'].str.strip().isin(['#N/D', ''])]
            
            if 'tipo_producao' in df_divulgacao.columns:
                df_divulgacao['categoria_mapeada'] = df_divulgacao['tipo_producao'].apply(
                    lambda texto: mapear_tipo_producao(texto, MAPEAMENTO_INTELIGENTE_DIVULGACAO)
                )
                df_divulgacao = df_divulgacao.sort_values(by='categoria_mapeada')
            else:
                df_divulgacao['categoria_mapeada'] = 'Outros'

            dados_divulgacao = df_divulgacao.to_dict('records')
        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de divulgação: {e}")        

    
    instituicoes_com_uf = []
    instituicoes_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'instituicoes')
    if instituicoes_path:
        try:
            # --- ROTINA DETETIVE PARA ACHAR O CABEÇALHO ---
            df_temp = pd.read_excel(instituicoes_path, header=None)
            header_row = 0 
            for i in range(min(10, len(df_temp))):
                row_str = ''.join(str(c) for c in df_temp.iloc[i]).lower()
                if 'instituicao' in row_str or 'instituição' in row_str:
                    header_row = i
                    break
            df_instituicoes = pd.read_excel(instituicoes_path, header=header_row)

            # --- PADRONIZAÇÃO E LIMPEZA ---
            df_instituicoes.columns = [remover_acentos(str(c)).strip().lower().replace(' ', '_') for c in df_instituicoes.columns]
            
            nome_longo = 'nome_da_empresa/fap/organizacao_parceira'
            if nome_longo in df_instituicoes.columns:
                df_instituicoes = df_instituicoes.rename(columns={nome_longo: 'instituicao'})

            colunas_desejadas = ['instituicao', 'classificacao', 'tipo', 'cidade', 'uf', 'pais']

            for coluna in colunas_desejadas:
                if coluna not in df_instituicoes.columns:
                    df_instituicoes[coluna] = ''

            instituicoes_com_uf = df_instituicoes[colunas_desejadas].fillna('').to_dict('records')

        except Exception as e:
            logging.error(f"ERRO ao ler o arquivo de instituições: {e}")

    lista_membros_equipe = []
    if membros_path:
        try:
            # --- ROTINA DETETIVE INTELIGENTE PARA MEMBROS (VERSÃO FINAL E VERIFICADA) ---

            # 1. Mapa de Colunas: Construído com os nomes exatos da sua planilha.
            COLUNA_MAP_MEMBROS = {
                'nome_membro':    ['MEMBRO PROJETO'],
                'titulacao':      ['ÚLTIMA TITULAÇÃO'],
                'area_atuacao':   ['Áreas de Atuação'],
                'instituicao':    ['INSTITUIÇÃO DO PESQUISADOR'],
                'uf':             ['UF'],
                'cidade':         ['Cidade'],
                'pais':           ['País'],
                'categoria':      ['PAPEL DO PESQUISADOR NA EQUIPE'],
                'status':         ['Status']
            }

            # Encontra o cabeçalho usando colunas que sabemos que existem
            header_row = find_header_row(membros_path, ['MEMBRO PROJETO', 'ÚLTIMA TITULAÇÃO'])
            if header_row is None:
                raise ValueError("Cabeçalho mínimo (MEMBRO PROJETO, ÚLTIMA TITULAÇÃO) não encontrado.")

            df_membros = pd.read_excel(membros_path, header=header_row)
            
            # Limpa e padroniza os nomes das colunas do arquivo para comparação
            colunas_no_arquivo = {remover_acentos(str(c).strip().upper()): str(c).strip() for c in df_membros.columns}

            # 2. Constrói o mapa de renomeação dinamicamente
            rename_map = {}
            for nome_interno, possíveis_nomes in COLUNA_MAP_MEMBROS.items():
                for nome in possíveis_nomes:
                    nome_padronizado = remover_acentos(nome.upper())
                    if nome_padronizado in colunas_no_arquivo:
                        nome_original = colunas_no_arquivo[nome_padronizado]
                        rename_map[nome_original] = nome_interno
                        break

            # 3. Processa o DataFrame
            # Garante que a coluna de nome do membro exista antes de tentar remover NAs
            nome_coluna_original = next((v for k, v in rename_map.items() if k == 'nome_membro'), df_membros.columns[0])
            df_membros.dropna(subset=[nome_coluna_original], inplace=True)
            df_renomeado = df_membros.rename(columns=rename_map)

            for col in df_renomeado.columns:
                # Verifica se a coluna é do tipo 'object' (geralmente strings)
                if df_renomeado[col].dtype == 'object':
                    df_renomeado[col] = df_renomeado[col].str.strip()

            # Garante que todas as colunas internas existam
            for col_interna in COLUNA_MAP_MEMBROS.keys():
                if col_interna not in df_renomeado.columns:
                    df_renomeado[col_interna] = ''
            
            df_final = df_renomeado[list(COLUNA_MAP_MEMBROS.keys())]
            df_unicos = df_final.drop_duplicates(subset=['nome_membro'], keep='first')
            
            lista_membros_equipe = df_unicos.fillna('').to_dict('records')

        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de membros: {e}")
    
    # =========================================================================
    # PASSO 1: Carrega os objetivos e agrupa por missão (COM NOME E DESCRIÇÃO SEPARADOS)
    # =========================================================================
    objetivos_por_id = {}
    missoes_agrupadas = {}
    objetivos_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'objetivos especificos')
    
    if objetivos_path:
        df_objetivos = pd.read_excel(objetivos_path)
        for _, row in df_objetivos.iterrows():
            obj_id = int(row['ID_Objetivo'])
            missao_nome = row['Missao']
            
            # --- CRIAÇÃO DO OBJETO DETALHADO ---
            objetivo_data = {
                "id": obj_id, 
                "nome": f"Objetivo {obj_id}",            
                "descricao": row['Descricao_Objetivo'],  
                "metas": [], 
                "missao": missao_nome
            }
            
            objetivos_por_id[obj_id] = objetivo_data
            
            if missao_nome not in missoes_agrupadas:
                missoes_agrupadas[missao_nome] = []
            missoes_agrupadas[missao_nome].append(objetivo_data)

    # =========================================================================
    # PASSO 2: Carrega as metas e vincula aos objetivos
    # =========================================================================
    lista_unica_metas = {}
    metas_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'metas')
    
    if metas_path and objetivos_por_id:
        df_metas = pd.read_excel(metas_path)
        for _, row in df_metas.iterrows():
            meta_id = int(row['ID_Meta'])
            ids_objetivos_str = str(row['ID_Objetivo']).split()
            objetivos_afetados_ids = [int(id_str) for id_str in ids_objetivos_str if id_str.isdigit()]

            # Cria a lista de objetos detalhados para enviar ao HTML
            objetivos_detalhados = []
            missoes_afetadas = []

            for obj_id in objetivos_afetados_ids:
                if obj_id in objetivos_por_id:
                    objetivos_detalhados.append(objetivos_por_id[obj_id])
                    
                    missao_nome = objetivos_por_id[obj_id]['missao']
                    if missao_nome not in missoes_afetadas:
                        missoes_afetadas.append(missao_nome)
                
            if meta_id not in lista_unica_metas:
                lista_unica_metas[meta_id] = {
                    "id": meta_id, 
                    "descricao": row['Descricao_Meta'],
                    "objetivos_afetados": objetivos_afetados_ids,
                    "objetivos": objetivos_detalhados, 
                    "missoes_afetadas": missoes_afetadas
                }
            
            for obj_id in objetivos_afetados_ids:
                if obj_id in objetivos_por_id:
                    meta_referencia = {"id": meta_id} 
                    objetivos_por_id[obj_id]['metas'].append(meta_referencia)
    
    # Define a ordem exata das missões
    ordem_missoes = [
        "Pesquisa",
        "Formação de Recursos Humanos",
        "Internacionalização",
        "Divulgação científica e popularização da ciência",
        "Transferência de Conhecimento para a indústria nacional para o Setor empresarial e/ou para o Setor Público",
        "Transferência de Conhecimentos para a Sociedade"
    ]

    missoes_para_progresso = []
    missao_id_counter = 1
    
    # Primeiro, percorre a lista na ordem desejada
    for missao_nome in ordem_missoes:
        if missao_nome in missoes_agrupadas:
            objetivos_lista = missoes_agrupadas[missao_nome]
            objetivos_lista_ordenada = sorted(objetivos_lista, key=lambda obj: obj['id'])
            
            missoes_para_progresso.append({
                "id": missao_id_counter, 
                "nome": missao_nome, 
                "objetivos": objetivos_lista_ordenada
            })
            missao_id_counter += 1
            del missoes_agrupadas[missao_nome]

    # Depois, adiciona qualquer outra missão que sobrou
    for missao_nome, objetivos_lista in missoes_agrupadas.items():
        objetivos_lista_ordenada = sorted(objetivos_lista, key=lambda obj: obj['id'])
        missoes_para_progresso.append({
            "id": missao_id_counter, 
            "nome": missao_nome, 
            "objetivos": objetivos_lista_ordenada
        })
        missao_id_counter += 1

    # lista_resultados = [] LEITURA PLANILHA EXCEL 6. RESULTADOS
    resultados_path = buscar_arquivo_em_pasta(caminho_pasta_projeto, 'resultados')
    
    if resultados_path:
        try:
            df_resultados = pd.read_excel(resultados_path).fillna('') # fillna('') evita erros com células vazias
            
            # Converte o DataFrame para lista de dicionários, mantendo os nomes originais das colunas
            lista_resultados = df_resultados.to_dict('records')
            
            for resultado in lista_resultados:
                if isinstance(resultado.get('Contexto'), str):
                    resultado['Contexto_lista'] = [item.strip() for item in resultado['Contexto'].split('/')]
                else:
                    resultado['Contexto_lista'] = []

                if isinstance(resultado.get('Dimensões'), str):
                    resultado['Dimensões_lista'] = [item.strip() for item in resultado['Dimensões'].split(',')]
                else:
                    resultado['Dimensões_lista'] = []
                
                if isinstance(resultado.get('Produtos'), str):
                    resultado['Produtos_lista'] = [item.strip() for item in resultado['Produtos'].split(',')]
                else:
                    resultado['Produtos_lista'] = []

        except Exception as e:
            logging.error(f"ERRO ao processar o arquivo de resultados: {e}")    

    caminho_nova_planilha_incts = "DADOS/Lista de todos os INCT's fornecidos pela COAFO.xlsx"
    df_incts = pd.read_excel(caminho_nova_planilha_incts, header=3)

    df_incts_renomeado = df_incts.rename(columns={
        'Titulo do Processo': 'nome',
        'Beneficiário': 'coordenador',
        'Grande Área': 'grande_area',
        'Área de Conhecimento': 'area_conhecimento'
    })
    
    colunas_necessarias = ['nome', 'coordenador', 'grande_area', 'area_conhecimento']
    dados_completos_incts = df_incts_renomeado[colunas_necessarias].to_dict(orient='records')
    
    dados_json_para_template = json.dumps(dados_completos_incts)   
    
    cidades_por_uf = {}
    caminho_municipios = os.path.join(DADOS_PATH, 'Estados - IBGE.xlsx')
    
    # Tenta ler o arquivo (se não achar xlsx, tenta xls)
    if not os.path.exists(caminho_municipios):
        caminho_municipios = os.path.join(DADOS_PATH, 'Estados - IBGE.xls')

    if os.path.exists(caminho_municipios):
        try:
            df_mun = pd.read_excel(caminho_municipios)
            
            # Padroniza nomes das colunas para maiúsculo (UF, CIDADE)
            df_mun.columns = [str(c).strip().upper() for c in df_mun.columns]

            if 'UF' in df_mun.columns and 'CIDADE' in df_mun.columns:
                # Remove linhas vazias
                df_mun.dropna(subset=['UF', 'CIDADE'], inplace=True)
                # Agrupa: {'MG': ['Belo Horizonte', ...], 'SP': ['Santos', ...]}
                cidades_por_uf = df_mun.groupby('UF')['CIDADE'].apply(list).to_dict()
            else:
                logging.warning(f"Colunas 'UF' e 'CIDADE' não encontradas em {caminho_municipios}")

        except Exception as e:
            logging.error(f"Erro ao carregar planilha de municípios: {e}")
    
    cidades_json = json.dumps(cidades_por_uf)

    return render_template(
        'formulario.html',
        coordenador=coordenador, 
        processo_formatado=processo_formatado,
        numero_processo=numero_proc,
        now=datetime.now(),
        cidades_por_uf_json=cidades_json,
        nome_projeto=nome_projeto_preenchido,        
        instituicao_sede=instituicao_sede_preenchida,  
        orcamento=orcamento_data,
        rh=rh_records.to_dict(orient='records') if not rh_records.empty else [], 
        producao_cientifica=dados_producao_cientifica,
        producao_tecnologica=dados_producao_tecnologica,
        dados_divulgacao=dados_divulgacao,
        instituicoes_com_uf=instituicoes_com_uf, 
        membros_equipe=lista_membros_equipe,
        missoes=missoes_para_progresso,
        metas_unicas=list(lista_unica_metas.values()),
        #resultados_propostos=lista_resultados,
        dados_completos_incts=dados_json_para_template,
        categorias=[],
        dados_producao={},
        tabela_producao = {},
        tabela_rh = {}
    )

@app.route('/gerar_pdf/<int:resposta_id>')
def gerar_pdf(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)

    # 1. Busca o usuário para encontrar o número do processo associado a esta resposta
    usuario = Usuario.query.filter_by(cpf=resposta.usuario_cpf).first()
    if not usuario:
        return "Erro: Usuário não encontrado para esta resposta.", 404
    
    processo_formatado = formatar_numero_processo(usuario.numero_processo)
    nome_coordenador = usuario.nome

    dados_principais = {c.name: getattr(resposta, c.name) for c in resposta.__table__.columns}
    
    # 2. Busca todas as tabelas filhas (inclusive as novas)
    membros = MembroEquipe.query.filter_by(resposta_id=resposta.id).all()
    orgs = OrganizacaoParceira.query.filter_by(resposta_id=resposta.id).all()
    recursos = RecursoAlavancado.query.filter_by(resposta_id=resposta.id).all()
    articulacoes = ArticulacaoINCT.query.filter_by(resposta_id=resposta.id).all()
    empresas_nac = EmpresaNacional.query.filter_by(resposta_id=resposta.id).all()
    empresas_est = EmpresaEstrangeira.query.filter_by(resposta_id=resposta.id).all()
    contratos = ContratoTecnologia.query.filter_by(resposta_id=resposta.id).all()
    ndas = AcordoNDA.query.filter_by(resposta_id=resposta.id).all()
    coops = CooperacaoInternacional.query.filter_by(resposta_id=resposta.id).all()
    divulgacoes = AtividadeDivulgacao.query.filter_by(resposta_id=resposta.id).all()
    metas = MetaProgresso.query.filter_by(resposta_id=resposta.id).all()
    resultados = ResultadoProposto.query.filter_by(resposta_id=resposta.id).all()
    visitantes = PesquisadorVisitante.query.filter_by(resposta_id=resposta.id).all()
    prod_tec = ProducaoTecnologicaValidada.query.filter_by(resposta_id=resposta.id).all()
    prod_biblio = ProducaoBibliograficaValidada.query.filter_by(resposta_id=resposta.id).all()
    prod_artistica = ProducaoArtisticaValidada.query.filter_by(resposta_id=resposta.id).all()
    formacao_rh = FormacaoRHValidada.query.filter_by(resposta_id=resposta.id).all()

    # 3. Organização de Dados para o Template do PDF
    
    projetos_empresas = []
    for emp in empresas_nac:
        projetos_empresas.append({"tipo_interacao": emp.tipo_interacao, "empresa": emp.nome, "pais": "Brasil", "status": emp.formalizacao})
    for emp in empresas_est:
        projetos_empresas.append({"tipo_interacao": emp.tipo_interacao, "empresa": emp.nome, "pais": emp.pais, "status": emp.formalizacao})

    interacoes_empresariais_internacionais = []
    for emp in empresas_est:
        interacoes_empresariais_internacionais.append({"natureza": f"Projeto ({emp.tipo_interacao})", "empresa": emp.nome, "pais": emp.pais})
    for c in contratos:
        if c.pais and c.pais.lower() != 'brasil':
            interacoes_empresariais_internacionais.append({"natureza": "Transferência de Tecnologia", "empresa": c.empresa, "pais": c.pais})
    for n in ndas:
        if n.localizacao and n.localizacao.lower() != 'brasil':
            interacoes_empresariais_internacionais.append({"natureza": "Acordo de Confidencialidade (NDA)", "empresa": n.empresa, "pais": n.localizacao})

    divulgacao_cientifica = [{"titulo": d.descricao, "tipo": d.instrumentos, "publico": d.publicos_alvo, "escopo": d.abrangencia} for d in divulgacoes]
    divulgacao_internacional = [{"titulo": d.instrumentos, "descricao": d.descricao} for d in divulgacoes if d.abrangencia == 'Internacional']

    resultados_alcançados = [{"descricao": r.descricao, "contexto": r.contexto, "dimensoes": r.dimensoes, "metas": r.objetivos_especificos} for r in resultados]
    metas_progresso_lista = [{"id": m.meta_id_original, "descricao": f"Progresso reportado para a Meta {m.meta_id_original}", "progresso": m.progresso} for m in metas]

    rh_membros_internacionais = []
    for m in membros:
        if m.pais and m.pais.lower() != 'brasil':
            rh_membros_internacionais.append({"nome": m.nome, "vinculo": "Membro da Equipe", "instituicao": m.instituicao, "pais": m.pais})
    for p in visitantes:
        rh_membros_internacionais.append({"nome": p.nome, "vinculo": "Pesquisador Visitante", "instituicao": p.origem, "pais": p.origem})

    autorizacoes_str = dados_principais.get('autorizacoes', '')
    lista_autorizacoes = [a.strip() for a in autorizacoes_str.split(',')] if autorizacoes_str else []

    # Resumos
    resumo_producoes = []
    for p in prod_tec:
        resumo_producoes.append({"categoria": "Técnica", "tipo": p.categoria, "quantidade": 1})
    for p in prod_biblio:
        resumo_producoes.append({"categoria": "Bibliográfica", "tipo": p.categoria, "quantidade": 1})
    for p in prod_artistica:
        resumo_producoes.append({"categoria": "Artística", "tipo": p.categoria, "quantidade": 1})

    resumo_rh_lista = []
    for rh in formacao_rh:
        resumo_rh_lista.append({"tipo": f"{rh.tipo} - {rh.subtipo}", "andamento": 1 if 'andamento' in rh.tipo.lower() else 0, "concluido": 1 if 'conclu' in rh.tipo.lower() else 0})

    resumo_prod_internacional = []
    for p in prod_biblio:
        if p.internacional == 'Sim':
            resumo_prod_internacional.append({"tipo": f"Bibliográfica - {p.categoria}", "quantidade": 1})
    for p in prod_artistica:
        if p.internacional == 'Sim':
            resumo_prod_internacional.append({"tipo": f"Artística - {p.categoria}", "quantidade": 1})
    for p in prod_tec:
        if p.abrangencia == 'Exterior':
            resumo_prod_internacional.append({"tipo": f"Técnica - {p.categoria}", "quantidade": 1})

    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')

    # Lê a logo e converte para Base64 para o PDF conseguir renderizar
    logo_path = os.path.join(app.root_path, 'static', 'logo_cnpq.png')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            logo_base64 = "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')

    # 4. Passa tudo para o template HTML
    html_para_pdf = render_template(
        "formulario_visual.html", 
        dados=dados_principais, 
        processo_formatado=processo_formatado,
        coordenador=nome_coordenador,
        data_geracao=data_geracao,
        logo_base64=logo_base64,
        membros_equipe=[m.__dict__ for m in membros],
        organizacoes_parceiras=[o.__dict__ for o in orgs],
        recursos_alavancados=[r.__dict__ for r in recursos],
        articulacoes_incts=[a.__dict__ for a in articulacoes],
        projetos_empresas=projetos_empresas,
        formacao_rh=[rh.__dict__ for rh in formacao_rh],
        atividades_divulgacao=divulgacao_cientifica,
        metas_progresso=metas_progresso_lista,
        resultados_propostos=[r.__dict__ for r in resultados],
        autorizacoes=lista_autorizacoes,
        prod_biblio=[pb.__dict__ for pb in prod_biblio],
        prod_tecnica=[pt.__dict__ for pt in prod_tec],
        prod_artistica=[pa.__dict__ for pa in prod_artistica],
        empresas_nacionais=[en.__dict__ for en in empresas_nac],
        empresas_estrangeiras=[ee.__dict__ for ee in empresas_est],
        contratos_tecnologia=[ct.__dict__ for ct in contratos],
        resumo_producoes=resumo_producoes,
        resumo_rh=resumo_rh_lista,
        resumo_prod_internacional=resumo_prod_internacional,
        interacoes_empresariais_internacionais=interacoes_empresariais_internacionais,
        rh_membros_internacionais=rh_membros_internacionais,
        acordos_cooperacao=[c.__dict__ for c in coops],
        divulgacao_internacional=divulgacao_internacional
    )
    
    try:
        pdf_content = asyncio.run(gerar_pdf_playwright(html_content=html_para_pdf))
        response = make_response(pdf_content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"inline; filename=relatorio_{resposta_id}.pdf"
        return response
    except Exception as e:
        logging.exception(f"Falha na geração do PDF para resposta_id={resposta_id}")
        return f"Erro interno ao gerar PDF: {e}", 500

@app.cli.command("init-db")
def init_db_command():
    """Cria as tabelas do banco de dados e cadastra os usuários iniciais."""
    try:
        db.create_all()
        print("\n✅ Estrutura do banco de dados criada com sucesso.")
        
        from cadastrar_usuarios import cadastrar_usuarios
        cadastrar_usuarios()
        print("✅ Usuários iniciais cadastrados com sucesso.")

    except Exception as e:
        print(f"\n❌ [ERRO CRÍTICO] Falha ao inicializar o banco de dados: {e}")
    print("\n")

@app.cli.command("reset-db")
def reset_db_command():
    """Apaga todas as tabelas e as recria do zero, SEM cadastrar usuários."""
    confirmacao = input("ATENÇÃO: Isso vai apagar TODOS os dados e usuários. Tem certeza? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return
    try:
        db.drop_all()
        print("-> Tabelas antigas removidas com sucesso.")
        db.create_all()
        print("✅ Banco de dados resetado com sucesso! (Estrutura limpa, sem usuários).")
    except Exception as e:
        print(f"❌ Erro ao resetar o banco de dados: {e}")    

@app.cli.command("clear-responses")
def clear_responses_command():
    """Apaga todas as respostas de formulários, mas mantém os usuários."""
    confirmacao = input("ATENÇÃO: Isso vai apagar TODAS as respostas de formulários enviadas. Os usuários e senhas serão MANTIDOS. Tem certeza? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return
    try:
        num_respostas_apagadas = db.session.query(Resposta).delete()
        db.session.commit()
        print(f"✅ Sucesso! {num_respostas_apagadas} respostas de formulário e todos os seus dados associados foram apagados.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao limpar as respostas: {e}")     

if __name__ == '__main__':
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("\n" + "="*50)
        print("Verificando status dos usuários na inicialização...")
    
        from cadastrar_usuarios import cadastrar_usuarios
        
        with app.app_context():
            cadastrar_usuarios()
        
        print("="*50 + "\n")

    app.run(host='0.0.0.0', debug=True, use_reloader=True)
