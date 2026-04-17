import os
import pdfplumber
import logging

# Silencia avisos
logging.getLogger("pdfminer").setLevel(logging.ERROR)

caminho_base = r"C:\Users\brahyan.souza\Documents\Robô extrator"
pastas_alvo = ["01 Fomento FAPs e CAPES", "00 Fomento CNPq"]

# Termos suspeitos que queremos investigar
suspeitos = [
    "VICE-COORDENADOR LÍDER",
    "VICE-COORDENADOR PESQUISADOR",
    "TÉCNICO PESQUISADOR"
]

print(f"--- INICIANDO INVESTIGAÇÃO ---")

for nome_pasta in pastas_alvo:
    pasta_completa = os.path.join(caminho_base, nome_pasta)
    if os.path.exists(pasta_completa):
        arquivos = [f for f in os.listdir(pasta_completa) if f.lower().endswith('.pdf')]
        
        for arq in arquivos:
            caminho_pdf = os.path.join(pasta_completa, arq)
            try:
                with pdfplumber.open(caminho_pdf) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        if not texto: continue
                        
                        # Normaliza para maiúsculo para facilitar a busca
                        texto_upper = texto.upper()
                        
                        # Verifica se algum dos suspeitos aparece "perto" (na mesma página)
                        # Vamos procurar pelas palavras chaves separadas
                        if "VICE-COORDENADOR" in texto_upper and "LÍDER" in texto_upper:
                             # Se achou, vamos mostrar as linhas da tabela dessa página
                             linhas = texto.split('\n')
                             for num, linha in enumerate(linhas):
                                 linha_limpa = linha.upper().strip()
                                 if "VICE-COORDENADOR" in linha_limpa:
                                     print(f"\n📄 ARQUIVO: {arq} (Página {i+1})")
                                     print(f"   Contexto encontrado:")
                                     print(f"   Linha {num}: '{linha}'")
                                     # Mostra a linha de baixo para ver se o robô colou errado
                                     if num + 1 < len(linhas):
                                         print(f"   Linha {num+1}: '{linhas[num+1]}'")
                                     print("-" * 30)

                        if "TÉCNICO" in texto_upper and "PESQUISADOR DA EQUIPE" in texto_upper:
                             linhas = texto.split('\n')
                             for num, linha in enumerate(linhas):
                                 linha_limpa = linha.upper().strip()
                                 # Procura a linha exata do Técnico para ver o que tem embaixo
                                 if linha_limpa.startswith("TÉCNICO") or linha_limpa.startswith("TECNICO"):
                                     # Evita pegar "Apoio Técnico"
                                     if "APOIO" not in linha_limpa:
                                        print(f"\n📄 ARQUIVO: {arq} (Página {i+1})")
                                        print(f"   Contexto encontrado:")
                                        print(f"   Linha {num}: '{linha}'")
                                        if num + 1 < len(linhas):
                                            print(f"   Linha {num+1}: '{linhas[num+1]}'")
                                        print("-" * 30)

            except Exception:
                pass

print("\nFim da investigação.")