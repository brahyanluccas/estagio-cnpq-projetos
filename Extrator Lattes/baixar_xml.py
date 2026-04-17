from zeep import Client
import zipfile
import io

WSDL_URL = 'http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl'
cliente = Client(WSDL_URL)

id_alvo = '7575602506067143' 

print(f"[*] Baixando o XML do ID {id_alvo}...")

try:
    zip_data = cliente.service.getCurriculoCompactado(id=id_alvo)
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        nome_xml = z.namelist()[0]
        with open(f"Curriculo_Teste_{id_alvo}.xml", "wb") as f_out:
            f_out.write(z.read(nome_xml))
            
    print(f"[+] SUCESSO! Arquivo salvo.")
except Exception as e:
    print(f"[-] ERRO: {e}")