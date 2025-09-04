#type: ignore
from PySide6 import QtCore, QtWidgets, QtGui
import os
import sys
import invoker
import settings as settingstab
import wgmodbrowser as wgb
from pathlib import Path
from stylesheets import MATERIAL_DARK, MATERIAL_LIGHT

app = None

class ModsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, mods:list, parent=None):
        super(ModsTableModel, self).__init__(parent)
        self.mods = mods
        self.header_labels = ["Name", "Mod Version", "Enabled"]

    def rowCount(self, parent):
        return len(self.mods)

    def columnCount(self, parent):
        return len(self.header_labels)

    def data(self, index, role):
        if not index.isValid():
            return None
        mod:invoker.Mod = self.mods[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return mod.name
            elif index.column() == 1:
                return mod.version
            elif index.column() == 2:
                return "Yes" if mod.isenabled else "No"
        elif role == QtCore.Qt.UserRole:
            return mod
        return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_labels[section]
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if column == 0:
            self.mods.sort(key=lambda x: x.name)
        elif column == 1:
            self.mods.sort(key=lambda x: x.version)
        elif column == 2:
            self.mods.sort(key=lambda x: x.isenabled)
        if order == QtCore.Qt.DescendingOrder:
            self.mods.reverse()
        self.layoutChanged.emit()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.myinvoker = invoker.ModManagerCore()
        # check if the Core is in the expected location
        if not os.path.exists(self.myinvoker.installation_path):
            self.show_error("Could not find the ModManagerCore executable at "+self.myinvoker.installation_path, "Error: Core not found")
            sys.exit(1)
                # Setup check
        if not self.myinvoker.get_game_installation_dir():
            self.show_error("It appears you are running this for the first time. Please select the game directory.", "First time setup", QtWidgets.QMessageBox.Information)
            self.setup_game_dir()
            self.show_error("Information: You can select a theme in the Settings tab. The default theme is Light.", "Info: Theme selection", QtWidgets.QMessageBox.Information)
        else:
            print("Game directory already set to: ", self.myinvoker.get_game_installation_dir())

        self.setWindowTitle("WoT Mod Manager GUI")

        # Tabs
        self.tabs = QtWidgets.QTabWidget(self)
        self.main_tab = QtWidgets.QWidget()
        self.mainlayout = QtWidgets.QVBoxLayout(self.main_tab)

        #region Main Tab widgets
        self.lbl_installed = QtWidgets.QLabel("Installed", alignment=QtCore.Qt.AlignCenter)
        self.lbl_installed.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))

        self.lbl_details = QtWidgets.QLabel("Details", alignment=QtCore.Qt.AlignCenter)
        self.lbl_description = QtWidgets.QLabel("Description", alignment=QtCore.Qt.AlignCenter, wordWrap=True)
        self.lbl_action_log = QtWidgets.QLabel("Action log", alignment=QtCore.Qt.AlignCenter)
        self.lbl_action_log.setWordWrap(True)

        # Mod table view
        self.mod_table_view = QtWidgets.QTableView(self)
        self.mod_table_view.setModel(ModsTableModel([]))
        self.mod_table_view.setSortingEnabled(True)
        self.mod_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.mod_table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.mod_table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.mod_table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.mod_table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.mod_table_view.setShowGrid(True)
        self.mod_table_view.setAlternatingRowColors(False)
        self.mod_table_view.setSortingEnabled(True)
        self.mod_table_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.mod_table_view.resizeColumnsToContents()
        self.mod_table_view.resizeRowsToContents()
        self.mod_table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.mod_table_view.setWordWrap(True)
        self.mod_table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.mod_table_view.verticalHeader().setVisible(False)  # Hide vertical header

        # Buttons
        self.btn_refresh = QtWidgets.QPushButton("Refresh mods")
        self.btn_refresh.setToolTip("Refresh the list of installed mods")

        self.btn_toggle = QtWidgets.QPushButton("Toggle (Active/Inactive)")
        self.btn_toggle.setToolTip("Toggle the selected mod between active and inactive")

        self.btn_install = QtWidgets.QPushButton("Install mod")
        self.btn_install.setToolTip("Install a mod from a .wotmod file")

        self.btn_moveall = QtWidgets.QPushButton("Import mods from older game version")
        self.btn_moveall.setToolTip("Move all mods from a previous game version to the current version")

        self.btn_disableall = QtWidgets.QPushButton("Disable all mods")
        self.btn_disableall.setToolTip("Disable all installed mods")

        self.btn_enableall = QtWidgets.QPushButton("Enable all mods")
        self.btn_enableall.setToolTip("Enable all installed mods")

        self.btn_moveall_to_prev = QtWidgets.QPushButton("Move all mods to a previous version")
        self.btn_moveall_to_prev.setToolTip("Move all mods to a previous game version")

        if sys.platform == "linux":
            self.btn_disableall.setIcon(QtGui.QIcon.fromTheme("edit-delete"))
            self.btn_enableall.setIcon(QtGui.QIcon.fromTheme("emblem-default"))
            self.btn_refresh.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
            self.btn_toggle.setIcon(QtGui.QIcon.fromTheme("object-flip-horizontal"))
            self.btn_install.setIcon(QtGui.QIcon.fromTheme("list-add"))
            self.btn_moveall.setIcon(QtGui.QIcon.fromTheme("go-next"))
            self.btn_moveall_to_prev.setIcon(QtGui.QIcon.fromTheme("go-previous"))

        # Set up main layout
        self.mainlayout.addSpacing(10)
        self.mainlayout.addWidget(self.lbl_installed)
        self.mainlayout.addWidget(self.mod_table_view)
        self.mainlayout.addWidget(self.lbl_details)
        self.mainlayout.addWidget(self.lbl_description)
        self.mainlayout.addStretch()
        self.mainlayout.addWidget(self.btn_refresh)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_toggle)
        self.hlayout.addWidget(self.btn_install)
        self.mainlayout.addLayout(self.hlayout)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_enableall)
        self.hlayout.addWidget(self.btn_disableall)
        self.mainlayout.addLayout(self.hlayout)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.btn_moveall)
        self.hlayout.addWidget(self.btn_moveall_to_prev)
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addWidget(self.lbl_action_log)
        #endregion

        
        #region Settings Tab
        self.settings_tab = QtWidgets.QWidget()
        self.settings_layout = QtWidgets.QVBoxLayout(self.settings_tab)
        self.settings_view = settingstab.SettingsTabView(self.myinvoker, app)
        self.settings_layout.addWidget(self.settings_view, alignment=QtCore.Qt.AlignCenter)
        #endregion

        #region Mod Browser Tab
        self.mod_browser_tab = QtWidgets.QWidget()
        self.mod_browser_layout = QtWidgets.QVBoxLayout(self.mod_browser_tab)
        self.mod_browser_view = wgb.WGModsSearchResultsView(self.myinvoker)
        self.mod_browser_layout.addWidget(self.mod_browser_view)
        #endregion


        # Add tabs to the tab widget
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.mod_browser_tab, "Mod Browser")

        # Set the main layout of the window
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.addWidget(self.tabs)

        # Connect signals
        self.btn_refresh.clicked.connect(self.reload_mods_gui)
        self.btn_install.clicked.connect(self.install_mod)
        self.btn_toggle.clicked.connect(self.toggle_mod)
        self.btn_disableall.clicked.connect(self.disable_all)
        self.btn_enableall.clicked.connect(self.enable_all)
        self.btn_moveall.clicked.connect(self.move_all_mods)
        #register table view click event
        self.mod_table_view.clicked.connect(self.display_mod_details)
        
        self.mod_table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mod_table_view.customContextMenuRequested.connect(self.show_mod_details_window)
        self.btn_moveall_to_prev.clicked.connect(self.move_all_mods_to_prev)

        self.reload_mods()

        # detect drag and drop
        self.setAcceptDrops(True)
    
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
            if err != 0:
                self.update_action_log(mods, err, action)
                return

            self.mod_model = ModsTableModel(mods)
            self.mod_table_view.setModel(self.mod_model)

            if updateLog:
                self.update_action_log("Successfully refreshed mods", err, action)
        except Exception as e:
            # Show qt popup message box
            self.show_error("Could not refresh mods: "+str(e), "Error: Could not refresh mods")

            # Set some dummy mods
            mods = [invoker.Mod("Dummy Mod","wgi231", "com.dummy.mod", "1.0", "This is a dummy mod", "dummy.wotmod", True)]
            self.mod_model = ModsTableModel(mods)
            self.mod_table_view.setModel(self.mod_model)

    def setup_game_dir(self):
        while True:
            # open file dialog
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select game directory")
            if folder:
                if self.myinvoker.set_game_installation_dir(folder):
                    self.show_error("Game directory set successfully.", "Success: Game directory set", QtWidgets.QMessageBox.Information)
                    break
                else:
                    self.show_error("Could not set the game directory. Please try again.", "Error: Could not set game directory")
            else:
                self.show_error("No directory selected. Please select the game directory.", "Error: No directory selected")

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
    @QtCore.Slot()
    def display_mod_details(self):
        
        index = self.mod_table_view.currentIndex()
        # get mod from index
        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        if mod is not None:
            mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
            self.lbl_details.setText(f"{mod.name} (v{mod.version}) - {mod.pckid}")
            self.lbl_description.setText(mod.desc)

    # Handler for right-clicking a mod
    @QtCore.Slot(QtCore.QPoint)
    def show_mod_details_window(self, index):
        index = self.mod_table_view.indexAt(index)
        if not index.isValid():
            return

        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        if mod is None:
            print("No mod selected")
            return
        secondary = ModInfoWindow(mod, self)
        secondary.exec()
        # Reload mods in case the mod was toggled or changed
        self.reload_mods()

    @QtCore.Slot()
    def toggle_mod(self):
        index = self.mod_table_view.currentIndex()
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
        # use the new ImportPrevModsWindow
        imp = ImportPrevModsWindow(self)
        imp.exec()
        self.reload_mods()

    @QtCore.Slot()
    def move_all_mods_to_prev(self):
        # use the new ExportPrevModsWindow
        exp = ExportPrevModsWindow(self)
        exp.exec()
        self.reload_mods()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # Reimplement dropEvent to handle the file drop
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()  # List of QUrls
            file_paths = [url.toLocalFile() for url in urls]  # Convert QUrls to local file paths

            for file_path in file_paths:
                print("Dropped file: ", file_path)
                # check if its a wotmod file
                if file_path.endswith(".wotmod"):
                    out = self.myinvoker.install_mod(file_path)
                    resp, err, act = self.myinvoker.parse_response(out)
                    if err != 0:
                        self.show_error(resp, "Error: Could not install mod")
                    self.update_action_log(resp, err, act)
                    self.reload_mods()
                else:
                    self.show_error("Only .wotmod files are supported yet", "Error: Unsupported file type")
        else:
            event.ignore()


    def show_error(self, message:str, title:str, icon=QtWidgets.QMessageBox.Critical):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        prefix = "Error: "
        if icon == QtWidgets.QMessageBox.Information:
            prefix = "Info: "
        msg.setText(prefix+message)
        msg.setWindowTitle(title)
        msg.exec()


