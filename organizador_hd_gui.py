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
                           QSplitter, QScrollArea, QCheckBox, QGroupBox, QGraphicsDropShadowEffect,
                           QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QLinearGradient, QPainter, QPainterPath, QBrush
from mesclar_hds import mesclar_hds, obter_pasta_tipo_arquivo

# Definição de estilos Apple-like com cores sólidas (sem blur)
STYLE = """
QMainWindow, QDialog {
    background-color: #f5f5f7;
    font-family: 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}

QTabWidget::pane {
    border: none;
    background-color: #f5f5f7;
    border-radius: 12px;
}

QTabBar::tab {
    background-color: #e0e0e5;
    color: #333333;
    padding: 10px 25px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    font-weight: 500;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #007aff;
    color: white;
}

QPushButton {
    background-color: #007aff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #0069d9;
}

QPushButton:pressed {
    background-color: #0051a8;
}

QPushButton:disabled {
    background-color: #b4b4b4;
    color: #f0f0f0;
}

QTextEdit {
    background-color: white;
    color: #333333;
    border: none;
    border-radius: 8px;
    padding: 8px;
    selection-background-color: rgba(0, 122, 255, 0.3);
}

QProgressBar {
    border: none;
    border-radius: 8px;
    text-align: center;
    height: 8px;
    background-color: #e0e0e5;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #007aff;
    border-radius: 8px;
}

QLabel {
    color: #333333;
    font-size: 13px;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #333333;
}

QLabel#subtitle {
    font-size: 16px;
    font-weight: 500;
    color: #666666;
}

QLabel#info {
    font-size: 13px;
    color: #888888;
}

QRadioButton, QCheckBox {
    color: #333333;
    spacing: 8px;
    padding: 4px;
    font-size: 13px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 20px;
    height: 20px;
}

QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 10px;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #007aff;
    border: 1px solid #007aff;
    border-radius: 10px;
}

QListWidget {
    background-color: white;
    color: #333333;
    border: none;
    border-radius: 8px;
    padding: 5px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 6px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #e6f2ff;
    color: #333333;
}

QListWidget::item:hover {
    background-color: #f0f0f0;
}

QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #b3b3b3;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#card {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    margin: 8px;
}

QGroupBox {
    color: #333333;
    border: 1px solid #e0e0e5;
    border-radius: 8px;
    margin-top: 1.5ex;
    padding-top: 1.5ex;
    font-weight: 500;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    color: #666666;
}

QWidget {
    font-family: 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}
"""

def calcular_hash_arquivo(caminho_arquivo, block_size=65536):
    """Calcula o hash SHA-256 de um arquivo"""
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def mover_para_duplicados(arquivo, pasta_duplicados):
    """
    Move um arquivo para a pasta de duplicados, organizando por tipo de arquivo.
    """
    # Obter nome e extensão do arquivo
    nome_arquivo = os.path.basename(arquivo)
    _, extensao = os.path.splitext(nome_arquivo)
    
    # Determinar a pasta de destino baseada no tipo de arquivo
    tipo_pasta = obter_pasta_tipo_arquivo(extensao)
    pasta_tipo = os.path.join(pasta_duplicados, tipo_pasta)
    
    # Criar a pasta do tipo se não existir
    os.makedirs(pasta_tipo, exist_ok=True)
    
    # Definir o caminho de destino
    destino = os.path.join(pasta_tipo, nome_arquivo)
    
    # Se já existe um arquivo com mesmo nome na pasta de destino
    contador = 1
    while os.path.exists(destino):
        nome_base, ext = os.path.splitext(nome_arquivo)
        destino = os.path.join(pasta_tipo, f"{nome_base}_{contador}{ext}")
        contador += 1
    
    # Mover o arquivo
    shutil.move(arquivo, destino)
    return destino

