from typing import Optional

from db_adaptors.txt_adaptor import TxtDBAdaptor
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QComboBox, QLabel, QFileDialog, QHBoxLayout,
                               QListWidget, QListWidgetItem, QPushButton,
                               QToolButton, QVBoxLayout, QWidget)

from application_manager import ApplicationManager


class TextDBConfigWidget(QWidget):
    def __init__(self, adaptor: TxtDBAdaptor) -> None:
        super().__init__()

        self._adaptor = adaptor
        self._combo_box_dict = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        folder_selector = FolderSelector()
        folder_selector.signal_on_folder_selected.connect(self._on_folder_selected)
        layout.addWidget(folder_selector)

        self.record_button = QPushButton()
        self.record_button.setText('Record')
        self.record_button.clicked.connect(self._on_record_clicked)
        layout.addWidget(self.record_button)

        field_ctl_layout = QHBoxLayout()
        layout.addLayout(field_ctl_layout)

        self.field_combo = QComboBox()
        field_ctl_layout.addWidget(self.field_combo)

        refresh_button = QToolButton()
        refresh_button.setText('R')
        refresh_button.clicked.connect(self._on_refresh_clicked)
        field_ctl_layout.addWidget(refresh_button)

        add_button = QToolButton()
        add_button.setText('+')
        add_button.clicked.connect(self._on_add_clicked)
        field_ctl_layout.addWidget(add_button)

        delete_button = QToolButton()
        delete_button.setText('-')
        delete_button.clicked.connect(self._on_delete_clicked)
        field_ctl_layout.addWidget(delete_button)

        add_all_button = QPushButton()
        add_all_button.setText('Add All')
        add_all_button.clicked.connect(self._on_add_all_clicked)
        layout.addWidget(add_all_button)

        self.list_view = QListWidget()
        layout.addWidget(self.list_view)

    def _on_refresh_clicked(self):
        self._do_refresh_combo_box()

    def _do_refresh_combo_box(self):
        # get all available channels
        devices = ApplicationManager.get_instance().list_connected_devices()
        self.field_combo.clear()
        self._combo_box_dict.clear()

        for device in devices:
            device_name = device.get_name()
            for channel in device.list_channels():
                string = f'{device_name}->{channel}'
                data = (device, channel)
                self.field_combo.addItem(string)
                self._combo_box_dict[string] = data
    
    def _on_add_clicked(self):
        selection = self.field_combo.currentText()
        self._try_add_channel(selection)

    def _try_add_channel(self, channel_text: str):
        if channel_text == '':
            return
        if len(self.list_view.findItems(channel_text, Qt.MatchFlag.MatchExactly)) > 0:
            return
        data = self._combo_box_dict[channel_text]
        item = QListWidgetItem(channel_text)
        item.device_channel_key = data
        self.list_view.addItem(item)
    
    def _on_add_all_clicked(self):
        self._do_refresh_combo_box()
        for text in self._combo_box_dict.keys():
            self._try_add_channel(text)
    
    def _on_delete_clicked(self):
        self.list_view.takeItem(self.list_view.currentRow())

    def _on_record_clicked(self):
        if self._adaptor.is_recording():
            self._adaptor.stop_recording()
            self.record_button.setText('Record')
        else:
            all_items = [self.list_view.item(x) for x in range(self.list_view.count())]
            active_channels = set()
            for item in all_items:
                active_channels.add(item.device_channel_key)
            subscribed_channels = self._adaptor.get_channels()

            for device, channel in active_channels.difference(subscribed_channels):
                self._adaptor.add_channel(device, channel)
            for device, channel in subscribed_channels.difference(active_channels):
                self._adaptor.remove_channel(device, channel)

            self._adaptor.start_recording()
            self.record_button.setText('Stop')
    
    def _on_folder_selected(self, new_folder):
        self._adaptor.set_output_folder(new_folder)


class FolderSelector(QWidget):
    signal_on_folder_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.select_directory)
        self.directory_label = QLabel('No directory selected')
        layout = QHBoxLayout()
        layout.addWidget(self.browse_button)
        layout.addWidget(self.directory_label)
        self.setLayout(layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory()
        if directory:
            self.directory_label.setText(directory)
            self.signal_on_folder_selected.emit(directory)
