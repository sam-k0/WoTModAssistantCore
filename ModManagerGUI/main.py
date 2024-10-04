import sys 
from PySide6 import QtCore, QtWidgets, QtGui
import invoker

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.myinvoker = invoker.ModManagerCore()
        self.mods = []

        self.setWindowTitle("Mod Manager")

        # Create widgets
        self.btn_refresh = QtWidgets.QPushButton("Refresh mods")
        self.lbl_installed = QtWidgets.QLabel("Installed", alignment=QtCore.Qt.AlignCenter )
        # make the text bold
        font = self.lbl_installed.font()
        font.setBold(True)
        self.lbl_installed.setFont(font)

        self.lbl_installdir = QtWidgets.QLabel("ModAssistantCore directory set to: "+self.myinvoker.installation_path, alignment=QtCore.Qt.AlignTop)
        # TODO: Make this actually reflect the games mod directory
        self.lbl_moddir = QtWidgets.QLabel("Managing mods from: "+"C:\\Games\\WoT\\mods\\1.26.0.2", alignment=QtCore.Qt.AlignTop)
        # make font smaller for the install directory label
        font.setPointSize(8)
        self.lbl_installdir.setFont(font)
        self.lbl_moddir.setFont(font)

        self.lbl_details = QtWidgets.QLabel("Details", alignment=QtCore.Qt.AlignCenter)
        self.lbl_description = QtWidgets.QLabel("Description", alignment=QtCore.Qt.AlignCenter, wordWrap=True)

        self.mod_list_view = QtWidgets.QListView(self)
        self.mod_model = QtGui.QStandardItemModel(self.mod_list_view)

        self.mod_list_view.setModel(self.mod_model)

        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        self.btn_install = QtWidgets.QPushButton("Install mod")
        self.btn_moveall = QtWidgets.QPushButton("Import mods from older game version")

        # Set up layout
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.addWidget(self.lbl_installdir)
        self.mainlayout.addWidget(self.lbl_moddir)
        self.mainlayout.addWidget(self.lbl_installed)
        self.mainlayout.addWidget(self.mod_list_view)
        self.mainlayout.addWidget(self.lbl_details)
        self.mainlayout.addWidget(self.lbl_description)
        # horizontal spacer
        self.mainlayout.addStretch()

        self.mainlayout.addWidget(self.btn_refresh)
        # 2 buttons in a horizontal layout
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_toggle)
        self.hlayout.addWidget(self.btn_install)
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addWidget(self.btn_moveall)

        # Connect button click to magic function
        self.btn_refresh.clicked.connect(self.reload_mods)
        self.btn_install.clicked.connect(self.install_mod)
        self.btn_toggle.clicked.connect(self.toggle_mod)
        # Connect the list view selection signal to a function to display mod details
        self.mod_list_view.selectionModel().currentChanged.connect(self.display_mod_details)
        # Connect right-click to show mod details
        self.mod_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mod_list_view.customContextMenuRequested.connect(self.show_mod_details_window)
    
    @QtCore.Slot()
    def reload_mods(self):
        try:
            mods, err, action = self.myinvoker.get_mods_list()
            # reset model
            self.mod_model.clear()
            # populate model with mod items
            for mod in mods:   
                active = "Active" if mod.isenabled else "Inactive"
                item = QtGui.QStandardItem(mod.name + " (v" + mod.version + ")" + " - " + active)
                item.setData(mod, QtCore.Qt.UserRole)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.mod_model.appendRow(item)
        except Exception as e:
            # Show qt popup message box
            self.show_error("Could not refresh mods: "+str(e), "Error: Could not refresh mods")

            # Set some dummy mods
            self.mod_model.clear()
            mods = [invoker.Mod("Dummy Mod","wgi231", "com.dummy.mod", "1.0", "This is a dummy mod", "dummy.wotmod", True)]
            for mod in mods:
                active = "Active" if mod.isenabled else "Inactive"
                item = QtGui.QStandardItem(mod.name + " (v" + mod.version + ")" + " - " + active)
                item.setData(mod, QtCore.Qt.UserRole)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.mod_model.appendRow(item)

    @QtCore.Slot()
    def install_mod(self):
        # open file dialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select mod file")
        if filename:
            try:
                self.myinvoker.install_mod(filename)
                self.reload_mods()
            except Exception as e:
                self.show_error("Could not install mod: "+str(e), "Error: Could not install mod")
        else:
            self.show_error("No file selected", "Error: No file selected")
    # show mod details when a mod is selected
    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def display_mod_details(self, index):
        # check if the index is valid
        if not index.isValid():
            return

        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        self.lbl_details.setText(f"{mod.name} (v{mod.version}) - {mod.pckid}")
        self.lbl_description.setText(mod.desc)

    # Handler for right-clicking a mod
    @QtCore.Slot(QtCore.QPoint)
    def show_mod_details_window(self, index):
        index = self.mod_list_view.indexAt(index)
        if not index.isValid():
            return

        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        secondary = ModInfoWindow(mod, self)
        secondary.exec()
        # Reload mods in case the mod was toggled or changed
        self.reload_mods()

    @QtCore.Slot()
    def toggle_mod(self):
        index = self.mod_list_view.currentIndex()
        if not index.isValid():
            print("No mod selected")
            return

        #toggle
        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        print("Toggling mod: ", mod.name)

        # refresh the mod list
        self.reload_mods()
        
    #TODO: Implement this
    @QtCore.Slot()
    def move_mods(self, keyword:str):
        response_output = self.myinvoker.move_mods(keyword)
        # handle response
        self.show_error("Not implemented", "Error: Not implemented")

    def show_error(self, message:str, title:str):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error: "+message)
        msg.setWindowTitle(title)
        msg.exec()


