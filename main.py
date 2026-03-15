import sys
import subprocess
import re
import os
import ctypes
import requests  # <-- Nossa nova ferramenta para conectar na internet
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PySide6.QtCore import Qt

# --- 1. O Motor de Leitura de Hardware ---
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

# --- 2. A Interface Gráfica ---
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
        
        self.ids_detectados = obter_ids_dos_monitores()
        
        texto_hardware = "Nenhum monitor detectado"
        botao_ativo = False
        
        if self.ids_detectados:
            texto_hardware = f"Painel Detectado: {', '.join(self.ids_detectados)}"
            botao_ativo = True 

        label_hardware = QLabel(texto_hardware)
        label_hardware.setObjectName("subtitulo")
        label_hardware.setAlignment(Qt.AlignCenter)
        
        # Mudamos o texto do botão para refletir a nova função
        btn_calibrar = QPushButton("Baixar e Aplicar Perfil (Nuvem)")
        btn_calibrar.setEnabled(botao_ativo) 
        btn_calibrar.clicked.connect(self.acao_calibrar)

        layout.setSpacing(15)
        layout.addWidget(label_titulo)
        layout.addWidget(label_hardware)
        layout.addSpacing(10)
        layout.addWidget(btn_calibrar, alignment=Qt.AlignCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)

    # --- 3. A Ação do Botão (Agora com Download e Padronização) ---
    def acao_calibrar(self):
        # SIMULAÇÃO DO NOSSO JSON NA NUVEM
        # No futuro, o código fará um "requests.get" para ler isso do nosso servidor.
        # Por enquanto, colocamos o link real do Notebookcheck diretamente aqui.
        banco_de_dados_nuvem = {
            "BOE0B17": "https://www.notebookcheck.net/uploads/tx_nbc2/NE160QDM_NZ2.icm"
        }

        perfil_aplicado = False

        if getattr(sys, 'frozen', False):
            pasta_base = sys._MEIPASS
        else:
            pasta_base = os.path.dirname(os.path.abspath(__file__))

        # Segurança extra: Garante que a pasta "perfis" existe. Se você apagou ela, o código cria de novo.
        pasta_perfis = os.path.join(pasta_base, "perfis")
        if not os.path.exists(pasta_perfis):
            os.makedirs(pasta_perfis)

        for id_monitor in self.ids_detectados:
            if id_monitor in banco_de_dados_nuvem:
                url_download = banco_de_dados_nuvem[id_monitor]
                
                # A REGRA DE PADRONIZAÇÃO: O nome do arquivo será SEMPRE o ID do monitor
                nome_padronizado = f"{id_monitor}.icm"
                caminho_completo = os.path.join(pasta_perfis, nome_padronizado)

                try:
                    print(f"Conectando à nuvem para baixar perfil do {id_monitor}...")
                    
                    # 1. Faz o download do arquivo
                    resposta = requests.get(url_download, timeout=10)
                    resposta.raise_for_status() # Verifica se o link não está quebrado
                    
                    # 2. Salva o arquivo no HD com o nome perfeito (ex: BOE0B17.icm)
                    with open(caminho_completo, 'wb') as arquivo:
                        arquivo.write(resposta.content)
                    
                    print(f"Download concluído! Salvo como: {nome_padronizado}")
                    
                    # 3. Instala no Windows
                    mscms = ctypes.windll.mscms
                    resultado_instalacao = mscms.InstallColorProfileW(None, caminho_completo)
                    
                    if resultado_instalacao:
                        print("Perfil instalado com sucesso no sistema!")
                        QMessageBox.information(self, "Sucesso", f"Perfil baixado da nuvem e aplicado com sucesso para a tela {id_monitor}!\n\nA calibração está ativa.")
                        perfil_aplicado = True
                    else:
                        QMessageBox.warning(self, "Erro", "O Windows recusou a instalação do perfil.")

                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível baixar o perfil da internet.\nVerifique sua conexão.\n\nDetalhes: {e}")
                    return

        if not perfil_aplicado:
            QMessageBox.warning(self, "Aviso", "Ainda não temos um perfil de laboratório para a sua tela específica no nosso banco de dados.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())