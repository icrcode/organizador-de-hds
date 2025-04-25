import PyInstaller.__main__
import os
import sys
from PyQt6 import QtCore

# Obtém o caminho do Qt
qt_path = os.path.dirname(QtCore.__file__)

PyInstaller.__main__.run([
    'organizador_hd_gui.py',
    '--onefile',
    '--windowed',
    '--name=Organizador_de_HD',
    '--icon=organizador_hd_gui.ico',
    '--path=' + qt_path,
    '--hidden-import=PyQt6.sip',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--collect-all=PyQt6',
    '--clean'
])
