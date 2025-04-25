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
                           QSizePolicy, QSpacerItem, QGridLayout, QStyle)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QRectF, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QLinearGradient, QPainter, QPainterPath, QBrush
from mesclar_hds import mesclar_hds, obter_pasta_tipo_arquivo

# Definição de estilos modernos e responsivos
STYLE = """
QMainWindow, QDialog {
    background-color: #f5f5f7;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
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
    font-size: 13px;
}

QProgressBar {
    border: none;
    border-radius: 8px;
    text-align: center;
    height: 10px;
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
    margin: 10px 0px;
}

QLabel#subtitle {
    font-size: 16px;
    font-weight: 500;
    color: #666666;
    margin: 5px 0px;
}

QLabel#info {
    font-size: 13px;
    color: #888888;
    margin: 5px 0px;
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
    font-size: 13px;
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
    font-size: 13px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    color: #666666;
}

QWidget {
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}

QScrollArea {
    border: none;
    background-color: transparent;
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
    """Frame com estilo moderno"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        # Configurar política de tamanho para ser expansível
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class WrappedCheckBox(QWidget):
    """Widget personalizado que contém um checkbox com texto que se ajusta automaticamente"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.checkbox = QCheckBox(parent)
        self.checkbox.toggled.connect(self.toggled.emit)
        
        self.label = QLabel(text, parent)
        self.label.setWordWrap(True)
        
        # Configurar políticas de tamanho
        self.checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        
    def isChecked(self):
        return self.checkbox.isChecked()
    
    def setChecked(self, checked):
        self.checkbox.setChecked(checked)

class WrappedRadioButton(QWidget):
    """Widget personalizado que contém um radio button com texto que se ajusta automaticamente"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.radio = QRadioButton(parent)
        self.radio.toggled.connect(self.toggled.emit)
        
        self.label = QLabel(text, parent)
        self.label.setWordWrap(True)
        
        # Configurar políticas de tamanho
        self.radio.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        layout.addWidget(self.radio)
        layout.addWidget(self.label)
        layout.addStretch()
        
    def isChecked(self):
        return self.radio.isChecked()
    
    def setChecked(self, checked):
        self.radio.setChecked(checked)

class SmoothButton(QPushButton):
    """Botão com animações suaves e responsivo"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        
        # Configurar política de tamanho para ser expansível horizontalmente
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Configurar animações
        self._hover_animation = QPropertyAnimation(self, b"styleSheet")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._press_animation = QPropertyAnimation(self, b"styleSheet")
        self._press_animation.setDuration(100)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Estilo base
        self.base_style = """
            background-color: #007aff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            min-height: 36px;
        """
        
        # Estilo hover
        self.hover_style = """
            background-color: #0069d9;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            min-height: 36px;
        """
        
        # Estilo pressionado
        self.pressed_style = """
            background-color: #0051a8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            min-height: 36px;
        """
        
        self.setStyleSheet(self.base_style)
    
    def enterEvent(self, event):
        self._hover_animation.setStartValue(self.styleSheet())
        self._hover_animation.setEndValue(self.hover_style)
        self._hover_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._hover_animation.setStartValue(self.styleSheet())
        self._hover_animation.setEndValue(self.base_style)
        self._hover_animation.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        self._press_animation.setStartValue(self.styleSheet())
        self._press_animation.setEndValue(self.pressed_style)
        self._press_animation.start()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self._press_animation.setStartValue(self.styleSheet())
        self._press_animation.setEndValue(self.hover_style if self.underMouse() else self.base_style)
        self._press_animation.start()
        super().mouseReleaseEvent(event)

class ScrollableWidget(QScrollArea):
    """Widget com rolagem automática que se adapta ao conteúdo"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Configurar política de tamanho
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Widget interno
        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(10)
        
        self.setWidget(self.inner_widget)
    
    def addWidget(self, widget):
        self.inner_layout.addWidget(widget)
    
    def addLayout(self, layout):
        self.inner_layout.addLayout(layout)

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

