import requests
import os
import json
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def carregar_banco():
    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
    if os.path.exists(caminho_db):
        with open(caminho_db, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_banco(banco):
    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
    with open(caminho_db, 'w', encoding='utf-8') as f:
        json.dump(banco, f, indent=4)

# ==========================================
# 1. O CAÇADOR VIP (TFTCentral - Desativado Temporariamente)
# ==========================================
def robo_forca_bruta_tftcentral():
    print("\n" + "=" * 55)
    print(f"[{time.strftime('%X')}] Iniciando Caçador VIP (TFTCentral)...")
    print("=" * 55)

    modelos_tft = ["34uc79g", "34gk950f", "27gl850", "32gk850g"]
    sucessos = 0
    banco = carregar_banco()
    pasta_perfis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis")
    if not os.path.exists(pasta_perfis):
        os.makedirs(pasta_perfis)

    for modelo in modelos_tft:
        url_arquivo = f"https://tftcentral.co.uk/icc_profiles/lg_{modelo}.icc"
        id_monitor = f"GSM_{modelo.upper()}"
        nome_padronizado = f"{id_monitor}.icm"
        caminho_arquivo = os.path.join(pasta_perfis, nome_padronizado)
        
        print(f"-> Testando (TFT): lg_{modelo}.icc")
        try:
            resposta = requests.get(url_arquivo, headers=HEADERS, timeout=(3.0, 5.0))
            if resposta.status_code == 200:
                with open(caminho_arquivo, 'wb') as f:
                    f.write(resposta.content)
                banco[id_monitor] = f"https://raw.githubusercontent.com/EstudioOC/perfis/main/{nome_padronizado}"
                sucessos += 1
                print(f"   ✅ Capturado e salvo como {nome_padronizado}!")
        except requests.exceptions.Timeout:
            print(f"   🐌 Ignorando timeout do servidor...")
        except Exception:
            pass
        time.sleep(1.5)

    salvar_banco(banco)
    print(f"-> TFTCentral finalizado. {sucessos} perfis verificados/baixados.")

# ==========================================
# 2. O CAÇADOR OFICIAL (Microsoft Update Catalog)
# ==========================================
def cacador_microsoft_update():
    print("\n" + "=" * 55)
    print(f"[{time.strftime('%X')}] Iniciando Invasão ao Microsoft Update Catalog...")
    print("=" * 55)

    # O seu Ultrawide está na mira!
    modelos_teste = ["34wp65c", "27gl850", "29um69g"]
    pasta_perfis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis")
    if not os.path.exists(pasta_perfis):
        os.makedirs(pasta_perfis)

    for modelo in modelos_teste:
        print(f"\n-> Pesquisando driver oficial para: LG {modelo.upper()}")
        url_pesquisa = f"https://www.catalog.update.microsoft.com/Search.aspx?q=LG%20{modelo}"
        
        try:
            resposta = requests.get(url_pesquisa, headers=HEADERS, timeout=15)
            ids_encontrados = re.findall(r"DownloadWindow\('([a-fA-F0-9\-]{36})'\)", resposta.text)
            
            if not ids_encontrados:
                print("   ❌ A Microsoft não tem o driver listado com esse exato nome.")
                continue
            
            update_id = ids_encontrados[0] 
            print(f"   🔓 ID de Download capturado! ({update_id.split('-')[0]}...)")
            
            url_popup = f"https://www.catalog.update.microsoft.com/DownloadDialog.aspx?updateIDs={update_id}"
            resp_popup = requests.get(url_popup, headers=HEADERS, timeout=15)
            links_cab = re.findall(r"href=['\"](https?://[^'\"]+\.cab)['\"]", resp_popup.text)
            
            if not links_cab:
                print("   ❌ Arquivo .cab não encontrado no popup.")
                continue
                
            link_download = links_cab[0]
            print("   ✅ Pacote do Windows encontrado. Baixando...")
            
            resp_cab = requests.get(link_download, headers=HEADERS, timeout=20)
            caminho_cab = os.path.join(pasta_perfis, f"temp_pacote_{modelo}.cab")
            
            with open(caminho_cab, 'wb') as f:
                f.write(resp_cab.content)
                
            print("   📦 Descompactando o cofre da Microsoft...")
            
            # COMANDO MÁGICO DO WINDOWS PARA EXTRAIR O .ICM
            comando_extracao = f'expand "{caminho_cab}" -F:*.icm "{pasta_perfis}" > nul'
            resultado_os = os.system(comando_extracao)
            
            if os.path.exists(caminho_cab):
                os.remove(caminho_cab)
                
            if resultado_os == 0:
                print(f"   🎉 SUCESSO! O perfil original de fábrica do {modelo.upper()} foi extraído para a sua pasta.")
            else:
                print(f"   ⚠️ O pacote foi baixado, mas não continha arquivos .icm soltos dentro dele.")
            
        except Exception as e:
            print(f"   ⚠️ Falha na operação: {e}")
            
        time.sleep(2)

# ==========================================
# PAINEL DE CONTROLE
# ==========================================
if __name__ == "__main__":
    # Desligamos o TFTCentral colocando o jogo da velha (comentário)
    # robo_forca_bruta_tftcentral()
    
    # Apenas o da Microsoft vai rodar!
    cacador_microsoft_update()
    
    print("\n🎉 ESQUADRÃO DE VARREDURA FINALIZOU TODAS AS MISSÕES!")