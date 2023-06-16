__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson <kelly@kellylarson.com>'
__docformat__ = 'restructuredtext en'

import sys
import os


from qt.core import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QListWidgetItem, QPushButton, 
                     QDialogButtonBox)
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs


class InspectDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.m3u_ids = []
        self.curm3u = 0

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db
        self.initializeUI()

    def initializeUI(self):
        """
        Initialize the window and display its contents to the screen
        """
        self.setGeometry(100, 100, 500, 400)
        self.setWindowTitle('Inspect M3U Files')
        self.setupWidgets()

#        self.show()

    def setupWidgets(self):
        """
        Create widgets for to do list GUI and arrange them in window
        """

        # Create Vertical layout
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Create top label
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # Create Plain Text Box
        self.textBrowser = QPlainTextEdit(self)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setReadOnly(True)
        self.verticalLayout.addWidget(self.textBrowser)

        # Create Horizontal Layout for buttons
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Previous Button
        self.PrevButton = QPushButton(self)
        self.PrevButton.setObjectName("PrevButton")
        self.horizontalLayout.addWidget(self.PrevButton)

        # OK Button
        self.OKButton = QPushButton(self)
        self.OKButton.setDefault(True)
        self.OKButton.setObjectName("OKButton")
        self.horizontalLayout.addWidget(self.OKButton)

        # Next Button
        self.NextButton = QPushButton(self)
        self.NextButton.setObjectName("NextButton")
        self.horizontalLayout.addWidget(self.NextButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Set text fields
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        # Connect button actions
        self.OKButton.clicked.connect(self.accept)
        self.PrevButton.clicked.connect(self.prev_file)
        self.NextButton.clicked.connect(self.next_file)

        #self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.setLayout(self.verticalLayout)

        
    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "M3U Inpector"))
        self.label.setText(_translate("Dialog", "TextLabel"))
        self.PrevButton.setText(_translate("Dialog", "Previous"))
        self.OKButton.setText(_translate("Dialog", "OK"))
        self.NextButton.setText(_translate("Dialog", "Next"))

    def init_data(self):
        from calibre.ebooks.metadata.meta import set_metadata
        from calibre.gui2 import error_dialog, info_dialog

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot browse M3U files',
                             'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.db.new_api
        self.m3u_ids = list(filter(lambda x: (db.has_format(x, "M3U")), ids))
        self.curm3u = 0
        if len(self.m3u_ids) == 0:
            return error_dialog(self.gui, 'Cannot browse M3U files',
                             'No books selected', show=True)
        self.set_label()
        self.load_text()
        self.enable_buttons()

    def set_label(self):
        db = self.db.new_api
        book_id = self.m3u_ids[self.curm3u]
        mi = db.get_metadata(book_id, get_cover=False)
        title = mi.get("title", "Unknown")
        author = mi.get("authors",["Unknown"])
        #print(f"authors: {' & '.join(author)}")
        self.label.setText(f"{' & '.join(author)} - {title} ({self.curm3u+1}/{len(self.m3u_ids)})")

    def load_text(self):
        db = self.db.new_api
        path = db.format_abspath(self.m3u_ids[self.curm3u], "M3U")
        with open(path, 'r', encoding="utf-8") as file:
            #filetext = file.read()
            self.textBrowser.setPlainText(file.read())
        #self.textBrowser.setPlainText(filetext)


    def next_file(self):
        self.curm3u += 1
        self.set_label()
        self.load_text()
        self.enable_buttons()


    def prev_file(self):
        self.curm3u -= 1
        self.set_label()
        self.load_text()
        self.enable_buttons()
        #print(f"curfile: {self.curfile} compared {(self.curfile>0)}")


    def enable_buttons(self):
        self.NextButton.setEnabled(self.curm3u+1<len(self.m3u_ids))
        self.PrevButton.setEnabled(self.curm3u>0)


    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])
