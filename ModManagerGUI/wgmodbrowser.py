import wgmodrequests as wgmods
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser
import invoker
import sys, os
import zipfile
import xml.etree.ElementTree as ET

# cross platform way to get the download directory for modbrowser
# creates the directory if it doesn't exist
def get_download_dir():
    download_dir = ""
    if sys.platform == "win32":
        installation_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core","download")
    elif sys.platform == "linux":
        download_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core", "download")
    else:
        raise Exception("Unsupported platform: "+sys.platform)
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    return download_dir

def clear_download_dir():
    download_dir = get_download_dir()
    for file in os.listdir(download_dir):
        os.remove(os.path.join(download_dir, file))

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
    def __init__(self,myinvoker:invoker.ModManagerCore, parent=None):
        super(WGModsSearchResultsView, self).__init__(parent)
        
        search_results = wgmods.WGModsRequest().get_start_page("en", 20,5,1,185)
        self.invoker_ref = myinvoker
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
        download_dialog = DownloadDialog(download_url, mod_name, game_version, author, modid, self.invoker_ref)
        download_dialog.exec()


# Download dialog window class
class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, download_url:str, mod_name:str, game_version:str, author:str, modid:int, myinvoker:invoker.ModManagerCore,parent=None):
        super(DownloadDialog, self).__init__(parent)
        self.invoker_ref = myinvoker
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
        # get the last part of the download URL, the filetype
        self.lbl_download_url = QtWidgets.QLabel("Download type: "+self.download_url.split(".")[-1], wordWrap=True)
        # progressbar for download
        self.progressbar = QtWidgets.QProgressBar(self)
        # set to hidden by default
        self.progressbar.hide()

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
        self.mainlayout.addWidget(self.progressbar)
        # spacing policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setFixedSize(self.sizeHint())
        
        # connect signals
        self.download_button.clicked.connect(self.download_mod)
        self.wgmodspage_button.clicked.connect(self.open_wgmods_page)

        # set download button to disabled if download is not a .wotmod or .zip file
        if not self.download_url.endswith(".wotmod"):
            self.download_button.setEnabled(False)
            self.download_button.setToolTip("Not available yet.")
    
    @QtCore.Slot()
    def download_mod(self):
        print("Downloading mod from URL:", self.download_url)
        # get the download directory
        download_dir = get_download_dir()
        # clear download directory
        print("Clearing download directory at ", download_dir)
        clear_download_dir()

        if self.download_url.endswith(".wotmod"):
            self.download_install_wotmod(download_url=self.download_url)

    @QtCore.Slot()
    def open_wgmods_page(self):
        print("Opening mod page on WGMods for mod ID:", self.modid)
        webbrowser.open(f"https://wgmods.net/{self.modid}")

    # Unpacks a .wotmod file, injects the mod ID into the meta.xml file, and repacks the .wotmod file
    def inject_wgmodid_to_meta(self, localpath:str):
        print("Extracting mod to ", self.invoker_ref.get_extraction_path())
        target = self.invoker_ref.get_extraction_path() + os.sep + self.mod_name
        with zipfile.ZipFile(localpath, 'r') as zip_ref:
            zip_ref.extractall(target)
        
        # find the meta.xml file
        metafile = None
        for root, dirs, files in os.walk(target):
            for file in files:
                if file == "meta.xml":
                    metafile = os.path.join(root, file)
                    break
            if metafile != None:
                break
        # add the mod ID to the meta.xml file
        if metafile != None:
            tree = ET.parse(metafile)
            root = tree.getroot()
            modid = ET.SubElement(root, "wgid")
            modid.text = str(self.modid)
            tree.write(metafile)
            print("Added mod ID to meta.xml file for mod:", self.mod_name)
        else:
            FileNotFoundError("Failed to add mod ID to meta.xml file for mod:", self.mod_name)
        
                # repack the mod back to a .wotmod file
        with zipfile.ZipFile(localpath, 'w') as zip_ref:
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, target)
                    zip_ref.write(file_path, arcname)
        
        print("Repacked mod to ", localpath)

    def callback_progress(self, downloaded:int, total:int):
        self.progressbar.show()
        self.progressbar.setMaximum(total)
        self.progressbar.setValue(downloaded)
        if downloaded == total:
            self.progressbar.hide()
            # set the download button to disabled
            self.download_button.setEnabled(False)
            self.download_button.setText("Installed!")
            self.download_button.setToolTip("Already installed!")

    def download_install_wotmod(self, download_url:str):
        localfilename = download_url.split("/")[-1] # get the filename from the URL
        localpath = os.path.join(get_download_dir(), localfilename)
        # download the file
        wgmods.download_from_url(download_url, localpath, self.callback_progress)
        
        # inject the mod ID into the meta.xml file
        self.inject_wgmodid_to_meta(localpath)

        # install the mod
        self.invoker_ref.install_mod(localpath)
        # Clean up the download directory
        clear_download_dir()
        

        
    