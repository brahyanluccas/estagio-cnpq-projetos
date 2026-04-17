from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    cpf = db.Column(db.String(11), primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    numero_processo = db.Column(db.String(50), nullable=False)
    primeiro_acesso = db.Column(db.Boolean, default=True)
    respostas = db.relationship('Resposta', backref='usuario', lazy=True)

class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_cpf = db.Column(db.String(11), db.ForeignKey('usuario.cpf'), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Seção 1
    nome_projeto = db.Column(db.String(300))
    sigla = db.Column(db.String(50))
    instituicao_sede = db.Column(db.String(300))

    # Seção 3.1 - Execução Financeira (Totais e Pagos)
    cnpq_custeio_pago = db.Column(db.Float, default=0.0)
    cnpq_custeio_gasto = db.Column(db.Float, default=0.0)
    cnpq_capital_pago = db.Column(db.Float, default=0.0)
    cnpq_capital_gasto = db.Column(db.Float, default=0.0)
    cnpq_bolsas_pais_pago = db.Column(db.Float, default=0.0)
    cnpq_bolsas_pais_gasto = db.Column(db.Float, default=0.0)
    cnpq_bolsas_ext_gasto = db.Column(db.Integer, default=0)

    capes_custeio_pago = db.Column(db.Float, default=0.0)
    capes_custeio_gasto = db.Column(db.Float, default=0.0)
    capes_capital_pago = db.Column(db.Float, default=0.0)
    capes_capital_gasto = db.Column(db.Float, default=0.0)
    capes_bolsas_pais_pago = db.Column(db.Float, default=0.0)
    capes_bolsas_pais_gasto = db.Column(db.Float, default=0.0)
    capes_bolsas_ext_gasto = db.Column(db.Integer, default=0)

    faps_custeio_pago = db.Column(db.Float, default=0.0)
    faps_custeio_gasto = db.Column(db.Float, default=0.0)
    faps_capital_pago = db.Column(db.Float, default=0.0)
    faps_capital_gasto = db.Column(db.Float, default=0.0)
    faps_bolsas_pais_pago = db.Column(db.Float, default=0.0)
    faps_bolsas_pais_gasto = db.Column(db.Float, default=0.0)
    faps_bolsas_ext_gasto = db.Column(db.Integer, default=0)

    # 3.1 Detalhamento de Gastos (Custeio)
    cnpq_custeio_passagens = db.Column(db.Float, default=0.0)
    cnpq_custeio_diarias = db.Column(db.Float, default=0.0)
    cnpq_custeio_terceiros = db.Column(db.Float, default=0.0)

    capes_custeio_passagens = db.Column(db.Float, default=0.0)
    capes_custeio_diarias = db.Column(db.Float, default=0.0)
    capes_custeio_terceiros = db.Column(db.Float, default=0.0)

    faps_custeio_passagens = db.Column(db.Float, default=0.0)
    faps_custeio_diarias = db.Column(db.Float, default=0.0)
    faps_custeio_terceiros = db.Column(db.Float, default=0.0)

    # 3.1 Detalhamento de Gastos (Capital)
    cnpq_capital_equipamentos = db.Column(db.Float, default=0.0)
    cnpq_capital_software = db.Column(db.Float, default=0.0)

    capes_capital_equipamentos = db.Column(db.Float, default=0.0)
    capes_capital_software = db.Column(db.Float, default=0.0)

    faps_capital_equipamentos = db.Column(db.Float, default=0.0)
    faps_capital_software = db.Column(db.Float, default=0.0)

    # Seção 3.2 e 3.3
    houve_alavancagem = db.Column(db.String(3))
    avaliacao_sede = db.Column(db.String(1))
    avaliacao_parceiras = db.Column(db.String(1))
    avaliacao_comentarios = db.Column(db.Text)
    
    # Seção 4
    articulacao_com_incts = db.Column(db.String(3))
    
    # (Estes campos da Seção 4 ficaram "órfãos" no seu HTML novo, mas mantive para não quebrar compatibilidade caso existam inputs escondidos)
    possui_coop_internacional = db.Column(db.String(3))
    houve_visita_estrangeiro = db.Column(db.String(3))
    apoio_bolsa_fonte = db.Column(db.String(100))
    apoio_diarias_fonte = db.Column(db.String(100))
    qtd_visitantes = db.Column(db.Integer)
    organizou_eventos = db.Column(db.String(3))
    
    # Seção 7
    houve_dificuldades = db.Column(db.String(3))
    dificuldades_encontradas = db.Column(db.Text)
    sugestoes_aprimoramento = db.Column(db.Text)
    divulgacao_leigos = db.Column(db.Text)

    # Seção 8 (no HTML virou a 8, embora a variável fosse da 9)
    autorizacoes = db.Column(db.String(200))

    # Relacionamentos com as tabelas filhas (Cascata)
    membros_equipe = db.relationship('MembroEquipe', backref='resposta', cascade="all, delete-orphan")
    organizacoes_parceiras = db.relationship('OrganizacaoParceira', backref='resposta', cascade="all, delete-orphan")
    recursos_alavancados = db.relationship('RecursoAlavancado', backref='resposta', cascade="all, delete-orphan")
    contratos_tecnologia = db.relationship('ContratoTecnologia', backref='resposta', cascade="all, delete-orphan")
    acordos_nda = db.relationship('AcordoNDA', backref='resposta', cascade="all, delete-orphan")
    cooperacoes_internacionais = db.relationship('CooperacaoInternacional', backref='resposta', cascade="all, delete-orphan")
    pesquisadores_visitantes = db.relationship('PesquisadorVisitante', backref='resposta', cascade="all, delete-orphan")
    eventos_organizados = db.relationship('EventoOrganizado', backref='resposta', cascade="all, delete-orphan")
    atividades_divulgacao = db.relationship('AtividadeDivulgacao', backref='resposta', cascade="all, delete-orphan")
    metas_progresso = db.relationship('MetaProgresso', backref='resposta', cascade="all, delete-orphan")
    articulacoes_incts = db.relationship('ArticulacaoINCT', backref='resposta', cascade="all, delete-orphan")
    publicacoes_coautoria = db.relationship('PublicacaoCoautoria', backref='resposta', cascade="all, delete-orphan")
    outras_orientacoes = db.relationship('OutraOrientacao', backref='resposta', cascade="all, delete-orphan")
    empresas_nacionais = db.relationship('EmpresaNacional', backref='resposta', cascade="all, delete-orphan")
    empresas_estrangeiras = db.relationship('EmpresaEstrangeira', backref='resposta', cascade="all, delete-orphan")
    resultados_propostos = db.relationship('ResultadoProposto', backref='resposta', cascade="all, delete-orphan")
    
    # Produções Validadas
    producoes_tecnologicas_validadas = db.relationship('ProducaoTecnologicaValidada', backref='resposta', cascade="all, delete-orphan")
    producoes_bibliograficas_validadas = db.relationship('ProducaoBibliograficaValidada', backref='resposta', cascade="all, delete-orphan")
    producoes_artisticas_validadas = db.relationship('ProducaoArtisticaValidada', backref='resposta', cascade="all, delete-orphan")
    formacoes_rh_validadas = db.relationship('FormacaoRHValidada', backref='resposta', cascade="all, delete-orphan")
    producoes_inovacao_validadas = db.relationship('ProducaoInovacaoValidada', backref='resposta', cascade="all, delete-orphan")
    projetos_empresa_validados = db.relationship('ProjetoEmpresaValidado', backref='resposta', cascade="all, delete-orphan")


class MembroEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(200))
    titulacao = db.Column(db.String(100))
    area_atuacao = db.Column(db.String(200))
    instituicao = db.Column(db.String(200))
    uf = db.Column(db.String(2))
    pais = db.Column(db.String(100))
    cidade = db.Column(db.String(100)) # Adicionado para espelhar o HTML
    categoria = db.Column(db.String(100))
    status_atual = db.Column(db.Boolean)
    status_novo = db.Column(db.Boolean)
    status_excluido = db.Column(db.Boolean)

class OrganizacaoParceira(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(200))
    pesquisador_responsavel = db.Column(db.String(200))
    classificacao = db.Column(db.String(100))
    natureza = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    pais = db.Column(db.String(100))
    setor = db.Column(db.String(100))
    natureza_outro = db.Column(db.String(100))
    classificacao_outro = db.Column(db.String(100))
    tipo_outro = db.Column(db.String(100))

class RecursoAlavancado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    fonte = db.Column(db.String(200))
    tipo_recurso = db.Column(db.String(100))
    valor = db.Column(db.Float)
    tipo_recurso_outro = db.Column(db.String(100))
    forma_aporte_outro = db.Column(db.String(100))
    inicio_aporte = db.Column(db.Date) # HTML usa data
    fim_aporte = db.Column(db.Date)    # HTML usa data
    periodo_aporte = db.Column(db.String(100)) # Legado
    natureza_fonte = db.Column(db.String(100))
    forma_aporte = db.Column(db.String(100))

class ArticulacaoINCT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    inct_nome = db.Column(db.String(300))
    coordenador = db.Column(db.String(200))
    grande_area = db.Column(db.String(100))
    area_conhecimento = db.Column(db.String(100))
    objetivo = db.Column(db.Text)
    vigencia_inicio = db.Column(db.Date)
    vigencia_fim = db.Column(db.Date)
    status = db.Column(db.String(50))
    natureza = db.Column(db.Text)
    natureza_outro = db.Column(db.String(200))
    resultados = db.Column(db.Text)
    resultados_outro = db.Column(db.String(200))
    periodicidade = db.Column(db.String(50))
    formalizacao = db.Column(db.String(50))

class PublicacaoCoautoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    tipo = db.Column(db.String(200))
    titulo = db.Column(db.String(500))
    autores = db.Column(db.String(500))
    ano = db.Column(db.String(4))
    paises = db.Column(db.Text)

class EmpresaNacional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(200))
    cnpj = db.Column(db.String(18))
    cnae = db.Column(db.String(10))
    uf = db.Column(db.String(2))
    municipio = db.Column(db.String(100))
    tipo_interacao = db.Column(db.Text) # Permite listas separadas por virgula
    tipo_interacao_outro = db.Column(db.String(100))
    formalizacao = db.Column(db.String(50))
    objetivo = db.Column(db.Text)
    resultado = db.Column(db.Text)