class ModernFrame(QFrame):
    """Frame com estilo moderno no estilo Apple"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.original_size = None
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        if not self.original_size:
            self.original_size = self.size()
        target_size = QSize(int(self.width() * 1.03), int(self.height() * 1.03))
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

class OrganizadorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    question_signal = pyqtSignal(str, list)
    duplicates_signal = pyqtSignal(dict)
    progress_update = pyqtSignal(int, int)  # valor atual, valor máximo
    
    def __init__(self, hd_path, batch_mode=False, duplicate_action=0):
        super().__init__()
        self.hd_path = hd_path
        self.folders_by_name = defaultdict(list)
        self.identical_groups = []
        self.user_response = None
        self.batch_mode = batch_mode
        self.duplicate_action = duplicate_action
        # 0: Perguntar para cada arquivo
        # 1: Manter todos os arquivos
        # 2: Manter apenas o primeiro arquivo
        # 3: Mover todos os duplicados para pasta específica
        
    def run(self):
        self.analyze_folders()
        self.identify_duplicates()
        self.compare_folders()
        self.find_duplicate_files()
        self.finished_signal.emit()
    
    def analyze_folders(self):
        self.progress_signal.emit("Analisando estrutura de pastas...")
        total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(self.hd_path)])
        processed_dirs = 0
        
        for root, dirs, files in os.walk(self.hd_path):
            for dir_name in dirs:
                full_path = os.path.join(root, dir_name)
                self.folders_by_name[dir_name.lower()].append(full_path)
                processed_dirs += 1
                self.progress_update.emit(processed_dirs, total_dirs)
                
    def identify_duplicates(self):
        self.progress_signal.emit("Identificando pastas duplicadas...")
        self.duplicate_folders = {
            name: paths for name, paths in self.folders_by_name.items() 
            if len(paths) > 1
        }
        
    def compare_folders(self):
        self.progress_signal.emit("Comparando conteúdo de pastas...")
        total_comparisons = sum([len(paths) * (len(paths) - 1) // 2 for paths in self.duplicate_folders.values()])
        processed_comparisons = 0
        
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
                        processed_comparisons += 1
                        self.progress_update.emit(processed_comparisons, total_comparisons)

    def find_duplicate_files(self):
        """Encontra todos os arquivos duplicados em todas as pastas"""
        self.progress_signal.emit("Procurando arquivos duplicados em todas as pastas...")
        
        # Dicionário para armazenar arquivos por tamanho
        arquivos_por_tamanho = defaultdict(list)
        
        # Primeiro, agrupa arquivos por tamanho
        total_files = sum([len(files) for _, _, files in os.walk(self.hd_path)])
        processed_files = 0
        
        for raiz, _, arquivos in os.walk(self.hd_path):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                try:
                    tamanho = os.path.getsize(caminho_completo)
                    arquivos_por_tamanho[tamanho].append(caminho_completo)
                except (OSError, IOError):
                    continue
                processed_files += 1
                self.progress_update.emit(processed_files, total_files)
        
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
                self.progress_update.emit(grupos_processados, total_grupos)
        
        # Emite sinal apenas com grupos que têm duplicados
        duplicados = {hash_: arquivos for hash_, arquivos in arquivos_por_hash.items() 
                     if len(arquivos) > 1}
        
        # Se estiver em modo de lote, processa automaticamente os duplicados
        if self.batch_mode and duplicados:
            pasta_duplicados = os.path.join(self.hd_path, "Arquivos Duplicados")
            os.makedirs(pasta_duplicados, exist_ok=True)
            
            if self.duplicate_action == 2:  # Manter apenas o primeiro arquivo
                for hash_arquivo, arquivos in duplicados.items():
                    for arquivo in arquivos[1:]:
                        novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                        self.progress_signal.emit(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}")
            elif self.duplicate_action == 3:  # Mover todos os duplicados para pasta específica
                for hash_arquivo, arquivos in duplicados.items():
                    for arquivo in arquivos:
                        # Obter nome e extensão do arquivo
                        nome_arquivo = os.path.basename(arquivo)
                        _, extensao = os.path.splitext(nome_arquivo)
                        
                        # Determinar a pasta de destino baseada no tipo de arquivo
                        tipo_pasta = obter_pasta_tipo_arquivo(extensao)
                        pasta_tipo = os.path.join(pasta_duplicados, tipo_pasta)
                        
                        # Criar a pasta do tipo se não existir
                        os.makedirs(pasta_tipo, exist_ok=True)
                        
                        # Definir o caminho de destino
                        destino = os.path.join(pasta_tipo, nome_arquivo)
                        
                        # Se já existe um arquivo com mesmo nome na pasta de destino
                        contador = 1
                        while os.path.exists(destino):
                            nome_base, ext = os.path.splitext(nome_arquivo)
                            destino = os.path.join(pasta_tipo, f"{nome_base}_{contador}{ext}")
                            contador += 1
                        
                        # Copiar o arquivo (mantém o original)
                        shutil.copy2(arquivo, destino)
                        self.progress_signal.emit(f"Arquivo duplicado copiado: {arquivo} -> {destino}")
        elif duplicados:
            self.duplicates_signal.emit(duplicados)

class StyledDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(STYLE)
        self.setMinimumSize(700, 500)
        
        # Configurar efeito de sombra para a janela
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class DuplicateFilesDialog(StyledDialog):
    def __init__(self, arquivos, parent=None):
        super().__init__("Arquivos Duplicados Encontrados", parent)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Arquivos Duplicados Encontrados")
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ModernFrame()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Lista de arquivos com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        
        self.list_widget = QListWidget()
        for arquivo in arquivos:
            self.list_widget.addItem(arquivo)
        list_layout.addWidget(self.list_widget)
        
        scroll.setWidget(list_container)
        main_layout.addWidget(scroll)
        
        # Opções
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        
        options_title = QLabel("Escolha uma opção")
        options_title.setObjectName("subtitle")
        options_layout.addWidget(options_title)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter todos os arquivos",
            "Manter apenas o primeiro arquivo",
            "Escolher manualmente qual manter"
        ]
        
        for i, text in enumerate(options):
            radio = QRadioButton(text)
            self.radio_group.addButton(radio, i)
            options_layout.addWidget(radio)
        
        # Seleciona a primeira opção por padrão
        self.radio_group.button(0).setChecked(True)
        
        main_layout.addWidget(options_frame)
        layout.addWidget(main_container)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        layout.addWidget(info_label)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = AnimatedButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = AnimatedButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class BatchSettingsDialog(StyledDialog):
    def __init__(self, parent=None):
        super().__init__("Configurações de Processamento em Lote", parent)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Configurações de Processamento em Lote")
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ModernFrame()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Opções para arquivos duplicados
        duplicate_group = QGroupBox("Tratamento de Arquivos Duplicados")
        duplicate_layout = QVBoxLayout(duplicate_group)
        duplicate_layout.setSpacing(10)
        
        self.duplicate_radio_group = QButtonGroup()
        duplicate_options = [
            "Perguntar para cada arquivo",
            "Manter todos os arquivos",
            "Manter apenas o primeiro arquivo (mover outros para pasta de duplicados)",
            "Mover todos os duplicados para pasta específica (mantém originais)"
        ]
        
        for i, text in enumerate(duplicate_options):
            radio = QRadioButton(text)
            self.duplicate_radio_group.addButton(radio, i)
            duplicate_layout.addWidget(radio)
        
        # Seleciona a opção padrão
        self.duplicate_radio_group.button(2).setChecked(True)
        
        main_layout.addWidget(duplicate_group)
        
        # Opções para pastas duplicadas
        folder_group = QGroupBox("Tratamento de Pastas Duplicadas")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(10)
        
        self.folder_radio_group = QButtonGroup()
        folder_options = [
            "Perguntar para cada pasta",
            "Manter todas as pastas",
            "Manter apenas a primeira pasta",
            "Mesclar conteúdo das pastas"
        ]
        
        for i, text in enumerate(folder_options):
            radio = QRadioButton(text)
            self.folder_radio_group.addButton(radio, i)
            folder_layout.addWidget(radio)
        
        # Seleciona a opção padrão
        self.folder_radio_group.button(3).setChecked(True)
        
        main_layout.addWidget(folder_group)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        main_layout.addWidget(info_label)
        
        layout.addWidget(main_container)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = AnimatedButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = AnimatedButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class FolderActionDialog(StyledDialog):
    def __init__(self, folder1, folder2):
        super().__init__("Ação para Pastas Duplicadas")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Pastas Idênticas Encontradas")
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ModernFrame()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Informação das pastas
        paths_frame = ModernFrame()
        paths_layout = QVBoxLayout(paths_frame)
        
        paths_title = QLabel("Pastas encontradas")
        paths_title.setObjectName("subtitle")
        paths_layout.addWidget(paths_title)
        
        paths_layout.addWidget(QLabel(f"1: {folder1}"))
        paths_layout.addWidget(QLabel(f"2: {folder2}"))
        main_layout.addWidget(paths_frame)
        
        # Opções
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        
        options_title = QLabel("Escolha uma opção")
        options_title.setObjectName("subtitle")
        options_layout.addWidget(options_title)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter ambas",
            "Manter apenas a primeira",
            "Manter apenas a segunda",
            "Mesclar conteúdo"
        ]
        
        for i, text in enumerate(options):
            radio = QRadioButton(text)
            self.radio_group.addButton(radio, i)
            options_layout.addWidget(radio)
        
        # Seleciona a primeira opção por padrão
        self.radio_group.button(0).setChecked(True)
        
        main_layout.addWidget(options_frame)
        layout.addWidget(main_container)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = AnimatedButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = AnimatedButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class MesclarThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    progress_update = pyqtSignal(int, int)  # valor atual, valor máximo
    
    def __init__(self, hd_destino, hd_origem, manter_primeiro=True):
        super().__init__()
        self.hd_destino = hd_destino
        self.hd_origem = hd_origem
        self.manter_primeiro = manter_primeiro
        
    def run(self):
        try:
            if mesclar_hds(self.hd_destino, self.hd_origem, self.manter_primeiro, self.update_progress):
                self.progress_signal.emit("Mesclagem concluída com sucesso!")
            else:
                self.progress_signal.emit("Erro durante a mesclagem!")
        except Exception as e:
            self.progress_signal.emit(f"Erro: {str(e)}")
        finally:
            self.finished_signal.emit()
            
    def update_progress(self, value, maximum):
        self.progress_update.emit(value, maximum)

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
        
        # Configurações padrão
        self.batch_mode = False
        self.duplicate_action = 0
        self.folder_action = 0
        self.manter_primeiro = True  # Opção padrão para mesclagem
        
    def setup_tab_organizacao(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Organizador de HD")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ModernFrame()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Área de seleção do HD
        hd_frame = ModernFrame()
        hd_layout = QHBoxLayout(hd_frame)
        hd_layout.setContentsMargins(15, 15, 15, 15)
        
        self.path_label = QLabel("Nenhum HD selecionado")
        select_btn = AnimatedButton("Selecionar HD")
        select_btn.clicked.connect(self.select_hd)
        
        hd_layout.addWidget(self.path_label, 1)
        hd_layout.addWidget(select_btn)
        main_layout.addWidget(hd_frame)
        
        # Opções de processamento
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Opções de Processamento")
        options_title.setObjectName("subtitle")
        options_layout.addWidget(options_title)
        
        # Checkbox para modo de lote
        self.batch_checkbox = QCheckBox("Processar todos os arquivos de uma vez (modo lote)")
        self.batch_checkbox.toggled.connect(self.toggle_batch_mode)
        options_layout.addWidget(self.batch_checkbox)
        
        # Botão de configurações de lote
        self.batch_settings_btn = AnimatedButton("Configurar Processamento em Lote")
        self.batch_settings_btn.clicked.connect(self.show_batch_settings)
        self.batch_settings_btn.setEnabled(False)
        options_layout.addWidget(self.batch_settings_btn)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        options_layout.addWidget(info_label)
        
        main_layout.addWidget(options_frame)
        
        # Área de log
        log_frame = ModernFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        log_title = QLabel("Log de Operações")
        log_title.setObjectName("subtitle")
        log_layout.addWidget(log_title)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        main_layout.addWidget(log_frame)
        
        # Barra de progresso
        progress_frame = ModernFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        progress_title = QLabel("Progresso")
        progress_title.setObjectName("subtitle")
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_btn = AnimatedButton("Iniciar Organização")
        self.start_btn.clicked.connect(self.start_organization)
        self.start_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_btn)
        
        main_layout.addLayout(buttons_layout)
        
        layout.addWidget(main_container)
        self.tab_organizacao.setLayout(layout)
        
    def setup_tab_mesclagem(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Mesclar HDs")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ModernFrame()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Área de seleção dos HDs
        hds_frame = ModernFrame()
        hds_layout = QVBoxLayout(hds_frame)
        hds_layout.setContentsMargins(15, 15, 15, 15)
        hds_layout.setSpacing(10)
        
        hds_title = QLabel("Selecione os HDs")
        hds_title.setObjectName("subtitle")
        hds_layout.addWidget(hds_title)
        
        # HD Destino
        destino_layout = QHBoxLayout()
        destino_label_title = QLabel("HD Destino:")
        self.destino_label = QLabel("Nenhum HD destino selecionado")
        select_destino_btn = AnimatedButton("Selecionar")
        select_destino_btn.clicked.connect(self.select_hd_destino)
        destino_layout.addWidget(destino_label_title)
        destino_layout.addWidget(self.destino_label, 1)
        destino_layout.addWidget(select_destino_btn)
        hds_layout.addLayout(destino_layout)
        
        # HD Origem
        origem_layout = QHBoxLayout()
        origem_label_title = QLabel("HD Origem:")
        self.origem_label = QLabel("Nenhum HD origem selecionado")
        select_origem_btn = AnimatedButton("Selecionar")
        select_origem_btn.clicked.connect(self.select_hd_origem)
        origem_layout.addWidget(origem_label_title)
        origem_layout.addWidget(self.origem_label, 1)
        origem_layout.addWidget(select_origem_btn)
        hds_layout.addLayout(origem_layout)
        
        main_layout.addWidget(hds_frame)
        
        # Opções de mesclagem
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Opções de Mesclagem")
        options_title.setObjectName("subtitle")
        options_layout.addWidget(options_title)
        
        # Checkbox para manter primeiro arquivo
        self.manter_primeiro_checkbox = QCheckBox("Manter primeiro arquivo e mover duplicatas para pasta 'Arquivos Duplicados'")
        self.manter_primeiro_checkbox.setChecked(True)
        self.manter_primeiro_checkbox.toggled.connect(self.toggle_manter_primeiro)
        options_layout.addWidget(self.manter_primeiro_checkbox)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        options_layout.addWidget(info_label)
        
        main_layout.addWidget(options_frame)
        
        # Área de log
        log_frame = ModernFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        log_title = QLabel("Log de Mesclagem")
        log_title.setObjectName("subtitle")
        log_layout.addWidget(log_title)
        
        self.log_mesclagem = QTextEdit()
        self.log_mesclagem.setReadOnly(True)
        log_layout.addWidget(self.log_mesclagem)
        
        main_layout.addWidget(log_frame)
        
        # Barra de progresso
        progress_frame = ModernFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        progress_title = QLabel("Progresso")
        progress_title.setObjectName("subtitle")
        progress_layout.addWidget(progress_title)
        
        self.progress_mesclagem = QProgressBar()
        self.progress_mesclagem.setTextVisible(True)
        self.progress_mesclagem.setFormat("%p%")
        progress_layout.addWidget(self.progress_mesclagem)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_mesclar_btn = AnimatedButton("Iniciar Mesclagem")
        self.start_mesclar_btn.clicked.connect(self.start_mesclagem)
        self.start_mesclar_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_mesclar_btn)
        
        main_layout.addLayout(buttons_layout)
        
        layout.addWidget(main_container)
        self.tab_mesclagem.setLayout(layout)
    
    def toggle_batch_mode(self, checked):
        self.batch_mode = checked
        self.batch_settings_btn.setEnabled(checked)
    
    def toggle_manter_primeiro(self, checked):
        self.manter_primeiro = checked
        
    def show_batch_settings(self):
        dialog = BatchSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.duplicate_action = dialog.duplicate_radio_group.checkedId()
            self.folder_action = dialog.folder_radio_group.checkedId()
            self.log_message(f"Configurações de lote atualizadas: Duplicados={self.duplicate_action}, Pastas={self.folder_action}")
    
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
        modo_texto = "Manter primeiro arquivo e mover duplicatas para pasta 'Arquivos Duplicados'" if self.manter_primeiro else "Modo padrão"
        
        reply = QMessageBox.question(
            self, 'Confirmação',
            f'Tem certeza que deseja mesclar os HDs?\n\nDestino: {self.hd_destino}\nOrigem: {self.hd_origem}\nModo: {modo_texto}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.worker_mesclar = MesclarThread(self.hd_destino, self.hd_origem, self.manter_primeiro)
            self.worker_mesclar.progress_signal.connect(self.log_mesclagem_message)
            self.worker_mesclar.finished_signal.connect(self.mesclagem_finished)
            self.worker_mesclar.progress_update.connect(self.update_mesclagem_progress)
            self.worker_mesclar.start()
            self.start_mesclar_btn.setEnabled(False)
    
    def log_mesclagem_message(self, message):
        self.log_mesclagem.append(message)
    
    def update_mesclagem_progress(self, value, maximum):
        self.progress_mesclagem.setMaximum(maximum)
        self.progress_mesclagem.setValue(value)
    
    def mesclagem_finished(self):
        QMessageBox.information(self, "Concluído", 
                              "Mesclagem dos HDs finalizada!")
        self.start_mesclar_btn.setEnabled(True)
        
    def start_organization(self):
        self.worker = OrganizadorThread(
            self.hd_path, 
            batch_mode=self.batch_mode,
            duplicate_action=self.duplicate_action
        )
        self.worker.progress_signal.connect(self.log_message)
        self.worker.finished_signal.connect(self.organization_finished)
        self.worker.question_signal.connect(self.show_folder_dialog)
        self.worker.duplicates_signal.connect(self.handle_duplicate_files)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.start()
        self.start_btn.setEnabled(False)
    
    def update_progress(self, value, maximum):
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        
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
        # Se estiver em modo de lote, usa a ação configurada
        if self.batch_mode and self.folder_action > 0:
            self.process_folder_action(folders[0], folders[1], self.folder_action - 1)
            return
            
        # Caso contrário, mostra o diálogo
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
                        novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                        self.log_message(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}")
                
                elif action == 2:  # Escolher manualmente
                    selecionado = dialog.list_widget.currentRow()
                    if selecionado >= 0:
                        arquivo_manter = arquivos[selecionado]
                        for i, arquivo in enumerate(arquivos):
                            if i != selecionado:
                                novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                                self.log_message(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
