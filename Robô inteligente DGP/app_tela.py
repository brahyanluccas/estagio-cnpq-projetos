import customtkinter as ctk
import threading
import os
import sys
from PIL import Image

import robo_cnpq

# =======================================================================
# --- FUNÇÃO MÁGICA PARA A LOGO FUNCIONAR NO .EXE ---
# =======================================================================
def obter_caminho_imagem(nome_arquivo):
    """Garante que a imagem seja encontrada rodando no VS Code ou no .exe"""
    try:
        # Quando o PyInstaller roda, ele cria essa pasta temporária _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se estiver rodando normal no VS Code
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, nome_arquivo)

# =======================================================================
# --- FUNÇÕES DE MODAIS (Telas sobrepostas) ---
# =======================================================================

def abrir_modal_instrucoes():
    modal = ctk.CTkToplevel(janela)
    modal.geometry("500x350")
    modal.title("Instruções de Uso")
    modal.attributes("-topmost", True)
    
    titulo_modal = ctk.CTkLabel(modal, text="Como usar o Extrator DGP", font=("Arial", 20, "bold"), text_color="#00509E")
    titulo_modal.pack(pady=(20, 10))
    
    texto_instrucoes = (
        "1. Parâmetro Único:\n"
        "Digite apenas uma palavra (ex: Sustentabilidade) e clique em Executar.\n\n"
        "2. Extração em Lote (Múltiplos Parâmetros):\n"
        "Digite várias palavras separadas obrigatoriamente por vírgula.\n"
        "Exemplo: Água, Solo, Clima, Energia Renovável\n\n"
        "3. Onde encontro os arquivos?\n"
        "O sistema criará automaticamente uma pasta chamada 'PDFs DGP' no\n"
        "mesmo local onde este programa está salvo. Dentro dela, haverá\n"
        "subpastas organizadas para cada termo pesquisado.\n\n"
        "⚠️ Atenção: Não feche esta janela ou o navegador durante a extração."
    )
    
    label_texto = ctk.CTkLabel(modal, text=texto_instrucoes, font=("Arial", 14), justify="left")
    label_texto.pack(pady=10, padx=20)
    
    botao_fechar = ctk.CTkButton(modal, text="Entendi", command=modal.destroy, width=120, fg_color="#00509E")
    botao_fechar.pack(pady=20)

def abrir_modal_conclusao(qtd_baixados):
    modal_fim = ctk.CTkToplevel(janela)
    modal_fim.geometry("480x250") 
    modal_fim.title("Status da Extração")
    modal_fim.attributes("-topmost", True)
    
    if qtd_baixados == 0:
        texto = "⚠️ Busca concluída sem resultados.\n\nNão encontramos nenhum documento no sistema\npara os parâmetros informados.\n\nDeseja realizar uma nova pesquisa?"
    else:
        texto = f"✅ Extração finalizada com sucesso!\n\nForam baixados {qtd_baixados} documento(s) no total.\n\nDeseja realizar uma nova extração?"
        
    lbl = ctk.CTkLabel(modal_fim, text=texto, font=("Arial", 16))
    lbl.pack(pady=(30, 20))
    
    frame_botoes = ctk.CTkFrame(modal_fim, fg_color="transparent")
    frame_botoes.pack(pady=10)
    
    def acao_sim():
        entrada_pesquisa.delete(0, 'end')
        botao_buscar.configure(state="normal")
        label_status.configure(text="")
        modal_fim.destroy()
        
    def acao_nao():
        janela.quit()
        
    btn_sim = ctk.CTkButton(frame_botoes, text="Sim, nova busca", width=140, fg_color="#27AE60", hover_color="#1E8449", font=("Arial", 14, "bold"), command=acao_sim)
    btn_sim.pack(side="left", padx=15)
    
    btn_nao = ctk.CTkButton(frame_botoes, text="Não, sair", width=140, fg_color="#C0392B", hover_color="#922B21", font=("Arial", 14, "bold"), command=acao_nao)
    btn_nao.pack(side="right", padx=15)

# =======================================================================
# --- FUNÇÕES PRINCIPAIS (Robô e Botões) ---
# =======================================================================

