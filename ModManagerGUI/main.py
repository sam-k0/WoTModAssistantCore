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

        self.lbl_installdir = QtWidgets.QLabel("Install directory set to "+self.myinvoker.installation_path, alignment=QtCore.Qt.AlignTop)
        # make font smaller for the install directory label
        font.setPointSize(8)
        self.lbl_installdir.setFont(font)

        self.lbl_details = QtWidgets.QLabel("Details", alignment=QtCore.Qt.AlignCenter)
        self.lbl_description = QtWidgets.QLabel("Description", alignment=QtCore.Qt.AlignCenter, wordWrap=True)

        self.mod_list_view = QtWidgets.QListView(self)
        self.mod_model = QtGui.QStandardItemModel(self.mod_list_view)

        self.mod_list_view.setModel(self.mod_model)

        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        self.btn_install = QtWidgets.QPushButton("Install mod")

        # Set up layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.lbl_installdir)
        self.layout.addWidget(self.lbl_installed)
        self.layout.addWidget(self.mod_list_view)
        self.layout.addWidget(self.lbl_details)
        self.layout.addWidget(self.lbl_description)
        # horizontal spacer
        self.layout.addStretch()

        self.layout.addWidget(self.btn_refresh)
        # 2 buttons in a horizontal layout
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_toggle)
        self.hlayout.addWidget(self.btn_install)
        self.layout.addLayout(self.hlayout)

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
        secondary = ModInfoWindow(mod)
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
        

    def show_error(self, message:str, title:str):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error: "+message)
        msg.setWindowTitle(title)
        msg.exec()


class ModInfoWindow(QtWidgets.QDialog):
    def __init__(self, mod:invoker.Mod):
        super().__init__()

        self.mod = mod
        self.setWindowTitle("Mod Info")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.lbl_name = QtWidgets.QLabel(mod.name)
        self.lbl_version = QtWidgets.QLabel("Version: "+mod.version)
        self.lbl_pckid = QtWidgets.QLabel("Package ID: "+mod.pckid)
        self.lbl_wgid = QtWidgets.QLabel("wgmods ID: "+mod.wgid)
        self.lbl_desc = QtWidgets.QLabel(mod.desc, wordWrap=True)
        # buttons for uninstalling and toggling
        self.btn_uninstall = QtWidgets.QPushButton("Uninstall")
        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        

        self.layout.addWidget(self.lbl_name)
        self.layout.addWidget(self.lbl_version)
        self.layout.addWidget(self.lbl_wgid)
        self.layout.addWidget(self.lbl_pckid)
        self.layout.addWidget(self.lbl_desc)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_uninstall)
        self.hlayout.addWidget(self.btn_toggle)
        self.layout.addLayout(self.hlayout)
        self.setLayout(self.layout)

        # connect magic
        self.btn_uninstall.clicked.connect(self.uninstall_mod)

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
            self.close()

        pass

    @QtCore.Slot()
    def toggle_mod(self):
        pass

    

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(400, 300)
    widget.show()

    sys.exit(app.exec_())
    