import pandas as pd
from werkzeug.security import generate_password_hash
import re
import os
import unicodedata

# Suas constantes e funções auxiliares permanecem aqui
DADOS_PATH = 'dados/'

def remover_acentos(txt):
    if not isinstance(txt, str):
        return str(txt)
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('utf-8')

def find_file_in_dir(directory, file_type_keyword):
    try:
        for filename in os.listdir(directory):
            if file_type_keyword in remover_acentos(filename.lower()):
                return os.path.join(directory, filename)
    except FileNotFoundError:
        return None
    return None

def find_header_row(excel_path, required_cols):
    try:
        df_test = pd.read_excel(excel_path, header=None, nrows=20)
        for index, row in df_test.iterrows():
            row_values = [str(c).strip() for c in row.values]
            if all(col in row_values for col in required_cols):
                return index
    except Exception:
        return None
    return None

# --- FUNÇÃO PRINCIPAL ATUALIZADA ---
def cadastrar_usuarios():
    # Os imports agora são feitos AQUI DENTRO para evitar o erro circular
    from app import app, db
    from moldes import Usuario

    print("[BOOTSTRAP] Iniciando verificação e cadastro de usuários...")
    
    with app.app_context():
        try:
            pastas_de_projeto = [d for d in os.listdir(DADOS_PATH) if os.path.isdir(os.path.join(DADOS_PATH, d))]
        except FileNotFoundError:
            print(f"[ERRO] A pasta de dados raiz '{DADOS_PATH}' não foi encontrada.")
            return

        if not pastas_de_projeto:
            print("[AVISO] Nenhuma pasta de projeto encontrada em 'dados/'.")
            return

        for numero_processo_pasta in pastas_de_projeto:
            if not numero_processo_pasta.isdigit():
                continue
            
            caminho_pasta_projeto = os.path.join(DADOS_PATH, numero_processo_pasta)
            print(f"\n--- Verificando Projeto: {numero_processo_pasta} ---")

            try:
                caminho_membros = find_file_in_dir(caminho_pasta_projeto, 'membros')
                if not caminho_membros:
                    print("[ERRO] Arquivo de 'membros' não encontrado nesta pasta."); continue

                colunas_necessarias = ['MEMBRO PROJETO', 'CPF', 'PAPEL DO PESQUISADOR NA EQUIPE']
                header_row_index = find_header_row(caminho_membros, colunas_necessarias)

                if header_row_index is None:
                    print(f"[ERRO] Cabeçalho com colunas {colunas_necessarias} não encontrado."); continue
                
                df_membros = pd.read_excel(caminho_membros, header=header_row_index)
                df_membros.columns = [str(c).strip() for c in df_membros.columns]

                coordenador_row = df_membros[df_membros['PAPEL DO PESQUISADOR NA EQUIPE'].str.strip() == 'Coordenador']
                
                if coordenador_row.empty:
                    print(f"[ERRO] Nenhum 'Coordenador' encontrado no arquivo."); continue

                nome_coordenador = coordenador_row.iloc[0]['MEMBRO PROJETO']
                cpf_raw = coordenador_row.iloc[0]['CPF']
                cpf = re.sub(r'\D', '', str(cpf_raw))

                usuario_existente = Usuario.query.filter_by(cpf=cpf).first()

                if not usuario_existente:
                    senha_provisoria = str(cpf)[:4] + str(cpf)[-2:]
                    senha_hash = generate_password_hash(senha_provisoria)
                    
                    novo_usuario = Usuario(
                        cpf=cpf,
                        nome=nome_coordenador,
                        senha_hash=senha_hash,
                        numero_processo=numero_processo_pasta,
                        primeiro_acesso=True
                    )
                    
                    db.session.add(novo_usuario)
                    
                    print(f"✅ [NOVO USUÁRIO CRIADO] {nome_coordenador} | CPF: {cpf}")
                    print(f"   └── Senha Provisória: {senha_provisoria}")
                else:
                    print(f"⏭️  [USUÁRIO EXISTENTE] {nome_coordenador} ({cpf}) | Nenhuma alteração feita.")

            except Exception as e:
                print(f"[ERRO CRÍTICO] Falha ao processar a pasta do projeto '{numero_processo_pasta}': {e}")

        try:
            db.session.commit()
            print("\n[BOOTSTRAP] Cadastro de usuários concluído. Alterações salvas no banco.")
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO CRÍTICO] Falha ao salvar alterações no banco de dados: {e}")

if __name__ == "__main__":
    cadastrar_usuarios()