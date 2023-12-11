import sys

from application_manager import ApplicationManager
from devices.example_device import ExampleDevice

# these are gui imports
from PySide6.QtWidgets import QApplication
from gui.gui_pyside.main_window import MainWindow


# creat an app manager instance
app_manager = ApplicationManager()

# add your new device
device = ExampleDevice()
app_manager.add_device(device)

# start the gui
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