class ModInfoWindow(QtWidgets.QDialog):
    def __init__(self, mod:invoker.Mod, parent_window):
        super().__init__()

        self.mod = mod
        self.myinvoker:invoker.ModManagerCore = parent_window.myinvoker
        self.setWindowTitle("Mod Info")
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.lbl_name = QtWidgets.QLabel(mod.name)
        self.lbl_version = QtWidgets.QLabel("Version: "+mod.version)
        self.lbl_pckid = QtWidgets.QLabel("Package ID: "+mod.pckid)
        self.lbl_wgid = QtWidgets.QLabel("wgmods ID: "+mod.wgid)
        self.lbl_desc = QtWidgets.QLabel(mod.desc, wordWrap=True)
        # buttons for uninstalling and toggling
        self.btn_uninstall = QtWidgets.QPushButton("Uninstall")
        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        self.btn_wgmods = QtWidgets.QPushButton("Show on wgmods.net")
        

        self.mainlayout.addWidget(self.lbl_name)
        self.mainlayout.addWidget(self.lbl_version)
        self.mainlayout.addWidget(self.lbl_wgid)
        self.mainlayout.addWidget(self.lbl_pckid)
        self.mainlayout.addWidget(self.lbl_desc)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_uninstall)
        self.hlayout.addWidget(self.btn_toggle)
        self.mainlayout.addLayout(self.hlayout)
        self.setLayout(self.mainlayout)
        self.mainlayout.addWidget(self.btn_wgmods)

        # connect magic
        self.btn_uninstall.clicked.connect(self.uninstall_mod)
        self.btn_toggle.clicked.connect(self.toggle_mod)
        self.btn_wgmods.clicked.connect(self.show_wgmods) 

    @QtCore.Slot()
    def uninstall_mod(self):
        # show confirmation dialog
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("Are you sure you want to uninstall this mod?")
        msg.setWindowTitle("Uninstall "+self.mod.pckid)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        ret = msg.exec()
        print(ret)

        if ret == QtWidgets.QMessageBox.Yes:
            # destroy the parent window
            # uninstall the mod
            try:
                print("Uninstalling mod: ", self.mod.pckid)
                self.myinvoker.uninstall_mod(self.mod.pckid)
            except Exception as e:
                print("Could not uninstall mod: ", e)

            self.close()
        pass

    #TODO: Implement this
    @QtCore.Slot()
    def toggle_mod(self):
        pass

    @QtCore.Slot()
    def show_wgmods(self):
        if self.mod.wgid != "unknown":
            QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://wgmods.net/"+self.mod.wgid))
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("This mod is not available on wgmods.net.\nThis may occur if you installed the mod manually.")
            msg.setWindowTitle("Mod not available")
            msg.exec()

    

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(400, 300)
    widget.show()

    sys.exit(app.exec_())
    