def iniciar_download(texto_bruto):
    sucesso = False
    qtd_baixados = 0
    
    try:
        lista_palavras = [palavra.strip() for palavra in texto_bruto.split(",") if palavra.strip()]
        qtd_termos = len(lista_palavras)
        
        label_status.configure(text=f"⏳ Processando {qtd_termos} parâmetro(s). Por favor, aguarde...", text_color="#E67E22") 
        
        qtd_baixados = robo_cnpq.executar_robo_download(lista_palavras)
        sucesso = True
        
    except Exception as e:
        label_status.configure(text=f"❌ Falha na execução do sistema: {e}", text_color="#C0392B") 
        janela.after(0, lambda: botao_buscar.configure(state="normal"))
        
    finally:
        if sucesso:
            if qtd_baixados == 0:
                label_status.configure(text="⚠️ Busca concluída. Nenhum documento encontrado.", text_color="#E67E22") 
            else:
                label_status.configure(text="✅ Operação concluída. Verifique a pasta 'PDFs DGP'.", text_color="#27AE60") 
                
            janela.after(0, abrir_modal_conclusao, qtd_baixados)

def botao_clicado():
    texto_digitado = entrada_pesquisa.get()
    
    if texto_digitado.strip() == "":
        label_status.configure(text="⚠️ Necessário informar ao menos um parâmetro de busca válido.", text_color="#E67E22")
        return

    botao_buscar.configure(state="disabled")
    
    thread_processo = threading.Thread(target=iniciar_download, args=(texto_digitado,))
    thread_processo.start()

# =======================================================================
# --- CRIANDO O VISUAL DA TELA (TEMA CNPq PROFISSIONAL) ---
# =======================================================================

ctk.set_appearance_mode("light") 

janela = ctk.CTk()
janela.geometry("650x450") 
janela.title("Extrator DGP - CNPq")
janela.iconbitmap(obter_caminho_imagem("icone_projeto.ico"))

botao_info = ctk.CTkButton(
    janela, text=" i ", command=abrir_modal_instrucoes, 
    width=30, height=30, corner_radius=15, font=("Arial", 16, "bold"), 
    fg_color="#00509E", hover_color="#003d7a", text_color="white"
)
botao_info.place(relx=0.95, rely=0.05, anchor="ne") 

# AQUI ESTÁ O TRUQUE: Usando a nova função para carregar a logo!
caminho_logo = obter_caminho_imagem("logo_cnpq.png")

if os.path.exists(caminho_logo):
    imagem_logo = ctk.CTkImage(light_image=Image.open(caminho_logo), size=(180, 60))
    label_logo = ctk.CTkLabel(janela, image=imagem_logo, text="")
    label_logo.pack(pady=(30, 0))
else:
    label_sem_logo = ctk.CTkLabel(janela, text="[Espaço reservado para Identidade Visual - CNPq]", font=("Arial", 12, "italic"), text_color="gray")
    label_sem_logo.pack(pady=(30, 0))

titulo = ctk.CTkLabel(janela, text="Sistema de Busca Automatizada", font=("Arial", 26, "bold"), text_color="#00509E")
titulo.pack(pady=(10, 5))

subtitulo = ctk.CTkLabel(
    janela, 
    text="Insira os termos separados por vírgula para extração em lote,\nou pesquise apenas um parâmetro por vez.", 
    font=("Arial", 14), text_color="#333333"
)
subtitulo.pack(pady=(0, 25))

entrada_pesquisa = ctk.CTkEntry(
    janela, placeholder_text="Ex: Energia Renovável, Mudanças Climáticas, Biodiversidade...", 
    width=450, height=45, font=("Arial", 15)
)
entrada_pesquisa.pack(pady=10)

botao_buscar = ctk.CTkButton(
    janela, text="Executar Extração", command=botao_clicado, 
    width=250, height=45, font=("Arial", 15, "bold"), 
    fg_color="#00509E", hover_color="#003d7a", text_color="white"
)
botao_buscar.pack(pady=20)

label_status = ctk.CTkLabel(janela, text="", font=("Arial", 14, "bold"))
label_status.pack(pady=10)

janela.after(500, abrir_modal_instrucoes)

janela.mainloop()