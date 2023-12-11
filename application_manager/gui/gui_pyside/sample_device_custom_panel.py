from devices.sample_device import SampleDevice
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget


class SampleDeviceCustomPanel(QWidget):

    def __init__(self, device: SampleDevice) -> None:
        super().__init__()
        self.device = device
        self.device.event_connection_state_changed.subscribe(self.set_connected)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.text_edit = QLineEdit()
        layout.addWidget(self.text_edit)
        self.button = QPushButton()
        self.button.setText('Connect')
        layout.addWidget(self.button)

        self.button.clicked.connect(self._on_custom_gui_button_clicked)

        self.set_connected(self.device.is_connected())
    
    def set_connected(self, connected: bool):
        if connected:
            self.button.setText('Disconnect')
        else:
            self.button.setText('Connect')
    
    def _on_custom_gui_button_clicked(self):
        if(self.device.is_connected()):
            self.device.disconnect()
        else:
            self.device.connect(text_edit = self.text_edit.text())