class EmpresaEstrangeira(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(200))
    pais = db.Column(db.String(100))
    area_atuacao = db.Column(db.String(200))
    vigencia_inicio = db.Column(db.Date)
    vigencia_fim = db.Column(db.Date)
    vigencia = db.Column(db.String(100)) # Legado
    tipo_interacao = db.Column(db.Text) # Permite listas separadas por virgula
    tipo_interacao_outro = db.Column(db.String(100))
    formalizacao = db.Column(db.String(50))
    objetivo = db.Column(db.Text)
    resultado = db.Column(db.Text)

class ContratoTecnologia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    empresa = db.Column(db.String(200))
    cnpj = db.Column(db.String(18))
    cnae = db.Column(db.String(20))
    uf = db.Column(db.String(2))
    municipio = db.Column(db.String(100))
    pais = db.Column(db.String(100)) 
    finalidade = db.Column(db.Text)
    data_assinatura = db.Column(db.Date)
    vigencia_inicio = db.Column(db.Date)
    vigencia_fim = db.Column(db.Date)
    vigencia = db.Column(db.String(100)) # Legado
    contrapartida_financeira = db.Column(db.Float)
    tipo_acordo = db.Column(db.String(100))
    tipo_acordo_outro = db.Column(db.String(100))

class AcordoNDA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    empresa = db.Column(db.String(200))
    finalidade = db.Column(db.Text)
    pais = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    municipio = db.Column(db.String(100))
    localizacao = db.Column(db.String(200)) # Legado
    vigencia_inicio = db.Column(db.Date)
    vigencia_fim = db.Column(db.Date)
    vigencia = db.Column(db.String(100)) # Legado
    vinculado_contrato = db.Column(db.String(3))

