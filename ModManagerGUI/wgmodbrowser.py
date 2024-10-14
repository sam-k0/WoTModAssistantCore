import wgmodrequests as wgmods
from PySide6 import QtCore, QtWidgets, QtGui


class WGModsSearchResultsModel(QtCore.QAbstractTableModel):
    def __init__(self, search_results:wgmods.WGModsSearchResults, parent=None):
        super(WGModsSearchResultsModel, self).__init__(parent)
        self.search_results = search_results
        self.new_mods_list = self.search_results.new_mods_list
        self.recommended_mods_list = self.search_results.recommended_mods_list
        self.updated_mods_list = self.search_results.updated_mods_list
        self.header_labels = ["Mod Name", "Author", "Game Version", "Download URL"]
    
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
        if order == QtCore.Qt.DescendingOrder:
            self.new_mods_list.reverse()
            self.recommended_mods_list.reverse()
            self.updated_mods_list.reverse()
        self.layoutChanged.emit()


class WGModsSearchResultsView(QtWidgets.QWidget):
    def __init__(self, search_results:wgmods.WGModsSearchResults, parent=None):
        super(WGModsSearchResultsView, self).__init__(parent)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Create the search bar
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setPlaceholderText("Search mods...")
        self.layout.addWidget(self.search_bar)
        
        # Create the table view
        self.table_view = QtWidgets.QTableView(self)
        self.layout.addWidget(self.table_view)
        
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
        
        # Connect the search bar to the filter method
        self.search_bar.textChanged.connect(self.filter_mods)
    
    def filter_mods(self, text):
        self.proxy_model.setFilterFixedString(text)