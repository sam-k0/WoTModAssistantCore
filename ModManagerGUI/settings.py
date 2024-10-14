from PySide6 import QtCore, QtWidgets, QtGui

class SettingsTabView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SettingsTabView, self).__init__(parent)
        self.mainlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainlayout)
        self.settings = QtCore.QSettings("WGMods", "ModManager")
        self.settings.beginGroup("Settings")
        self.init_widgets()
        self.load_settings()
    
    def init_widgets(self):
        self.settings_label = QtWidgets.QLabel("Settings")
        self.mainlayout.addWidget(self.settings_label)
        
        self.game_version_label = QtWidgets.QLabel("Game Version:")
        self.mainlayout.addWidget(self.game_version_label)
        self.game_version_combo = QtWidgets.QComboBox()
        self.game_version_combo.addItems(["1.11.1", "1.11.0", "1.10.1", "1.10.0", "1.9.0", "1.8.0", "1.7.1", "1.7.0", "1.6.1", "1.6.0", "1.5.1", "1.5.0", "1.4.1", "1.4.0", "1.3.0", "1.2.0", "1.1.0", "1.0.0", "0.9.0", "0.8.0", "0.7.0", "0.6.0", "0.5.0", "0.4.0", "0.3.0", "0.2.0", "0.1.0"])
        self.mainlayout.addWidget(self.game_version_combo)
        
        self.save_button = QtWidgets.QPushButton("Save")
        self.mainlayout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_settings)
    
    def load_settings(self):
        game_version = self.settings.value("game_version", "1.11.1")
        self.game_version_combo.setCurrentText(game_version)
    
    def save_settings(self):
        self.settings.setValue("game_version", self.game_version_combo.currentText())
        self.settings.sync()
        self.settings.endGroup()
        self.settings.beginGroup("Settings")
        self.settings.sync()
        self.settings.endGroup