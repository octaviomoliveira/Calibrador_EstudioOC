import requests
import zipfile
import io
import os
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def ninja_extrator_zip():
    print("\n" + "=" * 55)
    print(f"[{time.strftime('%X')}] Iniciando Extrator Ninja de ZIPs...")
    print("=" * 55)

    # ====================================================
    # 🎯 COLE O LINK DIRETO DO DOWNLOAD DO ZIP AQUI:
    link_direto_zip = "https://gscs-b2c.lge.com/downloadFile?fileId=ja0ABgm46PJM9uxzINjQ" 
    
    # QUAL É O MODELO DESSE MONITOR? (Deixe apenas letras e números)
    modelo_monitor = "34WP65C"
    # ====================================================

    pasta_perfis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis")
    if not os.path.exists(pasta_perfis):
        os.makedirs(pasta_perfis)

    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
    banco = {}
    if os.path.exists(caminho_db):
        with open(caminho_db, 'r', encoding='utf-8') as f:
            banco = json.load(f)

    id_monitor = f"GSM_{modelo_monitor.upper()}"
    nome_padronizado = f"{id_monitor}.icm"
    caminho_arquivo = os.path.join(pasta_perfis, nome_padronizado)

    print(f"-> Baixando pacote ZIP do modelo {modelo_monitor.upper()} para a memória RAM...")
    
    try:
        # 1. Baixa o ZIP em tempo real
        resposta = requests.get(link_direto_zip, headers=HEADERS, timeout=20)
        resposta.raise_for_status() # Verifica se o download não deu erro
        
        # 2. Abre o ZIP diretamente na memória (io.BytesIO)
        with zipfile.ZipFile(io.BytesIO(resposta.content)) as pacote_zip:
            lista_arquivos = pacote_zip.namelist()
            arquivo_icm_encontrado = None
            
            print("   📦 ZIP aberto! Vasculhando o conteúdo interno...")
            
            # 3. Caça qualquer arquivo que termine em .icm ou .icc lá dentro
            for nome_arquivo in lista_arquivos:
                if nome_arquivo.lower().endswith('.icm') or nome_arquivo.lower().endswith('.icc'):
                    arquivo_icm_encontrado = nome_arquivo
                    break
            
            if arquivo_icm_encontrado:
                print(f"   🎯 Alvo fixado: '{arquivo_icm_encontrado}' encontrado dentro do ZIP!")
                
                # 4. Extrai só o conteúdo do ICM e salva com o nosso nome padrão
                conteudo_icm = pacote_zip.read(arquivo_icm_encontrado)
                with open(caminho_arquivo, 'wb') as f:
                    f.write(conteudo_icm)
                
                # Atualiza o banco de dados do seu app
                banco[id_monitor] = f"https://raw.githubusercontent.com/EstudioOC/perfis/main/{nome_padronizado}"
                
                with open(caminho_db, 'w', encoding='utf-8') as f:
                    json.dump(banco, f, indent=4)
                    
                print(f"   🎉 SUCESSO! Perfil salvo limpo como: {nome_padronizado}")
                print("   🗑️ Arquivos inúteis do ZIP descartados da memória.")
            else:
                print("   ❌ O ZIP foi baixado, mas não tinha nenhum arquivo .icm ou .icc dentro.")

    except zipfile.BadZipFile:
        print("   ❌ Erro: O link não retornou um arquivo ZIP válido.")
    except Exception as e:
        print(f"   ⚠️ Falha na operação: {e}")

if __name__ == "__main__":
    ninja_extrator_zip()