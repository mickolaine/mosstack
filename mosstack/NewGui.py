from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import QDeclarativeView
 

class GUI():
    """
    Main class for PySide Graphical User Interface
    """

    def __init__(self, argv):
        """

        :param argv:
        :return:
        """

        self.app = QApplication(argv)
        self.view = QDeclarativeView()
        url = QUrl(self.app.applicationFilePath() + 'QML/main.qml')
        #url = QUrl('QML/main.qml')


        self.view.setSource(url)
        self.view.show()
