__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

# Import m3u handling utilities
from calibre_plugins.AudioM3U.m3u_utils import get_tags
from calibre_plugins.AudioM3U.m3u_utils import get_cover
from calibre_plugins.AudioM3U.m3u_utils import playtime

from calibre_plugins.AudioM3U.progress import ProgressBarWindow

#from polyglot.builtins import cmp, iteritems, itervalues, string_or_bytes

from qt.core import (QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QCheckBox, 
                     QDialogButtonBox, QGridLayout, QPushButton)
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs



class ImportDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.fields = ["cover", "title", "author", "narrator", "duration", "size", "sample_rate", "bitrate", "mode", "type", "num_files", "genre"]
        self.genre_fields = []

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
        Create widgets for metadata input GUI and arrange them in window
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

        # Selection Button Grid
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.nonePushButton = QPushButton(self)
        self.nonePushButton.setObjectName("nonePushButton")
        self.gridLayout.addWidget(self.nonePushButton, 0, 1, 1, 1)
        self.allPushButton = QPushButton(self)
        self.allPushButton.setObjectName("allPushButton")
        self.gridLayout.addWidget(self.allPushButton, 0, 0, 1, 1)
        self.defaultPushButton = QPushButton(self)
        self.defaultPushButton.setObjectName("defaultPushButton")
        self.gridLayout.addWidget(self.defaultPushButton, 1, 0, 1, 1)
        self.setDefaultPushButton = QPushButton(self)
        self.setDefaultPushButton.setObjectName("setDefaultPushButton")
        self.gridLayout.addWidget(self.setDefaultPushButton, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.nonePushButton.setText("Select None")
        self.allPushButton.setText("Select All")
        self.defaultPushButton.setText("Select Default")
        self.setDefaultPushButton.setText("Set as Default")

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

        # Hide unenabled fields
        self.apply_settings()

        # Progress Bar Window
        self.progress_window = ProgressBarWindow()
        self.progress_window.cancel_button.clicked.connect(self.set_stop)

        self.stop_op = False

        # Connect button actions
        self.nonePushButton.clicked.connect(self.do_sel_none)
        self.allPushButton.clicked.connect(self.do_sel_all)
        self.defaultPushButton.clicked.connect(self.do_sel_default)
        self.setDefaultPushButton.clicked.connect(self.do_set_default)
        
    def set_stop(self):
        self.stop_op = True

    def do_sel_none(self):
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)
        for item in all_items:
            item.setCheckState(Qt.Unchecked)

    def do_sel_all(self):
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)
        for item in all_items:
            item.setCheckState(Qt.Checked)

    def do_sel_default(self):
        checked_items = prefs['export_selected']
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)
        for item in all_items:
            if item.text() in checked_items:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def do_set_default(self):
        checked_items = []
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)
        for item in all_items:
            if ((not item.isHidden()) and (item.checkState() == Qt.Checked)):
                checked_items.append(item.text())
        prefs['export_selected'] = checked_items

    def accept(self):
        #print("ACCEPT!")
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
        if found[0].isHidden():
            return False
        return found[0].checkState() == Qt.Checked
    
    def expand_genre(self, input_genre):
        genres = input_genre.split(", ")
        result = []
        for genre in genres:
            if genre in self.genre_fields:
                result.append(genre)
                continue
            found = False
            for full_genre in self.genre_fields:
                if full_genre.endswith(genre):
                    result.append(full_genre)
                    found = True
                    break
            if not found:
                result.append(genre)
        return ", ".join(result)
    
    def get_audio_paths(self, book_id):
        db = self.db.new_api
        book_data = db.format(book_id, "M3U")
        m3u_text = book_data.decode("utf-8")
        lines = m3u_text.splitlines()
        lines = [line for line in lines if ((line != "") and (line[0] != '#'))]
        return lines
        
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

        # Initialize progress bar window
        show_progress = (len(m3u_ids)>3) # Only show progress dialog if we're updating at least 3 books
        if (show_progress):
            self.progress_window.progress_bar.setRange(0,len(m3u_ids)-1)
            self.progress_window.show()

        self.stop_op = False
        i = 0

        for book_id in m3u_ids:
            # Update the progress bar
            if (show_progress):
                self.progress_window.update_progress(i)
            i += 1
            if (self.stop_op): # Did we press 'cancel' from the progress bar?
                break

            # Get the paths for the audio files from the M3U file
            audio_file_paths = self.get_audio_paths(book_id)
            if (not len(audio_file_paths)):
                continue
            # Now get tags from the audio files
            audio_tags = get_tags(audio_file_paths)

            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            if not fmts:
                continue

            # Load array with genre fields if we're going to be expanding subcategories
            if (self.is_checked("genre") and prefs['genre']['expand']):
                self.genre_fields = db.get_id_map(prefs['genre']['column']).values()

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
                column = prefs['narrator']['column']
                if (update_all or mi.is_null(column)):
                    if "narrator" in audio_tags:
                        mi.set(column, audio_tags['narrator'])
            if (self.is_checked("genre")):
                column = prefs['genre']['column']
                if (update_all or mi.is_null(column)):
                    if "genre" in audio_tags:
                        if prefs['genre']['expand']:
                            mi.set(column, self.expand_genre(audio_tags['genre']))
                        else:
                            mi.set(column, audio_tags['genre'])
            if (self.is_checked("duration")):
                column = prefs['duration']['column']
                if (update_all or mi.is_null(column)):
                    if (prefs['duration']['format'] == 'text'):
                        mi.set(column, playtime(audio_tags['duration']))
                    elif (prefs['duration']['format'] == 'int'):
                        mi.set(column, audio_tags['duration'])
            if (self.is_checked("bitrate")):
                column = prefs['bitrate']['column']
                if (update_all or mi.is_null(column)):
                    mi.set(column, audio_tags['bitrate'])
            if (self.is_checked("sample_rate")):
                column = prefs['sample_rate']['column']
                if (update_all or mi.is_null(column)):
                    mi.set(column, audio_tags['sample_rate'])
            if (self.is_checked("size")):
                column = prefs['size']['column']
                if (update_all or mi.is_null(column)):
                    if (prefs['size']['format'] == 'float'):
                        mi.set(column, audio_tags['size'] / (1024*1024))
                    elif (prefs['size']['format'] == 'int'):
                        mi.set(column, audio_tags['size'])
            if (self.is_checked("type")):
                column = prefs['type']['column']
                if (update_all or mi.is_null(column)):
                    mi.set(column, audio_tags['type'])
            if (self.is_checked("mode")):
                column = prefs['mode']['column']
                if (update_all or mi.is_null(column)):
                    mi.set(column, audio_tags['mode'])
            if (self.is_checked("num_files")):
                column = prefs['num_files']['column']
                if (update_all or mi.is_null(column)):
                    mi.set(column, audio_tags['num_files'])

            if (self.is_checked("cover")):
                if (update_all or mi.is_null("cover_data")):
                    cover = get_cover(audio_file_paths[0])
                    mi.set("cover_data", cover) # This is a ('type', 'data') tuple

            # Update the metadata
            self.db.set_metadata(book_id, mi)
            self.gui.library_view.model().refresh_ids([book_id])

        # Now set the current index back to it's current position again to trigger a window refresh
        current_idx = self.gui.library_view.currentIndex()
        if current_idx.isValid():
            self.gui.library_view.model().current_changed(current_idx, current_idx)

        self.progress_window.hide()
            
        info_dialog(self, 'Updated files',
                f'Updated the metadata in the files of {i} of {len(ids)} book(s)',
                show=True)
        
        #self.footest()

    def apply_settings(self):
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)        
        for field in all_items:
            if field.text() in ("cover", "title", "author"): # Never hidden
                continue
            field.setHidden(not prefs[field.text()]['enabled'])

    def footest(self):        
        column_types = ['float','int']
        custom_columns = self.gui.library_view.model().custom_columns
        print(f"custom_columns: {custom_columns}")
        available_columns = {}
        for key, column in custom_columns.items():
            typ = column['datatype']
            print(f"key: {key}, typ: {typ}, column: {column}")
            if typ in column_types:
                available_columns[key] = column

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        #self.label.setText(prefs['hello_world_msg'])
