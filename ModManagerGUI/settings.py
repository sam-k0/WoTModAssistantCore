from PySide6 import QtCore, QtWidgets, QtGui
import invoker
import webbrowser


class SettingsTabView(QtWidgets.QWidget):
    def __init__(self, invoker:invoker.ModManagerCore,parent=None):
        super(SettingsTabView, self).__init__(parent)
        self.invoker_ref = invoker # save ref to invoker
        
        self.mainlayout = QtWidgets.QVBoxLayout()
        
        self.setLayout(self.mainlayout)
        self.init_widgets() # calls the init_widgets function self
        self.update_get_installed_mods() # calls the update_get_installed_mods function self
        self.update_get_game_versions() # calls the update_get_game_versions function self

    
    def init_widgets(self):
        self.lbl_settings_tab_top = QtWidgets.QLabel("Settings", alignment=QtCore.Qt.AlignCenter)
        self.lbl_detected_game_versions = QtWidgets.QLabel("Detected game versions:", alignment=QtCore.Qt.AlignCenter)   
        self.cbb_detected_game_versions = QtWidgets.QComboBox()
        self.cbb_detected_game_versions.addItem("none") # add a default item
        self.lbl_num_installed_mods = QtWidgets.QLabel("Number of installed mods: 0", alignment=QtCore.Qt.AlignCenter)

        self.lbl_installdir = QtWidgets.QLabel("ModAssistantCore directory set to: "+self.invoker_ref.installation_path, alignment=QtCore.Qt.AlignCenter)
        self.lbl_moddir = QtWidgets.QLabel("Managing mods from: unknown", alignment=QtCore.Qt.AlignCenter)
        self.lbl_about = QtWidgets.QLabel("About", alignment=QtCore.Qt.AlignCenter)
        self.btn_github = QtWidgets.QPushButton("View on GitHub")


        self.lbl_settings_tab_top.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.mainlayout.addWidget(self.lbl_settings_tab_top)
        self.mainlayout.addWidget(self.lbl_detected_game_versions)
        self.mainlayout.addWidget(self.cbb_detected_game_versions)
        self.mainlayout.addWidget(self.lbl_installdir)
        self.mainlayout.addWidget(self.lbl_moddir)
        self.mainlayout.addWidget(self.lbl_num_installed_mods)
        self.mainlayout.addWidget(self.lbl_about)
        self.mainlayout.addWidget(self.btn_github)

        self.btn_github.clicked.connect(self.on_btn_github_clicked)

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(self.sizeHint())  # Makes the window non-resizable and just large enough to fit content


    def update_get_installed_mods(self):
        mods, err, ac = self.invoker_ref.get_mods_list()
        if err != 0:
            self.lbl_num_installed_mods.setText(f"Error code {err} in response: {mods}")
        else:
            self.lbl_num_installed_mods.setText(f"Number of installed mods: <b>{len(mods)}</b>")

    def update_get_game_versions(self):
        versions = self.invoker_ref.get_all_mod_folders()
        self.cbb_detected_game_versions.clear()
        for version in versions:
            self.cbb_detected_game_versions.addItem(version)
        # set the current index to the newest version
        self.cbb_detected_game_versions.setCurrentIndex(len(versions)-1)
        # update moddir label
        self.lbl_moddir.setText(f"Managing mods from: <b>{self.invoker_ref.get_newest_mod_folder()}</b>")
        # update aobut label
        msg, err, act = self.invoker_ref.parse_response(self.invoker_ref.get_about())
        self.lbl_about.setText("Version: <b>"+msg+"</b>")

    @QtCore.Slot()
    def on_btn_github_clicked(self):
        # cross platform way to open a browser
        url = "https://github.com/sam-k0/WoTModAssistantCore"
        webbrowser.open(url, 0, True)