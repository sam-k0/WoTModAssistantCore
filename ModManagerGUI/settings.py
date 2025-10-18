#type:ignore
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser
import sys
import json

import modcore.manager
import modcore.config
from stylesheets import MATERIAL_DARK, MATERIAL_LIGHT

class SettingsTabView(QtWidgets.QWidget):
    def __init__(self, modmanager_ref:modcore.manager.ModManager, app:QtWidgets.QApplication, parent=None):
        super(SettingsTabView, self).__init__(parent)
        self.manager_ref = modmanager_ref # save ref to invoker
        self.app = app # save ref to app
        self.mainlayout = QtWidgets.QVBoxLayout()
        
        self.setLayout(self.mainlayout)
        self.init_widgets() # calls the init_widgets function self
        self.update_get_installed_mods() # calls the update_get_installed_mods function self
        self.update_get_game_versions() # calls the update_get_game_versions function self

    
    def init_widgets(self):
        self.lbl_settings_tab_top = QtWidgets.QLabel("Settings", alignment=QtCore.Qt.AlignCenter)
        self.lbl_settings_tab_top.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.lbl_detected_game_versions = QtWidgets.QLabel("Detected game versions:", alignment=QtCore.Qt.AlignCenter)   
        self.cbb_detected_game_versions = QtWidgets.QComboBox()
        self.cbb_detected_game_versions.addItem("none") # add a default item

        self.lbl_num_installed_mods = QtWidgets.QLabel("Number of installed mods: 0", alignment=QtCore.Qt.AlignLeft)

        self.lbl_installdir = QtWidgets.QLabel("ModAssistantCore directory set to: pythonEmbedded", alignment=QtCore.Qt.AlignLeft)
        # horizontal line
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.lbl_moddir = QtWidgets.QLabel("Managing mods from: unknown", alignment=QtCore.Qt.AlignLeft)
        self.lbl_about = QtWidgets.QLabel("About", alignment=QtCore.Qt.AlignLeft)

        self.btn_github = QtWidgets.QPushButton("View on GitHub")
        self.btn_github.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.btn_open_mod_directory = QtWidgets.QPushButton("Show mod directory")
        self.btn_open_mod_directory.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.btn_extract_dir = QtWidgets.QPushButton("Show cache directory")
        self.btn_extract_dir.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.btn_config_dir = QtWidgets.QPushButton("Show config directory")
        self.btn_config_dir.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.label_theme = QtWidgets.QLabel("Select Theme:", alignment=QtCore.Qt.AlignCenter)

        self.btn_change_theme = QtWidgets.QComboBox()
        self.btn_change_theme.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.btn_change_theme.addItem("Light")
        self.btn_change_theme.addItem("Dark")

        self.lbl_credit = QtWidgets.QLabel("Made with ♥ by sam-k0 and contributors.", alignment=QtCore.Qt.AlignCenter)

        # Shortcut buttons
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_github, alignment=QtCore.Qt.AlignCenter)
        self.hlayout.addWidget(self.btn_open_mod_directory, alignment=QtCore.Qt.AlignCenter)
        self.hlayout.addWidget(self.btn_extract_dir, alignment=QtCore.Qt.AlignCenter)
        self.hlayout.addWidget(self.btn_config_dir, alignment=QtCore.Qt.AlignCenter)
        # Themes
        theme_layout = QtWidgets.QHBoxLayout()
        theme_layout.addWidget(self.label_theme)
        theme_layout.addWidget(self.btn_change_theme)
        theme_widget = QtWidgets.QWidget()
        theme_widget.setLayout(theme_layout)
        self.hlayout.addWidget(theme_widget, alignment=QtCore.Qt.AlignCenter)
        

        self.mainlayout.addWidget(self.lbl_settings_tab_top)
        self.mainlayout.addWidget(self.lbl_detected_game_versions)
        self.mainlayout.addWidget(self.cbb_detected_game_versions)
        self.mainlayout.addWidget(self.line)
        self.mainlayout.addWidget(self.lbl_installdir)
        self.mainlayout.addWidget(self.lbl_moddir)
        self.mainlayout.addWidget(self.lbl_num_installed_mods)
        self.mainlayout.addWidget(self.lbl_about)
        # add shortcuts
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addWidget(self.lbl_credit)

        self.btn_github.clicked.connect(self.on_btn_github_clicked)
        self.btn_open_mod_directory.clicked.connect(self.on_btn_open_moddirectory_clicked)
        self.btn_extract_dir.clicked.connect(self.on_btn_show_extract_dir)
        self.btn_config_dir.clicked.connect(self.on_btn_show_config_dir)
        self.btn_change_theme.currentIndexChanged.connect(self.on_theme_change)

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(self.sizeHint())  # Makes the window non-resizable and just large enough to fit content


    def update_get_installed_mods(self):
        msg, err, ac = self.manager_ref.output_split(self.manager_ref.list_mods())  
        mods = json.loads(msg)
        if err.value != 0:
            self.lbl_num_installed_mods.setText(f"Error code {err} in response: {mods}")
        else:
            self.lbl_num_installed_mods.setText(f"Number of installed mods: <b>{len(mods)}</b>")

    def update_get_game_versions(self):
        msg, err, act =self.manager_ref.output_split( self.manager_ref.get_folders())
        if err.value != 0:
            raise Exception(f"Error code {err} in response: {msg}")
        # the msg is a json list of strings
        versions = json.loads(msg)
        self.cbb_detected_game_versions.clear()
        for version in versions:
            self.cbb_detected_game_versions.addItem(version)
        # set the current index to the newest version
        self.cbb_detected_game_versions.setCurrentIndex(len(versions)-1)
        # update moddir label



        self.lbl_moddir.setText(f"Managing mods from: <b>{self.manager_ref._newest_version_folder()}</b>")
        #TODO: update aobut label
        #msg, err, act = self.manager_ref.parse_response(self.manager_ref.get_about())
        msg = modcore.manager.VERSION
        self.lbl_about.setText("Version: <b>"+msg+"</b>")

    @QtCore.Slot()
    def on_theme_change(self):
        if self.btn_change_theme.currentText() == "Dark":
            self.app.setStyleSheet(MATERIAL_DARK)
        else:
            self.app.setStyleSheet(MATERIAL_LIGHT)

    @QtCore.Slot()
    def on_btn_github_clicked(self):
        # cross platform way to open a browser
        url = "https://github.com/sam-k0/WoTModAssistantCore"
        webbrowser.open(url, 0, True)

    @QtCore.Slot()
    def on_btn_open_moddirectory_clicked(self):
        """ Opens the directory of mods """
        path = "file://"+self.cbb_detected_game_versions.currentText()
        webbrowser.open(path,0, True)

    @QtCore.Slot()
    def on_btn_show_config_dir(self):
        """ Opens the config dir """
        path = "file://"+modcore.config.ConfigIO.get_config_dir()
        webbrowser.open(path, 0, True)
        pass

    @QtCore.Slot()
    def on_btn_show_extract_dir(self):
        """ Opens the directory used to extract mods """
        path = "file://"+modcore.config.ConfigIO.get_extract_folder()
        webbrowser.open(path,0, True)