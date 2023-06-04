__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson <kelly@kellylarson.com>'
__docformat__ = 'restructuredtext en'

import sys
import os

# Temporary Hack to get mutagen working
sys.path.append("c:\\Users\\kelly\\Documents\\Source\\AudioM3U")

# Import m3u handling utilities
from calibre_plugins.AudioM3U.m3u_utils import get_tags
from calibre_plugins.AudioM3U.m3u_utils import get_cover
from calibre_plugins.AudioM3U.m3u_utils import playtime
from calibre_plugins.AudioM3U.m3u_utils import export_tags

from polyglot.builtins import cmp, iteritems, itervalues, string_or_bytes

from qt.core import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QCheckBox, QDialogButtonBox
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs


class ExportDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.fields = ["cover", "title", "author", "narrator"]

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
        self.setGeometry(100, 100, 500, 150)
        self.setWindowTitle('Export metadata')
        self.setupWidgets()

#        self.show()

    def setupWidgets(self):
        """
        Create widgets for to do list GUI and arrange them in window
        """
        # create grid layout
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # Top Label
        self.top_label = QLabel(self)
        self.top_label.setObjectName("top_label")
        self.verticalLayout.addWidget(self.top_label)

        # Field List Widget
        self.field_list = QListWidget(self)
        self.field_list.setObjectName("field_list")
        self.field_list.setAlternatingRowColors(True)
        for item in self.fields:
            list_item = QListWidgetItem()
            list_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            list_item.setCheckState(Qt.Unchecked)
            list_item.setText(item)
            self.field_list.addItem(list_item)
        self.verticalLayout.addWidget(self.field_list)

        # No overwrite checkbox
        # self.blank_over_checkbox = QCheckBox(self)
        # self.blank_over_checkbox.setObjectName("blank_over_checkbox")
        # self.verticalLayout.addWidget(self.blank_over_checkbox)

        # # Only Blank Fields Import checkbox
        # self.only_blank_cb = QCheckBox(self)
        # self.only_blank_cb.setObjectName("only_bank_cb")
        # self.verticalLayout.addWidget(self.only_blank_cb)

        # Dialog Button Box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        # Set the text fields
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore
        QMetaObject.connectSlotsByName(self)

        self.setLayout(self.verticalLayout)
        
    def accept(self):
        print("ACCEPT!")
        self.export_metadata()
        #self.setWindowTitle('Whassup!')
        super().accept()
    
    def retranslateUi(self, ImportDialog):
        _translate = QCoreApplication.translate
        ImportDialog.setWindowTitle(_translate("ExportDialog", "Export Metadata"))
        self.top_label.setText(_translate("ExportDialog", "Metadata fields to export to audio files:"))
        #self.blank_over_checkbox.setText(_translate("ImportDialog", "Allow blank import data to overwrite existing data"))
        #self.only_blank_cb.setText(_translate("ImportDialog", "Only import to blank fields, don\'t overwrite existing data"))

    def is_checked(self, label):
        found = self.field_list.findItems(label, Qt.MatchExactly)
        if (len(found) != 1):
            return False
        #print(f"{label} Found: {type(found)} {len(found)}")
        return found[0].checkState() == Qt.Checked
    
    def export_metadata(self):
        '''
        Set the metadata in the files in the selected book's record to
        match the current metadata in the database.
        '''
        from calibre.ebooks.metadata.meta import set_metadata
        from calibre.gui2 import error_dialog, info_dialog

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                             'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.db.new_api
        m3u_ids = list(filter(lambda x: (db.has_format(x, "M3U")), ids))
        for book_id in m3u_ids:
            # Get the path for the .m3u file TODO: Change this to use 'format' as a memory image instead
            path = db.format_abspath(book_id, "M3U")
            print(f"Path: {path}")
            # Now get tags from the audio files
            #audio_tags = get_tags(path)
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            #fmts = db.formats(book_id)
            #if not fmts:
            #    continue
            # Now determine which fields, based on config and options, need to be updated
            #update_all = not self.only_blank_cb.isChecked()
            export_fields = list(filter(lambda x: (self.is_checked(x)),self.fields))

            export_meta = {}
            print(f"export_fields: {export_fields}")
            for field in export_fields:
                if ((field == "author") and (not mi.is_null("authors"))):
                    export_meta["author"] = " & ".join(mi.get("authors"))
                if ((field == "title") and (not mi.is_null("title"))):
                    export_meta["title"] = mi.get("title")
                if ((field == "narrator") and (not mi.is_null("#narrator"))):
                    print(f"Getting narrator: {mi.get('#narrator')}")
                    export_meta["narrator"] = " & ".join(mi.get("#narrator"))
                if ((field == "cover") and (not mi.is_null("cover_data"))):
                    export_meta["cover"] = mi.get("cover_data")
            #print(f"export_meta: {export_meta}")
            export_tags(path, export_meta)

            #self.db.set_metadata(book_id, mi)
            #self.gui.library_view.model().refresh_ids([book_id])
            
        info_dialog(self, 'Updated audio files',
                f'Exported the metadata to the audio files for {len(m3u_ids)} of {len(ids)} book(s)',
                show=True)

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])
