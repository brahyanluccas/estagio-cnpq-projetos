import base64
import os
from PIL import Image
from io import BytesIO

# --- CONFIGURAÇÃO ---
NOME_DA_IMAGEM = "logo cnpq.png" # O nome exato do seu arquivo original
NOVA_LARGURA = 250 # Largura ideal para um logo de topo (em pixels)

print(f"🔄 Processando: {NOME_DA_IMAGEM}...")

if not os.path.exists(NOME_DA_IMAGEM):
    print(f"❌ ERRO: Não encontrei '{NOME_DA_IMAGEM}'.")
else:
    try:
        # 1. Abre a imagem original
        img = Image.open(NOME_DA_IMAGEM)
        
        # 2. Calcula a nova altura mantendo a proporção (para não esticar o logo)
        proporcao = (NOVA_LARGURA / float(img.size[0]))
        nova_altura = int((float(img.size[1]) * float(proporcao)))
        
        print(f"📏 Redimensionando de {img.size[0]}x{img.size[1]} para {NOVA_LARGURA}x{nova_altura}...")

        # 3. Redimensiona com alta qualidade
        img_redimensionada = img.resize((NOVA_LARGURA, nova_altura), Image.Resampling.LANCZOS)
        
        # 4. Salva a imagem otimizada na memória (não cria arquivo no disco)
        buffered = BytesIO()
        # Se for PNG, mantem transparência. Se for JPG, otimiza.
        formato = img.format if img.format else 'PNG'
        img_redimensionada.save(buffered, format=formato, optimize=True, quality=85)
        
        # 5. Converte o resultado otimizado para Base64
        encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Detecta extensão para o cabeçalho
        extensao = NOME_DA_IMAGEM.split('.')[-1].lower()
        if extensao == 'jpg': extensao = 'jpeg'
        
        # Monta o código final
        codigo_final = f"data:image/{extensao};base64,{encoded_string}"
        
        # Salva no arquivo de texto
        with open("codigo_da_imagem_OTIMIZADO.txt", "w") as f:
            f.write(codigo_final)
            
        print(f"\n✅ SUCESSO! Imagem otimizada e código gerado.")
        tamanho_original = os.path.getsize(NOME_DA_IMAGEM) / 1024
        tamanho_novo = len(codigo_final) / 1024
        print(f"📉 O código Base64 foi reduzido de ~{tamanho_original:.1f}KB (estimado) para {tamanho_novo:.1f}KB.")
        print(f"📁 Pegue o novo código no arquivo 'codigo_da_imagem_OTIMIZADO.txt'")

    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        print("Dica: Verifique se instalou o Pillow: pip install Pillow")