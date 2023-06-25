__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

from qt.core import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QMetaObject, 
                     QGroupBox, QGridLayout, QRadioButton, QSpacerItem, QSizePolicy, QCheckBox,
                     QCoreApplication)

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/audio_m3u')

# Set defaults
prefs.defaults['narrator'] = { 'enabled' : False,
                               'column' : '',
                                'format' : 'text' }
prefs.defaults['duration'] = { 'enabled' : False,
                               'column' : '',
                               'format' : 'text' }
prefs.defaults['size'] = { 'enabled' : False,
                           'column' : '',
                           'format' : 'float' }
prefs.defaults['sample_rate'] = { 'enabled' : False,
                                  'column' : '',
                                  'format' : 'int' }
prefs.defaults['bitrate'] = { 'enabled' : False,
                              'column' : '',
                              'format' : 'int' }
prefs.defaults['mode'] = { 'enabled' : False,
                           'column' : '',
                           'format' : 'text' }
prefs.defaults['type'] = { 'enabled' : False,
                           'column' : '',
                           'format' : 'text' }
prefs.defaults['num_files'] = { 'enabled' : False,
                                'column' : '',
                                'format' : 'int' }
prefs.defaults['genre'] = { 'enabled' : False,
                            'column' : '',
                            'format' : 'text',
                            'expand' : True,
                            'trim' : True }
