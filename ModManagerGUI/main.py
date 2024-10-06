import sys 
from PySide6 import QtCore, QtWidgets, QtGui
import os
import invoker

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.myinvoker = invoker.ModManagerCore()

        self.setWindowTitle("Mod Manager")
        # Create widgets
        self.lbl_installed = QtWidgets.QLabel("Installed", alignment=QtCore.Qt.AlignCenter )
        # make the text bold
        font = self.lbl_installed.font()
        font.setBold(True)
        self.lbl_installed.setFont(font)
        # labels for settings
        self.lbl_settings_top = QtWidgets.QLabel("Settings", alignment=QtCore.Qt.AlignCenter)
        self.lbl_installdir = QtWidgets.QLabel("ModAssistantCore directory set to: "+self.myinvoker.installation_path, alignment=QtCore.Qt.AlignTop)
        self.lbl_moddir = QtWidgets.QLabel("Managing mods from: unknown", alignment=QtCore.Qt.AlignTop)
        # make font smaller for the install directory label
        font.setPointSize(8)
        self.lbl_installdir.setFont(font)
        self.lbl_moddir.setFont(font)

        self.lbl_details = QtWidgets.QLabel("Details", alignment=QtCore.Qt.AlignCenter)
        self.lbl_description = QtWidgets.QLabel("Description", alignment=QtCore.Qt.AlignCenter, wordWrap=True)
        # Action log will display the output of the last action / debug information
        self.lbl_action_log = QtWidgets.QLabel("Action log", alignment=QtCore.Qt.AlignCenter)
        self.lbl_action_log.setWordWrap(True)


        # List view for mods
        self.mod_list_view = QtWidgets.QListView(self)
        self.mod_model = QtGui.QStandardItemModel(self.mod_list_view)

        self.mod_list_view.setModel(self.mod_model)

        self.btn_refresh = QtWidgets.QPushButton("Refresh mods")
        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        self.btn_install = QtWidgets.QPushButton("Install mod")
        self.btn_moveall = QtWidgets.QPushButton("Import mods from older game version")
        self.btn_disableall = QtWidgets.QPushButton("Disable all mods")
        self.btn_enableall = QtWidgets.QPushButton("Enable all mods")
        # set button icons
        self.btn_disableall.setIcon(QtGui.QIcon.fromTheme("edit-delete"))
        self.btn_enableall.setIcon(QtGui.QIcon.fromTheme("emblem-default"))
        self.btn_refresh.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.btn_toggle.setIcon(QtGui.QIcon.fromTheme("object-flip-horizontal"))
        self.btn_install.setIcon(QtGui.QIcon.fromTheme("list-add"))
        self.btn_moveall.setIcon(QtGui.QIcon.fromTheme("go-next"))


        # Set up layout
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.addWidget(self.lbl_settings_top)
        self.mainlayout.addWidget(self.lbl_installdir)
        self.mainlayout.addWidget(self.lbl_moddir)
        # set a vertical spacing line between the labels and the list view
        self.mainlayout.addSpacing(10)

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
        # 2 buttons in a horizontal layout
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_enableall)
        self.hlayout.addWidget(self.btn_disableall)
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addWidget(self.btn_moveall)
        self.mainlayout.addWidget(self.lbl_action_log)

        # Connect button click to magic function
        self.btn_refresh.clicked.connect(self.reload_mods_gui)
        self.btn_install.clicked.connect(self.install_mod)
        self.btn_toggle.clicked.connect(self.toggle_mod)
        self.btn_disableall.clicked.connect(self.disable_all)
        self.btn_enableall.clicked.connect(self.enable_all)
        self.btn_moveall.clicked.connect(self.move_all_mods)
        # Connect the list view selection signal to a function to display mod details
        self.mod_list_view.selectionModel().currentChanged.connect(self.display_mod_details)
        # Connect right-click to show mod details
        self.mod_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mod_list_view.customContextMenuRequested.connect(self.show_mod_details_window)

        # Make sure the Core is configured correctly
        if not self.myinvoker.get_game_installation_dir():
            self.show_error("It appears you are running this for the first time. Please select the game directory.", "First time setup", QtWidgets.QMessageBox.Information)
            self.setup_game_directory()

        # Update the game mod folder label
        self.lbl_moddir.setText("Managing mods from: "+self.myinvoker.get_newest_mod_folder())
        # Populate the mod list
        self.reload_mods()
    
    def update_action_log(self, message:str, errcode:int=0,actioncode:int=-99):
        # only include error and action code if they are not the default
        errmessage = f"Error! Errcode: {errcode}\n" if errcode != 0 else "Success: " # default error code is 0
        actionmessage = f"Action code: {actioncode}" if actioncode != -99 else ""
        self.lbl_action_log.setText(f"{errmessage} {message} ({actionmessage})")

    @QtCore.Slot() # The actual function that will be called when the refresh button is clicked
    def reload_mods_gui(self):
        self.reload_mods(updateLog=True)

    # When having to reload the mods list internally, 
    # use this function to avoid updating the action log and possibly overwriting an error message
    def reload_mods(self, updateLog:bool=False):
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

            if updateLog:
                self.update_action_log("Successfully refreshed mods", err, action)
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
                out = self.myinvoker.install_mod(filename)
                resp, err, act = self.myinvoker.parse_response(out)
                self.update_action_log(resp, err, act)
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
        out = self.myinvoker.toggle_mod(mod.pckid)
        resp, err, act = self.myinvoker.parse_response(out)
        self.update_action_log(resp, err, act)
        # refresh the mod list
        self.reload_mods()
        
    @QtCore.Slot()
    def disable_all(self):
        out = self.myinvoker.set_all_mods(False)
        resp, err, act = self.myinvoker.parse_response(out)
        self.update_action_log(resp, err, act)
        self.reload_mods()
    
    @QtCore.Slot()
    def enable_all(self):
        out = self.myinvoker.set_all_mods(True)
        resp, err, act = self.myinvoker.parse_response(out)
        self.update_action_log(resp, err, act)
        self.reload_mods()

    @QtCore.Slot()
    def move_all_mods(self):
        # show confirmation dialog
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("This will import all mods from your previous game version to the current one.\nAre you sure you want to do this?")
        msg.setWindowTitle("Move all mods")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        ret = msg.exec()

        if ret == QtWidgets.QMessageBox.Yes:
            response_output = self.myinvoker.move_mods("all")
            # handle response jsonself.lbl_moddir.setText("Managing mods from: "+self.myinvoker.get_mod_folders("newest"))
            response, err, act = self.myinvoker.parse_response(response_output)
            self.update_action_log(response, err, act)
            # Show error if there was an error
            if err != 0:
                # get all detected mod folders
                mod_folders = self.myinvoker.get_all_mod_folders()

                self.show_error(f"Could not move mods as you only have one mod folder.\nDetected mod folders ({len(mod_folders)}):\n"+str(mod_folders), "Error: Could not move mods")

        self.reload_mods()

    def setup_game_directory(self):
        # open file dialog
        while True: # do not let the user escape without selecting a valid game directory
            foldername = QtWidgets.QFileDialog.getExistingDirectory(self, "Select game directory")
            if foldername:
                # check if it contains the WorldOfTanks.exe
                if not "WorldOfTanks.exe" in os.listdir(foldername):
                    self.show_error("This directory does not contain WorldOfTanks.exe", "Error: Invalid game directory")
                else:
                    break
            else:
                self.show_error("No directory selected, please select the game directory.", "Error: No directory selected")
        
        # set the game directory
        self.myinvoker.set_game_installation_dir(foldername)


    def show_error(self, message:str, title:str, icon=QtWidgets.QMessageBox.Critical):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText("Error: "+message)
        msg.setWindowTitle(title)
        msg.exec()


class ModInfoWindow(QtWidgets.QDialog):
    def __init__(self, mod:invoker.Mod, parent_window):
        super().__init__()

        self.mod:invoker.Mod = mod
        self.myinvoker:invoker.ModManagerCore = parent_window.myinvoker
        self.parent_window:MainWindow = parent_window

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

        if ret == QtWidgets.QMessageBox.Yes:
            print("Uninstalling mod: ", self.mod.pckid)
            resp = self.myinvoker.uninstall_mod(self.mod.pckid)
            msg, err, act = self.myinvoker.parse_response(resp)
            self.parent_window.update_action_log(msg, err, act)

            self.close()
        pass

    @QtCore.Slot()
    def toggle_mod(self):
        out = self.myinvoker.toggle_mod(self.mod.pckid)
        resp, err, act = self.myinvoker.parse_response(out)
        self.parent_window.update_action_log(resp, err, act)
        self.parent_window.reload_mods()


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
    widget.resize(400, 500)
    widget.show()

    sys.exit(app.exec())
    