from queue import Empty
from typing import Optional

from db_adaptors.txt_adaptor import TxtDBAdaptor
from device import Device
from devices.nordic_ble.nordic_ble import NordicBLE
from devices.ported_device import PortedDevice
from devices.sample_device import SampleDevice
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QPushButton,
                               QSplitter, QVBoxLayout, QWidget)

from application_manager import ApplicationManager

from .plot_widgets.gyro_plot_widget import GyroPlotWidget
from .plot_widgets.scrolling_list_plot_widget import ScrollingListPlotWidget
from .ported_device_custom_panel import PortedDeviceCustomPanel
from .sample_device_custom_panel import SampleDeviceCustomPanel
from .text_db_config_widget import TextDBConfigWidget


class MainWindow(QWidget):

    SUB_ID = 'pyqt_gui'
    
    def __init__(self):
        super().__init__()

        # GUI
        self.setWindowTitle('NRF5340 GUI')
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        self.device_layout = QVBoxLayout()
        device_panel = QWidget()
        device_panel.setLayout(self.device_layout)
        splitter.addWidget(device_panel)

        button = QPushButton()
        button.setText('Add')
        button.clicked.connect(self._on_add_button_clicked)
        self.device_layout.addWidget(button)

        self.device_layout.addStretch(1)

        graph_panel = QWidget()
        graph_layout = QVBoxLayout()
        graph_panel.setLayout(graph_layout)
        splitter.addWidget(graph_panel)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(self._on_combo_box_selected)
        graph_layout.addWidget(self.combo_box)

        graph_hsplit = QHBoxLayout()
        graph_layout.addLayout(graph_hsplit)

        # add two main plotting widgets
        self.channel_plot_widget = ScrollingListPlotWidget()
        for i in range(4, 12):
            channel_name = f'ch{i}'
            self.channel_plot_widget.add_channel(channel_name)
        self.channel_plot_widget.set_render_count(500)
        self.channel_plot_widget.set_time_range(5)
        graph_hsplit.addWidget(self.channel_plot_widget)

        self.gyro_plot_widget = GyroPlotWidget()
        self.gyro_plot_widget.set_render_count(500)
        self.gyro_plot_widget.set_time_range(5)
        graph_hsplit.addWidget(self.gyro_plot_widget)

        self.db_adaptor = TxtDBAdaptor()
        splitter.addWidget(TextDBConfigWidget(self.db_adaptor))


        data_refresh_timer = QTimer(self)
        data_refresh_timer.setSingleShot(False)
        data_refresh_timer.timeout.connect(self._on_timer)
        data_refresh_timer.start(100)
        
        # Manager
        app_manager = ApplicationManager.instance
        assert app_manager is not None

        self.connected_device_map = {}
        for device in app_manager.list_devices():
            self._add_device_gui(device)
            self.connected_device_map[device.get_name()] = device
        
        app_manager.event_device_added.subscribe(self._on_manager_device_added)
        app_manager.event_device_connected.subscribe(self._on_manager_device_connection_updated)
        app_manager.event_device_disconnected.subscribe(self._on_manager_device_connection_updated)

        # other
        self.active_device: Optional[Device] = None


    
    def _add_device_gui(self, device: Device):
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)

        if type(device) is SampleDevice:
            custom_panel = SampleDeviceCustomPanel(device)
        elif isinstance(device, PortedDevice):
            custom_panel = PortedDeviceCustomPanel(device)
        else:
            raise NotImplementedError(f'custom panel for device type {type(device)} is not implemented yet!')
        
        group_box_layout.addWidget(custom_panel)
        self.device_layout.insertWidget(1, group_box, 0)
    
    def _set_active_device(self, device: Device):
        ApplicationManager.get_instance().unsubscribe_all_device_data(self.SUB_ID)
        self.active_device = device

        # if it is sample device, auto subscribe the gyro data
        if isinstance(device, SampleDevice):
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_x', self.SUB_ID)
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_y', self.SUB_ID)
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_z', self.SUB_ID)
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_r1', self.SUB_ID)
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_r2', self.SUB_ID)
            ApplicationManager.get_instance().subscribe_device_data(device, 'gyro_r3', self.SUB_ID)
            for i in range(8):
                name = f'ch{i}'
                ApplicationManager.get_instance().subscribe_device_data(device, name, self.SUB_ID)        
        
        elif isinstance(device, NordicBLE):
            # enable 8 normal channels
            for i in range(4, 12):
                name = f'ch{i}'
                ApplicationManager.get_instance().subscribe_device_data(device, name, self.SUB_ID)

            # enable gyro channel
            for i in range(6):
                ApplicationManager.get_instance().subscribe_device_data(device, f"gyro{i}", self.SUB_ID)


        if device is not None:
            self.gyro_plot_widget.clear_plot()
            self.channel_plot_widget.clear_plot()
    
    # gui callbacks
    def _on_add_button_clicked(self):
        ApplicationManager.get_instance().add_device(SampleDevice())

    def _on_combo_box_selected(self, text: str):
        if text != '':
            self._set_active_device(self.connected_device_map[text])
        else:
            self._set_active_device(None)
    
    def _on_timer(self):
        if self.active_device is None:
            return
        
        if isinstance(self.active_device, SampleDevice):
            gyro_channel_connection_list = (
                ('gyro_x', 'x'),
                ('gyro_y', 'y'),
                ('gyro_z', 'z'),
                ('gyro_r1', 'r1'),
                ('gyro_r2', 'r2'),
                ('gyro_r3', 'r3'),
            )
            for source, destination in gyro_channel_connection_list:
                while True:
                    try:
                        xs, ys = ApplicationManager.get_instance().read_device_data(self.active_device, source, self.SUB_ID)
                    except Empty:
                        break
                    self.gyro_plot_widget.push_data(destination, xs, ys)
            self.gyro_plot_widget.redraw()

            for i in range(8):
                name = f'ch{i}'
                while True:
                    try:
                        xs, ys = ApplicationManager.get_instance().read_device_data(self.active_device, name, self.SUB_ID)
                    except Empty:
                        break
                    self.channel_plot_widget.push_data(name, xs, ys)
            self.channel_plot_widget.redraw()

        elif isinstance(self.active_device, NordicBLE):
            for i in range(4, 12):
                name = f'ch{i}'
                while True:
                    try:
                        xs, ys = ApplicationManager.get_instance().read_device_data(self.active_device, name, self.SUB_ID)
                    except Empty:
                        break
                    self.channel_plot_widget.push_data(name, xs, ys)
            self.channel_plot_widget.redraw()
            
            # gyro
            gyro_channel_map = (
                ('gyro0', 'x'),
                ('gyro1', 'y'),
                ('gyro2', 'z'),
                ('gyro3', 'r1'),
                ('gyro4', 'r2'),
                ('gyro5', 'r3'),
            )
            for gyro_ch_name, display_ch_name in gyro_channel_map:
                while True:
                    try:
                        xs, ys = ApplicationManager.get_instance().read_device_data(self.active_device, gyro_ch_name, self.SUB_ID)
                    except Empty:
                        break
                    self.gyro_plot_widget.push_data(display_ch_name, xs, ys)
            self.gyro_plot_widget.redraw()

    # manager callbacks
    def _on_manager_device_added(self, new_device: Device):
        self._add_device_gui(new_device)
    
    def _on_manager_device_connection_updated(self, device: Device):
        self.combo_box.clear()
        self.connected_device_map.clear()
        connected_devices = ApplicationManager.get_instance().list_connected_devices()
        for device in connected_devices:
            self.connected_device_map[device.get_name()] = device
            self.combo_box.addItem(device.get_name())

