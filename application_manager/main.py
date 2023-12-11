import sys
from enum import Enum, auto

from device import Device
from devices.nordic_ble.nordic_ble import NordicBLE
from devices.sample_device import SampleDevice
from devices.usb_test_device import USBTestDevice

from application_manager import ApplicationManager

# setup app manager
app_manager = ApplicationManager()
# app_manager.add_device(SampleDevice())
# app_manager.add_device(USBTestDevice())
app_manager.add_device(NordicBLE())


# main gui
class GuiType(Enum):
    PYSIDE6 = auto()
    KIVY = auto()

ACTIVE_GUI_TYPE: GuiType = GuiType.PYSIDE6
# ACTIVE_GUI_TYPE: GuiType = GuiType.KIVY


if ACTIVE_GUI_TYPE == GuiType.PYSIDE6:
    # import pyside6 and start gui
    from gui.gui_pyside.main_window import MainWindow
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

elif ACTIVE_GUI_TYPE == GuiType.KIVY:
    from gui.gui_kivy.main_app import MainApp
    MainApp().run()
else:
    print('Unknown/not implemented gui type, exiting')
    exit(0)
