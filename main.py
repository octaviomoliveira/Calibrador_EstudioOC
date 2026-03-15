import sys
import subprocess
import re
import os
import ctypes
import requests  # <-- Essencial para a conexão com a nuvem
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PySide6.QtCore import Qt

# ==========================================================
# --- CONFIGURAÇÕES DA SUA NUVEM (GLOBAL) ---
# ==========================================================
# MUITO IMPORTANTE: Substitua pelos seus dados reais do GitHub

# 1. Defina o seu nome de usuário do GitHub como string
USUARIO_GITHUB = "octaviomoliveira"

# 2. Defina o nome do seu repositório onde está o 'database.json'
# Substitua "NOME_DO_REPOSITORIO" pelo nome real (ex: "Calibrador_EstudioOC")
REPOSITORIO_PERFIS = "Calibrador_EstudioOC"

# 3. Monte a URL usando os NOMES DAS VARIÁVEIS dentro das chaves {}
URL_DATABASE_JSON = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPOSITORIO_PERFIS}/main/database.json"

# --- 1. O Motor de Leitura de Hardware (Detecção do ID) ---
def obter_ids_dos_monitores():
    comando = 'powershell "Get-WmiObject Win32_PnPEntity | Where-Object {$_.PNPClass -eq \'Monitor\'} | Select-Object -ExpandProperty HardwareID"'
    resultado = subprocess.run(comando, capture_output=True, text=True, shell=True)
    
    if resultado.returncode == 0:
        linhas = resultado.stdout.strip().split('\n')
        ids_limpos = []
        for linha in linhas:
            busca = re.search(r'MONITOR\\([A-Z0-9]+)', linha)
            if busca:
                id_painel = busca.group(1)
                if id_painel not in ids_limpos:
                    ids_limpos.append(id_painel)
        return ids_limpos
    return []

# --- 2. A Interface Gráfica e Lógica Principal ---
class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Estúdio OC! - Calibrador de Cores")
        self.resize(450, 300)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e24; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel#titulo { font-size: 22px; font-weight: bold; }
            QLabel#subtitulo { font-size: 14px; color: #9ba1a6; }
            QPushButton {
                background-color: #0066cc; color: white; border: none;
                border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0052a3; }
            QPushButton:pressed { background-color: #004080; }
            QPushButton:disabled { background-color: #333333; color: #777777; }
        """)

        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label_titulo = QLabel("Calibração de Monitor")
        label_titulo.setObjectName("titulo")
        label_titulo.setAlignment(Qt.AlignCenter)
        
        # Chama a função de detecção
        self.ids_detectados = obter_ids_dos_monitores()
        
        texto_hardware = "Nenhum monitor detectado"
        botao_ativo = False
        
        if self.ids_detectados:
            texto_hardware = f"Painel Detectado: {', '.join(self.ids_detectados)}"
            botao_ativo = True 

        label_hardware = QLabel(texto_hardware)
        label_hardware.setObjectName("subtitulo")
        label_hardware.setAlignment(Qt.AlignCenter)
        
        btn_calibrar = QPushButton("Aplicar Calibração na Nuvem")
        btn_calibrar.setEnabled(botao_ativo) 
        btn_calibrar.clicked.connect(self.acao_calibrar)

        layout.setSpacing(15)
        layout.addWidget(label_titulo)
        layout.addWidget(label_hardware)
        layout.addSpacing(10)
        layout.addWidget(btn_calibrar, alignment=Qt.AlignCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)

    # --- 3. A Ação do Botão (A lógica de nuvem que você enviou) ---
    def acao_calibrar(self):
        perfil_aplicado = False

        # 1. Definir os caminhos de pasta
        if getattr(sys, 'frozen', False):
            pasta_base = sys._MEIPASS
        else:
            pasta_base = os.path.dirname(os.path.abspath(__file__))

        pasta_perfis = os.path.join(pasta_base, "perfis")
        if not os.path.exists(pasta_perfis):
            os.makedirs(pasta_perfis)

        try:
            # 2. CONECTAR NA NUVEM PARA BAIXAR O BANCO DE DADOS ATUALIZADO
            print("Conectando ao GitHub para buscar o banco de dados atualizado...")
            
            # Faz o download do arquivo database.json
            resposta_json = requests.get(URL_DATABASE_JSON, timeout=10)
            resposta_json.raise_for_status() # Verifica se o link não está quebrado

            # Converte o conteúdo baixado em um dicionário Python
            banco_de_dados_nuvem = resposta_json.json()
            perfis_disponiveis = banco_de_dados_nuvem.get("perfis", {})

            print("Banco de dados baixado e processado com sucesso!")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível conectar ao servidor para buscar as calibrações.\nVerifique sua conexão.\n\nDetalhes: {e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Ocorreu um erro ao processar o banco de dados da nuvem:\n{e}")
            return

        # 3. Lógica de Download e Aplicação do arquivo .icm
        for id_monitor in self.ids_detectados:
            if id_monitor in perfis_disponiveis:
                url_download = perfis_disponiveis[id_monitor]
                
                nome_padronizado = f"{id_monitor}.icm"
                caminho_completo = os.path.join(pasta_perfis, nome_padronizado)

                try:
                    print(f"Baixando perfil de calibração para o painel {id_monitor}...")
                    
                    # 3.1. Faz o download do arquivo .icm
                    resposta_icm = requests.get(url_download, timeout=15)
                    resposta_icm.raise_for_status()
                    
                    # 3.2. Salva o arquivo no HD
                    with open(caminho_completo, 'wb') as arquivo:
                        arquivo.write(resposta_icm.content)
                    
                    print(f"Download concluído! Salvo como: {nome_padronizado}")
                    
                    # 3.3. Instala no Windows
                    mscms = ctypes.windll.mscms
                    resultado_instalacao = mscms.InstallColorProfileW(None, caminho_completo)
                    
                    if resultado_instalacao:
                        print("Perfil instalado com sucesso no sistema!")
                        QMessageBox.information(self, "Sucesso", f"Calibração para o painel {id_monitor} foi baixada e aplicada com sucesso!\n\nA calibração está ativa.")
                        perfil_aplicado = True
                    else:
                        QMessageBox.warning(self, "Erro", "O Windows recusou a instalação do perfil.")

                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Erro de Download", f"Não foi possível baixar a calibração para o painel {id_monitor}.\n\nDetalhes: {e}")

        if not perfil_aplicado:
            QMessageBox.warning(self, "Aviso", "Ainda não temos um perfil de laboratório para a sua tela específica no nosso banco de dados da nuvem.")

# ==========================================================
# --- 4. PONTO DE ENTRADA (Essencial para o app abrir) ---
# ==========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())