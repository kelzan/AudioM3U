#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson <kelly@kellylarson.com>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.AudioM3U.main import DemoDialog
from calibre_plugins.AudioM3U.meta_in import ImportDialog
from calibre_plugins.AudioM3U.meta_out import ExportDialog


from qt.core import QToolButton, QMenu

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
                           "images/plus.png", "images/question.png", "images/tick.png", "images/checkbox.png"])

        # The qaction is automatically created from the action_spec defined
        # above
        self.qaction.setIcon(icons["images/icon.png"])
        #self.qaction.triggered.connect(self.show_dialog)
        self.qaction.triggered.connect(self.do_import)

        m = self.qaction.menu()
        self.create_menu_action(m, "m3u_import", "Import metadata", icons["images/arrow.png"], 
                                None, "Import metadata from M3U audio files", self.do_import)    
        self.create_menu_action(m, "m3u_export", "Export metadata", icons["images/arrow-180.png"], 
                                None, "Export metadata to M3U audio files", self.do_export)
        self.create_menu_action(m, "m3u_addm3u", "Add M3U to book", icons["images/plus.png"], 
                                None, "Creates an M3U file for existing book", self.do_addm3u)
        self.create_menu_action(m, "m3u_createm3u", "Create M3U", icons["images/disc.png"], 
                                None, "Creates an M3U file and adds to library as new book", self.do_createm3u)
        self.create_menu_action(m, "m3u_validate", "Validate M3U", icons["images/tick.png"], 
                                None, "Validates M3U audio file paths", self.do_validate)
        self.create_menu_action(m, "m3u_customize", "Customize", icons["images/checkbox.png"], 
                                None, "Customize Audio M3U plugin", self.do_customize)
        self.create_menu_action(m, "m3u_help", "Help", icons["images/question.png"], 
                                None, "Help", self.do_help)
        
        self.min_dlg = None # Placeholder for Metadata Import Dialog
        self.mout_dlg = None # Placeholder for Metadata Export Dialog

#    def do_import(self):
#        print("Do Import")

    # def do_export(self):
    #     print("Do Export")

    def do_addm3u(self):
        print("do addm3u")

    def do_createm3u(self):
        print("do createm3u")

    def do_validate(self):
        print("do validate")

    def do_customize(self):
        print("do customize")

    def do_help(self):
        print("do_help")


    def show_dialog(self):
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
        d = DemoDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def do_import(self):
        print("Do Import")
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
        if (self.min_dlg == None):
            self.min_dlg = ImportDialog(self.gui, self.qaction.icon(), do_user_config)
        self.min_dlg.show()

    def do_export(self):
        print("Do Export")
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
        if (self.mout_dlg == None):
            self.mout_dlg = ExportDialog(self.gui, self.qaction.icon(), do_user_config)
        self.mout_dlg.show()

    def apply_settings(self):
        from calibre_plugins.AudioM3U.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        print("---> apply_settings()")
        prefs
