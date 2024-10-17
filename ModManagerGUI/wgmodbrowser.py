import wgmodrequests as wgmods
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser

class WGModsSearchResultsModel(QtCore.QAbstractTableModel):
    def __init__(self, search_results:wgmods.WGModsSearchResults, parent=None):
        super(WGModsSearchResultsModel, self).__init__(parent)
        self.search_results = search_results
        self.new_mods_list = self.search_results.new_mods_list
        self.recommended_mods_list = self.search_results.recommended_mods_list
        self.updated_mods_list = self.search_results.updated_mods_list
        self.header_labels = ["Mod Name", "Author", "Game Version", "Download URL", "Mod ID"]
    
    def rowCount(self, parent):
        return len(self.search_results.get_new_mods()) + len(self.search_results.get_recommended_mods()) + len(self.search_results.get_updated_mods())
    
    def columnCount(self, parent):
        return len(self.header_labels)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0: # The real count of mods is determined by list length.
                if index.row() < len(self.new_mods_list):
                    return self.new_mods_list[index.row()].mod_name_eng
                elif index.row() < len(self.new_mods_list) + len(self.recommended_mods_list):
                    return self.recommended_mods_list[index.row() - len(self.new_mods_list)].mod_name_eng
                else:
                    return self.updated_mods_list[index.row() - len(self.new_mods_list) - len(self.recommended_mods_list)].mod_name_eng
                
            elif index.column() == 1:
                if index.row() < len(self.new_mods_list):
                    return self.new_mods_list[index.row()].author_name
                elif index.row() < len(self.new_mods_list) + len(self.recommended_mods_list):
                    return self.recommended_mods_list[index.row() - len(self.new_mods_list)].author_name
                else:
                    return self.updated_mods_list[index.row() - len(self.new_mods_list) - len(self.recommended_mods_list)].author_name
                
            elif index.column() == 2:
                if index.row() < len(self.new_mods_list):
                    return self.new_mods_list[index.row()].game_version_human
                elif index.row() < len(self.new_mods_list) + len(self.recommended_mods_list):
                    return self.recommended_mods_list[index.row() - len(self.new_mods_list)].game_version_human
                else:
                    return self.updated_mods_list[index.row() - len(self.new_mods_list) - len(self.recommended_mods_list)].game_version_human
                
            elif index.column() == 3:
                if index.row() < len(self.new_mods_list):
                    return self.new_mods_list[index.row()].download_url
                elif index.row() < len(self.new_mods_list) + len(self.recommended_mods_list):
                    return self.recommended_mods_list[index.row() - len(self.new_mods_list)].download_url
                else:
                    return self.updated_mods_list[index.row() - len(self.new_mods_list) - len(self.recommended_mods_list)].download_url
                
            elif index.column() == 4:
                if index.row() < len(self.new_mods_list):
                    return self.new_mods_list[index.row()].mod_id
                elif index.row() < len(self.new_mods_list) + len(self.recommended_mods_list):
                    return self.recommended_mods_list[index.row() - len(self.new_mods_list)].mod_id
                else:
                    return self.updated_mods_list[index.row() - len(self.new_mods_list) - len(self.recommended_mods_list)].mod_id
        return None
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_labels[section]
        return None
    
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    
    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if column == 0:
            self.new_mods_list.sort(key=lambda x: x.mod_name_eng)
            self.recommended_mods_list.sort(key=lambda x: x.mod_name_eng)
            self.updated_mods_list.sort(key=lambda x: x.mod_name_eng)
        elif column == 1:
            self.new_mods_list.sort(key=lambda x: x.author_name)
            self.recommended_mods_list.sort(key=lambda x: x.author_name)
            self.updated_mods_list.sort(key=lambda x: x.author_name)
        elif column == 2:
            self.new_mods_list.sort(key=lambda x: x.game_version_human)
            self.recommended_mods_list.sort(key=lambda x: x.game_version_human)
            self.updated_mods_list.sort(key=lambda x: x.game_version_human)
        elif column == 3:
            self.new_mods_list.sort(key=lambda x: x.download_url)
            self.recommended_mods_list.sort(key=lambda x: x.download_url)
            self.updated_mods_list.sort(key=lambda x: x.download_url)
        elif column == 4:
            self.new_mods_list.sort(key=lambda x: x.mod_id)
            self.recommended_mods_list.sort(key=lambda x: x.mod_id)
            self.updated_mods_list.sort(key=lambda x: x.mod_id)
        
        if order == QtCore.Qt.DescendingOrder:
            self.new_mods_list.reverse()
            self.recommended_mods_list.reverse()
            self.updated_mods_list.reverse()
        self.layoutChanged.emit()


class WGModsSearchResultsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WGModsSearchResultsView, self).__init__(parent)
        
        search_results = wgmods.WGModsRequest().get_start_page("en", 20,5,1,185)

        self.mainlayout = QtWidgets.QVBoxLayout(self)
        
        # Create the search bar
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setPlaceholderText("Search mods...")
        self.mainlayout.addWidget(self.search_bar)
        
        # Create the table view
        self.table_view = QtWidgets.QTableView(self)
        self.mainlayout.addWidget(self.table_view)
        
        # Create the model and proxy model
        self.model = WGModsSearchResultsModel(search_results)
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Filter all columns
        
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_view.setShowGrid(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self.table_view.setWordWrap(True)
        
        # connect signals
        self.search_bar.textChanged.connect(self.filter_mods)
        self.table_view.clicked.connect(self.table_view_left_click)

    
    def filter_mods(self, text):
        self.proxy_model.setFilterFixedString(text)

    @QtCore.Slot()
    def table_view_left_click(self):
        # get the associated download info
        index = self.table_view.currentIndex()
        download_url = self.proxy_model.data(self.proxy_model.index(index.row(), 3))
        mod_name = self.proxy_model.data(self.proxy_model.index(index.row(), 0))
        game_version = self.proxy_model.data(self.proxy_model.index(index.row(), 2))
        author = self.proxy_model.data(self.proxy_model.index(index.row(), 1))
        modid = self.proxy_model.data(self.proxy_model.index(index.row(), 4))

        if author == None:
            author = "n/a"
        # create a download dialog window
        download_dialog = DownloadDialog(download_url, mod_name, game_version, author, modid)
        download_dialog.exec()


# Download dialog window class

class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, download_url:str, mod_name:str, game_version:str, author:str, modid:int, parent=None):
        super(DownloadDialog, self).__init__(parent)
        self.download_url = download_url
        self.mod_name = mod_name
        self.game_version = game_version
        self.author = author
        self.modid = modid
        
        # window stuff
        self.setWindowTitle(f"Download {self.mod_name} for {self.game_version}")
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.lbl_info = QtWidgets.QLabel("Download information for:")
        self.lbl_name = QtWidgets.QLabel(self.mod_name, wordWrap=True)
        self.lbl_name.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        self.lbl_version = QtWidgets.QLabel("<b>For Game Version</b>: "+self.game_version)
        self.lbl_wgid = QtWidgets.QLabel("wgmods ID: "+str(self.modid))
        self.lbl_author = QtWidgets.QLabel("Author: "+self.author)
        self.lbl_download_url = QtWidgets.QLabel("Download URL: "+self.download_url, wordWrap=True)
        # buttons
        self.download_button = QtWidgets.QPushButton("Download and install", self)
        self.wgmodspage_button = QtWidgets.QPushButton("Show on wgmods.net", self)

        # add widgets to layout
        self.mainlayout.addWidget(self.lbl_info)
        self.mainlayout.addWidget(self.lbl_name)
        self.mainlayout.addWidget(self.lbl_version)
        self.mainlayout.addWidget(self.lbl_wgid)
        self.mainlayout.addWidget(self.lbl_author)
        self.mainlayout.addWidget(self.lbl_download_url)

        self.mainlayout.addWidget(self.download_button)
        self.mainlayout.addWidget(self.wgmodspage_button)
        # spacing policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setFixedSize(self.sizeHint())
        
        # connect signals
        self.download_button.clicked.connect(self.download_mod)
        self.wgmodspage_button.clicked.connect(self.open_wgmods_page)
    
    @QtCore.Slot()
    def download_mod(self):
        print("Downloading mod from URL:", self.download_url)

    @QtCore.Slot()
    def open_wgmods_page(self):
        print("Opening mod page on WGMods for mod ID:", self.modid)
        webbrowser.open(f"https://wgmods.net/{self.modid}")