from PySide6 import QtCore, QtWidgets, QtGui
import invoker

class SettingsTabView(QtWidgets.QWidget):
    def __init__(self, invoker:invoker.ModManagerCore,parent=None):
        super(SettingsTabView, self).__init__(parent)
        self.invoker_ref = invoker # save ref to invoker
        
        self.mainlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainlayout)
        self.init_widgets() # calls the init_widgets function self

    
    def init_widgets(self):
        self.settings_tab_top_label = QtWidgets.QLabel("Settings", alignment=QtCore.Qt.AlignTop)
        self.detected_game_versions_label = QtWidgets.QLabel("Detected game versions:", alignment=QtCore.Qt.AlignTop)   
        self.detected_game_versions_list = QtWidgets.QComboBox()
        self.detected_game_versions_list.addItem("none") # add a default item
        self.number_installed_mods_label = QtWidgets.QLabel("Number of installed mods: 0")


        self.settings_tab_top_label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.mainlayout.addWidget(self.settings_tab_top_label)
        self.mainlayout.addWidget(self.detected_game_versions_label)
        self.mainlayout.addWidget(self.detected_game_versions_list)
        self.mainlayout.addWidget(self.number_installed_mods_label)