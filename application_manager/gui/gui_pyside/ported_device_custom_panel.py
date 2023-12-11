

from typing import Optional

import PySide6.QtCore
from devices.ported_device import PortedDevice
from PySide6.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QWidget


class PortedDeviceCustomPanel(QWidget):
    def __init__(self, device: PortedDevice) -> None:
        super().__init__()
        self.device = device

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.combo = QComboBox()
        layout.addWidget(self.combo)

        refresh = QPushButton()
        refresh.setText('refresh')
        refresh.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(refresh)

        self.button = QPushButton()
        self.button.setText('Connect')
        layout.addWidget(self.button)

        self.button.clicked.connect(self._on_connect_clicked)
        self.device.event_connection_state_changed.subscribe(self._on_device_connection_status_changed)

    def _on_refresh_clicked(self):
        ports = self.device.scan_ports()
        self.combo.clear()
        self.combo.addItems(ports)
    
    def _on_connect_clicked(self):
        if self.device.is_connected():
            self.device.disconnect()
        else:
            self.device.connect(port=self.combo.currentText())

    def _on_device_connection_status_changed(self, new_status: bool):
        print('device connection status changed', new_status)
        self.button.setText('Disconnect' if new_status else 'Connect')