class CooperacaoInternacional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    instituicao = db.Column(db.String(300))
    pais = db.Column(db.String(100))
    tipo_interacao = db.Column(db.String(100))
    tipo_interacao_outro = db.Column(db.String(100))
    objetivo = db.Column(db.Text)
    vigencia_inicio = db.Column(db.Date)
    vigencia_fim = db.Column(db.Date)
    vigencia = db.Column(db.String(100)) # Legado
    status = db.Column(db.String(50))
    resultados = db.Column(db.Text)

class PesquisadorVisitante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(200))
    origem = db.Column(db.String(200))
    area_atuacao = db.Column(db.String(200))
    natureza_participacao = db.Column(db.String(100))
    natureza_outro = db.Column(db.String(100))
    duracao_tempo = db.Column(db.Integer)
    duracao_unidade = db.Column(db.String(20))
    objetivo = db.Column(db.String(100))
    objetivo_outro = db.Column(db.String(100))
    
class EventoOrganizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    nome = db.Column(db.String(300))
    tipo = db.Column(db.String(100))
    tipo_outro = db.Column(db.String(100))
    publico_alvo = db.Column(db.Text)
    abrangencia = db.Column(db.String(50))
    num_participantes = db.Column(db.Integer)
    data = db.Column(db.String(7))
    local = db.Column(db.String(150))

class OutraOrientacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    tipo = db.Column(db.String(100))
    tipo_outro = db.Column(db.String(100))
    orientando = db.Column(db.String(200))
    vinculo = db.Column(db.String(100))
    vinculo_outro = db.Column(db.String(100))
    titulo = db.Column(db.String(300))
    inicio = db.Column(db.Date)
    status = db.Column(db.String(50))
    
class AtividadeDivulgacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    instrumentos = db.Column(db.Text)
    instrumento_outro = db.Column(db.String(100))
    publicos_alvo = db.Column(db.Text)
    publico_outro = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    periodicidade = db.Column(db.String(50))
    abrangencia = db.Column(db.String(50))
    alcance_estimado = db.Column(db.Integer)
    municipio = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    foco_vulneraveis = db.Column(db.String(10)) # Sim / Não
    pop_vulneraveis = db.Column(db.Text)
    pop_vulneravel_outro = db.Column(db.String(100))

class ResultadoProposto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    descricao = db.Column(db.Text)
    contexto = db.Column(db.String(255))
    dimensoes = db.Column(db.String(255))
    objetivos_especificos = db.Column(db.Text)
    produtos = db.Column(db.String(255))

class MetaProgresso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta_id_original = db.Column(db.String(100), nullable=False)
    progresso = db.Column(db.Integer, nullable=False) 
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)

# Tabelas de Validação do Lattes (Seção 4.2 e 4.4)
class ProducaoTecnologicaValidada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    titulo = db.Column(db.String(500))
    pesquisador = db.Column(db.String(200))
    ano = db.Column(db.Integer)
    pais_origem = db.Column(db.String(100))
    categoria = db.Column(db.String(200))
    abrangencia = db.Column(db.String(50))  
    pais_colaboracao = db.Column(db.String(100), nullable=True) 

class ProducaoBibliograficaValidada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(500))
    autor = db.Column(db.String(200))
    ano = db.Column(db.Integer)
    categoria = db.Column(db.String(200))
    internacional = db.Column(db.String(10))
    paises_colaboracao = db.Column(db.String(500))
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'))

class ProducaoArtisticaValidada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(500))
    autor = db.Column(db.String(200))
    ano = db.Column(db.Integer)
    categoria = db.Column(db.String(200))
    internacional = db.Column(db.String(10))
    paises_colaboracao = db.Column(db.String(500))
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'))

class ProducaoInovacaoValidada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    titulo = db.Column(db.Text)
    ano = db.Column(db.Integer)
    categoria = db.Column(db.String(150))
    escopo = db.Column(db.String(50))
    paises_colaboracao = db.Column(db.Text)
    tipos_internacionalizacao = db.Column(db.Text)
    tipo_outro_texto = db.Column(db.String(255))

class ProjetoEmpresaValidado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=False)
    titulo = db.Column(db.Text)
    ano = db.Column(db.Integer)
    natureza = db.Column(db.String(150))
    escopo = db.Column(db.String(50))
    paises_colaboracao = db.Column(db.Text)

class FormacaoRHValidada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orientando = db.Column(db.String(200))
    orientador = db.Column(db.String(200))
    tipo = db.Column(db.String(200))
    subtipo = db.Column(db.String(200))
    pais = db.Column(db.String(100))
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'))