class ResponsiveDialog(QDialog):
    """Diálogo base responsivo com ajuste automático de tamanho"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(STYLE)
        self.setMinimumSize(700, 500)
        
        # Configurar política de tamanho para ser expansível
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configurar efeito de sombra para a janela
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def resizeEvent(self, event):
        """Ajusta o layout quando o diálogo é redimensionado"""
        super().resizeEvent(event)
        # Implementação específica nas subclasses

class DuplicateFilesDialog(ResponsiveDialog):
    def __init__(self, arquivos, parent=None):
        super().__init__("Arquivos Duplicados Encontrados", parent)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Arquivos Duplicados Encontrados")
        title_label.setObjectName("title")
        title_label.setWordWrap(True)  # Permite quebra de linha
        layout.addWidget(title_label)
        
        # Container principal
        main_container = ScrollableWidget()
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(15)
        
        # Lista de arquivos com scroll
        list_frame = ModernFrame()
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(15, 15, 15, 15)
        
        list_title = QLabel("Arquivos encontrados:")
        list_title.setObjectName("subtitle")
        list_title.setWordWrap(True)
        list_layout.addWidget(list_title)
        
        self.list_widget = QListWidget()
        for arquivo in arquivos:
            self.list_widget.addItem(arquivo)
        
        # Configurar para que os itens da lista possam quebrar linha
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setWordWrap(True)
        
        list_layout.addWidget(self.list_widget)
        container_layout.addWidget(list_frame)
        
        # Opções
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Escolha uma opção")
        options_title.setObjectName("subtitle")
        options_title.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(options_title)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter todos os arquivos",
            "Manter apenas o primeiro arquivo",
            "Escolher manualmente qual manter"
        ]
        
        for i, text in enumerate(options):
            radio = WrappedRadioButton(text)
            self.radio_group.addButton(radio.radio, i)
            options_layout.addWidget(radio)
            if i == 0:  # Seleciona a primeira opção por padrão
                radio.setChecked(True)
        
        container_layout.addWidget(options_frame)
        
        # Informação sobre organização por tipo
        info_frame = ModernFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        info_label.setWordWrap(True)  # Permite quebra de linha
        info_layout.addWidget(info_label)
        
        container_layout.addWidget(info_frame)
        
        main_container.setWidget(container_widget)
        layout.addWidget(main_container)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = SmoothButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMaximumWidth(150)
        
        confirm_btn = SmoothButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setMaximumWidth(150)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class BatchSettingsDialog(ResponsiveDialog):
    def __init__(self, parent=None):
        super().__init__("Configurações de Processamento em Lote", parent)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Configurações de Processamento em Lote")
        title_label.setObjectName("title")
        title_label.setWordWrap(True)  # Permite quebra de linha
        layout.addWidget(title_label)
        
        # Container principal com scroll
        main_container = ScrollableWidget()
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(15)
        
        # Opções para arquivos duplicados
        duplicate_frame = ModernFrame()
        duplicate_layout = QVBoxLayout(duplicate_frame)
        duplicate_layout.setContentsMargins(15, 15, 15, 15)
        
        duplicate_title = QLabel("Tratamento de Arquivos Duplicados")
        duplicate_title.setObjectName("subtitle")
        duplicate_title.setWordWrap(True)
        duplicate_layout.addWidget(duplicate_title)
        
        self.duplicate_radio_group = QButtonGroup()
        duplicate_options = [
            "Perguntar para cada arquivo",
            "Manter todos os arquivos",
            "Manter apenas o primeiro arquivo (mover outros para pasta de duplicados)",
            "Mover todos os duplicados para pasta específica (mantém originais)"
        ]
        
        for i, text in enumerate(duplicate_options):
            radio = WrappedRadioButton(text)
            self.duplicate_radio_group.addButton(radio.radio, i)
            duplicate_layout.addWidget(radio)
            if i == 2:  # Seleciona a opção padrão
                radio.setChecked(True)
        
        container_layout.addWidget(duplicate_frame)
        
        # Opções para pastas duplicadas
        folder_frame = ModernFrame()
        folder_layout = QVBoxLayout(folder_frame)
        folder_layout.setContentsMargins(15, 15, 15, 15)
        
        folder_title = QLabel("Tratamento de Pastas Duplicadas")
        folder_title.setObjectName("subtitle")
        folder_title.setWordWrap(True)
        folder_layout.addWidget(folder_title)
        
        self.folder_radio_group = QButtonGroup()
        folder_options = [
            "Perguntar para cada pasta",
            "Manter todas as pastas",
            "Manter apenas a primeira pasta",
            "Mesclar conteúdo das pastas"
        ]
        
        for i, text in enumerate(folder_options):
            radio = WrappedRadioButton(text)
            self.folder_radio_group.addButton(radio.radio, i)
            folder_layout.addWidget(radio)
            if i == 3:  # Seleciona a opção padrão
                radio.setChecked(True)
        
        container_layout.addWidget(folder_frame)
        
        # Informação sobre organização por tipo
        info_frame = ModernFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        info_label.setWordWrap(True)  # Permite quebra de linha
        info_layout.addWidget(info_label)
        
        container_layout.addWidget(info_frame)
        
        main_container.setWidget(container_widget)
        layout.addWidget(main_container)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = SmoothButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMaximumWidth(150)
        
        confirm_btn = SmoothButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setMaximumWidth(150)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class FolderActionDialog(ResponsiveDialog):
    def __init__(self, folder1, folder2):
        super().__init__("Ação para Pastas Duplicadas")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Pastas Idênticas Encontradas")
        title_label.setObjectName("title")
        title_label.setWordWrap(True)  # Permite quebra de linha
        layout.addWidget(title_label)
        
        # Container principal com scroll
        main_container = ScrollableWidget()
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(15)
        
        # Informação das pastas
        paths_frame = ModernFrame()
        paths_layout = QVBoxLayout(paths_frame)
        paths_layout.setContentsMargins(15, 15, 15, 15)
        
        paths_title = QLabel("Pastas encontradas")
        paths_title.setObjectName("subtitle")
        paths_title.setWordWrap(True)  # Permite quebra de linha
        paths_layout.addWidget(paths_title)
        
        path1_label = QLabel(f"1: {folder1}")
        path1_label.setWordWrap(True)  # Permite quebra de linha
        paths_layout.addWidget(path1_label)
        
        path2_label = QLabel(f"2: {folder2}")
        path2_label.setWordWrap(True)  # Permite quebra de linha
        paths_layout.addWidget(path2_label)
        
        container_layout.addWidget(paths_frame)
        
        # Opções
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Escolha uma opção")
        options_title.setObjectName("subtitle")
        options_title.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(options_title)
        
        self.radio_group = QButtonGroup()
        options = [
            "Manter ambas",
            "Manter apenas a primeira",
            "Manter apenas a segunda",
            "Mesclar conteúdo"
        ]
        
        for i, text in enumerate(options):
            radio = WrappedRadioButton(text)
            self.radio_group.addButton(radio.radio, i)
            options_layout.addWidget(radio)
            if i == 0:  # Seleciona a primeira opção por padrão
                radio.setChecked(True)
        
        container_layout.addWidget(options_frame)
        
        main_container.setWidget(container_widget)
        layout.addWidget(main_container)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = SmoothButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMaximumWidth(150)
        
        confirm_btn = SmoothButton("Confirmar")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setMaximumWidth(150)
        
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
        
        # Configurar timer para animações fluidas
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(16)  # ~60 FPS
        
    def setup_tab_organizacao(self):
        # Usar ScrollableWidget para garantir que todo o conteúdo seja visível
        scroll_area = ScrollableWidget()
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Organizador de HD")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)  # Permite quebra de linha
        main_layout.addWidget(title_label)
        
        # Área de seleção do HD
        hd_frame = ModernFrame()
        hd_layout = QVBoxLayout(hd_frame)
        hd_layout.setContentsMargins(15, 15, 15, 15)
        
        hd_title = QLabel("Selecione o HD")
        hd_title.setObjectName("subtitle")
        hd_title.setWordWrap(True)
        hd_layout.addWidget(hd_title)
        
        hd_content = QWidget()
        hd_content_layout = QHBoxLayout(hd_content)
        hd_content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_label = QLabel("Nenhum HD selecionado")
        self.path_label.setWordWrap(True)  # Permite quebra de linha
        self.path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        select_btn = SmoothButton("Selecionar HD")
        select_btn.clicked.connect(self.select_hd)
        select_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        select_btn.setMaximumWidth(150)
        
        hd_content_layout.addWidget(self.path_label, 1)
        hd_content_layout.addWidget(select_btn)
        
        hd_layout.addWidget(hd_content)
        main_layout.addWidget(hd_frame)
        
        # Opções de processamento
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Opções de Processamento")
        options_title.setObjectName("subtitle")
        options_title.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(options_title)
        
        # Checkbox para modo de lote
        self.batch_checkbox = WrappedCheckBox("Processar todos os arquivos de uma vez (modo lote)")
        self.batch_checkbox.toggled.connect(self.toggle_batch_mode)
        options_layout.addWidget(self.batch_checkbox)
        
        # Botão de configurações de lote
        self.batch_settings_btn = SmoothButton("Configurar Processamento em Lote")
        self.batch_settings_btn.clicked.connect(self.show_batch_settings)
        self.batch_settings_btn.setEnabled(False)
        self.batch_settings_btn.setMaximumWidth(300)
        options_layout.addWidget(self.batch_settings_btn)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        info_label.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(info_label)
        
        main_layout.addWidget(options_frame)
        
        # Área de log
        log_frame = ModernFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        log_title = QLabel("Log de Operações")
        log_title.setObjectName("subtitle")
        log_title.setWordWrap(True)  # Permite quebra de linha
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
        progress_title.setWordWrap(True)  # Permite quebra de linha
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_btn = SmoothButton("Iniciar Organização")
        self.start_btn.clicked.connect(self.start_organization)
        self.start_btn.setEnabled(False)
        self.start_btn.setMaximumWidth(200)
        buttons_layout.addWidget(self.start_btn)
        
        main_layout.addLayout(buttons_layout)
        
        scroll_area.setWidget(main_widget)
        
        # Layout principal da aba
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        self.tab_organizacao.setLayout(tab_layout)
        
    def setup_tab_mesclagem(self):
        # Usar ScrollableWidget para garantir que todo o conteúdo seja visível
        scroll_area = ScrollableWidget()
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Mesclar HDs")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)  # Permite quebra de linha
        main_layout.addWidget(title_label)
        
        # Área de seleção dos HDs
        hds_frame = ModernFrame()
        hds_layout = QVBoxLayout(hds_frame)
        hds_layout.setContentsMargins(15, 15, 15, 15)
        hds_layout.setSpacing(10)
        
        hds_title = QLabel("Selecione os HDs")
        hds_title.setObjectName("subtitle")
        hds_title.setWordWrap(True)  # Permite quebra de linha
        hds_layout.addWidget(hds_title)
        
        # HD Destino
        destino_container = QWidget()
        destino_layout = QHBoxLayout(destino_container)
        destino_layout.setContentsMargins(0, 0, 0, 0)
        
        destino_label_title = QLabel("HD Destino:")
        destino_label_title.setWordWrap(True)  # Permite quebra de linha
        destino_label_title.setMinimumWidth(100)
        destino_label_title.setMaximumWidth(100)
        
        self.destino_label = QLabel("Nenhum HD destino selecionado")
        self.destino_label.setWordWrap(True)  # Permite quebra de linha
        self.destino_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        select_destino_btn = SmoothButton("Selecionar")
        select_destino_btn.clicked.connect(self.select_hd_destino)
        select_destino_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        select_destino_btn.setMaximumWidth(150)
        
        destino_layout.addWidget(destino_label_title)
        destino_layout.addWidget(self.destino_label, 1)
        destino_layout.addWidget(select_destino_btn)
        hds_layout.addWidget(destino_container)
        
        # HD Origem
        origem_container = QWidget()
        origem_layout = QHBoxLayout(origem_container)
        origem_layout.setContentsMargins(0, 0, 0, 0)
        
        origem_label_title = QLabel("HD Origem:")
        origem_label_title.setWordWrap(True)  # Permite quebra de linha
        origem_label_title.setMinimumWidth(100)
        origem_label_title.setMaximumWidth(100)
        
        self.origem_label = QLabel("Nenhum HD origem selecionado")
        self.origem_label.setWordWrap(True)  # Permite quebra de linha
        self.origem_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        select_origem_btn = SmoothButton("Selecionar")
        select_origem_btn.clicked.connect(self.select_hd_origem)
        select_origem_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        select_origem_btn.setMaximumWidth(150)
        
        origem_layout.addWidget(origem_label_title)
        origem_layout.addWidget(self.origem_label, 1)
        origem_layout.addWidget(select_origem_btn)
        hds_layout.addWidget(origem_container)
        
        main_layout.addWidget(hds_frame)
        
        # Opções de mesclagem
        options_frame = ModernFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        options_title = QLabel("Opções de Mesclagem")
        options_title.setObjectName("subtitle")
        options_title.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(options_title)
        
        # Checkbox para manter primeiro arquivo
        self.manter_primeiro_checkbox = WrappedCheckBox("Manter primeiro arquivo e mover duplicatas para pasta 'Arquivos Duplicados'")
        self.manter_primeiro_checkbox.setChecked(True)
        self.manter_primeiro_checkbox.toggled.connect(self.toggle_manter_primeiro)
        options_layout.addWidget(self.manter_primeiro_checkbox)
        
        # Informação sobre organização por tipo
        info_label = QLabel("Os arquivos duplicados serão organizados em subpastas por tipo (PDFs, Imagens, etc.)")
        info_label.setObjectName("info")
        info_label.setWordWrap(True)  # Permite quebra de linha
        options_layout.addWidget(info_label)
        
        main_layout.addWidget(options_frame)
        
        # Área de log
        log_frame = ModernFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        log_title = QLabel("Log de Mesclagem")
        log_title.setObjectName("subtitle")
        log_title.setWordWrap(True)  # Permite quebra de linha
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
        progress_title.setWordWrap(True)  # Permite quebra de linha
        progress_layout.addWidget(progress_title)
        
        self.progress_mesclagem = QProgressBar()
        self.progress_mesclagem.setTextVisible(True)
        self.progress_mesclagem.setFormat("%p%")
        progress_layout.addWidget(self.progress_mesclagem)
        
        main_layout.addWidget(progress_frame)
        
        # Botão de início
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.start_mesclar_btn = SmoothButton("Iniciar Mesclagem")
        self.start_mesclar_btn.clicked.connect(self.start_mesclagem)
        self.start_mesclar_btn.setEnabled(False)
        self.start_mesclar_btn.setMaximumWidth(200)
        buttons_layout.addWidget(self.start_mesclar_btn)
        
        main_layout.addLayout(buttons_layout)
        
        scroll_area.setWidget(main_widget)
        
        # Layout principal da aba
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        self.tab_mesclagem.setLayout(tab_layout)
    
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
    
    def resizeEvent(self, event):
        """Ajusta o layout quando a janela é redimensionada"""
        super().resizeEvent(event)
        # Atualizar layout para garantir que todos os elementos se ajustem corretamente

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
