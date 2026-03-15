import requests
from bs4 import BeautifulSoup
import re
import os
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def extrair_e_baixar_perfil(url_review):
    print(f"[{time.strftime('%X')}] Iniciando varredura na URL...")
    
    try:
        resposta = requests.get(url_review, headers=HEADERS, timeout=10)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, 'html.parser')

        # O REGEX DEFINITIVO E ONIPOTENTE (Agora enxerga os AMOLEDs da SDC/SEC)
        id_painel = None
        texto_da_pagina = soup.get_text()
        busca_id = re.search(r'(BOE|LGD|AUO|SHP|CMN|SDC|SEC|IVO|CSO|JDI|HCP|APP|LEN)[0-9A-Z]{3,6}', texto_da_pagina)
        
        if busca_id:
            id_painel = busca_id.group(0)
            print(f"-> ID do Monitor encontrado: {id_painel}")
        else:
            print("-> Nenhum ID suportado nesta página.")
            return False

        link_download = None
        for tag_a in soup.find_all('a', href=True):
            if tag_a['href'].endswith(('.icc', '.icm')):
                link_download = "https://www.notebookcheck.net/" + tag_a['href'].lstrip('/')
                print(f"-> Arquivo de calibração encontrado: {link_download}")
                break

        if not link_download:
            print("-> Nenhum arquivo encontrado.")
            return False

        pasta_perfis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis")
        if not os.path.exists(pasta_perfis):
            os.makedirs(pasta_perfis)

        nome_padronizado = f"{id_painel}.icm"
        caminho_arquivo = os.path.join(pasta_perfis, nome_padronizado)

        print(f"-> Baixando e salvando: {nome_padronizado}...")
        resposta_arquivo = requests.get(link_download, headers=HEADERS, timeout=10)
        resposta_arquivo.raise_for_status()

        with open(caminho_arquivo, 'wb') as f:
            f.write(resposta_arquivo.content)

        link_nosso_servidor = f"https://raw.githubusercontent.com/EstudioOC/perfis/main/{nome_padronizado}"
        atualizar_banco_de_dados(id_painel, link_nosso_servidor)
        
        print("✅ Processo concluído!\n")
        return True

    except Exception as e:
        print(f"❌ Erro na página: {e}")
        return False

def atualizar_banco_de_dados(id_painel, link_download):
    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
    if os.path.exists(caminho_db):
        with open(caminho_db, 'r', encoding='utf-8') as f:
            banco = json.load(f)
    else:
        banco = {}

    banco[id_painel] = link_download

    with open(caminho_db, 'w', encoding='utf-8') as f:
        json.dump(banco, f, indent=4)

# =========================================================
# --- LISTA SAMSUNG (O Retorno com o Radar Destravado) ---
# =========================================================

lista_de_reviews = [
    # ==========================================
    # 🔵 DELL (G15, Alienware e XPS)
    # ==========================================
    "https://www.notebookcheck.net/Dell-G15-5530-review-RTX-4050-gaming-laptop-in-Dark-Shadow-Gray.796557.0.html", # G15 5530
    "https://www.notebookcheck.net/Dell-G15-5510-laptop-review-Budget-gaming-laptop-with-the-RTX-3050.629381.0.html", # G15 5510 Clássico
    "https://www.notebookcheck.net/Alienware-m16-R1-AMD.751623.0.html", # Alienware m16
    "https://www.notebookcheck.net/Dell-XPS-15-9530-RTX-4070-laptop-review-Both-impressive-and-underwhelming.709129.0.html", # XPS 15 (OLED)

    # ==========================================
    # 🟢 AVELL (Disfarçados como XMG / Schenker)
    # ==========================================
    "https://www.notebookcheck.net/XMG-Neo-16-2025-Preview-The-fastest-gaming-notebook-now-with-AMD-RTX-5000-and-300-Hz-Mini-LED.991135.0.html", # Equivalente ao Avell ION pesado (Mini-LED)
    "https://www.notebookcheck.net/The-fastest-gaming-laptop-is-now-even-better-thanks-to-300-Hz-mini-LED-XMG-Neo-16-E25-RTX-5090-laptop-review.1016705.0.html", # Avell ION 2024/2025
    "https://www.notebookcheck.net/XMG-Neo-16-Early-24-review-Full-RTX-4090-power-in-a-compact-gaming-laptop.851243.0.html", # Avell de Alta Performance
    "https://www.notebookcheck.net/Schenker-Vision-14-M23-review-The-lightweight-ultrabook-with-an-RTX-3050.751842.0.html", # Equivalente ao Avell B.On

    # ==========================================
    # ⚪ APPLE (MacBooks com telas Mini-LED e Retina)
    # ==========================================
    "https://www.notebookcheck.net/Apple-MacBook-Pro-16-2023-M3-Max-Review-M3-Max-challenges-HX-CPUs-from-AMD-Intel.766414.0.html", # MacBook Pro 16 M3 Max
    "https://www.notebookcheck.net/Apple-MacBook-Pro-16-2023-M3-Pro-review-Efficiency-before-performance.772025.0.html", # MacBook Pro 16 M3 Pro
    "https://www.notebookcheck.net/Apple-MacBook-Pro-14-2021-M1-Pro-Review-How-much-does-the-M1-Pro-cap-performance.576658.0.html", # MacBook Pro 14 M1
    "https://www.notebookcheck.net/Apple-MacBook-Pro-16-2023-M2-Max-Review-More-efficiency-and-even-more-performance.696322.0.html" # MacBook Pro 16 M2
]

print("\n" + "=" * 55)
print(f"Iniciando REPESCAGEM DEFINITIVA SAMSUNG em {len(lista_de_reviews)} links...")
print("=" * 55 + "\n")

for url in lista_de_reviews:
    extrair_e_baixar_perfil(url)
    time.sleep(3)

print("🎉 Repescagem finalizada! Verifique a pasta 'perfis' e o 'database.json'.")