class ModInfoWindow(QtWidgets.QDialog):
    def __init__(self, mod:invoker.Mod, parent_window):
        super().__init__()

        self.mod:invoker.Mod = mod
        self.myinvoker:invoker.ModManagerCore = parent_window.myinvoker
        self.parent_window:MainWindow = parent_window

        self.setWindowTitle("Mod Info - "+mod.name)
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.lbl_name = QtWidgets.QLabel(mod.name)
        self.lbl_name.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
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

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(self.sizeHint())  # Makes the window non-resizable and just large enough to fit content

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

class ImportPrevModsWindow(QtWidgets.QDialog):
    def __init__(self, parent_window: MainWindow):
        super().__init__()

        self.myinvoker: invoker.ModManagerCore = parent_window.myinvoker
        self.parent_window = parent_window

        self.setWindowTitle("Import mods from previous version")
        
        # Main layout
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.setContentsMargins(10, 10, 10, 10)  # Adjust margins (left, top, right, bottom)
        self.mainlayout.setSpacing(5)  # Adjust spacing between widgets

        self.lbl_title = QtWidgets.QLabel("Import mods from a previous version")
        self.cbb_mod_folders = QtWidgets.QComboBox()
        self.btn_import = QtWidgets.QPushButton("Import")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

        # Set QLabel to avoid expanding unnecessarily
        self.lbl_title.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Add widgets to layout
        self.mainlayout.addWidget(self.lbl_title)
        self.mainlayout.addWidget(self.cbb_mod_folders)
        
        # Button layout
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setSpacing(5)  # Reduce spacing between buttons
        self.hlayout.addWidget(self.btn_import)
        self.hlayout.addWidget(self.btn_cancel)
        self.mainlayout.addLayout(self.hlayout)
        
        # Set layout to the dialog
        self.setLayout(self.mainlayout)

        # Adjust the window size to fit contents tightly
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(self.sizeIncrement())  
        
        self.update_mod_folders()

        # Connect signals
        self.btn_import.clicked.connect(self.import_mods)
        self.btn_cancel.clicked.connect(self.close)

    def update_mod_folders(self):
        folders = self.myinvoker.get_all_mod_folders()
        self.cbb_mod_folders.clear()
        for folder in folders:
            self.cbb_mod_folders.addItem(folder)

        # set the current index to the newest version
        self.cbb_mod_folders.setCurrentIndex(len(folders)-1)

    @QtCore.Slot()
    def import_mods(self):
        folder = self.cbb_mod_folders.currentText()
        response = self.myinvoker.move_all_to_newest_from_game_version(folder)
        msg, err, act = self.myinvoker.parse_response(response)
        if err != 0:
            self.parent_window.show_error(f"An error occurred.\n{msg}", "Error: Could not move mods")
        self.parent_window.update_action_log(msg, err, act)
        self.close()

