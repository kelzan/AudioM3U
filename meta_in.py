__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson <kelly@kellylarson.com>'
__docformat__ = 'restructuredtext en'

import sys
import os

# Temporary Hack to get mutagen working
#sys.path.append("c:\\Users\\kelly\\Documents\\Source\\AudioM3U")

# Import m3u handling utilities
from calibre_plugins.AudioM3U.m3u_utils import get_tags
from calibre_plugins.AudioM3U.m3u_utils import get_cover
from calibre_plugins.AudioM3U.m3u_utils import playtime

from polyglot.builtins import cmp, iteritems, itervalues, string_or_bytes

from qt.core import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QCheckBox, QDialogButtonBox
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs


class ImportDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.fields = ["cover", "title", "author", "narrator", "duration", "total_size", "sample_rate", "bitrate", "mode", "type", "num_files"]

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
        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle('Import metadata')
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

        # Only Blank Fields Import checkbox
        self.only_blank_cb = QCheckBox(self)
        self.only_blank_cb.setObjectName("only_bank_cb")
        self.verticalLayout.addWidget(self.only_blank_cb)

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
        self.update_metadata()
        #self.setWindowTitle('Whassup!')
        super().accept()
    
    def retranslateUi(self, ImportDialog):
        _translate = QCoreApplication.translate
        ImportDialog.setWindowTitle(_translate("ImportDialog", "Import Metadata"))
        self.top_label.setText(_translate("ImportDialog", "Metadata fields to import from audio files:"))
        #self.blank_over_checkbox.setText(_translate("ImportDialog", "Allow blank import data to overwrite existing data"))
        self.only_blank_cb.setText(_translate("ImportDialog", "Only import to blank fields, don\'t overwrite existing data"))

    def is_checked(self, label):
        found = self.field_list.findItems(label, Qt.MatchExactly)
        if (len(found) != 1):
            return False
        #print(f"{label} Found: {type(found)} {len(found)}")
        return found[0].checkState() == Qt.Checked
    
    # def can_write(self, is_field_null, is_import_null):
    #     print(f"({self.blank_over_checkbox.isChecked()} or ({not is_import_null})) and (({not self.only_blank_cb.isChecked()}) or {not is_field_null})")
    #     return ((self.blank_over_checkbox.isChecked() or (not is_import_null)) and
    #             ((not self.only_blank_cb.isChecked()) or (not is_field_null)))

    def update_metadata(self):
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
            audio_tags = get_tags(path)
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            if not fmts:
                continue
            #print("audio_tags: ",audio_tags)
            #non_none_fields = mi.all_non_none_fields()
            #print("non none:",non_none_fields)
            # Now determine which fields, based on config and options, need to be updated
            update_all = not self.only_blank_cb.isChecked()

            if (self.is_checked("author")):
                if (update_all or mi.is_null("authors")):
                    if "author" in audio_tags:
                        mi.set("authors", audio_tags['author'].split(" & "))
            if (self.is_checked("title")):
                if (update_all or mi.is_null("title")):
                    if "title" in audio_tags:
                        mi.set("title", audio_tags['title'])
            if (self.is_checked("narrator")):
                if (update_all or mi.is_null("#narrator")):
                    if "narrator" in audio_tags:
                        mi.set("#narrator", audio_tags['narrator'])
            if (self.is_checked("duration")):
                if (update_all or mi.is_null("#duration")):
                    mi.set("#duration", playtime(audio_tags['duration']))
            if (self.is_checked("bitrate")):
                if (update_all or mi.is_null("#bitrate")):
                    mi.set("#bitrate", audio_tags['bitrate'])
            if (self.is_checked("sample_rate")):
                if (update_all or mi.is_null("#sample_rate")):
                    mi.set("#sample_rate", audio_tags['sample_rate'])
            if (self.is_checked("total_size")):
                if (update_all or mi.is_null("#size")):
                    mi.set("#size", audio_tags['size'] / (1024*1024))
            if (self.is_checked("type")):
                if (update_all or mi.is_null("#type")):
                    mi.set("#type", audio_tags['type'])
            if (self.is_checked("mode")):
                if (update_all or mi.is_null("#mode")):
                    mi.set("#mode", audio_tags['mode'])
            if (self.is_checked("num_files")):
                if (update_all or mi.is_null("#num_files")):
                    mi.set("#num_files", audio_tags['num_files'])

            if (self.is_checked("cover")):
                if (update_all or mi.is_null("cover_data")):
                    cover = get_cover(path)
                    mi.set("cover_data", cover) # This is a ('type', 'data') tuple

            self.db.set_metadata(book_id, mi)

            self.gui.library_view.model().refresh_ids([book_id])
            #print(f"type: {type(self.gui.book_details)}")
            #self.gui.book_details.show_data(mi)
            #self.gui.book_details.reset_info()
            #self.gui.book_details.update_layout()
            
        info_dialog(self, 'Updated files',
                f'Updated the metadata in the files of {len(m3u_ids)} of {len(ids)} book(s)',
                show=True)

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])
