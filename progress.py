__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

from qt.core import QWidget, QProgressBar, QPushButton, QApplication, QVBoxLayout

class ProgressBarWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 500, 300, 30)
        self.setWindowTitle("Progress Bar")
        self.layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.cancel_button = QPushButton("Cancel")

        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.cancel_button)
        self.setLayout(self.layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()