# Window popup to export mods to a previous version
class ExportPrevModsWindow(QtWidgets.QDialog):
    def __init__(self, parent_window: MainWindow):
        super().__init__()

        self.myinvoker: invoker.ModManagerCore = parent_window.myinvoker
        self.parent_window = parent_window

        self.setWindowTitle("Export mods to a previous version")
        
        # Main layout
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.setContentsMargins(10, 10, 10, 10)  # Adjust margins (left, top, right, bottom)
        self.mainlayout.setSpacing(5)  # Adjust spacing between widgets

        self.lbl_title = QtWidgets.QLabel("Export mods to a previous version")
        self.cbb_mod_folders = QtWidgets.QComboBox()
        self.btn_export = QtWidgets.QPushButton("Export")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

        # Set QLabel to avoid expanding unnecessarily
        self.lbl_title.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Add widgets to layout
        self.mainlayout.addWidget(self.lbl_title)
        self.mainlayout.addWidget(self.cbb_mod_folders)
        
        # Button layout
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setSpacing(5)  # Reduce spacing between buttons
        self.hlayout.addWidget(self.btn_export)
        self.hlayout.addWidget(self.btn_cancel)
        self.mainlayout.addLayout(self.hlayout)
        
        # Set layout to the dialog
        self.setLayout(self.mainlayout)

        # Adjust the window size to fit contents tightly
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(self.sizeIncrement())  
        
        self.update_mod_folders()

        # Connect signals
        self.btn_export.clicked.connect(self.export_mods)
        self.btn_cancel.clicked.connect(self.close)

    def update_mod_folders(self):
        folders = self.myinvoker.get_all_mod_folders()
        self.cbb_mod_folders.clear()
        for folder in folders:
            self.cbb_mod_folders.addItem(folder)

        # set the current index to the newest version
        self.cbb_mod_folders.setCurrentIndex(len(folders)-1)

    @QtCore.Slot()
    def export_mods(self):
        folder = self.cbb_mod_folders.currentText()
        response = self.myinvoker.move_all_to_previous_version(folder)
        msg, err, act = self.myinvoker.parse_response(response)# type: ignore 
        if err != 0:
            self.parent_window.show_error(f"An error occurred.\n{msg}", "Error: Could not move mods")
        self.parent_window.update_action_log(msg, err, act)
        self.close()


if __name__ == '__main__':
    argadd = []
    if sys.platform == "linux":
        pass
    elif sys.platform == "win32":
        argadd = ['-platform', 'windows:darkmode=2']
    elif sys.platform == "darwin":
        # show error if running on macOS
        print("This application is not supported on macOS. Please use a Linux or Windows system.")
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv + argadd)

    
    app.setStyleSheet(MATERIAL_LIGHT)

    widget = MainWindow()
    widget.resize(400, 500)
    widget.show()

    sys.exit(app.exec())
    