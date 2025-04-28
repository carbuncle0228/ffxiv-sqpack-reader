import logging
import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import settings
from app.excel import exd_handler
from app.sqpack import SQPack
from app.ui.settings_dialog import SettingsDialog


class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()

        self.sqpack = SQPack(settings.folder_path)
        self.target_folder = os.path.join(
            os.path.normpath(os.path.expanduser(settings.target_path)),
            self.sqpack.game_version,
        )
        os.makedirs(self.target_folder, exist_ok=True)

    def run(self):
        try:
            total_files = len(self.sqpack.files)
            for i, file_path in enumerate(self.sqpack.files.keys()):
                try:
                    exd_handler.write_csv(
                        sqpack=self.sqpack,
                        target_folder=self.target_folder,
                        file_path=file_path,
                    )
                    self.progress.emit(int((i + 1) / total_files * 100))
                except Exception as e:
                    logging.error(f"處理 {file_path} 失敗")
                    logging.error(e, exc_info=True)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFXIV Patcher")
        self.setup_ui()
        self.worker = None

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog()
        settings_dialog.exec()  # Open dialog in modal mode

    def setup_ui(self):
        # 建立選單
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("設定")
        settings_action = QAction("Open Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(settings_action)

        # 主視窗內容
        central_widget = QWidget()
        layout = QVBoxLayout()

        # 狀態標籤
        self.status_label = QLabel("準備就緒")
        layout.addWidget(self.status_label)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # 按鈕
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("開始匯出")
        self.start_button.clicked.connect(self.start_export)
        button_layout.addWidget(self.start_button)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 狀態列
        self.statusBar().showMessage("準備就緒")

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def start_export(self):
        self.start_button.setEnabled(False)
        self.status_label.setText("正在匯出...")
        self.progress_bar.setValue(0)

        # 建立工作執行緒

        self.worker = WorkerThread()
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.export_finished)
        self.worker.error.connect(self.export_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def export_finished(self):
        self.start_button.setEnabled(True)
        self.status_label.setText("匯出完成")
        self.statusBar().showMessage("匯出完成")

    def export_error(self, error_msg):
        self.start_button.setEnabled(True)
        self.status_label.setText(f"匯出失敗: {error_msg}")
        self.statusBar().showMessage(f"匯出失敗: {error_msg}")
