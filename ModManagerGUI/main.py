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
        self.btn_refresh = QtWidgets.QPushButton("refresh mods")
        self.text = QtWidgets.QLabel("Installed", alignment=QtCore.Qt.AlignCenter)
        self.toptext = QtWidgets.QLabel("Install directory set to "+self.myinvoker.installation_path, alignment=QtCore.Qt.AlignTop)
        self.detail_label = QtWidgets.QLabel("Details", alignment=QtCore.Qt.AlignCenter)
        self.description_label = QtWidgets.QLabel("Description", alignment=QtCore.Qt.AlignCenter, wordWrap=True)

        self.mod_list_view = QtWidgets.QListView(self)
        self.mod_model = QtGui.QStandardItemModel(self.mod_list_view)

        self.mod_list_view.setModel(self.mod_model)

        # Set up layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.toptext)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.mod_list_view)
        self.layout.addWidget(self.detail_label)
        self.layout.addWidget(self.description_label)

        self.layout.addWidget(self.btn_refresh)

        # Connect button click to magic function
        self.btn_refresh.clicked.connect(self.reload_mods)
        # Connect the list view selection signal to a function to display mod details
        self.mod_list_view.selectionModel().currentChanged.connect(self.display_mod_details)
    
    @QtCore.Slot()
    def reload_mods(self):
        mods, err, action = self.myinvoker.get_mods_list()
        # reset model
        self.mod_model.clear()
        # populate model with mod items
        for mod in mods:   
            item = QtGui.QStandardItem(mod.name + " (v" + mod.version + ")")
            item.setData(mod, QtCore.Qt.UserRole)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mod_model.appendRow(item)

    # show mod details when a mod is selected
    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def display_mod_details(self, index):
        # check if the index is valid
        if not index.isValid():
            return

        mod:invoker.Mod = index.data(QtCore.Qt.UserRole)
        self.detail_label.setText(f"{mod.name} (v{mod.version}) - {mod.pckid}")
        self.description_label.setText(mod.desc)




if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(400, 300)
    widget.show()

    sys.exit(app.exec_())
    