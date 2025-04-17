import sys
import os
import shutil
import filecmp
import hashlib
from collections import defaultdict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QWidget, QLabel, QFileDialog, QTextEdit,
                           QMessageBox, QProgressBar, QDialog, QRadioButton, 
                           QButtonGroup, QTabWidget, QListWidget, QFrame,
                           QSplitter, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from mesclar_hds import mesclar_hds

# Definição de estilos
STYLE = """
QMainWindow, QDialog {
    background-color: #2b2b2b;
}

QTabWidget::pane {
    border: 1px solid #3d3d3d;
    background-color: #2b2b2b;
    border-radius: 5px;
}

QTabBar::tab {
    background-color: #3d3d3d;
    color: #ffffff;
    padding: 8px 20px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #0d47a1;
}

QPushButton {
    background-color: #0d47a1;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0a3d87;
}

QPushButton:disabled {
    background-color: #666666;
}

QTextEdit {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 5px;
    selection-background-color: #0d47a1;
}

QProgressBar {
    border: 2px solid #3d3d3d;
    border-radius: 5px;
    text-align: center;
    height: 25px;
    background-color: #1e1e1e;
    color: white;
}

QProgressBar::chunk {
    background-color: #0d47a1;
    border-radius: 3px;
}

QLabel {
    color: #ffffff;
    font-size: 12px;
}

QRadioButton {
    color: #ffffff;
    spacing: 8px;
    padding: 2px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    background-color: #1e1e1e;
    border: 2px solid #3d3d3d;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    background-color: #0d47a1;
    border: 2px solid #3d3d3d;
    border-radius: 9px;
}

QListWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: #0d47a1;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QScrollBar:vertical {
    border: none;
    background-color: #1e1e1e;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #3d3d3d;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4d4d4d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#card {
    background-color: #3d3d3d;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
}
"""

def calcular_hash_arquivo(caminho_arquivo, block_size=65536):
    """Calcula o hash SHA-256 de um arquivo"""
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

class OrganizadorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    question_signal = pyqtSignal(str, list)
    duplicates_signal = pyqtSignal(dict)
    
    def __init__(self, hd_path):
        super().__init__()
        self.hd_path = hd_path
        self.folders_by_name = defaultdict(list)
        self.identical_groups = []
        self.user_response = None
        
    def run(self):
        self.analyze_folders()
        self.identify_duplicates()
        self.compare_folders()
        self.find_duplicate_files()
        self.finished_signal.emit()
    
    def analyze_folders(self):
        self.progress_signal.emit("Analisando estrutura de pastas...")
        for root, dirs, files in os.walk(self.hd_path):
            for dir_name in dirs:
                full_path = os.path.join(root, dir_name)
                self.folders_by_name[dir_name.lower()].append(full_path)
                
    def identify_duplicates(self):
        self.progress_signal.emit("Identificando pastas duplicadas...")
        self.duplicate_folders = {
            name: paths for name, paths in self.folders_by_name.items() 
            if len(paths) > 1
        }
        
    def compare_folders(self):
        self.progress_signal.emit("Comparando conteúdo de pastas...")
        for name, paths in self.duplicate_folders.items():
            compared = set()
            for i in range(len(paths)):
                for j in range(i+1, len(paths)):
                    path1, path2 = paths[i], paths[j]
                    if (path1, path2) not in compared:
                        comparison = filecmp.dircmp(path1, path2)
                        if not comparison.left_only and not comparison.right_only and not comparison.diff_files:
                            self.identical_groups.append((path1, path2))
                        compared.add((path1, path2))

    def find_duplicate_files(self):
        """Encontra todos os arquivos duplicados em todas as pastas"""
        self.progress_signal.emit("Procurando arquivos duplicados em todas as pastas...")
        
        # Dicionário para armazenar arquivos por tamanho
        arquivos_por_tamanho = defaultdict(list)
        
        # Primeiro, agrupa arquivos por tamanho
        for raiz, _, arquivos in os.walk(self.hd_path):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                try:
                    tamanho = os.path.getsize(caminho_completo)
                    arquivos_por_tamanho[tamanho].append(caminho_completo)
                except (OSError, IOError):
                    continue
        
        # Para arquivos com mesmo tamanho, calcula o hash
        arquivos_por_hash = defaultdict(list)
        total_grupos = len([g for g in arquivos_por_tamanho.values() if len(g) > 1])
        grupos_processados = 0
        
        for tamanho, arquivos in arquivos_por_tamanho.items():
            if len(arquivos) > 1:
                grupos_processados += 1
                self.progress_signal.emit(f"Analisando grupo {grupos_processados}/{total_grupos} de arquivos com mesmo tamanho...")
                for arquivo in arquivos:
                    try:
                        hash_arquivo = calcular_hash_arquivo(arquivo)
                        arquivos_por_hash[hash_arquivo].append(arquivo)
                    except (OSError, IOError):
                        continue
        
        # Emite sinal apenas com grupos que têm duplicados
        duplicados = {hash_: arquivos for hash_, arquivos in arquivos_por_hash.items() 
                     if len(arquivos) > 1}
        if duplicados:
            self.duplicates_signal.emit(duplicados)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.original_size = None
    
    def enterEvent(self, event):
        if not self.original_size:
            self.original_size = self.size()
        target_size = QSize(int(self.width() * 1.05), int(self.height() * 1.05))
        self._animation.setStartValue(self.size())
        self._animation.setEndValue(target_size)
        self._animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if self.original_size:
            self._animation.setStartValue(self.size())
            self._animation.setEndValue(self.original_size)
            self._animation.start()
        super().leaveEvent(event)

class StyledDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(STYLE)
        self.setMinimumSize(700, 500)

class DuplicateFilesDialog(StyledDialog):
    def __init__(self, arquivos, parent=None):
        super().__init__("Arquivos Duplicados Encontrados", parent)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Arquivos Duplicados Encontrados")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Container principal
        main_container = QFrame()
        main_container.setObjectName("card")
        main_layout = QVBoxLayout(main_container)
        
        # Lista de arquivos com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        
        self.list_widget = QListWidget()
        for arquivo in arquivos:
            self.list_widget.addItem(arquivo)
        list_layout.addWidget(self.list_widget)
        
        scroll.setWidget(list_container)
        main_layout.addWidget(scroll)
        
        # Opções
        options_frame = QFrame()
        options_frame.setObjectName("card")
        options_layout = QVBoxLayout(options_frame)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter todos os arquivos",
            "Manter apenas o primeiro arquivo",
            "Escolher manualmente qual manter"
        ]
        
        for i, text in enumerate(options):
            radio = QRadioButton(text)
            radio.setStyleSheet("font-size: 14px;")
            self.radio_group.addButton(radio, i)
            options_layout.addWidget(radio)
        
        main_layout.addWidget(options_frame)
        layout.addWidget(main_container)
        
        # Botão de confirmação
        confirm_btn = AnimatedButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
        
        self.setLayout(layout)

class FolderActionDialog(StyledDialog):
    def __init__(self, folder1, folder2):
        super().__init__("Ação para Pastas Duplicadas")
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Pastas Idênticas Encontradas")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Container principal
        main_container = QFrame()
        main_container.setObjectName("card")
        main_layout = QVBoxLayout(main_container)
        
        # Informação das pastas
        paths_frame = QFrame()
        paths_frame.setObjectName("card")
        paths_layout = QVBoxLayout(paths_frame)
        paths_layout.addWidget(QLabel(f"1: {folder1}"))
        paths_layout.addWidget(QLabel(f"2: {folder2}"))
        main_layout.addWidget(paths_frame)
        
        # Opções
        options_frame = QFrame()
        options_frame.setObjectName("card")
        options_layout = QVBoxLayout(options_frame)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter ambas",
            "Manter apenas a primeira",
            "Manter apenas a segunda",
            "Mesclar conteúdo"
        ]
        
        for i, text in enumerate(options):
            radio = QRadioButton(text)
            radio.setStyleSheet("font-size: 14px;")
            self.radio_group.addButton(radio, i)
            options_layout.addWidget(radio)
        
        main_layout.addWidget(options_frame)
        layout.addWidget(main_container)
        
        # Botão de confirmação
        confirm_btn = AnimatedButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)
        
        self.setLayout(layout)

class MesclarThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, hd_destino, hd_origem):
        super().__init__()
        self.hd_destino = hd_destino
        self.hd_origem = hd_origem
        
    def run(self):
        try:
            if mesclar_hds(self.hd_destino, self.hd_origem):
                self.progress_signal.emit("Mesclagem concluída com sucesso!")
            else:
                self.progress_signal.emit("Erro durante a mesclagem!")
        except Exception as e:
            self.progress_signal.emit(f"Erro: {str(e)}")
        finally:
            self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de HD")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLE)
        
        # Widget principal com abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Aba de Organização
        self.tab_organizacao = QWidget()
        self.setup_tab_organizacao()
        self.tabs.addTab(self.tab_organizacao, "Organizar HD")
        
        # Aba de Mesclagem
        self.tab_mesclagem = QWidget()
        self.setup_tab_mesclagem()
        self.tabs.addTab(self.tab_mesclagem, "Mesclar HDs")
        
    def setup_tab_organizacao(self):
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Organizador de HD")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Container principal
        main_container = QFrame()
        main_container.setObjectName("card")
        main_layout = QVBoxLayout(main_container)
        
        # Área de seleção do HD
        hd_frame = QFrame()
        hd_frame.setObjectName("card")
        hd_layout = QHBoxLayout(hd_frame)
        
        self.path_label = QLabel("Nenhum HD selecionado")
        select_btn = AnimatedButton("Selecionar HD")
        select_btn.clicked.connect(self.select_hd)
        
        hd_layout.addWidget(self.path_label)
        hd_layout.addWidget(select_btn)
        main_layout.addWidget(hd_frame)
        
        # Área de log
        log_frame = QFrame()
        log_frame.setObjectName("card")
        log_layout = QVBoxLayout(log_frame)
        
        log_title = QLabel("Log de Operações")
        log_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        log_layout.addWidget(log_title)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        main_layout.addWidget(log_frame)
        
        # Barra de progresso
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_layout = QVBoxLayout(progress_frame)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        self.start_btn = AnimatedButton("Iniciar Organização")
        self.start_btn.clicked.connect(self.start_organization)
        self.start_btn.setEnabled(False)
        main_layout.addWidget(self.start_btn)
        
        layout.addWidget(main_container)
        self.tab_organizacao.setLayout(layout)
        
    def setup_tab_mesclagem(self):
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Mesclar HDs")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Container principal
        main_container = QFrame()
        main_container.setObjectName("card")
        main_layout = QVBoxLayout(main_container)
        
        # Área de seleção dos HDs
        hds_frame = QFrame()
        hds_frame.setObjectName("card")
        hds_layout = QVBoxLayout(hds_frame)
        
        # HD Destino
        destino_layout = QHBoxLayout()
        self.destino_label = QLabel("Nenhum HD destino selecionado")
        select_destino_btn = AnimatedButton("Selecionar HD Destino")
        select_destino_btn.clicked.connect(self.select_hd_destino)
        destino_layout.addWidget(self.destino_label)
        destino_layout.addWidget(select_destino_btn)
        hds_layout.addLayout(destino_layout)
        
        # HD Origem
        origem_layout = QHBoxLayout()
        self.origem_label = QLabel("Nenhum HD origem selecionado")
        select_origem_btn = AnimatedButton("Selecionar HD Origem")
        select_origem_btn.clicked.connect(self.select_hd_origem)
        origem_layout.addWidget(self.origem_label)
        origem_layout.addWidget(select_origem_btn)
        hds_layout.addLayout(origem_layout)
        
        main_layout.addWidget(hds_frame)
        
        # Área de log
        log_frame = QFrame()
        log_frame.setObjectName("card")
        log_layout = QVBoxLayout(log_frame)
        
        log_title = QLabel("Log de Mesclagem")
        log_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        log_layout.addWidget(log_title)
        
        self.log_mesclagem = QTextEdit()
        self.log_mesclagem.setReadOnly(True)
        log_layout.addWidget(self.log_mesclagem)
        
        main_layout.addWidget(log_frame)
        
        # Barra de progresso
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_layout = QVBoxLayout(progress_frame)
        
        self.progress_mesclagem = QProgressBar()
        self.progress_mesclagem.setTextVisible(True)
        self.progress_mesclagem.setFormat("%p%")
        progress_layout.addWidget(self.progress_mesclagem)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        self.start_mesclar_btn = AnimatedButton("Iniciar Mesclagem")
        self.start_mesclar_btn.clicked.connect(self.start_mesclagem)
        self.start_mesclar_btn.setEnabled(False)
        main_layout.addWidget(self.start_mesclar_btn)
        
        layout.addWidget(main_container)
        self.tab_mesclagem.setLayout(layout)
    
    def select_hd(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar HD")
        if folder:
            self.hd_path = folder
            self.path_label.setText(folder)
            self.start_btn.setEnabled(True)
            
    def select_hd_destino(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar HD Destino")
        if folder:
            self.hd_destino = folder
            self.destino_label.setText(folder)
            self.check_mesclagem_ready()
    
    def select_hd_origem(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar HD Origem")
        if folder:
            self.hd_origem = folder
            self.origem_label.setText(folder)
            self.check_mesclagem_ready()
    
    def check_mesclagem_ready(self):
        if hasattr(self, 'hd_destino') and hasattr(self, 'hd_origem'):
            if self.hd_destino != self.hd_origem:
                self.start_mesclar_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Erro", 
                                  "Os HDs de origem e destino não podem ser iguais!")
                self.start_mesclar_btn.setEnabled(False)
    
    def start_mesclagem(self):
        reply = QMessageBox.question(
            self, 'Confirmação',
            f'Tem certeza que deseja mesclar os HDs?\n\nDestino: {self.hd_destino}\nOrigem: {self.hd_origem}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.worker_mesclar = MesclarThread(self.hd_destino, self.hd_origem)
            self.worker_mesclar.progress_signal.connect(self.log_mesclagem_message)
            self.worker_mesclar.finished_signal.connect(self.mesclagem_finished)
            self.worker_mesclar.start()
            self.start_mesclar_btn.setEnabled(False)
    
    def log_mesclagem_message(self, message):
        self.log_mesclagem.append(message)
    
    def mesclagem_finished(self):
        QMessageBox.information(self, "Concluído", 
                              "Mesclagem dos HDs finalizada!")
        self.start_mesclar_btn.setEnabled(True)
        
    def start_organization(self):
        self.worker = OrganizadorThread(self.hd_path)
        self.worker.progress_signal.connect(self.log_message)
        self.worker.finished_signal.connect(self.organization_finished)
        self.worker.question_signal.connect(self.show_folder_dialog)
        self.worker.duplicates_signal.connect(self.handle_duplicate_files)
        self.worker.start()
        self.start_btn.setEnabled(False)
        
    def organization_finished(self):
        QMessageBox.information(self, "Concluído", 
                              "Organização do HD finalizada com sucesso!")
        self.start_btn.setEnabled(True)
        
    def log_message(self, message):
        """Adiciona mensagem à área de log da aba de organização"""
        self.log_area.append(message)
        
    def process_folder_action(self, folder1, folder2, action):
        """Processa a ação escolhida para pastas duplicadas"""
        try:
            if action == 1:  # Manter apenas a primeira
                shutil.rmtree(folder2)
                self.log_message(f"Pasta removida: {folder2}")
            elif action == 2:  # Manter apenas a segunda
                shutil.rmtree(folder1)
                self.log_message(f"Pasta removida: {folder1}")
            elif action == 3:  # Mesclar conteúdo
                # Mover arquivos únicos da segunda pasta para a primeira
                for item in os.listdir(folder2):
                    src = os.path.join(folder2, item)
                    dst = os.path.join(folder1, item)
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                        self.log_message(f"Arquivo movido: {src} -> {dst}")
                
                # Remover a segunda pasta após a mesclagem
                shutil.rmtree(folder2)
                self.log_message(f"Pastas mescladas em: {folder1}")
            else:  # Manter ambas (action == 0)
                self.log_message("Ambas as pastas mantidas")
        except Exception as e:
            self.log_message(f"Erro ao processar pastas: {str(e)}")
        
    def show_folder_dialog(self, message, folders):
        dialog = FolderActionDialog(folders[0], folders[1])
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            action = dialog.radio_group.checkedId()
            self.process_folder_action(folders[0], folders[1], action)

    def handle_duplicate_files(self, duplicados):
        pasta_duplicados = os.path.join(self.hd_path, "Arquivos Duplicados")
        os.makedirs(pasta_duplicados, exist_ok=True)
        
        for hash_arquivo, arquivos in duplicados.items():
            dialog = DuplicateFilesDialog(arquivos, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                action = dialog.radio_group.checkedId()
                
                if action == 1:  # Manter apenas o primeiro
                    primeiro = arquivos[0]
                    for arquivo in arquivos[1:]:
                        novo_nome = os.path.join(pasta_duplicados, os.path.basename(arquivo))
                        contador = 1
                        while os.path.exists(novo_nome):
                            base, ext = os.path.splitext(os.path.basename(arquivo))
                            novo_nome = os.path.join(pasta_duplicados, f"{base}_{contador}{ext}")
                            contador += 1
                        shutil.move(arquivo, novo_nome)
                        self.log_message(f"Arquivo duplicado movido: {arquivo} -> {novo_nome}")
                
                elif action == 2:  # Escolher manualmente
                    selecionado = dialog.list_widget.currentRow()
                    if selecionado >= 0:
                        arquivo_manter = arquivos[selecionado]
                        for i, arquivo in enumerate(arquivos):
                            if i != selecionado:
                                novo_nome = os.path.join(pasta_duplicados, os.path.basename(arquivo))
                                contador = 1
                                while os.path.exists(novo_nome):
                                    base, ext = os.path.splitext(os.path.basename(arquivo))
                                    novo_nome = os.path.join(pasta_duplicados, f"{base}_{contador}{ext}")
                                    contador += 1
                                shutil.move(arquivo, novo_nome)
                                self.log_message(f"Arquivo duplicado movido: {arquivo} -> {novo_nome}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 