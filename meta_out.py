__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

# Import m3u handling utilities
from calibre_plugins.AudioM3U.m3u_utils import export_tags

from calibre_plugins.AudioM3U.progress import ProgressBarWindow

from qt.core import (QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QDialogButtonBox,
                     QGridLayout, QPushButton)
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs


class ExportDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.fields = ["cover", "title", "author", "genre", "narrator"]

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

    def setupWidgets(self):
        """
        Create widgets for metadata output GUI and arrange them in window
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
        checked_items = prefs['import_selected']
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
        prefs['import_selected'] = checked_items

    def accept(self):
        #print("ACCEPT!")
        self.export_metadata()
        #self.setWindowTitle('Whassup!')
        super().accept()
    
    def retranslateUi(self, ImportDialog):
        _translate = QCoreApplication.translate
        ImportDialog.setWindowTitle(_translate("ExportDialog", "Export Metadata"))
        self.top_label.setText(_translate("ExportDialog", "Metadata fields to export to audio files:"))

    def is_checked(self, label):
        found = self.field_list.findItems(label, Qt.MatchExactly)
        if (len(found) != 1):
            return False
        if found[0].isHidden():
            return False
        #print(f"{label} Found: {type(found)} {len(found)}")
        return found[0].checkState() == Qt.Checked

    def trim_genre(self, input_genre):
        if isinstance(input_genre, str):  # Handle a single string
            last_dot_index = input_genre.rfind('.')
            if last_dot_index != -1:
                return input_genre[last_dot_index + 1:]
            else:
                return input_genre
        elif isinstance(input_genre, list):  # Handle a list of strings
            return [self.trim_genre(string) for string in input_genre]
        else:
            raise TypeError("Input genre must be a string or a list of strings.")
        
    def get_audio_paths(self, book_id):
        db = self.db.new_api
        book_data = db.format(book_id, "M3U")
        m3u_text = book_data.decode("utf-8")
        lines = m3u_text.splitlines()
        lines = [line for line in lines if ((line != "") and (line[0] != '#'))]
        return lines

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

        # Initialize progress bar window
        self.progress_window.progress_bar.setRange(0,len(m3u_ids)-1)
        self.progress_window.show()
        self.stop_op = False
        i = 0

        for book_id in m3u_ids:
            # Update progress bar
            self.progress_window.update_progress(i)
            i += 1
            if (self.stop_op): # Did we press 'cancel' from the progress bar?
                break
            
            # Get the paths for the audio files from the M3U file
            audio_file_paths = self.get_audio_paths(book_id)
            if (not len(audio_file_paths)):
                continue            
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            # Now determine which fields, based on config and options, need to be updated
            export_fields = list(filter(lambda x: (self.is_checked(x)),self.fields))

            export_meta = {}
            #print(f"export_fields: {export_fields}")
            for field in export_fields:
                if ((field == "author") and (not mi.is_null("authors"))):
                    export_meta["author"] = " & ".join(mi.get("authors"))
                if ((field == "title") and (not mi.is_null("title"))):
                    export_meta["title"] = mi.get("title")
                if (field == "narrator"):
                    column = prefs['narrator']['column']
                    if not mi.is_null(column):
                        #print(f"Getting narrator {column}: {mi.get(column)} type {type(mi.get(column))}")
                        # Support either ampersand separated names (list), or straight text field for narrator
                        if type(mi.get(column)) == list:
                            export_meta["narrator"] = " & ".join(mi.get(column))
                        elif type(mi.get(column)) == str:
                            export_meta["narrator"] = mi.get(column)
                if (field == "genre"):
                    column = prefs['genre']['column']
                    if not mi.is_null(column):
                        # Support either multiple genres (list), or straight text field for genre
                        if (prefs['genre']['trim']):
                            gen_export = self.trim_genre(mi.get(column))
                        else:
                            gen_export = mi.get(column)
                        if type(gen_export) == list:
                            export_meta["genre"] = ", ".join(gen_export)
                            #print("GENRE LIST")
                        elif type(gen_export) == str:
                            export_meta["genre"] = gen_export
                            #print("GENRE STR")
                if ((field == "cover") and (not mi.is_null("cover_data"))):
                    export_meta["cover"] = mi.get("cover_data")
            #print(f"export_meta: {export_meta}")
            export_tags(audio_file_paths, export_meta)
            
        # Hide the progress bar
        self.progress_window.hide()

        info_dialog(self, 'Updated audio files',
                f'Exported the metadata to the audio files for {i} of {len(ids)} book(s)',
                show=True)

    def apply_settings(self):
        all_items = self.field_list.findItems('', Qt.MatchRegularExpression)        
        for field in all_items:
            if field.text() in ("cover", "title", "author"): # Never hidden
                continue
            field.setHidden(not prefs[field.text()]['enabled'])

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])
