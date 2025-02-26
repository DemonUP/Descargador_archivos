import os
# Asegúrate de que la ruta a VLC esté en el PATH para que python-vlc encuentre libvlc.dll
os.environ['PATH'] += r';D:\Descargador_archivos\VLC'

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox,
    QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
import yt_dlp
import vlc

class InfernalDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargador Infernal")
        self.setGeometry(100, 100, 1100, 800)
        self.video_file = None
        self.video_info = None
        self.available_formats = None

        # Widget principal y layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Título principal
        title_label = QLabel("Descargador Infernal")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #B22222;")
        self.main_layout.addWidget(title_label)

        # Grupo de opciones (ingreso de URL y botones)
        input_group = QGroupBox("Opciones de Video")
        input_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #B22222;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #FF6666;
                font-size: 18px;
            }
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        # URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ingresa la URL de YouTube...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        input_layout.addLayout(url_layout)

        # Botones de acciones
        button_layout = QHBoxLayout()
        self.get_options_button = QPushButton("Obtener Opciones")
        self.get_options_button.clicked.connect(self.get_video_info)
        button_layout.addWidget(self.get_options_button)
        self.download_button = QPushButton("Descargar Seleccionado")
        self.download_button.clicked.connect(self.download_selected_format)
        button_layout.addWidget(self.download_button)
        self.stream_button = QPushButton("Ver Online (Streaming)")
        self.stream_button.clicked.connect(self.stream_video)
        button_layout.addWidget(self.stream_button)
        input_layout.addLayout(button_layout)

        # Selección de formato
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        self.format_combo = QComboBox()
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        input_layout.addLayout(format_layout)

        self.main_layout.addWidget(input_group)

        # Grupo de reproducción
        video_group = QGroupBox("Reproducción")
        video_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #B22222;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #FF6666;
                font-size: 18px;
            }
        """)
        video_layout = QVBoxLayout(video_group)
        self.video_frame = QFrame()
        self.video_frame.setMinimumHeight(400)
        video_layout.addWidget(self.video_frame)
        self.play_button = QPushButton("Reproducir Video Descargado")
        self.play_button.clicked.connect(self.play_video)
        video_layout.addWidget(self.play_button)
        self.main_layout.addWidget(video_group)

        # Inicializar VLC
        self.vlc_instance = vlc.Instance('--plugin-path=C:\\Program Files\\VideoLAN\\VLC\\plugins')
        self.mediaplayer = self.vlc_instance.media_player_new()

        # Estilo global "infernal"
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a0000, stop:1 #000000);
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QLineEdit, QComboBox {
                background-color: #2c2c2c;
                color: #FFFFFF;
                border: 2px solid #B22222;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #B22222;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff3333;
            }
            QGroupBox {
                background-color: transparent;
            }
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #B22222;
                border-radius: 8px;
            }
        """)

    def get_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Debes ingresar una URL.")
            return

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener información del video:\n{str(e)}")
            return

        formats = self.video_info.get('formats', [])
        self.available_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
        if not self.available_formats:
            QMessageBox.warning(self, "Error", "No se encontraron formatos adecuados.")
            return

        self.format_combo.clear()
        for f in self.available_formats:
            filesize = f.get('filesize') or 0
            filesize_mb = f"{round(filesize / (1024*1024), 2)} MB" if filesize else "Desconocido"
            text = f"ID: {f.get('format_id')} - {f.get('resolution', 'N/A')} - {f.get('ext')} - {filesize_mb}"
            self.format_combo.addItem(text)
        QMessageBox.information(self, "Formatos Encontrados", "Selecciona un formato infernal para continuar.")

    def download_selected_format(self):
        idx = self.format_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_formats):
            QMessageBox.warning(self, "Error", "Selecciona un formato.")
            return
        format_id = self.available_formats[idx].get('format_id')
        url = self.url_input.text().strip()
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Video", "", "MP4 Files (*.mp4)")
        if not save_path:
            return

        ydl_opts = {
            'quiet': True,
            'format': format_id,
            'outtmpl': save_path,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.video_file = save_path
            QMessageBox.information(self, "Descarga Completa", f"Video descargado en:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al descargar el video:\n{str(e)}")

    def play_video(self):
        if not self.video_file or not os.path.exists(self.video_file):
            QMessageBox.warning(self, "Error", "Primero descarga un video para reproducirlo.")
            return

        media = self.vlc_instance.media_new(self.video_file)
        self.mediaplayer.set_media(media)
        if sys.platform.startswith('win'):
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        elif sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(self.video_frame.winId())
        elif sys.platform.startswith('darwin'):
            self.mediaplayer.set_nsobject(int(self.video_frame.winId()))
        self.mediaplayer.play()

    def stream_video(self):
        idx = self.format_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_formats):
            QMessageBox.warning(self, "Error", "Selecciona un formato para streaming.")
            return
        stream_url = self.available_formats[idx].get('url')
        if not stream_url:
            QMessageBox.warning(self, "Error", "No se encontró URL para streaming.")
            return
        media = self.vlc_instance.media_new(stream_url)
        self.mediaplayer.set_media(media)
        if sys.platform.startswith('win'):
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        elif sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(self.video_frame.winId())
        elif sys.platform.startswith('darwin'):
            self.mediaplayer.set_nsobject(int(self.video_frame.winId()))
        self.mediaplayer.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InfernalDownloader()
    window.show()
    sys.exit(app.exec_())