prefs.defaults['export_selected'] = []
prefs.defaults['import_selected'] = []

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initializeUI()

    def initializeUI(self):
        """
        Initialize the window and display its contents to the screen
        """
        self.setGeometry(100, 100, 500, 500)
        #self.setWindowTitle('Configure Audio M3U')
        self.setupWidgets()

    def setupWidgets(self):
        # Narrator
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.narratorGroupBox = QGroupBox(self)
        self.narratorGroupBox.setCheckable(True)
        self.narratorGroupBox.setChecked(False)
        self.narratorGroupBox.setObjectName("narratorGroupBox")
        self.narratorHLayout = QHBoxLayout(self.narratorGroupBox)
        self.narratorHLayout.setContentsMargins(-1, 1, -1, 1)
        self.narratorHLayout.setObjectName("narratorHLayout")
        self.narratorLabel = QLabel(self.narratorGroupBox)
        self.narratorLabel.setObjectName("narratorLabel")
        self.narratorHLayout.addWidget(self.narratorLabel)
        self.narratorLineEdit = QLineEdit(self.narratorGroupBox)
        self.narratorLineEdit.setObjectName("narratorLineEdit")
        self.narratorHLayout.addWidget(self.narratorLineEdit)
        self.verticalLayout.addWidget(self.narratorGroupBox)

        # Duration
        self.durationGroupBox = QGroupBox(self)
        self.durationGroupBox.setCheckable(True)
        self.durationGroupBox.setChecked(False)
        self.durationGroupBox.setObjectName("durationGroupBox")
        self.durationGridLayout = QGridLayout(self.durationGroupBox)
        self.durationGridLayout.setContentsMargins(-1, 1, -1, 1)
        self.durationGridLayout.setObjectName("durationGridLayout")
        self.durationLineEdit = QLineEdit(self.durationGroupBox)
        self.durationLineEdit.setObjectName("durationLineEdit")
        self.durationGridLayout.addWidget(self.durationLineEdit, 0, 1, 1, 1)
        self.durationLabel = QLabel(self.durationGroupBox)
        self.durationLabel.setObjectName("durationLabel")
        self.durationGridLayout.addWidget(self.durationLabel, 0, 0, 1, 1)
        self.durationHorizontalLayout = QHBoxLayout()
        self.durationHorizontalLayout.setObjectName("durationHorizontalLayout")
        self.hmmssRadioButton = QRadioButton(self.durationGroupBox)
        self.hmmssRadioButton.setChecked(True)
        self.hmmssRadioButton.setObjectName("hmmssRadioButton")
        self.durationHorizontalLayout.addWidget(self.hmmssRadioButton)
        self.totsecRadioButton = QRadioButton(self.durationGroupBox)
        self.totsecRadioButton.setObjectName("totsecRadioButton")
        self.durationHorizontalLayout.addWidget(self.totsecRadioButton)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.durationHorizontalLayout.addItem(spacerItem)
        self.durationGridLayout.addLayout(self.durationHorizontalLayout, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.durationGroupBox)

        # Size
        self.sizeGroupBox = QGroupBox(self)
        self.sizeGroupBox.setCheckable(True)
        self.sizeGroupBox.setObjectName("sizeGroupBox")
        self.sizeGridLayout = QGridLayout(self.sizeGroupBox)
        self.sizeGridLayout.setContentsMargins(-1, 1, -1, 1)
        self.sizeGridLayout.setObjectName("sizeGridLayout")
        self.sizeLabel = QLabel(self.sizeGroupBox)
        self.sizeLabel.setObjectName("sizeLabel")
        self.sizeGridLayout.addWidget(self.sizeLabel, 0, 0, 1, 1)
        self.sizeLineEdit = QLineEdit(self.sizeGroupBox)
        self.sizeLineEdit.setObjectName("sizeLineEdit")
        self.sizeGridLayout.addWidget(self.sizeLineEdit, 0, 1, 1, 1)
        self.sizeHLayout = QHBoxLayout()
        self.sizeHLayout.setObjectName("sizeHLayout")
        self.megsRadioButton = QRadioButton(self.sizeGroupBox)
        self.megsRadioButton.setChecked(True)
        self.megsRadioButton.setObjectName("megsRadioButton")
        self.sizeHLayout.addWidget(self.megsRadioButton)
        self.bytesRadioButton = QRadioButton(self.sizeGroupBox)
        self.bytesRadioButton.setObjectName("bytesRadioButton")
        self.sizeHLayout.addWidget(self.bytesRadioButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sizeHLayout.addItem(spacerItem1)
        self.sizeGridLayout.addLayout(self.sizeHLayout, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.sizeGroupBox)

        # Sample Rate
        self.sampleGroupBox = QGroupBox(self)
        self.sampleGroupBox.setCheckable(True)
        self.sampleGroupBox.setObjectName("sampleGroupBox")
        self.horizontalLayout = QHBoxLayout(self.sampleGroupBox)
        self.horizontalLayout.setContentsMargins(9, -1, 9, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sampleLabel = QLabel(self.sampleGroupBox)
        self.sampleLabel.setObjectName("sampleLabel")
        self.horizontalLayout.addWidget(self.sampleLabel)
        self.sampleLineEdit = QLineEdit(self.sampleGroupBox)
        self.sampleLineEdit.setObjectName("sampleLineEdit")
        self.horizontalLayout.addWidget(self.sampleLineEdit)
        self.verticalLayout.addWidget(self.sampleGroupBox)

        # Bitrate
        self.bitrateGroupBox = QGroupBox(self)
        self.bitrateGroupBox.setCheckable(True)
        self.bitrateGroupBox.setObjectName("bitrateGroupBox")
        self.bitrateHLayout = QHBoxLayout(self.bitrateGroupBox)
        self.bitrateHLayout.setContentsMargins(9, 1, 9, 1)
        self.bitrateHLayout.setObjectName("bitrateHLayout")
        self.bitrateLabel = QLabel(self.bitrateGroupBox)
        self.bitrateLabel.setObjectName("bitrateLabel")
        self.bitrateHLayout.addWidget(self.bitrateLabel)
        self.bitrateLineEdit = QLineEdit(self.bitrateGroupBox)
        self.bitrateLineEdit.setObjectName("bitrateLineEdit")
        self.bitrateHLayout.addWidget(self.bitrateLineEdit)
        self.verticalLayout.addWidget(self.bitrateGroupBox)

        # Mode
        self.modeGroupBox = QGroupBox(self)
        self.modeGroupBox.setCheckable(True)
        self.modeGroupBox.setObjectName("modeGroupBox")
        self.modeHLayout = QHBoxLayout(self.modeGroupBox)
        self.modeHLayout.setContentsMargins(-1, 1, -1, 1)
        self.modeHLayout.setObjectName("modeHLayout")
        self.modeLabel = QLabel(self.modeGroupBox)
        self.modeLabel.setObjectName("modeLabel")
        self.modeHLayout.addWidget(self.modeLabel)
        self.modeLineEdit = QLineEdit(self.modeGroupBox)
        self.modeLineEdit.setObjectName("modeLineEdit")
        self.modeHLayout.addWidget(self.modeLineEdit)
        self.verticalLayout.addWidget(self.modeGroupBox)

        # Type
        self.typeGroupBox = QGroupBox(self)
        self.typeGroupBox.setCheckable(True)
        self.typeGroupBox.setObjectName("typeGroupBox")
        self.typeHLayout = QHBoxLayout(self.typeGroupBox)
        self.typeHLayout.setContentsMargins(-1, 1, -1, 1)
        self.typeHLayout.setObjectName("typeHLayout")
        self.typeLabel = QLabel(self.typeGroupBox)
        self.typeLabel.setObjectName("typeLabel")
        self.typeHLayout.addWidget(self.typeLabel)
        self.typeLineEdit = QLineEdit(self.typeGroupBox)
        self.typeLineEdit.setObjectName("typeLineEdit")
        self.typeHLayout.addWidget(self.typeLineEdit)
        self.verticalLayout.addWidget(self.typeGroupBox)

        # Number of Files
        self.numfilesGroupBox = QGroupBox(self)
        self.numfilesGroupBox.setCheckable(True)
        self.numfilesGroupBox.setObjectName("numfilesGroupBox")
        self.numfilesHLayout = QHBoxLayout(self.numfilesGroupBox)
        self.numfilesHLayout.setContentsMargins(-1, 1, -1, 1)
        self.numfilesHLayout.setObjectName("nufilesHLayout")
        self.numfilesLabel = QLabel(self.numfilesGroupBox)
        self.numfilesLabel.setObjectName("numfilesLabel")
        self.numfilesHLayout.addWidget(self.numfilesLabel)
        self.numfilesLineEdit = QLineEdit(self.numfilesGroupBox)
        self.numfilesLineEdit.setObjectName("numfilesLineEdit")
        self.numfilesHLayout.addWidget(self.numfilesLineEdit)
        self.verticalLayout.addWidget(self.numfilesGroupBox)

        # Genre
        self.genreGroupBox = QGroupBox(self)
        self.genreGroupBox.setCheckable(True)
        self.genreGroupBox.setObjectName("genreGroupBox")
        self.gridLayout = QGridLayout(self.genreGroupBox)
        self.gridLayout.setContentsMargins(-1, 1, -1, 1)
        self.gridLayout.setObjectName("gridLayout")
        self.genreLabel = QLabel(self.genreGroupBox)
        self.genreLabel.setObjectName("genreLabel")
        self.gridLayout.addWidget(self.genreLabel, 0, 0, 1, 1)
        self.genreLineEdit = QLineEdit(self.genreGroupBox)
        self.genreLineEdit.setObjectName("genreLineEdit")
        self.gridLayout.addWidget(self.genreLineEdit, 0, 1, 1, 1)
        self.genreHorizontalLayout = QHBoxLayout()
        self.genreHorizontalLayout.setObjectName("genreHorizontalLayout")
        self.expandCheckBox = QCheckBox(self.genreGroupBox)
        self.expandCheckBox.setObjectName("expandCheckBox")
        self.genreHorizontalLayout.addWidget(self.expandCheckBox)
        self.trimCheckBox = QCheckBox(self.genreGroupBox)
        self.trimCheckBox.setObjectName("trimCheckBox")
        self.genreHorizontalLayout.addWidget(self.trimCheckBox)
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.genreHorizontalLayout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.genreHorizontalLayout, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.genreGroupBox)

        spacerItem3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)

        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

        self.configure_settings()

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Configure Audio M3U"))

        self.narratorGroupBox.setToolTip(_translate("Dialog", "The narrator of the audiobook.\n"
                                                    "Audio M3U assumes this is stored in the \'composer\' field in the audio file tag.\n"
                                                    "It is recommend that the column type is \'ampersand separated text\' so that multiple\n"
                                                    "narrators can be easily specified."))
        self.narratorGroupBox.setTitle(_translate("Dialog", "Narrator"))
        self.narratorLabel.setText(_translate("Dialog", "Custom Column:"))
        self.narratorLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#narrator\' This must be of text type."))

        self.durationGroupBox.setToolTip(_translate("Dialog", "This will store the total duration of all of the audiofiles\n"
                                                    "in the book. You can choose to store this as a text formatted string (H:MM:SS),\n"
                                                    "or as an integer with the total number of seconds."))
        self.durationGroupBox.setTitle(_translate("Dialog", "Duration"))
        self.durationLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#duration\' This must be either text or integer."))
        self.durationLabel.setText(_translate("Dialog", "Custom Column:"))
        self.hmmssRadioButton.setText(_translate("Dialog", "H:MM:SS (Text)"))
        self.totsecRadioButton.setText(_translate("Dialog", "Total seconds (Integer)"))

        self.sizeGroupBox.setToolTip(_translate("Dialog", "This stores the combined file size of all of the audiofiles in the book.\n"
                                                "You can choose to have this be a floating point value with the number of megabytes,\n"
                                                "or an integer with the total number of bytes. For megabytes it might be handy to define\n"
                                                 "the display format for the column to something like \'{0:.1f} MB\'"))
        self.sizeGroupBox.setTitle(_translate("Dialog", "Total Size"))
        self.sizeLabel.setText(_translate("Dialog", "Custom Column:"))
        self.sizeLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#size\' This must be floating point or integer."))
        self.megsRadioButton.setText(_translate("Dialog", "Megs (Floating Point)"))
        self.bytesRadioButton.setText(_translate("Dialog", "Bytes (Integer)"))

        self.sampleGroupBox.setToolTip(_translate("Dialog", "The sample rate of the file in hertz.\n"
                                                  "This is stored as an integer. Common values include 44100, 22050, 11025 etc. Generally\n"
                                                  "the higher the simple rate, the better the quality but the larger the file."))
        self.sampleGroupBox.setTitle(_translate("Dialog", "Sample Rate"))
        self.sampleLabel.setText(_translate("Dialog", "Custom Column:"))
        self.sampleLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#sample_rate\' Must be integer."))

        self.bitrateGroupBox.setToolTip(_translate("Dialog", "The bitrate that the files are encoded in, measured in kbps.\n"
                                                   "Generally the higher the bitrate, the higher the quality, but the larger the file.\n"
                                                   "It is recommended to configure the the display format of the column to something\n"
                                                   "like \'{0:d} kbps\' if desired."))
        self.bitrateGroupBox.setTitle(_translate("Dialog", "Bitrate"))
        self.bitrateLabel.setText(_translate("Dialog", "Custom Column:"))
        self.bitrateLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#bitrate\' Must be integer."))

        self.modeGroupBox.setToolTip(_translate("Dialog", "Stores the mode that the audiofiles were recorded in, for example \'stereo\', \n"
                                                "\'mono\', \'joint stereo\', etc."))
        self.modeGroupBox.setTitle(_translate("Dialog", "Mode"))
        self.modeLabel.setText(_translate("Dialog", "Custom Column:"))
        self.modeLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#mode\' Must be text type."))

        self.typeGroupBox.setToolTip(_translate("Dialog", "Stores the type of the audiofiles.\n"
                                                "Supported file types include \"MP3\", \"M4A\" and \"M4B\""))
        self.typeGroupBox.setTitle(_translate("Dialog", "File Type"))
        self.typeLabel.setText(_translate("Dialog", "Custom Column:"))
        self.typeLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#type\' Must be text type."))

        self.numfilesGroupBox.setToolTip(_translate("Dialog", "Stores the total number of audiofiles for the book in an integer field."))
        self.numfilesGroupBox.setTitle(_translate("Dialog", "# of Audio Files"))
        self.numfilesLabel.setText(_translate("Dialog", "Custom Column:"))
        self.numfilesLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#num_files\' This must be integer."))

        self.genreGroupBox.setToolTip(_translate("Dialog", "Stores the genre of the audiobook in a text field.\n"
                                                 "This can be a regular text field, or a 'comma separated text field' if you want to be\n"
                                                 "able to store more than one genre for a book. If you select 'Trim to Subgroup Export', only the\n"
                                                 "text to the right of the final '.' will be exported when heirarchical genres are used,\n"
                                                 "ex: Nonfiction.Science.Biology -> Biology\n"
                                                 "If you select 'Expand Subgroup on Import', then existing genres will be searched when\n"
                                                 "importing in an attempt to upconvert to the full hierarchy, \n"
                                                 "ex: Biology -> Nonfiction.Science.Biology"))
        self.genreGroupBox.setTitle(_translate("Dialog", "Genre"))
        self.genreLabel.setText(_translate("Dialog", "Custom Column:"))
        self.genreLineEdit.setPlaceholderText(_translate("Dialog", "ex. \'#genre\' Must be text type"))
        self.expandCheckBox.setText(_translate("Dialog", "Expand Subgroup on Import"))
        self.trimCheckBox.setText(_translate("Dialog", "Trim to Subgroup on Export"))

    def configure_settings(self):

        self.narratorGroupBox.setChecked(prefs['narrator']['enabled'])
        self.narratorLineEdit.setText(prefs['narrator']['column'])

        self.durationGroupBox.setChecked(prefs['duration']['enabled'])
        self.durationLineEdit.setText(prefs['duration']['column'])
        self.hmmssRadioButton.setChecked(prefs['duration']['format'] == 'text')
        self.totsecRadioButton.setChecked(prefs['duration']['format'] == 'int')

        self.sizeGroupBox.setChecked(prefs['size']['enabled'])
        self.sizeLineEdit.setText(prefs['size']['column'])
        self.megsRadioButton.setChecked(prefs['size']['format'] == 'float')
        self.bytesRadioButton.setChecked(prefs['size']['format'] == 'int')

        self.sampleGroupBox.setChecked(prefs['sample_rate']['enabled'])
        self.sampleLineEdit.setText(prefs['sample_rate']['column'])

        self.bitrateGroupBox.setChecked(prefs['bitrate']['enabled'])
        self.bitrateLineEdit.setText(prefs['bitrate']['column'])

        self.modeGroupBox.setChecked(prefs['mode']['enabled'])
        self.modeLineEdit.setText(prefs['mode']['column'])

        self.typeGroupBox.setChecked(prefs['type']['enabled'])
        self.typeLineEdit.setText(prefs['type']['column'])

        self.numfilesGroupBox.setChecked(prefs['num_files']['enabled'])
        self.numfilesLineEdit.setText(prefs['num_files']['column'])

        self.genreGroupBox.setChecked(prefs['genre']['enabled'])
        self.genreLineEdit.setText(prefs['genre']['column'])
        self.expandCheckBox.setChecked(prefs['genre']['expand'])
        self.trimCheckBox.setChecked(prefs['genre']['trim'])

    def save_settings(self):
        prefs['duration'] = { 'enabled' : self.durationGroupBox.isChecked(),
                              'column' : self.durationLineEdit.text(),
                              'format' : 'text' if self.hmmssRadioButton.isChecked() else 'int' }

        prefs['narrator'] = { 'enabled' : self.narratorGroupBox.isChecked(),
                              'column' : self.narratorLineEdit.text(),
                              'format' : 'text' }
        
        prefs['size'] = { 'enabled' : self.sizeGroupBox.isChecked(),
                          'column' : self.sizeLineEdit.text(),
                          'format' : 'float' if self.megsRadioButton.isChecked() else 'int' }
 
        prefs['sample_rate'] = { 'enabled' : self.sampleGroupBox.isChecked(),
                                 'column' : self.sampleLineEdit.text(),
                                 'format' : 'int' }
       
        prefs['bitrate'] = { 'enabled' : self.bitrateGroupBox.isChecked(),
                             'column' : self.bitrateLineEdit.text(),
                             'format' : 'int' }

        prefs['mode'] = { 'enabled' : self.modeGroupBox.isChecked(),
                          'column' : self.modeLineEdit.text(),
                          'format' : 'text' }
         
        prefs['type'] = { 'enabled' : self.typeGroupBox.isChecked(),
                          'column' : self.typeLineEdit.text(),
                          'format' : 'text'  }
        
        prefs['num_files'] = { 'enabled' : self.numfilesGroupBox.isChecked(),
                               'column' : self.numfilesLineEdit.text(),
                               'format' : 'int' }
        
        prefs['genre'] = { 'enabled' : self.genreGroupBox.isChecked(),
                           'column' : self.genreLineEdit.text(),
                           'format' : 'text',
                           'expand' : self.expandCheckBox.isChecked(),
                           'trim'   : self.trimCheckBox.isChecked() }       

