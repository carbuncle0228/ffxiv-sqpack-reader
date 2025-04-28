import os

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.config import settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 語言設定
        lang_layout = QHBoxLayout()
        lang_label = QLabel("語言：")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(
            [
                "Japanese",
                "English",
                "German",
                "French",
                "ChineseSimplified",
                "ChineseTraditional",
                "Korean",
            ]
        )
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # 遊戲檔案路徑
        folder_layout = QHBoxLayout()
        folder_label = QLabel("遊戲檔案路徑：")
        self.folder_path = QLineEdit()
        folder_browse = QPushButton("瀏覽")
        folder_browse.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(folder_browse)
        layout.addLayout(folder_layout)

        # 匯出目標路徑
        target_layout = QHBoxLayout()
        target_label = QLabel("匯出目標路徑：")
        self.target_path = QLineEdit()
        target_browse = QPushButton("瀏覽")
        target_browse.clicked.connect(self.browse_target)
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(target_browse)
        layout.addLayout(target_layout)

        # 匯出選項
        self.only_str_mode = QCheckBox("僅匯出字串資料")
        self.hex_str_mode = QCheckBox("將 SeString 直接匯出為 hexcode")
        layout.addWidget(self.only_str_mode)
        layout.addWidget(self.hex_str_mode)

        # 按鈕
        button_layout = QHBoxLayout()
        save_button = QPushButton("儲存")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇遊戲檔案資料夾")
        if folder:
            self.folder_path.setText(folder)

    def browse_target(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇匯出目標資料夾")
        if folder:
            self.target_path.setText(folder)

    def load_settings(self):
        self.lang_combo.setCurrentText(settings.language)
        self.folder_path.setText(settings.folder_path)
        self.target_path.setText(settings.target_path)
        self.only_str_mode.setChecked(settings.ONLY_STR_MODE)
        self.hex_str_mode.setChecked(settings.HEX_STR_MODE)

    def save_settings(self):
        # 更新設定
        settings.language = self.lang_combo.currentText()
        settings.folder_path = self.folder_path.text()
        settings.target_path = self.target_path.text()
        settings.ONLY_STR_MODE = self.only_str_mode.isChecked()
        settings.HEX_STR_MODE = self.hex_str_mode.isChecked()

        # 儲存到 .env 檔案
        env_path = os.path.join("config", ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"language={settings.language}\n")
            f.write(f"folder_path={settings.folder_path}\n")
            f.write(f"target_path={settings.target_path}\n")
            f.write(f"ONLY_STR_MODE={str(settings.ONLY_STR_MODE).lower()}\n")
            f.write(f"HEX_STR_MODE={str(settings.HEX_STR_MODE).lower()}\n")

        self.accept()
