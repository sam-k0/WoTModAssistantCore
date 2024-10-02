import sys 
from PySide6 import QtCore, QtWidgets, QtGui

"""if __name__ == '__main__':
    from invoker import invoke
    llist = ["--help", "all"]
    out = invoke(llist)
    print(out)"""


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hello World!"]
        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)   
        # top bar text 
        self.setWindowTitle("Mod Manager")
        self.toptext = QtWidgets.QLabel("install directory set to xx", alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.toptext)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)



        self.button.clicked.connect(self.magic)
    
    @QtCore.Slot()
    def magic(self):
        self.text.setText("Hello World")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
    