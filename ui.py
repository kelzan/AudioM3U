__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

import os
import io

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
#from calibre_plugins.AudioM3U.main import DemoDialog
from calibre_plugins.AudioM3U.meta_in import ImportDialog
from calibre_plugins.AudioM3U.meta_out import ExportDialog
from calibre_plugins.AudioM3U.inspect import InspectDialog
from calibre_plugins.AudioM3U.validate import ValidateDialog

from calibre_plugins.AudioM3U.m3u_utils import create_m3u
from calibre.ebooks.metadata.book.base import Metadata

from calibre.gui2 import error_dialog, open_url
from qt.core import QToolButton, QFileDialog, QUrl

HELP_URL = 'https://github.com/kelzan/AudioM3U/wiki/Audio-M3U-Documentation'

class InterfacePlugin(InterfaceAction):

    name = 'Audio M3U'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('Audio M3U', None,
            'Work with audiobooks as M3U files', None)
    popup_type = QToolButton.MenuButtonPopup
    action_add_menu = True
    #action_menu_clone_qaction = "Export Metadata"

    def genesis(self):
        # This method is called once per plugin, do initial setup here

        # Set the icon for this interface action
        # The get_icons function is a builtin function defined for all your
        # plugin code. It loads icons from the plugin zip file. It returns
        # QIcon objects, if you want the actual data, use the analogous
        # get_resources builtin function.
        #
        # Note that if you are loading more than one icon, for performance, you
        # should pass a list of names to get_icons. In this case, get_icons
        # will return a dictionary mapping names to QIcons. Names that
        # are not found in the zip file will result in null QIcons.
        #icon = get_icons('images/icon.png', 'Audio M3U Plugin')
        icons = get_icons(["images/icon.png", "images/arrow.png", "images/arrow-180.png", "images/disc.png",
                           "images/plus.png", "images/question.png", "images/tick.png", "images/checkbox.png",
                           "images/magnifier.png"])

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setIcon(icons["images/icon.png"])
        self.qaction.triggered.connect(self.do_import)

        m = self.qaction.menu()
        self.create_menu_action(m, "m3u_import", "Import metadata...", icons["images/arrow.png"], 
                                None, "Import metadata from M3U audio files", self.do_import)    
        self.create_menu_action(m, "m3u_export", "Export metadata...", icons["images/arrow-180.png"], 
                                None, "Export metadata to M3U audio files", self.do_export)
        self.create_menu_action(m, "m3u_addm3u", "Create/Update M3U for book(s)...", icons["images/plus.png"], 
                                None, "Creates or updates M3U files for existing books", self.do_addm3u)
        self.create_menu_action(m, "m3u_createm3u", "Create new M3U book...", icons["images/disc.png"], 
                                None, "Creates an M3U file and adds it to library as a new book", self.do_createm3u)
        self.create_menu_action(m, "m3u_inspectm3u", "Inspect M3U...", icons["images/magnifier.png"],
                                None, "Inspects contents of M3U files", self.do_inspect)
        self.create_menu_action(m, "m3u_validate", "Validate M3U...", icons["images/tick.png"], 
                                None, "Validates M3U audio file paths", self.do_validate)
        self.create_menu_action(m, "m3u_customize", "Customize...", icons["images/checkbox.png"], 
                                None, "Customize Audio M3U plugin", self.do_customize)
        self.create_menu_action(m, "m3u_help", "Help", icons["images/question.png"], 
                                None, "Help", self.do_help)
        
        self.min_dlg = None # Placeholder for Metadata Import Dialog
        self.mout_dlg = None # Placeholder for Metadata Export Dialog
        self.validate_dlg = None # Placeholder for Validate Dialog
        self.inspect_dlg = None # Placeholder for Inspect Dialog


    def library_changed(self, db):
        #print("LIBRARY CHANGED!")
        if (self.min_dlg != None):
            self.min_dlg.db = db
        if (self.mout_dlg != None):
            self.mout_dlg.db = db
        if (self.validate_dlg != None):
            self.validate_dlg.db = db
        if (self.inspect_dlg != None):
            self.inspect_dlg.db = db

    def do_addm3u(self):
        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                             'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.gui.current_db.new_api

        id_cnt = 1
        for book_id in ids:
            mi = db.get_metadata(book_id, get_cover=False)
            title = mi.get("title", "Unknown")
            author = mi.get("authors",["Unknown"])
            #print(f"authors: {' & '.join(author)}")
            dialog_title = f"Add/Update M3U for \"{' & '.join(author)} - {title}\" ({id_cnt}/{len(ids)})"
            dirpath = str(QFileDialog.getExistingDirectory(self.gui, dialog_title))
            if (dirpath == ""):
                return # We pressed 'cancel'
            # Now scan the directory for audiofiles, and create M3U in memory
            m3u = create_m3u(dirpath)
            m3u_flat = "\n".join(m3u)

            # Skip if we don't find any audio files
            if (not len(m3u)):
                error_dialog(self.gui, 'Cannot add M3U','No audio files found in directory', show=True)
                continue

            # Create the map with Bytes data and Metadata for the new book
            #md = Metadata(title=booktitle)
            bb = m3u_flat.encode()
            bf = io.BytesIO(bb)

            # Add the new book to the library
            db = self.gui.current_db.new_api
            db.add_format(book_id, "M3U", bf)

            id_cnt += 1
            self.gui.library_view.model().refresh_ids([book_id])

        # Now mark the ids we updated
        self.gui.current_db.set_marked_ids(ids)

        # Now set the current index back to it's current position again to trigger a book detail panel refresh
        current_idx = self.gui.library_view.currentIndex()
        if current_idx.isValid():
            self.gui.library_view.model().current_changed(current_idx, current_idx)

    def do_createm3u(self):
        # Open Dialog window to get the directory
        dirpath = str(QFileDialog.getExistingDirectory(self.gui, "Select Directory containing audio files"))
        booktitle = os.path.basename(dirpath)
        print(f"dirpath: {dirpath}, title: {booktitle}")
        if (dirpath == ""):
            return # We pressed 'cancel'
        
        # Now scan the directory for audiofiles, and create M3U in memory
        m3u = create_m3u(dirpath)
        m3u_flat = "\n".join(m3u)

        if (not len(m3u)):
            return error_dialog(self.gui, 'Cannot add M3U','No audio files found in directory', show=True)

        # Create the map with Bytes data and Metadata for the new book
        md = Metadata(title=booktitle)
        bb = m3u_flat.encode()
        bf = io.BytesIO(bb) # Docs say that byte array should work, but only seems to work when I make it BytesIO object
        bookmap = [(md, {'M3U' : bf})]
        #print(f"{type(bookmap)}")
        
        # Add the new book to the library
        db = self.gui.current_db.new_api
        one, two = db.add_books(bookmap)

        # Now do a bunch of stuff to make the addition visible in the gui
        self.gui.current_db.data.books_added(one)
        self.gui.db_images.reset()
        self.gui.library_view.model().books_added(len(one))
        self.gui.library_view.set_current_row(0)
        self.gui.refresh_cover_browser()
        self.gui.tags_view.recount()

    def do_validate(self):
        #print("do validate")
        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        if (self.validate_dlg == None):
            # The base plugin object defined in __init__.py
            base_plugin_object = self.interface_action_base_plugin
            # Show the config dialog
            # The config dialog can also be shown from within
            # Preferences->Plugins, which is why the do_user_config
            # method is defined on the base plugin class
            do_user_config = base_plugin_object.do_user_config
            self.validate_dlg = ValidateDialog(self.gui, self.qaction.icon(), do_user_config)
        self.validate_dlg.show()

    def do_customize(self):
        #print("do customize")
        self.interface_action_base_plugin.do_user_config(self.gui)

    def do_help(self):
        #print("do_help")
        #db = self.gui.current_db.new_api
        #genremap = db.get_id_map('#genre').values()
        #print(f"genremap: {genremap}")
        open_url(QUrl(HELP_URL))

    # def show_dialog(self):
    #     # The base plugin object defined in __init__.py
    #     base_plugin_object = self.interface_action_base_plugin
    #     # Show the config dialog
    #     # The config dialog can also be shown from within
    #     # Preferences->Plugins, which is why the do_user_config
    #     # method is defined on the base plugin class
    #     do_user_config = base_plugin_object.do_user_config

    #     # self.gui is the main calibre GUI. It acts as the gateway to access
    #     # all the elements of the calibre user interface, it should also be the
    #     # parent of the dialog
    #     d = DemoDialog(self.gui, self.qaction.icon(), do_user_config)
    #     d.show()

    def do_import(self):
        # The base plugin object defined in __init__.py
        base_plugin_object = self.interface_action_base_plugin
        # Show the config dialog
        # The config dialog can also be shown from within
        # Preferences->Plugins, which is why the do_user_config
        # method is defined on the base plugin class
        do_user_config = base_plugin_object.do_user_config

        # If the columns don't check out, show error dialogs and exit
        if not self.validate_columns():
            return

        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        if (self.min_dlg == None):
            self.min_dlg = ImportDialog(self.gui, self.qaction.icon(), do_user_config)
        self.min_dlg.show()

    def do_export(self):
        # The base plugin object defined in __init__.py
        base_plugin_object = self.interface_action_base_plugin
        # Show the config dialog
        # The config dialog can also be shown from within
        # Preferences->Plugins, which is why the do_user_config
        # method is defined on the base plugin class
        do_user_config = base_plugin_object.do_user_config

        # If the columns don't check out, show error dialogs and exit
        if not self.validate_columns():
            return
        
        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        if (self.mout_dlg == None):
            self.mout_dlg = ExportDialog(self.gui, self.qaction.icon(), do_user_config)
        self.mout_dlg.show()

    def do_inspect(self):
        if (self.inspect_dlg == None):
            # The base plugin object defined in __init__.py
            base_plugin_object = self.interface_action_base_plugin
            # Show the config dialog
            # The config dialog can also be shown from within
            # Preferences->Plugins, which is why the do_user_config
            # method is defined on the base plugin class
            do_user_config = base_plugin_object.do_user_config

            # self.gui is the main calibre GUI. It acts as the gateway to access
            # all the elements of the calibre user interface, it should also be the
            # parent of the dialog
            self.inspect_dlg = InspectDialog(self.gui, self.qaction.icon(), do_user_config)
        if (self.inspect_dlg.init_data()):
            self.inspect_dlg.show()

    def validate_columns(self):
        from calibre.gui2 import error_dialog
        from calibre_plugins.AudioM3U.config import prefs
        columns = ["narrator", "duration", "size", "sample_rate", "bitrate", "mode", "type", "num_files", "genre"]
        custom_columns = self.gui.library_view.model().custom_columns
        #print(f"custom_columns: {custom_columns}")
        for column in columns:
            if prefs[column]['enabled']:
                colname = prefs[column]['column']
                coltype = prefs[column]['format']
                #print(f"Column type for '{column},' name: {colname}, type: {custom_columns[colname]['datatype']}")
                if not prefs[column]['column'] in custom_columns:
                    error_dialog(self.gui, 'Invalid custom column',
                                 f"Custom column configured for '{column}' does not exist: '{colname}'", show=True)
                    return False
                if custom_columns[colname]['datatype'] != coltype:
                    error_dialog(self.gui, 'Invalid custom column type',
                                     f"Custom column for '{column}' is type '{custom_columns[colname]['datatype']},' should be '{coltype}'",
                                     show=True)
                    return False
                    
        return True


    def apply_settings(self):
        from calibre_plugins.AudioM3U.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        #print("---> apply_settings()")
        if (self.min_dlg != None):
            self.min_dlg.apply_settings()
        if (self.mout_dlg != None):
            self.mout_dlg.apply_settings()
        prefs
