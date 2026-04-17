from zeep import Client

# A URL oficial do Web Service
WSDL_URL = 'http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl'

def testar_extrator(id_lattes):
    print(f"[*] Iniciando conexão com o Web Service do CNPq...")
    
    try:
        # Cria o cliente SOAP
        client = Client(WSDL_URL)
        
        print(f"[*] Solicitando o currículo ID: {id_lattes}")
        
        # Faz o pedido. O zeep já converte automaticamente o retorno para os bytes do ZIP!
        zip_data = client.service.getCurriculoCompactado(id=id_lattes)
        
        if not zip_data:
            print("[-] Erro: O CNPq não retornou dados.")
            return

        nome_arquivo = f"curriculo_teste_{id_lattes}.zip"
        
        # Salva o arquivo diretamente (wb = write binary)
        with open(nome_arquivo, 'wb') as arquivo_zip:
            arquivo_zip.write(zip_data)
            
        print(f"[+] Sucesso! Conexão estabelecida e currículo salvo como '{nome_arquivo}'.")

    except Exception as erro:
        print(f"[-] Ocorreu uma falha: {erro}")

# ==========================================
# ÁREA DE EXECUÇÃO
# ==========================================
ID_TESTE = '4053837419956792'

if __name__ == "__main__":
    testar_extrator(ID_TESTE)