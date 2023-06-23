__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

import sys
import os


from qt.core import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QPlainTextEdit, QCheckBox, QPushButton, 
                     QSpacerItem, QSizePolicy, QRadioButton)
from PyQt5.QtCore import (Qt, QCoreApplication, QMetaObject)

from calibre_plugins.AudioM3U.config import prefs

from calibre_plugins.AudioM3U.progress import ProgressBarWindow


class ValidateDialog(QDialog):

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
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Validate M3U Files')
        self.setupWidgets()

    def setupWidgets(self):
        # Vertical Layout
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        # Text Edit Widget
        self.plainTextEdit = QPlainTextEdit(self)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        # Option Group Box
        self.optionGroupBox = QGroupBox(self)
        #sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.optionGroupBox.sizePolicy().hasHeightForWidth())
        #self.optionGroupBox.setSizePolicy(sizePolicy)
        self.optionGroupBox.setObjectName("optionGroupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.optionGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        # Check Invalid Paths Check Box
        self.invalidCheckBox = QCheckBox(self.optionGroupBox)
        self.invalidCheckBox.setToolTip("Now is the time to have a whats this string")
        self.invalidCheckBox.setChecked(True)
        self.invalidCheckBox.setObjectName("invalidCheckBox")
        self.horizontalLayout_2.addWidget(self.invalidCheckBox)
        # Check for duplicates Check Box
        self.duplicateCheckBox = QCheckBox(self.optionGroupBox)
        self.duplicateCheckBox.setWhatsThis("")
        self.duplicateCheckBox.setObjectName("duplicateCheckBox")
        self.horizontalLayout_2.addWidget(self.duplicateCheckBox)
        # Mark Issues Check Box
        self.markissuesCheckBox = QCheckBox(self.optionGroupBox)
        self.markissuesCheckBox.setWhatsThis("")
        self.markissuesCheckBox.setChecked(True)
        self.markissuesCheckBox.setObjectName("markissuesCheckBox")
        self.horizontalLayout_2.addWidget(self.markissuesCheckBox)
        # Horizontal Spacer for Options Box
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.optionGroupBox)
        # Search Scope Group Box
        self.scopeGroupBox = QGroupBox(self)
        self.scopeGroupBox.setObjectName("scopeGroupBox")
        self.horizontalLayout_3 = QHBoxLayout(self.scopeGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        # Selected Radio Button
        self.selectedRadioButton = QRadioButton(self.scopeGroupBox)
        self.selectedRadioButton.setChecked(True)
        self.selectedRadioButton.setObjectName("selectedRadioButton")
        self.horizontalLayout_3.addWidget(self.selectedRadioButton)
        # Library Radio Button
        self.libraryRadioButton = QRadioButton(self.scopeGroupBox)
        self.libraryRadioButton.setObjectName("libraryRadioButton")
        self.horizontalLayout_3.addWidget(self.libraryRadioButton)
        # Horizontal Spacer for Scope Box
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.scopeGroupBox)
        # Bottom Button Box
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        # Search Button
        self.validateButton = QPushButton(self)
        self.validateButton.setObjectName("validateButton")
        self.horizontalLayout.addWidget(self.validateButton)
        # Done Button
        self.doneButton = QPushButton(self)
        self.doneButton.setObjectName("doneButton")
        self.horizontalLayout.addWidget(self.doneButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        # Connect button actions
        self.doneButton.clicked.connect(self.do_done)
        self.validateButton.clicked.connect(self.do_validate)

        # Progress Bar Window
        self.progress_window = ProgressBarWindow()
        self.progress_window.cancel_button.clicked.connect(self.set_stop)

        self.stop_op = False
        
    def set_stop(self):
        self.stop_op = True

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        #Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.optionGroupBox.setTitle(_translate("Dialog", "Search Options"))
        self.invalidCheckBox.setText(_translate("Dialog", "Check for invalid paths"))
        self.duplicateCheckBox.setText(_translate("Dialog", "Check for duplicates"))
        self.markissuesCheckBox.setText(_translate("Dialog", "Mark found issues"))
        self.scopeGroupBox.setTitle(_translate("Dialog", "Search Scope"))
        self.selectedRadioButton.setText(_translate("Dialog", "Selected books"))
        self.libraryRadioButton.setText(_translate("Dialog", "Library"))
        self.validateButton.setText(_translate("Dialog", "Validate"))
        self.doneButton.setText(_translate("Dialog", "Done"))

    def get_title(self, book_id):
        db = self.db.new_api
        author = db.field_for('authors',book_id)
        title = db.field_for('title',book_id)
        return(f"{' & '.join(author)} - {title}")

    def do_validate(self):
        from calibre.gui2 import error_dialog
        db = self.db.new_api
        if (self.selectedRadioButton.isChecked()):
            # Get currently selected books
            rows = self.gui.library_view.selectionModel().selectedRows()
            if not rows or len(rows) == 0:
                return error_dialog(self.gui, 'Cannot complete validation',
                                'No books selected', show=True)
            # Map the rows to book ids
            ids = list(map(self.gui.library_view.model().id, rows))
        else:
            ids = db.all_book_ids()

        # Filter list to contain only books with M3U format
        #print(f"ids: {ids}")
        m3u_ids = list(filter(lambda x: (db.has_format(x, "M3U")), ids))

        # Initialize progress bar window
        show_progress = (len(m3u_ids)>10) # Only show progress dialog if we're updating enough books
        if (show_progress):
            self.progress_window.progress_bar.setRange(0,len(m3u_ids)-1)
            self.progress_window.show()

        self.stop_op = False
        invalid_ids = set(())
        dup_ids = set(())
        book_cnt = 0
        path_cnt = 0
        badpath_cnt = 0
        duppath_cnt = 0
        all_paths = {}
        for book_id in m3u_ids:
            # Update the progress bar
            if (show_progress):
                self.progress_window.update_progress(book_cnt)
            book_cnt += 1
            if (self.stop_op): # Did we press 'cancel' from the progress bar?
                break
            
            book_dups = set(())
            last_dup_id = 0
            # Get M3U data for book_id, convert to list of strings
            book_data = db.format(book_id, "M3U")
            m3u_text = book_data.decode("utf-8")
            m3u_text = m3u_text.replace('\\','/') # Normalize direction of slash
            lines = m3u_text.splitlines()
            for line in lines:
                if ((line == "") or (line[0] == '#')): # Skip blank lines and comments
                    continue
                path_cnt += 1
                if (self.invalidCheckBox.isChecked()):
                    if (not os.path.isfile(line)):
                        badpath_cnt += 1
                        if (book_id not in invalid_ids):
                            invalid_ids.add(book_id)
                            self.plainTextEdit.appendPlainText(f"Invalid paths for ID {book_id}: {self.get_title(book_id)}")
                        self.plainTextEdit.appendPlainText(f"     {line}")
                if (self.duplicateCheckBox.isChecked()):
                    if line in all_paths: # Did we find a dup?
                        duppath_cnt += 1
                        dup_ids.add(book_id) # Add current book_id to list
                        dup_id = all_paths[line]
                        if (dup_id != last_dup_id):
                            dup_ids.add(dup_id) # Add discovered dup to list
                            last_dup_id = dup_id
                            self.plainTextEdit.appendPlainText(f"Duplicate paths for ID {dup_id}: {self.get_title(dup_id)} and ID {book_id}: {self.get_title(book_id)}")
                        self.plainTextEdit.appendPlainText(f"     {line}")
                    else:
                        all_paths[line] = book_id


        #print(f"bad_ids: f{invalid_ids.union(dup_ids)}")
        self.progress_window.hide()
        # Append a Post-Validate summary
        self.plainTextEdit.appendPlainText(f"Checked {path_cnt} paths in {book_cnt} books")
        if (self.invalidCheckBox.isChecked()):
            self.plainTextEdit.appendPlainText(f"{badpath_cnt} invalid paths found in {len(invalid_ids)} books")
        if (self.duplicateCheckBox.isChecked()):
            self.plainTextEdit.appendPlainText(f"{duppath_cnt} duplicate paths found in {len(dup_ids)} books")

        # Mark issues if configured
        if (self.markissuesCheckBox.isChecked() and ((len(invalid_ids)>0) or (len(dup_ids)>0))):
            # Now mark the ids we updated
            self.gui.current_db.set_marked_ids(invalid_ids.union(dup_ids))
            # Tell the GUI to search for all marked records
            self.gui.search.setEditText('marked:true')
            self.gui.search.do_search()

    def do_done(self):
        self.plainTextEdit.clear()
        self.accept()